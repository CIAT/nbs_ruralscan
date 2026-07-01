"""Opt-in result checkpoint (analysis-side; ``load`` never calls this implicitly).

Run a function once, cache its result keyed by a **content hash of the call args**
(``dask.tokenize`` — so args may be arrays, incl. lazy dask, as well as AOI/GeoBox/scalars),
reopen on later calls. Generic across result types:
  * ``xarray`` DataArray / Dataset      -> zarr, reopened **lazily** (dem, glw, a merged index)
  * anything else (DataFrame, dict, ...) -> pickle, eager (tables / csv-derived data)
The caller picks the dir; nothing global, never auto-invoked by ``load``.

    cache = checkpoint(run_dir)

    @cache
    def dem(target):           return load("copernicus_dem_glo30", target)   # -> zarr (lazy)
    @cache
    def mask(dem, suit, thr):  return dem.where(suit >= thr)   # arrays-as-args OK; result -> zarr
    @cache
    def admin_stats(iso3):     return zonal_table                            # -> pickle

    dem(grid)   # 1st call computes + writes; later calls reopen from disk
"""

from __future__ import annotations

import functools
import pickle
from collections.abc import Callable
from pathlib import Path

import xarray as xr
from dask.base import tokenize

_DA = "__dataarray__"  # sentinel var so a wrapped DataArray reopens as a DataArray, not a Dataset


def _reopen(zarr_path: Path):
    ds = xr.open_dataset(zarr_path, engine="zarr", chunks={})  # lazy, native chunking
    return ds[_DA] if _DA in ds.data_vars else ds


def checkpoint(run_dir: str | Path) -> Callable:
    """Decorator factory: cache a fn's result under ``run_dir``, keyed by ``dask.tokenize`` of
    ``(fn name, args, kwargs)``. xarray -> zarr (lazy reopen); everything else -> pickle."""
    run_dir = Path(run_dir)

    def decorate(fn: Callable) -> Callable:
        name = getattr(fn, "__name__", "fn")
        body = getattr(
            getattr(fn, "__code__", None), "co_code", b""
        )  # bust cache when edited

        @functools.wraps(fn)
        def wrapped(*args, **kw):
            # Key via dask.tokenize — a deterministic content (numpy) / graph (lazy dask) hash
            # that also covers AOI/GeoBox/scalars; ``body`` (the fn's bytecode) is folded in so
            # editing the function invalidates its cache (like joblib.Memory). Unlike repr it
            # never collides on arrays, so arrays (incl. lazy dask) ARE allowed as args; only
            # the RESULT is materialised. (A huge *materialised* array arg hashes its bytes; a
            # lazy arg hashes the cheap graph.)
            stem = run_dir / f"{name}-{tokenize(name, body, args, kw)[:16]}"
            zarr_path, pkl_path = stem.with_suffix(".zarr"), stem.with_suffix(".pkl")
            if zarr_path.exists():
                return _reopen(zarr_path)
            if pkl_path.exists():
                return pickle.loads(pkl_path.read_bytes())

            result = fn(*args, **kw)
            run_dir.mkdir(parents=True, exist_ok=True)
            if isinstance(result, xr.DataArray | xr.Dataset):
                ds = (
                    result
                    if isinstance(result, xr.Dataset)
                    else result.to_dataset(name=_DA)
                )
                ds.to_zarr(zarr_path)  # computes the graph once
                return _reopen(zarr_path)
            pkl_path.write_bytes(
                pickle.dumps(result)
            )  # gdf, df, dict, scalar, ... (eager)
            return result

        return wrapped

    return decorate
