"""Gridded Livestock of the World v4 (GLW4, 2020) livestock densities.

Source is a single global EPSG:4326 Zarr cube (~10 km, dasymetric "D-DA" product)
mirrored on S3, one variable per species. We read it lazily and only the chunks
overlapping the AOI are pulled. Like the DEM loader owns elevation+slope+aspect, this file
owns all GLW4 products: the requested ``variable`` selects a single species or the derived
ruminant-TLU composite. Returns native ~10 km densities for an ``AOI``; ``to_target``
reprojects only when handed a ``GeoBox`` (MCDA).

Values are **densities** (``head/km2``; ``ruminant_tlu`` is ``TLU/km2``). Density is
intensive, so reprojecting onto a grid is value-safe regardless of the bilinear default.
The GLW caveat about lat/long over-representing high-latitude densities is a *display /
count-summation* concern, not a loader one — if you need head **counts** or area-weighted
sums, do that downstream in an equal-area CRS, not here.

``ruminant_tlu`` consumed by ``runtime/farming_system.py`` (its thresholds are TLU/km²).
"""

from __future__ import annotations

import xarray as xr
from obstore.store import HTTPStore
from zarr.storage import ObjectStore

from ..core import AOI, GeoBox, to_target

# Public S3 store read over its https endpoint via obstore (bundled Rust client; no
# botocore/aiohttp). The store is consolidated, so no S3 key-listing is needed. Swap
# HTTPStore -> obstore.store.S3Store(..., skip_signature=True) if a store ever needs
# real S3 semantics (private / non-consolidated) — same ObjectStore wrapper, no new dep.
_ZARR = "https://digital-atlas.s3.amazonaws.com/cdh/data/glw4-2020/glw4-2020.zarr"
_SPECIES = ("cattle", "buffalo", "sheep", "goat", "pig", "chicken")

# Tropical Livestock Unit weights (Jahnke 1982 / FAO; ILRI tropical convention).
# head/km² × weight = TLU/km².
_TLU_RUMINANT = {"cattle": 0.7, "buffalo": 0.7, "sheep": 0.1, "goat": 0.1}


def load(target: AOI | GeoBox, variable: str = "ruminant_tlu") -> xr.DataArray:
    store = ObjectStore(HTTPStore.from_url(_ZARR), read_only=True)
    ds = xr.open_dataset(
        store,  # ty: ignore[invalid-argument-type]  (zarr store; not in xarray's typed union)
        engine="zarr",
        consolidated=True,
        chunks={},  # dask-lazy (native chunking); to_target prunes the read to the AOI
    )
    if variable in _SPECIES:
        da = ds[variable]
    elif variable == "ruminant_tlu":
        # A species is NaN where it's modelled absent (e.g. buffalo across W. Africa) —
        # a true zero contribution, so fillna(0) before weighting. (Genuine nodata like
        # ocean also becomes 0; harmless for a livestock layer clipped to the AOI.)
        layers = [w * ds[sp].fillna(0) for sp, w in _TLU_RUMINANT.items()]
        # weighted sum across ruminant species → TLU/km²
        da = xr.concat(layers, dim="species").sum("species")
        da.attrs["units"] = "TLU/km2"
    else:
        raise ValueError(
            f"unknown GLW4 variable {variable!r}; expected one of "
            f"{(*_SPECIES, 'ruminant_tlu')}"
        )
    return to_target(da, target)
