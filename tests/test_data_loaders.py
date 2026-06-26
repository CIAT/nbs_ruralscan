"""Tests for the data-loader plumbing (AOI keys, target dispatch, native vs grid).

Pure-unit tests run offline. The boundaries integration test needs network + the WB
download, so it's skipped unless NBS_RUN_NET=1.
"""

from __future__ import annotations

import importlib
import inspect
import os
import pkgutil
import typing
from pathlib import Path

import pytest
import xarray as xr

from nbs_ruralscan.data_loaders import AOI, GeoBox, available, datasets, load, to_target


def test_every_dataset_module_exposes_load_accepting_target():
    """Contract guard: each datasets/<id>.py the dispatcher can reach must expose a
    callable load() that accepts `target` (the dispatcher calls load(target=target, **kw))."""
    names = [
        m.name
        for m in pkgutil.iter_modules(datasets.__path__)
        if not m.name.startswith("_")
    ]
    assert names, "no dataset loaders found"
    for name in names:
        fn = getattr(
            importlib.import_module(f"{datasets.__name__}.{name}"), "load", None
        )
        assert callable(fn), f"datasets/{name}.py must expose a callable load()"
        params = inspect.signature(fn).parameters
        accepts_target = "target" in params or any(
            p.kind == p.VAR_KEYWORD for p in params.values()
        )
        assert accepts_target, f"datasets/{name}.load() must accept `target`"


def test_bind_variables_covered_by_loader_literals():
    """Design-A wiring guard: BIND resolves a canonical variable -> a dataset_id; the loader's
    ``variable`` Literal must SPEAK that variable. For every BIND row whose dataset has a loader
    that declares a Literal, the bound variable must be in it — so a loader can't silently forget
    a canonical variable routed to it (e.g. CHELSA omitting heat_stress_hazard). Datasets with no
    loader yet are skipped (that's a build-out gap, not a wiring bug)."""
    from nbs_ruralscan.runtime.binding import load_bindings

    schema_root = Path(__file__).resolve().parents[1] / "schema"
    have = set(available())
    for b in load_bindings(schema_root):
        if not b.dataset_id or b.dataset_id not in have:
            continue  # requires_upload, or dataset has no loader yet
        mod = importlib.import_module(f"{datasets.__name__}.{b.dataset_id}")
        if "variable" not in inspect.signature(mod.load).parameters:
            continue  # loader serves a single product / takes no `variable`
        allowed = set(typing.get_args(typing.get_type_hints(mod.load).get("variable")))
        if not allowed:
            continue  # `variable` left untyped — no Literal to check
        assert b.variable in allowed, (
            f"{b.dataset_id} loader must declare canonical variable {b.variable!r}; "
            f"its Literal allows {sorted(allowed)}"
        )


def test_checkpoint_caches_any_type_by_arg_checksum(tmp_path):
    from nbs_ruralscan.data_loaders import checkpoint

    cache = checkpoint(tmp_path)
    calls = []

    @cache
    def raster(scale):  # xarray -> zarr, lazy reopen
        calls.append(("raster", scale))
        return xr.DataArray([[1.0, 2.0], [3.0, 4.0]], dims=("y", "x")) * scale

    @cache
    def table(n):  # non-xarray -> pickle
        calls.append(("table", n))
        return {"rows": n, "ok": True}

    a, b = raster(2), raster(2)  # 2nd call: reopened, not recomputed
    raster(3)  # different checksum -> recompute
    t1, t2 = table(5), table(5)

    assert calls == [("raster", 2), ("raster", 3), ("table", 5)]  # each computed once
    assert float(a.sum()) == float(b.sum()) == 20.0
    assert b.chunks is not None  # raster reopened lazily (dask-backed)
    assert t1 == t2 == {"rows": 5, "ok": True}  # table round-trips via pickle
    assert len(list(tmp_path.glob("*.zarr"))) == 2  # scale 2 and 3
    assert len(list(tmp_path.glob("*.pkl"))) == 1

    # arrays CAN be passed as args — keyed by dask.tokenize (content), not repr: same content
    # hits the cache, different content recomputes (no silent collision)
    seen = []

    @cache
    def doubled(layer):
        seen.append(float(layer.sum()))
        return layer * 2

    arr1 = xr.DataArray([[1.0, 2.0], [3.0, 4.0]], dims=("y", "x"))
    arr2 = xr.DataArray([[9.0, 9.0], [9.0, 9.0]], dims=("y", "x"))
    r1, r1b, r2 = doubled(arr1), doubled(arr1), doubled(arr2)
    assert seen == [10.0, 36.0]  # arr1 computed once (r1b was a cache hit), arr2 once
    assert float(r1.sum()) == float(r1b.sum()) == 20.0
    assert float(r2.sum()) == 72.0


def test_to_target_native_aoi_vs_grid():
    """The core contract: an AOI clips to NATIVE resolution (no resample); a GeoBox
    reprojects onto the grid. Guards the native-default / grid-opt-in split."""
    import numpy as np

    da = xr.DataArray(
        np.arange(16.0).reshape(4, 4),
        coords={"y": [3.5, 2.5, 1.5, 0.5], "x": [0.5, 1.5, 2.5, 3.5]},
        dims=("y", "x"),
    ).rio.write_crs("EPSG:4326")

    native = to_target(da, AOI(bounds=(0.0, 0.0, 2.0, 2.0)))
    assert (
        abs(float(native.rio.resolution()[0])) == 1.0
    )  # native 1° preserved, no resample

    gridded = to_target(
        da, GeoBox.from_bbox((0.0, 0.0, 4.0, 4.0), "EPSG:4326", resolution=2.0)
    )
    assert tuple(gridded.shape) == (2, 2)  # 4°/2° -> reprojected to the grid


def test_load_dispatches_by_name_and_stamps_id_without_writing(tmp_path, monkeypatch):
    # Register a fake dataset module on the dispatch path; confirm load() finds it by name,
    # stamps dataset_id, and is side-effect-free (no disk writes — caching is the caller's job).
    import sys
    import types

    monkeypatch.chdir(tmp_path)  # any stray writes would land here
    aoi = AOI(bounds=(0.0, 0.0, 2.0, 2.0))
    da = (
        xr.DataArray([[1.0, 2.0], [3.0, 4.0]], dims=("y", "x"))
        .rio.write_crs("EPSG:4326")
        .rio.set_spatial_dims("x", "y")
    )

    fake = types.ModuleType("nbs_ruralscan.data_loaders.datasets.fake_ds")
    fake.load = lambda target=None, **kw: da  # noqa: ARG005
    sys.modules["nbs_ruralscan.data_loaders.datasets.fake_ds"] = fake

    out = load("fake_ds", aoi)
    assert out.attrs["dataset_id"] == "fake_ds"
    assert not list(tmp_path.iterdir())  # pure: nothing materialised


@pytest.mark.skipif(
    os.environ.get("NBS_RUN_NET") != "1", reason="needs network + WB download"
)
def test_boundaries_sle():
    sle = load("wb_admin_boundaries", level=0, region="SLE")
    assert len(sle) == 1
    with pytest.raises(ValueError, match="unknown"):
        load("wb_admin_boundaries", level=0, region="XXX")


@pytest.mark.skipif(
    os.environ.get("NBS_RUN_NET") != "1", reason="needs network + WB download"
)
def test_aoi_from_region():
    aoi = AOI.from_region("SLE")
    assert aoi.geometry is not None  # dissolved polygon mask, not just a bbox
    minx, miny, maxx, maxy = aoi.bounds
    assert minx < maxx and miny < maxy
