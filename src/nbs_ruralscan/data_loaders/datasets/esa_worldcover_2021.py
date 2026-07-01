"""ESA WorldCover 2021 v200 — land cover + derived fractions (T1: esa_worldcover_2021).

GEE-hosted (``ESA/WorldCover/v200``), a single global 10 m class raster (band ``Map``),
pulled via xee. ``variable`` selects the product:

  * ``land_cover`` (default) — raw class codes (categorical → ``nearest``). Use for the
    urban exclusion directly (``land_cover != 50``) or any class logic.
  * ``cropland_fraction`` — share of each target cell that is cropland (class 40).
  * ``built_up_fraction`` — share that is built-up (class 50). Urban-exclusion mask is then
    ``built_up_fraction > <your threshold>`` downstream — the loader extracts, you set the cut.

Fractions are **derive-then-aggregate** (the locked rule): the class is masked at native
10 m, then averaged up to the target cell server-side via ``reduceResolution`` — never
resample-then-classify. So fractions are meaningful only against a (coarser) ``GeoBox``;
a native ``AOI`` just returns the 10 m 0/1 mask. Classes are nominal → ``land_cover`` uses
``nearest``; the fractions are continuous → ``average``.

GEE loader: needs Earth Engine auth (Colab / service account) and is **verified there, not
offline**. ``reduceResolution(maxPixels=65535)`` covers ~10 m→1 km (~10⁴ source px/cell);
a much coarser grid (≳8 km) would exceed it and need a two-step reduce.

NOTE: a fitness-equivalent COG version is on AWS Open Data (no EE auth):
https://registry.opendata.aws/esa-worldcover-vito/ — tiled 3°×3° (s3://esa-worldcover, the
``ESA_WorldCover_10m_2021_v200_*_Map.tif`` files). To drop the GEE dependency, switch to
read_raster() over the AOI-overlapping tiles (mosaic them) and do the fraction aggregation
client-side at native res — losing the server-side reduceResolution, so weigh it against the
auth/quota tradeoff. dataset_id stays the same, so it's a localised swap (Design A).
"""

from __future__ import annotations

from typing import Literal

from ..core import AOI, GeoBox, ee_to_xarray

_ASSET = "ESA/WorldCover/v200"
_NATIVE_M = 10
_CLASS = {"cropland_fraction": 40, "built_up_fraction": 50}  # ESA WorldCover codes

WorldCoverVar = Literal["land_cover", "cropland_fraction", "built_up_fraction"]


def load(target: AOI | GeoBox, variable: WorldCoverVar = "land_cover"):
    import ee

    wc = ee.ImageCollection(_ASSET).first().select("Map")  # single global image
    if variable == "land_cover":
        return ee_to_xarray(wc, target, resampling="nearest", native_scale=_NATIVE_M)

    mask = wc.eq(_CLASS[variable])  # 1 where the class, 0 elsewhere — at native 10 m
    if isinstance(target, GeoBox):
        # average the 10 m 0/1 mask onto the grid cell → fraction (derive-then-aggregate),
        # pinned to the exact GeoBox grid via crs + affine (no scale-unit ambiguity).
        mask = mask.reduceResolution(ee.Reducer.mean(), maxPixels=65535).reproject(
            crs=str(target.crs), crsTransform=list(target.affine)[:6]
        )
    return ee_to_xarray(mask, target, resampling="average", native_scale=_NATIVE_M)
