"""Tests for the data-loader plumbing (grid math, cache keys, dispatch).

Pure-unit tests run offline. The boundaries integration test needs network + the WB
download, so it's skipped unless NBS_RUN_NET=1.
"""

from __future__ import annotations

import os

import pytest
import xarray as xr

from nbs_ruralscan.data_loaders import TargetGrid, load


def test_grid_shape_and_transform():
    grid = TargetGrid(bounds=(-13.0, 7.0, -10.0, 10.0), res=1.0)
    assert grid.shape == (3, 3)  # 3°/1° each way
    assert grid.transform.a == 1.0 and grid.transform.e == -1.0


def test_grid_key_is_numpy_repr_free_and_stable():
    import numpy as np

    g1 = TargetGrid(bounds=(-13.0, 7.0, -10.0, 10.0), res=1.0)
    g2 = TargetGrid(
        bounds=tuple(np.float64(x) for x in (-13.0, 7.0, -10.0, 10.0)), res=1.0
    )
    assert "np.float64" not in g1.key
    assert g1.key == g2.key  # numpy floats normalise to the same key


def test_load_dispatches_to_named_module(monkeypatch, tmp_path):
    # Point the cache at a temp dir, then register a fake dataset module under the
    # dispatch path and confirm load() finds it by name and caches the result as COG.
    import sys
    import types

    from nbs_ruralscan.data_loaders import core

    monkeypatch.setattr(core, "CACHE_DIR", tmp_path)
    grid = TargetGrid(bounds=(0.0, 0.0, 2.0, 2.0), res=1.0)
    da = (
        xr.DataArray([[1.0, 2.0], [3.0, 4.0]], dims=("y", "x"))
        .rio.write_crs("EPSG:4326")
        .rio.set_spatial_dims("x", "y")
    )

    fake = types.ModuleType("nbs_ruralscan.data_loaders.datasets.fake_ds")
    fake.load = lambda grid=None, **kw: da  # noqa: ARG005
    sys.modules["nbs_ruralscan.data_loaders.datasets.fake_ds"] = fake

    out = load("fake_ds", grid)
    assert out.attrs["dataset_id"] == "fake_ds"
    assert (tmp_path / f"{core._cache_key('fake_ds', grid, {})}.tif").exists()


@pytest.mark.skipif(
    os.environ.get("NBS_RUN_NET") != "1", reason="needs network + WB download"
)
def test_boundaries_sle():
    sle = load("wb_admin_boundaries", level=0, region="SLE")
    assert len(sle) == 1
    with pytest.raises(ValueError, match="unknown"):
        load("wb_admin_boundaries", level=0, region="XXX")
