"""Tests for the T4 synthesis engine."""

from __future__ import annotations

from typing import Any

from nbs_ruralscan.recipe.evidence import EvidenceUnit
from nbs_ruralscan.recipe.synthesis import (
    _dedupe_lineage,
    _harmonise,
    normalize_shape_keys,
    synthesise_t4_row,
    SynthesisReport,
)


def test_normalize_shape_keys_maps_aliases():
    # non-canonical range keys (from the 2026-07 FMNR sweep) → canonical shape keys
    assert normalize_shape_keys({"range_min": 100, "range_max": 950})["abs_min"] == 100
    assert (
        normalize_shape_keys({"precip_mm_low": 251, "precip_mm_high": 750})["abs_max"]
        == 750
    )
    assert (
        normalize_shape_keys({"optimum_low_mm": 400, "optimum_high_mm": 800})["opt_low"]
        == 400
    )
    # never overwrite an existing canonical key
    assert normalize_shape_keys({"abs_min": 5, "range_min": 99})["abs_min"] == 5
    # non-numeric alias is ignored (categorical); non-shape keys pass through untouched
    out = normalize_shape_keys({"range_min": "low", "direction": "envelope"})
    assert "abs_min" not in out and out["direction"] == "envelope"


def test_harmonise_reads_aliased_range():
    u = _sample_unit(relationship={"range_min": 251, "range_max": 750, "unit": "mm"})
    h = _harmonise(u, "mm")
    assert h["abs_min"] == 251 and h["abs_max"] == 750


def _sample_unit(**overrides: Any) -> EvidenceUnit:
    defaults: dict[str, Any] = dict(
        evidence_id="ev_01",
        source_id="smith_2020",
        nbs_id="agroforestry",
        suitability_family_id="F1",
        variable="slope",
        use_role="structural_suitability",
        evidence_type="literature_relationship",
        claim_basis="primary_measured",
        claim_scope="practice_technology",
        extraction_confidence="high",
        quote="slope < 15%",
        page=2,
        relationship={"abs_min": 0, "abs_max": 15, "unit": "%"},
    )
    defaults.update(overrides)
    return EvidenceUnit(**defaults)


def test_dedupe_lineage_recursive():
    """Ensure lineage echoes collapse recursively to primary studies when present."""
    # Cascade: C -> B -> A (primary)
    # Also another cascade: E -> D (external, D not in units list)
    units = [
        _sample_unit(evidence_id="ev_A", source_id="paper_A", lineage_of=None),
        _sample_unit(evidence_id="ev_B", source_id="paper_B", lineage_of="paper_A"),
        _sample_unit(evidence_id="ev_C", source_id="paper_C", lineage_of="ev_B"),
        _sample_unit(
            evidence_id="ev_E", source_id="paper_E", lineage_of="paper_D_external"
        ),
    ]

    tiers = {
        "paper_A": "high",
        "paper_B": "medium",
        "paper_C": "low",
        "paper_E": "medium",
    }
    report = SynthesisReport()

    kept = _dedupe_lineage(units, tiers, report)

    # We should keep paper_A (primary, highest weight in that lineage tree)
    # and paper_E (whose lineage is external, so it's the root we have for that tree)
    kept_ev_ids = {u.evidence_id for u in kept}
    assert kept_ev_ids == {"ev_A", "ev_E"}

    # Check that collapsed reports are populated correctly
    collapsed_pairs = sorted(report.collapsed)
    assert len(collapsed_pairs) == 2
    # ev_B collapses to paper_A
    # ev_C collapses to paper_A
    assert collapsed_pairs[0] == ("ev_B", "paper_A")
    assert collapsed_pairs[1] == ("ev_C", "paper_A")


def test_harmonise_bidirectional_conversions():
    """Ensure pct-to-deg and deg-to-pct conversions work in both directions."""
    # 1. Pct to Deg (slope of 100% is 45 degrees)
    u_pct = _sample_unit(relationship={"abs_min": 0, "abs_max": 100, "unit": "%"})
    res_deg = _harmonise(u_pct, canonical_unit="degrees")
    assert res_deg["abs_min"] == 0.0
    assert res_deg["abs_max"] == 45.0

    # 2. Deg to Pct (slope of 45 degrees is 100%)
    u_deg = _sample_unit(relationship={"abs_min": 0, "abs_max": 45, "unit": "deg"})
    res_pct = _harmonise(u_deg, canonical_unit="percent")
    assert res_pct["abs_min"] == 0.0
    assert abs(res_pct["abs_max"] - 100.0) < 0.2


def test_uncertainty_spread_multiple_parameters():
    """Ensure spread calculation applies across multiple threshold parameters."""
    # We need at least two contributing units to evaluate spread.
    # Unit 1: opt_low=10, abs_max=30
    # Unit 2: opt_low=12, abs_max=40
    # Weighted median (equal weights) of opt_low is 11, of abs_max is 35
    # Spread for opt_low: (12 - 10) / 11 * 100 = 18.18%
    # Spread for abs_max: (40 - 30) / 35 * 100 = 28.57%
    # Overall uncertainty should be max of these: 29%
    u1 = _sample_unit(
        evidence_id="ev_01",
        source_id="src_1",
        relationship={
            "abs_min": 0,
            "opt_low": 10,
            "opt_high": 25,
            "abs_max": 30,
            "unit": "deg",
        },
    )
    u2 = _sample_unit(
        evidence_id="ev_02",
        source_id="src_2",
        relationship={
            "abs_min": 0,
            "opt_low": 12,
            "opt_high": 25,
            "abs_max": 40,
            "unit": "deg",
        },
    )
    u3 = _sample_unit(
        evidence_id="ev_03",
        source_id="src_3",
        relationship={
            "abs_min": 0,
            "opt_low": 11,
            "opt_high": 25,
            "abs_max": 35,
            "unit": "deg",
        },
    )

    tiers = {"src_1": "high", "src_2": "high", "src_3": "high"}

    row, rep = synthesise_t4_row(
        [u1, u2, u3],
        tiers,
        variable="slope",
        family="F1",
        canonical_unit="deg",
    )

    # Three independent sources -> no thin evidence penalty.
    # Reconciled parameters: opt_low = 11, abs_max = 35.
    # Max spread pct is from abs_max: (40 - 30) / 35 * 100 = 28.57% -> 29.0
    assert row["uncertainty_pct"] == 29.0
