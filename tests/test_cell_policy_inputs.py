"""Explicit synthesis policy inputs cannot fall back to installed schema state."""

from copy import deepcopy
import subprocess
import sys
from typing import Any

import pytest

from nbs_ruralscan.recipe import cell_synthesis as cs
from nbs_ruralscan.recipe.evidence import EvidenceUnit


STRONG_BANDS = [
    {"metric": "pct_change", "abs_min": 0, "abs_max": "", "strength_class": "strong"}
]
XW = [cs.XWRow("water_yield", "T6", "water_stress")]


def unit(n, *, positive=True, family="planted", income="low", magnitude=None):
    relationship: dict[str, Any] = {
        "direction": "positive" if positive else "negative",
        "strength_class": "unspecified" if magnitude is None else "moderate",
        "metric": "pct_change",
        "unit": "percent",
        "design": "meta_analysis" if family == "planted" else "expert",
    }
    if magnitude is None:
        relationship.update(magnitude_low=10, magnitude_high=20)
    else:
        relationship["magnitude"] = magnitude
    return EvidenceUnit(
        evidence_id=f"e{n}",
        source_id=f"s{n}",
        nbs_id="riparian_buffer",
        suitability_family_id=f"riparian_buffer__{family}",
        variable="water_yield",
        use_role="nbs_effect",
        evidence_type="literature_relationship",
        claim_basis="primary_measured",
        claim_scope="practice_technology",
        extraction_confidence="high",
        quote="Synthetic policy-plumbing fixture",
        locator_type="page",
        page=1,
        relationship=relationship,
        context={"income_group": income},
    )


def opposing_groups():
    return [unit(i, income="high") for i in range(2)] + [
        unit(i, positive=False, family="natural") for i in range(2, 4)
    ]


def compile_cells(units, *, families=False, **policy):
    compile_cell = cs.synthesise_cell_with_families if families else cs.synthesise_cell
    return compile_cell(
        units,
        {u.source_id: "high" for u in units},
        table="T6",
        nbs_id="riparian_buffer",
        target_key="water_stress",
        xw_rows=XW,
        **policy,
    )


def forbidden(*args, **kwargs):
    pytest.fail("Explicit policy must not read installed-checkout defaults")


@pytest.fixture
def explicit_only(monkeypatch):
    monkeypatch.setattr(cs, "_default_bands", forbidden)
    monkeypatch.setattr(cs, "_default_design_weights", forbidden)


def test_interleaved_policies_reach_global_and_scope_rows(explicit_only):
    units = opposing_groups()
    positive = {"meta_analysis": 20.0, "expert": 1.0}
    negative = {"meta_analysis": 0.1, "expert": 4.0}
    before = deepcopy((units, STRONG_BANDS, positive, negative))
    a, _ = compile_cells(units, bands=STRONG_BANDS, design_weights=positive)
    b, _ = compile_cells(units, bands=STRONG_BANDS, design_weights=negative)
    again, _ = compile_cells(units, bands=STRONG_BANDS, design_weights=positive)
    assert a == again
    assert a[0]["effect_direction"] == "strong_positive"
    assert b[0]["effect_direction"] == "strong_negative"
    assert [(r["scope_id"], r["effect_direction"]) for r in a[1:]] == [
        ("lic_lmic", "strong_negative")
    ]
    assert [(r["scope_id"], r["effect_direction"]) for r in b[1:]] == [
        ("high", "strong_positive")
    ]
    assert (units, STRONG_BANDS, positive, negative) == before


def test_explicit_empty_policies_stay_empty(explicit_only):
    u = unit(0)
    assert cs.design_factor(u, design_weights={}) == 1.0
    assert cs.unit_weight(u, "high", "", 0, design_weights={}) == (
        cs.TIER_W["high"] * cs.BASIS_W[u.claim_basis]
    )
    assert cs.unit_rank(u, bands=[]) == (1, None)
    rows, _ = compile_cells(opposing_groups(), bands=[], design_weights={})
    assert rows[0]["effect_direction"] == "slight_negative"
    assert rows[1]["scope_id"] == "high"
    assert rows[1]["effect_direction"] == "slight_positive"


def test_policy_reaches_family_rows(explicit_only):
    rows, _ = compile_cells(
        opposing_groups(),
        families=True,
        bands=STRONG_BANDS,
        design_weights={"meta_analysis": 20.0, "expert": 1.0},
    )
    families = {
        r["suitability_family_id"]: r for r in rows if r["suitability_family_id"]
    }
    assert families["riparian_buffer__planted"]["effect_direction"] == "strong_positive"
    assert families["riparian_buffer__natural"]["effect_direction"] == "strong_negative"


def test_weights_and_bands_control_magnitude_summary(explicit_only):
    units = [unit(0, magnitude=10), unit(1, family="natural", magnitude=40)]
    bands = [
        {
            "metric": "pct_change",
            "abs_min": 0,
            "abs_max": 20,
            "strength_class": "slight",
        },
        {
            "metric": "pct_change",
            "abs_min": 20,
            "abs_max": "",
            "strength_class": "strong",
        },
    ]
    low, _ = compile_cells(
        units, bands=bands, design_weights={"meta_analysis": 10.0, "expert": 1.0}
    )
    high, _ = compile_cells(
        units, bands=bands, design_weights={"meta_analysis": 1.0, "expert": 10.0}
    )
    empty, _ = compile_cells(units, bands=[], design_weights={})
    assert low[0]["magnitude_summary"]["median"] == 10
    assert low[0]["magnitude_summary"]["class"] == "slight"
    assert high[0]["magnitude_summary"]["median"] == 40
    assert high[0]["magnitude_summary"]["class"] == "strong"
    assert empty[0]["magnitude_summary"]["class"] == "unspecified"


def test_none_keeps_lazy_legacy_defaults(monkeypatch):
    loads = []
    weights = {"meta_analysis": 20.0, "expert": 1.0}

    def load():
        loads.append("design")
        return weights

    cs._default_design_weights.cache_clear()
    monkeypatch.setattr(cs, "load_design_weights", load)
    monkeypatch.setattr(cs, "_default_bands", lambda: STRONG_BANDS)
    try:
        default, _ = compile_cells(opposing_groups(), bands=None, design_weights=None)
        explicit, _ = compile_cells(
            opposing_groups(), bands=STRONG_BANDS, design_weights=weights
        )
        assert default == explicit
        assert loads == ["design"]
    finally:
        cs._default_design_weights.cache_clear()


def test_import_does_not_probe_installed_design_policy():
    script = """
import builtins
from pathlib import Path

old_open, old_path_open, old_exists = builtins.open, Path.open, Path.exists
def guard(path):
    if str(path).endswith('design_weights.csv'):
        raise AssertionError('Import read installed design weights')
def checked_open(path, *args, **kwargs):
    guard(path)
    return old_open(path, *args, **kwargs)
def checked_path_open(path, *args, **kwargs):
    guard(path)
    return old_path_open(path, *args, **kwargs)
def checked_exists(path):
    guard(path)
    return old_exists(path)
builtins.open, Path.open, Path.exists = checked_open, checked_path_open, checked_exists
from nbs_ruralscan.recipe import cell_synthesis
assert cell_synthesis._default_design_weights.cache_info().currsize == 0
"""
    subprocess.run(
        [sys.executable, "-c", script], check=True, capture_output=True, text=True
    )
