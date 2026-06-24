"""Shared data-loader plumbing: grid, cache, readers, dispatcher.

One public surface per dataset: ``datasets/<dataset_id>.py`` exposes ``load(grid, **kw)``
returning a grid-aligned ``xarray.DataArray`` (raster) or a ``GeoDataFrame`` (vector, e.g.
boundaries). Everything those loaders share — pulling from Earth Engine, reading a COG,
reprojecting to the run grid, on-disk caching — lives here.

Two on-disk locations, both gitignored (see ``.gitignore`` ``data/`` + ``.cache/``):
- ``DATA_DIR`` (``data/``)        — persistent full datasets we can't stream (downloaded once).
- ``CACHE_DIR`` (``.cache/data``) — normalised, grid-aligned outputs, so reruns don't re-hit
  GEE / cloud sources during local dev. Delete the dir to invalidate.
"""

from __future__ import annotations

import hashlib
import importlib
import os
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

import geopandas as gpd
import rioxarray  # noqa: F401  (registers the .rio accessor)
import xarray as xr
from rasterio.enums import Resampling
from rasterio.transform import from_bounds

DATA_DIR = Path(os.environ.get("NBS_DATA_DIR", "data"))
CACHE_DIR = Path(os.environ.get("NBS_CACHE_DIR", ".cache/data"))


@dataclass(frozen=True)
class TargetGrid:
    """The AOI grid every raster loader snaps to. ``res`` is in ``crs`` units."""

    bounds: tuple[float, float, float, float]  # minx, miny, maxx, maxy
    crs: str = "EPSG:4326"
    res: float = (
        0.0083333  # ~1 km in degrees; pass metres + a metric crs for projected runs
    )
    resampling: str = "bilinear"
    geometry: object = field(
        default=None, compare=False
    )  # optional shapely mask; bbox if None

    @property
    def shape(self) -> tuple[int, int]:
        minx, miny, maxx, maxy = self.bounds
        return round((maxy - miny) / self.res), round((maxx - minx) / self.res)

    @property
    def transform(self):
        h, w = self.shape
        return from_bounds(*self.bounds, w, h)

    @property
    def key(self) -> str:
        b = tuple(
            round(float(x), 6) for x in self.bounds
        )  # plain floats, numpy-repr-free
        return f"{self.crs}_{b}_{self.res}"

    def match(self, da: xr.DataArray) -> xr.DataArray:
        """Reproject/clip ``da`` onto this grid. Idempotent enough to call unconditionally."""
        h, w = self.shape
        out = da.rio.reproject(
            self.crs,
            shape=(h, w),
            transform=self.transform,
            resampling=Resampling[self.resampling],
        )
        if self.geometry is not None:
            out = out.rio.clip([self.geometry], self.crs)
        return out


# --- shared readers -------------------------------------------------------------


def download(url: str, name: str | None = None) -> Path:
    """Fetch ``url`` into DATA_DIR once; return the local path. stdlib only."""
    p = DATA_DIR / (name or url.split("/")[-1].split("?")[0])
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, p)
    return p


def read_raster(src, grid: TargetGrid, band=None) -> xr.DataArray:
    """Open a local/remote COG/GeoTIFF/NetCDF and snap it to ``grid``."""
    da = rioxarray.open_rasterio(src, masked=True)
    assert isinstance(
        da, xr.DataArray
    )  # single-band/file path; not a multi-subdataset NetCDF
    if band is not None:
        da = da.sel(band=band) if "band" in da.dims else da
    return grid.match(da)


def ee_to_xarray(image, grid: TargetGrid) -> xr.DataArray:
    """Materialise a (possibly server-side-computed) ``ee.Image`` onto ``grid`` via xee."""
    import ee  # lazy: heavy import + needs auth

    bounds = ee.Geometry.Rectangle(list(grid.bounds), proj=grid.crs, geodesic=False)
    ds = xr.open_dataset(
        ee.ImageCollection([image]),  # ty: ignore[invalid-argument-type]  (xee custom engine)
        engine="ee",
        geometry=bounds,
        scale=grid.res,
        crs=grid.crs,
    )
    # one-image collection -> drop the singleton time dim, take the lone band as a DataArray
    da = ds.isel(time=0).to_dataarray().squeeze()
    return grid.match(da)


# --- provenance + cache ---------------------------------------------------------


def _stamp(da: xr.DataArray, dataset_id: str) -> xr.DataArray:
    # Only dataset_id — everything else (citation, license, ...) is recoverable from T1.
    da.attrs["dataset_id"] = dataset_id
    return da


def _cache_key(dataset_id: str, grid: TargetGrid | None, kw: dict) -> str:
    raw = f"{dataset_id}|{grid.key if grid else ''}|{sorted(kw.items())}"
    return f"{dataset_id}__{hashlib.sha1(raw.encode()).hexdigest()[:8]}"


def load(dataset_id: str, grid: TargetGrid | None = None, **kw):
    """Dispatch to ``datasets/<dataset_id>.load`` with disk caching + provenance.

    Raster loaders take ``grid``; vector loaders (boundaries) ignore it and use kwargs
    like ``region`` / ``level``. Caching keys on dataset + grid + kwargs.
    """
    key = _cache_key(dataset_id, grid, kw)
    cog, pq = CACHE_DIR / f"{key}.tif", CACHE_DIR / f"{key}.parquet"
    if cog.exists():
        da = rioxarray.open_rasterio(
            cog, masked=True
        )  # dataset_id read back from GDAL tags
        assert isinstance(da, xr.DataArray)
        return da
    if pq.exists():
        return gpd.read_parquet(pq)

    mod = importlib.import_module(f"{__package__}.datasets.{dataset_id}")
    result = mod.load(grid=grid, **kw)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if isinstance(result, xr.DataArray):
        result = _stamp(result, dataset_id)
        # dataset_id -> GDAL metadata tag, so it survives the COG round-trip
        result.rio.to_raster(cog, driver="COG", tags={"dataset_id": dataset_id})
    elif isinstance(result, gpd.GeoDataFrame):
        result.to_parquet(pq)
    return result
