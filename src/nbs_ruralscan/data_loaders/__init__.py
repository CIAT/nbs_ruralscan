"""Dataset loaders for Earth Engine and other geospatial inputs.

``load(dataset_id, grid, **kw)`` is the entry point; it dispatches to a per-dataset
module under ``datasets/`` and caches the result. Shared plumbing lives in ``core``.
"""

from .core import TargetGrid, download, ee_to_xarray, load, read_raster

__all__ = ["TargetGrid", "download", "ee_to_xarray", "load", "read_raster"]
