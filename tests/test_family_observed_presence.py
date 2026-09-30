from typing import Any

from nbs_ruralscan.recipe.evidence import EvidenceUnit
from nbs_ruralscan.recipe.family import is_observed_presence, synthesise_family


def _u(**kw: Any) -> EvidenceUnit:
    d: dict[str, Any] = dict(
        evidence_id="ev_lit",
        source_id="lit_2020",
        nbs_id="water_harvesting_conservation",
        suitability_family_id="water_harvesting__terracing",
        variable="slope",
        use_role="structural_suitability",
        evidence_type="literature_relationship",
        claim_basis="primary_measured",
        claim_scope="practice_technology",
        extraction_confidence="high",
        quote="terraces suit slopes of 5 to 25%",
        page=2,
        relationship={"abs_min": 5, "abs_max": 25, "unit": "percent"},
    )
    d.update(kw)
    return EvidenceUnit(**d)


def _wocat(i: int) -> EvidenceUnit:
    return _u(
        evidence_id=f"ev_wocat_{i}",
        source_id=f"wocat_{i}_2020",
        evidence_type="scoping_candidate",
        claim_basis="expert_assertion",
        quote="NATURAL ENVIRONMENT Slope steep (31-60%)",
        relationship={
            "type": "observed_presence",
            "observed_classes": ["steep (31-60%)"],
            "observed_min": 31,
            "observed_max": 60,
            "unit": "percent",
        },
    )


def test_marker():
    assert is_observed_presence(_wocat(1))
    assert not is_observed_presence(_u())


def test_observed_presence_neither_votes_nor_sets_thresholds():
    def run(units: list[EvidenceUnit]):
        return synthesise_family(
            units,
            {"lit_2020": "high"},
            family="water_harvesting__terracing",
            corpus_n=1,
            group_map={"slope": "topographic"},
            canonical_units={"slope": "percent"},
        )

    base = run([_u()])
    with_forms = run([_u()] + [_wocat(i) for i in range(10)])
    assert (
        base.rows[0]["relationship_params"] == with_forms.rows[0]["relationship_params"]
    )
    assert [r["evidence_ids"] for r in base.rows] == [
        r["evidence_ids"] for r in with_forms.rows
    ]
