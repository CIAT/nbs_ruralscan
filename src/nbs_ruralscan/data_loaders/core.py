"""Shared data-loader plumbing: target (AOI/GeoBox), cache, readers, dispatcher.

One public surface per dataset: ``datasets/<dataset_id>.py`` exposes ``load(target, **kw)``
returning an ``xarray.DataArray`` (raster) or a ``GeoDataFrame`` (vector, e.g. boundaries).
Everything those loaders share — pulling from Earth Engine, reading a COG, clipping to the
AOI, reprojecting to a grid, on-disk caching — lives here.

**Native is the default; the MCDA grid is opt-in.** Most data is *not* headed for the MCDA:
admin extraction, map display, and other pipelines just want the dataset's own pixels inside
a bbox, untouched. So a loader's target is normally an :class:`AOI` (bbox + optional polygon,
native resolution, NO resampling). Only when layers must be pixel-aligned for stacking/MCDA
do you pass an :class:`odc.geo.geobox.GeoBox` (a CRS + resolution + extent), which reprojects
onto that grid. Combining several native layers, then resampling the *combination* once, is
the intended flow — you never pay to resample every input up to a fine grid first.

Reprojection/grid algebra is delegated to **odc-geo** (the Open Data Cube ``GeoBox`` +
``.odc`` accessor) — dask-lazy, CRS-correct, the ecosystem standard — rather than hand-rolled.
rioxarray still does IO + native ``clip_box``; obstore does zarr IO. They compose.

**Lazy by default (Pangeo/ARCO norm).** Every source opens dask-chunked (``chunks=``), so
``load`` returns a graph that computes nothing — combine several native layers and resample
the *combination* once, materialising only at the last minute.

**The library does not cache computed results** — checkpointing an extract (e.g. a GEE pull)
is the analysis pipeline's job (``da.to_zarr(run_dir/...)`` / ``.persist()``), kept out of
here so the package stays reusable and side-effect-free. It writes to disk only to acquire
**non-streamable sources**: ``DATA_DIR`` (``data/``, gitignored) holds files we must download
to read — e.g. the WB boundaries GeoPackage → its GeoParquet store.
"""

from __future__ import annotations

import importlib
import os
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

import odc.geo.xr  # noqa: F401  (registers the .odc accessor)
import rioxarray  # noqa: F401  (registers the .rio accessor)
import xarray as xr
from odc.geo.geobox import GeoBox

DATA_DIR = Path(
    os.environ.get("NBS_DATA_DIR", "data")
)  # downloaded non-streamable sources


@dataclass(frozen=True)
class AOI:
    """An area to extract — a bbox (+ optional polygon mask) in ``crs``, at the data's
    NATIVE resolution. The default loader target: most data just wants its own pixels inside
    a bbox, untouched (admin extraction, map display, non-MCDA pipelines). No resampling.
    Pass a :class:`~odc.geo.geobox.GeoBox` instead only when layers must align (MCDA/stacking).
    """

    bounds: tuple[float, float, float, float]  # minx, miny, maxx, maxy (in `crs`)
    crs: str = "EPSG:4326"
    geometry: object = field(
        default=None, compare=False
    )  # optional shapely mask; bbox only if None

    @classmethod
    def from_region(cls, region: str | list[str]) -> AOI:
        """Build an AOI from World Bank **country** boundaries (ISO3) — bbox + dissolved
        polygon mask, so a native extract is clipped to the country outline, not just its
        box. ``region`` is one ISO3 or a list (unioned into one mask).

        Country-level only: a sub-national province would need a name/code selector, not an
        admin level (unioning all admin1s just rebuilds the country). For a sub-national or
        otherwise custom area, build ``AOI(bounds=..., geometry=<polygon>)`` directly from
        any shapely geometry (a watershed, a TTL project area, an uploaded boundary)."""
        gdf = load("wb_admin_boundaries", region=region)  # level 0 (countries)
        minx, miny, maxx, maxy = gdf.total_bounds
        return cls(
            bounds=(minx, miny, maxx, maxy),
            crs=str(gdf.crs) if gdf.crs else "EPSG:4326",
            geometry=gdf.geometry.union_all(),  # one mask if region spans many countries
        )

    def clip(self, da: xr.DataArray) -> xr.DataArray:
        """Extract ``da`` to the AOI at native resolution — bbox window (bounds taken in
        ``self.crs``) + optional polygon mask. NO reproject/resample."""
        out = da.rio.clip_box(*self.bounds, crs=self.crs)
        if self.geometry is not None:
            out = out.rio.clip([self.geometry], self.crs)
        return out


def target_bounds(
    target: AOI | GeoBox,
) -> tuple[tuple[float, float, float, float], str]:
    """``((minx, miny, maxx, maxy), crs)`` for an AOI or GeoBox — used to pre-window a global
    source (e.g. a zarr cube) before reading, so only the AOI's chunks transfer."""
    if isinstance(target, GeoBox):
        bb = target.boundingbox
        return (bb.left, bb.bottom, bb.right, bb.top), str(bb.crs)
    return target.bounds, target.crs


