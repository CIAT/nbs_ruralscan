"""Copernicus DEM GLO-30 (~30 m global) and its server-side terrain derivatives.

Elevation source for the pipeline (replaces SRTM): newer (TanDEM-X 2011–2015),
void-filled and edited, globally complete — cleaner slope/aspect than SRTM. The GLO-30
GEE asset is an ImageCollection of tiles, so we mosaic to one image; terrain derivatives
are computed at native 30 m on Earth Engine (derive-then-aggregate) and only the
AOI-gridded result is pulled via xee.

``load(target, variable)`` returns a continuous product (``elevation`` / ``slope`` /
``aspect``). ``slope_suitable_fraction(target, max_slope_deg)`` is the derive-then-aggregate
product: the slope cut is applied at native 30 m and *then* averaged onto the target grid,
so sub-cell terrain isn't lost (the locked rule for scale-dependent derivatives, VONT
``slope.derive_then_aggregate=true``).

**All Earth Engine / xee code lives in this module.** The runtime calls these functions and
never touches an ``ee.Image``, so swapping the DEM source = rewriting this one file; callers
and the schema are untouched. The slope cut is a parameter (from ``T4.relationship_params``,
e.g. agroforestry ≈ 3°) — never hardcoded here.

NOTE: a fitness-equivalent COG version is on AWS Open Data / STAC
(https://registry.opendata.aws/copernicus-dem/ · s3://copernicus-dem-30m/). To drop the
Earth Engine dependency, reimplement these functions with read_raster() over the AOI tiles +
client-side xarray slope/coarsen — same signatures, so nothing downstream changes (but the
derive-then-aggregate then runs client-side rather than server-side).
"""

from __future__ import annotations

from typing import Literal

from ..core import AOI, GeoBox, ee_to_xarray

_NATIVE_SCALE_M = 30  # GLO-30; EE pulls at this scale for a bare (native) AOI

# canonical variable names this loader serves (the BIND vocabulary it translates).
DemVar = Literal["elevation", "slope", "aspect"]


def _dem():
    """The mosaicked GLO-30 elevation ``ee.Image`` (band ``DEM``). Internal — not exposed,
    so no ``ee.Image`` ever leaks to the runtime."""
    import ee

    return ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM").mosaic()


def load(target: AOI | GeoBox, variable: DemVar = "elevation"):
    import ee

    dem = _dem()
    if variable == "elevation":
        img = dem
    elif variable == "slope":
        img = ee.Terrain.slope(dem)
    elif variable == "aspect":
        img = ee.Terrain.aspect(dem)
    else:
        raise ValueError(
            f"unknown variable {variable!r}; expected elevation/slope/aspect"
        )
    return ee_to_xarray(img, target, native_scale=_NATIVE_SCALE_M)


def slope_suitable_fraction(target: AOI | GeoBox, max_slope_deg: float):
    """Fraction of each target cell whose slope is ≤ ``max_slope_deg`` — derive-then-aggregate,
    all server-side. The slope cut is applied at native 30 m, then averaged onto the target
    grid, so sub-cell steepness isn't washed out by resampling slope first.

    ``max_slope_deg`` comes from T4 (the suitability rule), not this module. Against a coarser
    ``GeoBox`` the result is a true 0–1 fraction; on a native ``AOI`` it's the 30 m 0/1 mask
    (no coarsening to fraction). ``reduceResolution(maxPixels=65535)`` covers 30 m → ~7 km
    cells; a coarser grid would need a two-step reduce.
    """
    import ee

    suitable = ee.Terrain.slope(_dem()).lte(
        max_slope_deg
    )  # 1 where slope ≤ cut, native 30 m
    if isinstance(target, GeoBox):
        suitable = suitable.reduceResolution(
            ee.Reducer.mean(), maxPixels=65535
        ).reproject(crs=str(target.crs), crsTransform=list(target.affine)[:6])
    return ee_to_xarray(
        suitable, target, resampling="average", native_scale=_NATIVE_SCALE_M
    )
