"""JRC/CEMS GloFAS global river-flood hazard, server-side (T1: jrc_global_flood_hazard).

GEE ImageCollection ``JRC/CEMS_GLOFAS/FloodHazard/v2_1`` — return-period river-flood
inundation **depth** (metres) at **90 m**, global. Bands ``RP{n}_depth`` for n in
{10, 20, 50, 75, 100, 200, 500} (+ ``_category`` / permanent-water bands). The collection is
spatial tiles, so we mosaic to one image and select the requested return period.

``return_period`` comes from the caller (T2/T4), not hardcoded — RP100 is the scoping
default. Continuous depth → bilinear when gridded. Riverine flood only (no pluvial/coastal);
the model assumes existing flood protection per FLOPROS.

GEE loader: needs Earth Engine auth; verified in Colab, not offline.
"""

from __future__ import annotations

from ..core import AOI, GeoBox, ee_to_xarray

_ASSET = "JRC/CEMS_GLOFAS/FloodHazard/v2_1"
_NATIVE_SCALE_M = 90
_RETURN_PERIODS = (10, 20, 50, 75, 100, 200, 500)


def load(target: AOI | GeoBox, return_period: int = 100):
    """Return-period river-flood inundation depth (m) for ``return_period`` (one of
    10/20/50/75/100/200/500). Mosaicked + pulled onto ``target`` via xee."""
    if return_period not in _RETURN_PERIODS:
        raise ValueError(
            f"unknown return_period {return_period!r}; expected one of {_RETURN_PERIODS}"
        )
    import ee

    flood = ee.ImageCollection(_ASSET).mosaic().select(f"RP{return_period}_depth")
    return ee_to_xarray(flood, target, native_scale=_NATIVE_SCALE_M)