def to_target(
    da: xr.DataArray, target: AOI | GeoBox, resampling: str = "bilinear"
) -> xr.DataArray:
    """Bring native data onto the requested target. A bare :class:`AOI` clips to native
    resolution (no resample); a ``GeoBox`` reprojects onto the grid (odc-geo, dask-lazy).
    Native is the default — MCDA (the grid) is the special case. ``resampling`` applies only
    to the grid case (set it for categorical/fractional data — see ``datasets`` docstring)."""
    if isinstance(target, GeoBox):
        return da.odc.reproject(target, resampling=resampling)
    return target.clip(da)


# --- shared readers -------------------------------------------------------------


def download(url: str, name: str | None = None) -> Path:
    """Fetch ``url`` into DATA_DIR once; return the local path. stdlib only.

    Downloads to a sibling ``.part`` then atomically renames, so an interrupted
    transfer never leaves a truncated file that ``p.exists()`` would trust.
    """
    p = DATA_DIR / (name or url.split("/")[-1].split("?")[0])
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_name(p.name + ".part")
        urllib.request.urlretrieve(url, tmp)
        tmp.replace(p)
    return p


def read_raster(
    src, target: AOI | GeoBox, band=None, resampling: str = "bilinear"
) -> xr.DataArray:
    """Open a local/remote COG/GeoTIFF/NetCDF and bring it onto ``target`` (see ``to_target``):
    native clip for an AOI, reproject for a GeoBox.

    ``resampling`` is used only in the grid case — set it for categorical/fractional data;
    the default suits continuous rasters.
    """
    da = rioxarray.open_rasterio(src, masked=True, chunks=True)  # dask-lazy, per-block
    assert isinstance(
        da, xr.DataArray
    )  # single-band/file path; not a multi-subdataset NetCDF
    if band is not None:
        da = da.sel(band=band) if "band" in da.dims else da
    return to_target(da, target, resampling=resampling)


def ee_to_xarray(
    image,
    target: AOI | GeoBox,
    resampling: str = "bilinear",
    native_scale: float | None = None,
) -> xr.DataArray:
    """Materialise a (possibly server-side-computed) ``ee.Image`` over ``target`` via xee.

    EE always resamples server-side to the scale it's asked for, so a bare AOI needs an
    explicit ``native_scale`` (the asset's native resolution); a GeoBox uses its resolution.
    ``resampling`` applies only to the final grid snap.
    """
    import ee  # lazy: heavy import + needs auth

    (minx, miny, maxx, maxy), crs = target_bounds(target)
    scale = target.resolution.x if isinstance(target, GeoBox) else native_scale
    if scale is None:
        raise ValueError(
            "ee_to_xarray: a bare AOI needs native_scale (EE pulls at a fixed scale)"
        )
    bounds = ee.Geometry.Rectangle([minx, miny, maxx, maxy], proj=crs, geodesic=False)
    ds = xr.open_dataset(
        ee.ImageCollection([image]),  # ty: ignore[invalid-argument-type]  (xee custom engine)
        engine="ee",
        geometry=bounds,
        scale=abs(scale),
        crs=crs,
    )
    # one-image collection -> drop the singleton time dim, take the lone band as a DataArray
    da = ds.isel(time=0).to_dataarray().squeeze()
    return to_target(da, target, resampling=resampling)


# --- dispatcher -----------------------------------------------------------------


def load(dataset_id: str, target: AOI | GeoBox | None = None, **kw):
    """Dispatch to ``datasets/<dataset_id>.load(target=...)``. **Pure and lazy** — returns a
    dask-backed graph that computes nothing until the caller materialises it.

    Pass an :class:`AOI` for a native bbox/polygon extract (the default — admin extraction,
    map display, non-MCDA pipelines); pass a ``GeoBox`` only when the layer must align to a
    common analysis grid (MCDA/stacking). Vector loaders (boundaries) ignore ``target`` and
    use kwargs like ``region`` / ``level``.

    **Caching is the analysis layer's job, not the library's** — combine native layers, then
    at the last minute the pipeline checkpoints with ``.to_zarr(run_dir/...)`` / ``.persist()``
    (worth it mainly for GEE, where a re-pull is slow + quota'd), or the opt-in
    :func:`~nbs_ruralscan.data_loaders.checkpoint.checkpoint` decorator (caller's dir). The
    library stays side-effect-free so it's reusable across pipelines.
    """
    result = importlib.import_module(f"{__package__}.datasets.{dataset_id}").load(
        target=target, **kw
    )
    if isinstance(result, xr.DataArray):
        result.attrs["dataset_id"] = dataset_id  # only id; rest recoverable from T1
    return result
