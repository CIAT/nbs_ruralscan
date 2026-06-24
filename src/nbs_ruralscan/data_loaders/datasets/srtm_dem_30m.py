"""Template loader: SRTM 30 m DEM and its server-side terrain derivatives.

The pattern for every dataset — one file named for its ``dataset_id``, exposing
``load(grid, **kw)``. The dataset's file owns *all* products derivable from it; the
requested ``variable`` selects which. Terrain derivatives are computed server-side at
native resolution (derive-then-aggregate), and only the grid-aligned result is pulled.
"""

from __future__ import annotations

from ..core import TargetGrid, ee_to_xarray


def load(grid: TargetGrid, variable: str = "elevation", **kw):
    import ee

    dem = ee.Image("USGS/SRTMGL1_003")
    img = {
        "slope": lambda: ee.Terrain.slope(dem),
        "aspect": lambda: ee.Terrain.aspect(dem),
    }.get(variable, lambda: dem)()
    return ee_to_xarray(img, grid)
