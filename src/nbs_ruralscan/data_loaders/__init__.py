"""Dataset loaders for Earth Engine and other geospatial inputs.

``load(dataset_id, target, **kw)`` is the entry point; it dispatches to a per-dataset
module under ``datasets/`` and caches the result. Pass an ``AOI`` for a native bbox/polygon
extract (the default), or an ``odc.geo.GeoBox`` to additionally reproject onto an MCDA grid
(re-exported here for convenience). Shared plumbing lives in ``core``.
"""

from odc.geo.geobox import GeoBox

from .core import (
    AOI,
    download,
    ee_to_xarray,
    load,
    read_raster,
    target_bounds,
    to_target,
)

__all__ = [
    "AOI",
    "GeoBox",
    "download",
    "ee_to_xarray",
    "load",
    "read_raster",
    "target_bounds",
    "to_target",
]
