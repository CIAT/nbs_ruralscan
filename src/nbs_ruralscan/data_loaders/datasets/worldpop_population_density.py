"""WorldPop 2024 population, as density or count (T1: worldpop_population_density).

Source is a single global EPSG:4326 COG of **population counts** (persons per pixel),
tiled 512×512 on the digital-atlas S3 mirror, read over GDAL /vsicurl — only the AOI's
tiles transfer.

``variable`` selects the product:
  * ``population_density`` (default) — persons/km². The reproject-safe primitive: density
    is *intensive*, so ``to_target``'s reproject is value-correct.
  * ``population_count`` — persons per cell. Counts are *extensive* (people don't average),
    so we never reproject them directly. Instead we reproject the density and multiply by
    the **target** cell area: on a native AOI this returns the raw counts unchanged; on an
    MCDA ``GeoBox`` it returns counts aggregated to the grid (people conserved). The count
    assumes a geographic or equal-area target — the cell-area conversion is exact for those
    (the project grid is EPSG:4326). Density is CRS-agnostic and needs no such assumption.

In EPSG:4326 a cell's ground area shrinks toward the poles, so the count↔density factor is
the per-row cell area, not a constant; a projected target grid has a constant cell area.
``_cell_area_km2`` handles both and is used in both directions.

"Rural" is not masked here: urban is dropped once upstream as a T4 hard-exclusion (ESA
WorldCover built-up class) and exposure is clipped to the rural/ag opportunity space, so a
separate rural-population mask is redundant.
"""

from __future__ import annotations

from typing import Literal

import numpy as np
import odc.geo.xr  # noqa: F401  (registers the .odc accessor)
import rioxarray  # noqa: F401  (registers the .rio accessor)
import xarray as xr

from ..core import AOI, GeoBox, to_target

_URL = "https://digital-atlas.s3.amazonaws.com/domain=exposure/source=worldpop2024/region=global/processing=analysis-ready/variable=pop/settlement=total/sex=total/pop_total_total.tif"

_R_M = 6_371_007.181  # authalic Earth radius (m) — for spherical cell-area

PopVar = Literal["population_density", "population_count"]


def _cell_area_km2(da: xr.DataArray) -> xr.DataArray | float:
    """Per-cell ground area (km²). Geographic CRS → R²·Δlon·(sin(lat+½Δlat) − sin(lat−½Δlat)),
    a per-row vector of latitude (broadcasts, stays lazy). Projected CRS → constant from the
    metre resolution. Uses odc accessors so it also works post-reproject, where the y-dim may
    be ``latitude`` rather than ``y``."""
    dx, dy = (abs(r) for r in da.rio.resolution())
    if da.odc.geobox.crs.geographic:
        half = np.deg2rad(dy) / 2
        lat = np.deg2rad(da[da.odc.spatial_dims[0]])  # y-dim name (y / latitude)
        return (
            _R_M**2 * np.deg2rad(dx) * (np.sin(lat + half) - np.sin(lat - half)) / 1e6
        )
    return dx * dy / 1e6  # metres → km², constant


def load(target: AOI | GeoBox, variable: PopVar = "population_density") -> xr.DataArray:
    da = rioxarray.open_rasterio(_URL, masked=True, chunks=True)  # counts, native, lazy
    assert isinstance(da, xr.DataArray)  # single-band COG
    density = da / _cell_area_km2(da)  # → persons/km² (intensive) before any reproject
    out = to_target(density, target)  # reproject-safe on AOI or GeoBox
    if variable == "population_count":
        out = out * _cell_area_km2(out)  # density → counts on the TARGET cells
        out.attrs["units"] = "persons"
    else:
        out.attrs["units"] = "persons/km2"
    return out
