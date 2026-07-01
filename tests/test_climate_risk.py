"""Tests for M2 climate-risk compute — the implemented arithmetic (offline, synthetic).

The methodology stubs (standardize_hazard, vulnerability_composite) intentionally raise
until authored in Session C; this asserts that contract too.
"""

from __future__ import annotations

import numpy as np
import pytest
import xarray as xr

from nbs_ruralscan.modules.climate_risk import compute


def _da(vals):
    return xr.DataArray(np.array(vals, dtype=float), dims=("y", "x"))


def test_normalize_01_rescales_and_handles_flat():
    out = compute.normalize_01(_da([[0.0, 5.0], [10.0, 10.0]]))
    assert float(out.min()) == 0.0 and float(out.max()) == 1.0
    flat = compute.normalize_01(_da([[3.0, 3.0], [3.0, 3.0]]))
    assert float(flat.max()) == 0.0  # no range → zeros, no divide-by-zero


def test_combine_hazard_exposure_ops():
    h, e = _da([[1.0, 0.5]]), _da([[0.4, 1.0]])
    assert compute.combine_hazard_exposure(h, e, "multiply").values.tolist() == [
        [0.4, 0.5]
    ]
    with pytest.raises(ValueError, match="unknown combine op"):
        compute.combine_hazard_exposure(h, e, "bogus")


def test_composite_risk_weighted_and_normalised():
    layers = {"drought": _da([[0.0, 1.0]]), "heat": _da([[1.0, 0.0]])}
    out = compute.composite_risk(
        layers, {"drought": 3.0, "heat": 1.0}
    )  # unequal, un-normalised
    assert float(out.min()) == 0.0 and float(out.max()) == 1.0
    with pytest.raises(ValueError, match="no per-hazard"):
        compute.composite_risk({}, {})


def test_delta_is_signed_difference():
    d = compute.delta(_da([[0.8, 0.2]]), _da([[0.5, 0.5]]))
    assert d.values.tolist() == [[pytest.approx(0.3), pytest.approx(-0.3)]]


def test_methodology_stubs_not_yet_implemented():
    with pytest.raises(NotImplementedError):
        compute.standardize_hazard(_da([[1.0]]), {})
    with pytest.raises(NotImplementedError):
        compute.vulnerability_composite(_da([[1.0]]), _da([[1.0]]))
