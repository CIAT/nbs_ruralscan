"""Tests for the data-loader plumbing (AOI keys, target dispatch, native vs grid).

Pure-unit tests run offline. The boundaries integration test needs network + the WB
download, so it's skipped unless NBS_RUN_NET=1.
"""

from __future__ import annotations

import importlib
import inspect
import os
import pkgutil

import pytest
import xarray as xr

from nbs_ruralscan.data_loaders import AOI, GeoBox, datasets, load, to_target


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
