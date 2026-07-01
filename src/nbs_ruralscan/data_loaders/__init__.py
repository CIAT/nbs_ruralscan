"""Dataset loaders for Earth Engine and other geospatial inputs.

**Two doors to the same loaders:**

* ``load(dataset_id, target, **kw)`` — the *dynamic* door. The ``dataset_id`` is a string,
  typically resolved at run time from BIND (``runtime.binding.resolve_binding``), so this is
  the path pipelines/MCDA use. No completion (the id is data, not code); it stamps
  ``attrs["dataset_id"]`` for provenance and fails with the valid list on an unknown id.
* ``from .datasets import <id>; <id>.load(target, variable=…)`` — the *direct* door. Use it
  when you already know the dataset (notebooks, tests): the module name and the ``Literal``
  ``variable`` both autocomplete and are type-checked. Prefer this over hand-typing a string.

**Contract (Design A — the loader owns the band).** BIND resolves a *canonical variable* →
a ``dataset_id`` only. The loader's ``variable=`` kwarg speaks that same canonical vocabulary
and translates each name into whatever it physically is — a band (CHELSA ``annual_precipitation``
→ ``bio12`` + its scale/offset), a derivation (DEM ``slope`` → ``ee.Terrain.slope``), or a
zarr layer (GLW ``cattle``). The pipeline passes the resolved variable straight through:
``load(res.dataset_id, target, variable=res.variable)``. There is no ``band`` column in BIND —
band/scale/offset live together in the loader, the one place that already needs them.

Pass an ``AOI`` for a native bbox/polygon extract (the default), or an ``odc.geo.GeoBox`` to
additionally reproject onto an MCDA grid (re-exported here). Shared plumbing lives in ``core``.
"""

from odc.geo.geobox import GeoBox

from .checkpoint import checkpoint
from .core import (
    AOI,
    LoaderModule,
    available,
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
    "LoaderModule",
    "available",
    "checkpoint",
    "download",
    "ee_to_xarray",
    "load",
    "read_raster",
    "target_bounds",
    "to_target",
]
