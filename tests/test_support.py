"""Tests for the variable and group support prevalence logic."""

from nbs_ruralscan.evidence import EvidenceUnit
from nbs_ruralscan.support import (
    variable_support,
    group_support,
    selection_table,
    attach_support,
)


def test_variable_support_without_tiers():
    """Without tiers, prevalence is a simple percentage of papers."""
    units = [
        EvidenceUnit(
            evidence_id="ev1",
            source_id="src_a",
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
        ),
        EvidenceUnit(
            evidence_id="ev2",
            source_id="src_b",
            nbs_id="agroforestry",
            suitability_family_id="F1",
            variable="slope",
            use_role="structural_suitability",
            evidence_type="literature_relationship",
            claim_basis="primary_measured",
            claim_scope="practice_technology",
            extraction_confidence="high",
            quote="slope < 20%",
            page=4,
        ),
        EvidenceUnit(
            evidence_id="ev3",
            source_id="src_a",
            nbs_id="agroforestry",
            suitability_family_id="F1",
            variable="rainfall",
            use_role="structural_suitability",
            evidence_type="literature_relationship",
            claim_basis="primary_measured",
            claim_scope="practice_technology",
            extraction_confidence="high",
            quote="rainfall > 800",
            page=3,
        ),
    ]

    # total corpus count of papers is 2 (src_a and src_b are seen)
    res = variable_support(units, corpus_n=2)

    # slope is in both papers (src_a, src_b) -> 2/2 = 100%
    assert res["slope"].pct == 100.0
    assert res["slope"].n_sources == 2
    assert res["slope"].corpus_n == 2

    # rainfall is in one paper (src_a) -> 1/2 = 50%
    assert res["rainfall"].pct == 50.0
    assert res["rainfall"].n_sources == 1
    assert res["rainfall"].corpus_n == 2


def test_variable_support_with_tiers():
    """With tiers, prevalence is scaled by benchmark_tier (High=1.0, Med=0.6, Low=0.35)."""
    units = [
        # high-tier source
        EvidenceUnit(
            evidence_id="ev1",
            source_id="src_high",
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
        ),
        # low-tier source
        EvidenceUnit(
            evidence_id="ev2",
            source_id="src_low",
            nbs_id="agroforestry",
            suitability_family_id="F1",
            variable="rainfall",
            use_role="structural_suitability",
            evidence_type="literature_relationship",
            claim_basis="primary_measured",
            claim_scope="practice_technology",
            extraction_confidence="high",
            quote="rainfall > 800",
            page=3,
        ),
    ]

    tiers = {"src_high": "high", "src_low": "low"}
    # If corpus_n is a set of the source ids:
    res = variable_support(units, corpus_n={"src_high", "src_low"}, tiers=tiers)

    # Denominator = weight(src_high) + weight(src_low) = 1.0 + 0.35 = 1.35
    # slope is in src_high (weight 1.0) -> 1.0 / 1.35 = ~74.1%
    # rainfall is in src_low (weight 0.35) -> 0.35 / 1.35 = ~25.9%
    assert res["slope"].pct == 74.1
    assert res["rainfall"].pct == 25.9

    # Test with integer corpus_n
    # When corpus_n is an integer (say 3), the unseen paper is assumed to have default "medium" weight = 0.6
    # Denominator = weight(src_high) + weight(src_low) + 1 * weight(unseen_medium) = 1.0 + 0.35 + 0.6 = 1.95
    # slope in src_high -> 1.0 / 1.95 = ~51.3%
    # rainfall in src_low -> 0.35 / 1.95 = ~17.9%
    res_int = variable_support(units, corpus_n=3, tiers=tiers)
    assert res_int["slope"].pct == 51.3
    assert res_int["rainfall"].pct == 17.9


def test_group_support():
    """Group support rolls up variables to their groups using set-union over papers."""
    units = [
        EvidenceUnit(
            evidence_id="ev1",
            source_id="src_a",
            nbs_id="agroforestry",
            suitability_family_id="F1",
            variable="slope",
            use_role="structural_suitability",
            evidence_type="literature_relationship",
            claim_basis="primary_measured",
            claim_scope="practice_technology",
            extraction_confidence="high",
            quote="...",
            page=1,
        ),
        EvidenceUnit(
            evidence_id="ev2",
            source_id="src_a",
            nbs_id="agroforestry",
            suitability_family_id="F1",
            variable="elevation",
            use_role="structural_suitability",
            evidence_type="literature_relationship",
            claim_basis="primary_measured",
            claim_scope="practice_technology",
            extraction_confidence="high",
            quote="...",
            page=2,
        ),
        EvidenceUnit(
            evidence_id="ev3",
            source_id="src_b",
            nbs_id="agroforestry",
            suitability_family_id="F1",
            variable="elevation",
            use_role="structural_suitability",
            evidence_type="literature_relationship",
            claim_basis="primary_measured",
            claim_scope="practice_technology",
            extraction_confidence="high",
            quote="...",
            page=3,
        ),
    ]

    group_map = {"slope": "topographic", "elevation": "topographic"}
    res = group_support(units, group_map, corpus_n=2)

    # Both papers mention at least one topographic variable.
    # So set-union is {src_a, src_b} -> 2/2 = 100%
    assert res["topographic"].pct == 100.0
    assert res["topographic"].n_sources == 2
    assert res["topographic"].members == ["elevation", "slope"]


def test_selection_table():
    """Test floor_pct and override rules."""
    from nbs_ruralscan.support import Support

    var_support = {
        "slope": Support(key="slope", n_sources=3, corpus_n=10, pct=30.0),
        "elevation": Support(key="elevation", n_sources=1, corpus_n=10, pct=10.0),
    }

    # Default floor_pct = 20.0
    # slope (30%) -> include
    # elevation (10%) -> review_low_support
    res1 = selection_table(var_support, floor_pct=20.0)
    rows = {r.variable: r for r in res1}
    assert rows["slope"].decision == "include"
    assert rows["elevation"].decision == "review_low_support"

    # With ML override on elevation
    res2 = selection_table(var_support, floor_pct=20.0, ml_important={"elevation"})
    rows2 = {r.variable: r for r in res2}
    assert rows2["elevation"].decision == "include_ml_override"


def test_attach_support():
    from nbs_ruralscan.support import Support

    var_support = {"slope": Support(key="slope", n_sources=3, corpus_n=10, pct=30.0)}
    row = {"variable": "slope", "justification": "foo"}
    attach_support(row, var_support)
    assert row["paper_support_pct"] == 30.0
    assert row["n_sources"] == 3
    assert row["corpus_n"] == 10
