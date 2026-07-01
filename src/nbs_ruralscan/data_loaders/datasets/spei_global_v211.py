"""SPEIbase v2.11 (CSIC) drought frequency, server-side (T1: spei_global_v211).

GEE ImageCollection ``CSIC/SPEI/2_11`` — monthly SPEI at 1–48 month accumulations, 0.5°
(~55 km), 1901–present, Penman-Monteith PET. ``load`` reduces the **12-month** band
(agricultural drought) to a drought-**frequency** hazard: the fraction of months in a
baseline window with SPEI-12 below a deficit threshold. The reduce runs server-side; only
the AOI grid is pulled via xee.

SPEI is negative for moisture deficit, so drought = ``SPEI < threshold`` (default -1.0 =
moderate drought, the standard SPEI class boundary). Higher output = more drought-prone, so
the sign is already correct for a positive-risk hazard. ``threshold`` and ``baseline`` come
from the caller (T2/T4), not hardcoded — same contract as the DEM slope cut.

0.5° is coarse for within-country differentiation (weak for small AOIs); a CHELSA 1 km SPEI
is the documented fitness upgrade — Design-A keeps that swap localised to this module.

GEE loader: needs Earth Engine auth; verified in Colab, not offline.
"""

from __future__ import annotations

from ..core import AOI, GeoBox, ee_to_xarray

_ASSET = "CSIC/SPEI/2_11"
_BAND = "SPEI_12_month"  # 12-month accumulation = agricultural drought
_NATIVE_SCALE_M = 55_000  # 0.5°
_BASELINE = ("1991-01-01", "2021-01-01")  # WMO 1991–2020 normal; override from T2/T4


def load(
    target: AOI | GeoBox,
    baseline: tuple[str, str] = _BASELINE,
    threshold: float = -1.0,
):
    """Drought-frequency hazard: fraction of months in ``baseline`` with SPEI-12 < ``threshold``.
    Server-side reduce on ``CSIC/SPEI/2_11``; pulled onto ``target`` via xee."""
    import ee

    start, end = baseline
    spei12 = ee.ImageCollection(_ASSET).select(_BAND).filterDate(start, end)
    # mean of the 0/1 "below threshold" mask over the window = fraction of months in drought
    freq = spei12.map(lambda img: img.lt(threshold)).mean()
    return ee_to_xarray(freq, target, native_scale=_NATIVE_SCALE_M)
