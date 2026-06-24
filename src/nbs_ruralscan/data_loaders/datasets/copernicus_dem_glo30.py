"""Copernicus DEM GLO-30 (~30 m global) and its server-side terrain derivatives.

Elevation source for the pipeline (replaces SRTM): newer (TanDEM-X 2011–2015),
void-filled and edited, globally complete — cleaner slope/aspect than SRTM. The GLO-30
GEE asset is an ImageCollection of tiles, so we mosaic to one image; terrain derivatives
are computed at native 30 m on Earth Engine (derive-then-aggregate) and only the
AOI-gridded result is pulled via xee. This file owns all products derivable from the DEM;
the requested ``variable`` selects which.

NOTE: a fitness-equivalent COG version is on AWS Open Data / STAC
(https://registry.opendata.aws/copernicus-dem/ · s3://copernicus-dem-30m/). If we ever
want to drop the Earth Engine dependency, switch this loader to read_raster() against
those COGs — but then slope must be derived client-side after mosaicking the tiles,
which loses the server-side derive-then-aggregate guarantee.
"""

from __future__ import annotations

from ..core import TargetGrid, ee_to_xarray


def load(grid: TargetGrid, variable: str = "elevation"):
    import ee

    # GLO-30 is a tiled ImageCollection (band "DEM"); mosaic to a single image first.
    dem = ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM").mosaic()
    img = {
        "slope": lambda: ee.Terrain.slope(dem),
        "aspect": lambda: ee.Terrain.aspect(dem),
    }.get(variable, lambda: dem)()
    return ee_to_xarray(img, grid)
