"""CHELSA v2.1 bioclim, 1981–2010 baseline (T1: chelsa_bioclim_v21_baseline).

Global ~1 km COGs, EPSG:4326, streamed via /vsicurl (tiled + overviewed, so only AOI tiles
transfer). Continuous climate surfaces → bilinear (the read_raster default) when handed a
GeoBox; an AOI clips at native res.

**Design: the loader owns the band.** BIND resolves a canonical variable → this dataset_id;
the loader translates that canonical name into CHELSA's own band + the scale/offset/unit
needed to turn raw uint16 into physical units. Same job the DEM loader does turning "slope"
into ``ee.Terrain.slope`` — so there is no ``band`` column in BIND. Heat stress is bio5
(max temp of warmest month), its **own layer** — NOT derived from mean temp (bio1).

Raw uint16 is decoded per band by ``_Band`` (scale/offset → physical units). uint16 cannot
hold NaN, so nodata masking relies on the COG declaring nodata=65535 (read_raster opens
masked=True).
"""

from __future__ import annotations

from typing import Literal, NamedTuple

import xarray as xr

from ..core import AOI, GeoBox, read_raster

# CHELSA EnviDat COGs (UNIL Switch object store). Per-band layout:
#   {_BASE}/{code}/1981-2010/CHELSA_{code}_1981-2010_V.2.1.tif
# read_raster opens these over GDAL /vsicurl — only the AOI's tiles transfer (COG-windowed).
_BASE = "https://os.unil.cloud.switch.ch/chelsa02/chelsa/global/bioclim"


class _Band(NamedTuple):
    """One CHELSA layer + how to decode it: ``physical = raw * scale + offset``.

    CHELSA v2.1 ships bioclim as **raw uint16**, NOT physical units — every read MUST be
    scaled or the numbers are nonsense (e.g. an unscaled bio01 reads ~2980, not ~25 °C).
      * temperature bands store Kelvin×10  → scale 0.1, offset -273.15 gives °C.
      * precip bio12 (annual) stores mm/yr directly → scale 1.0 (at ×10 it would overflow
        uint16 in the wet tropics: 12 000 mm × 10 = 120 000 > 65 535).
      * precip bio13-19 (monthly/quarterly, smaller values) store mm×10 → scale 0.1 for finer
        precision. NB: NOT the same scale as bio12 — verified empirically (a wettest-quarter
        read that exceeds the annual total means the ×10 wasn't undone). Extreme-wet quarters
        (>6553 mm) may clip in uint16; a non-issue for the LDC pilots.
    """

    code: str  # CHELSA band file code, zero-padded (e.g. "bio01")
    scale: float  # multiply the raw DN by this ...
    offset: float  # ... then add this
    unit: str  # unit of the decoded result


# canonical BIND variable -> how this loader pulls + decodes it (see _Band).
_VARS: dict[str, _Band] = {
    "mean_annual_temperature": _Band("bio01", scale=0.1, offset=-273.15, unit="degC"),
    "heat_stress_hazard": _Band(
        "bio05", scale=0.1, offset=-273.15, unit="degC"
    ),  # warmest-month Tmax (BIO5)
    "frost_hazard": _Band(
        "bio06", scale=0.1, offset=-273.15, unit="degC"
    ),  # coldest-month Tmin (BIO6); lower = more frost risk (invert in membership)
    "annual_precipitation": _Band(
        "bio12", scale=1.0, offset=0.0, unit="mm"
    ),  # direct mm/yr
    "precip_wettest_quarter": _Band(
        "bio16", scale=0.1, offset=0.0, unit="mm"
    ),  # sustained wet-season water input (waterlogging composite); mm×10, NOT bio12's scale
}
ChelsaVar = Literal[
    "mean_annual_temperature",
    "heat_stress_hazard",
    "frost_hazard",
    "annual_precipitation",
    "precip_wettest_quarter",
]


def _url(code: str) -> str:
    return f"{_BASE}/{code}/1981-2010/CHELSA_{code}_1981-2010_V.2.1.tif"


def load(
    target: AOI | GeoBox, variable: ChelsaVar = "mean_annual_temperature"
) -> xr.DataArray:
    try:
        code, scale, offset, units = _VARS[variable]
    except KeyError:
        raise ValueError(
            f"unknown CHELSA variable {variable!r}; expected one of {list(_VARS)}"
        ) from None
    da = read_raster(_url(code), target) * scale + offset  # raw uint16 → physical units
    da.attrs["units"] = units
    return da
