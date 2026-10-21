"""Uncalibrated suitability direction is valid evidence, not an executable curve."""

import pytest

from nbs_ruralscan.recipe.evidence import EvidenceUnit, validate_units
from nbs_ruralscan.recipe.t4_relationships import decode


@pytest.mark.parametrize(
    "direction",
    ["increasing", "decreasing", "optimum_range", "non_monotonic", "unclear"],
)
def test_direction_survives_extraction_without_inventing_numeric_response(direction):
    unit = EvidenceUnit(
        evidence_id="directional_claim",
        source_id="example",
        nbs_id="agroforestry",
        suitability_family_id="agroforestry__cross_family",
        variable="slope",
        use_role="structural_suitability",
        evidence_type="scoping_candidate",
        claim_basis="figure_read",
        claim_scope="practice_technology",
        extraction_confidence="medium",
        quote="Suitability table: slope direction is shown by the suitability colour key.",
        page=10,
        relationship={"direction": direction},
        context={"reported_values": {"source_endpoints": [0, 45], "unit": "%"}},
    )
    assert validate_units([unit]) == {}
    kind, params, hold = decode(unit.relationship)
    assert kind == ""
    assert params == {}
    assert hold
    assert unit.relationship == {"direction": direction}
    assert unit.context["reported_values"]["source_endpoints"] == [0, 45]


def test_source_weight_does_not_calibrate_direction():
    kind, params, hold = decode({"direction": "increasing", "source_weight_pct": 16.66})
    assert not kind and not params and hold
