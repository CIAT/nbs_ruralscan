"""Human-reviewed steps preserve source claims, boundaries and unknown tails."""

from copy import deepcopy
import json

import numpy as np
import pytest

from nbs_ruralscan.recipe.evidence import EvidenceUnit
from nbs_ruralscan.recipe.numeric_bands import (
    compile_bands,
    completion_fingerprint,
    context_fingerprint,
)
from nbs_ruralscan.runtime.numeric import evaluate_numeric


def band(lower, upper, label, lower_inclusive=True, upper_inclusive=True):
    return dict(
        lower=lower,
        upper=upper,
        label=label,
        lower_inclusive=lower_inclusive,
        upper_inclusive=upper_inclusive,
    )


def setup():
    unit = EvidenceUnit(
        evidence_id="reviewed",
        source_id="source",
        nbs_id="wetland_management",
        suitability_family_id="wetland_management__peatland",
        variable="water_table_depth",
        use_role="structural_suitability",
        evidence_type="literature_relationship",
        claim_basis="table",
        claim_scope="practice_technology",
        extraction_confidence="high",
        quote="Source class table, with no zero tail.",
        page=3,
        reviewer_ok=True,
        relationship={"unit": "cm", "source_classes": ["0-30", "30-80", "80-160"]},
        context={"scope": "drained former-wetland farmland"},
    )
    adaptation = dict(
        kind="human_reviewed_step_profile",
        reviewer="Pete",
        reviewed_date="2026-11-05",
        decision_ref="methodology/decisions/review.md#water-depth",
        scope="Rewetting drained former-wetland farmland only",
        note="Human normalized scores and zero tail; not a source ecological limit.",
        input_unit="cm",
        evidence_fingerprint=completion_fingerprint(unit),
        context_fingerprint=context_fingerprint(unit),
        intervals=[
            band(0, 30, "high"),
            band(30, 80, "moderate", False),
            band(80, 160, "marginal", False),
            band(160, None, "screened_out", False, False),
        ],
    )
    policy = dict(
        action="compile",
        encoding="reviewed_intervals",
        input_unit="cm",
        ordinal_scale=json.dumps(
            {"high": 3, "moderate": 2, "marginal": 1, "screened_out": 0}
        ),
        applicability_note=adaptation["scope"],
        harmonization=dict(
            version="human_reviewed_steps_v1",
            score_kind="ordinal",
            class_scores={
                "high": 1,
                "moderate": 0.66,
                "marginal": 0.33,
                "screened_out": 0,
            },
            source_scores={"high": 3, "moderate": 2, "marginal": 1},
            reviewed_adaptation=adaptation,
        ),
    )
    return unit, policy


def compile_case(unit, policy):
    return compile_bands([unit], {unit.evidence_id: policy}, "cm", {})


def evaluate(params, values, selected=True):
    return evaluate_numeric(
        {"relationship_type": "piecewise", "relationship_params": params},
        values,
        profile_id="reviewed" if selected else None,
    )


def test_reviewed_boundaries_scores_and_provenance_are_exact():
    unit, policy = setup()
    source = deepcopy(unit.relationship)
    params, used, unresolved = compile_case(unit, policy)
    assert used == ["reviewed"] and unresolved == []
    np.testing.assert_allclose(
        evaluate(params, [-1, 0, 30, 30.01, 80, 80.01, 160, 160.01, np.nan]),
        [np.nan, 1, 1, 0.66, 0.66, 0.33, 0.33, 0, np.nan],
        equal_nan=True,
    )
    profile = params["profiles"][0]
    assert unit.relationship == source == profile["source_relationship"]
    assert (
        profile["reviewed_adaptation"] == policy["harmonization"]["reviewed_adaptation"]
    )
    assert profile["intervals"][1]["source_score"] == 2
    assert profile["intervals"][1]["score_basis"] == "reviewed_scoping_adaptation"
    assert params["harmonization"]["pools"] == []
    assert np.isnan(evaluate(params, [10], selected=False)).all()


def test_unapproved_tail_and_negative_domain_remain_unknown():
    unit, policy = setup()
    policy["harmonization"]["reviewed_adaptation"]["intervals"].pop()
    params, _, unresolved = compile_case(unit, policy)
    assert not unresolved
    np.testing.assert_allclose(
        evaluate(params, [-1, 160, 161]), [np.nan, 0.33, np.nan], equal_nan=True
    )


def test_qualitative_classes_do_not_invent_normalization():
    unit, policy = setup()
    policy["harmonization"]["class_scores"] = {}
    params, _, unresolved = compile_case(unit, policy)
    assert not unresolved
    assert np.isnan(evaluate(params, [0, 40, 100, 200])).all()
    assert params["profiles"][0]["intervals"][0]["source_score"] == 3


@pytest.mark.parametrize(
    "field,value",
    [
        ("quote", "Changed source text"),
        ("source_id", "other_source"),
        ("suitability_family_id", "another_family"),
        ("context", {"scope": "all farmland"}),
        ("relationship", {"unit": "m"}),
        ("reviewer_ok", False),
        ("review_state", "dropped"),
        ("claim_scope", "species_specific"),
        ("use_role", "nbs_effect"),
    ],
)
def test_changed_claim_or_scope_cannot_reuse_approval(field, value):
    unit, policy = setup()
    setattr(unit, field, value)
    params, used, unresolved = compile_case(unit, policy)
    assert not params and not used
    assert unresolved == [("reviewed", "invalid_or_stale_reviewed_adaptation")]


@pytest.mark.parametrize(
    "field,value",
    [
        ("reviewer", ""),
        ("note", " "),
        ("scope", ""),
        ("decision_ref", ""),
        ("kind", "inferred"),
        ("evidence_fingerprint", "bad"),
        ("context_fingerprint", "bad"),
        ("input_unit", "m"),
        ("reviewed_date", "2026-02-30"),
        ("reviewed_date", "20261105"),
    ],
)
def test_unsigned_stale_or_invalid_provenance_is_rejected(field, value):
    unit, policy = setup()
    policy["harmonization"]["reviewed_adaptation"][field] = value
    params, used, unresolved = compile_case(unit, policy)
    assert not params and not used and unresolved


@pytest.mark.parametrize(
    "mutation",
    [
        lambda b: b[1].update(lower_inclusive=True),
        lambda b: b[1].update(lower=29),
        lambda b: b[1].update(lower=True),
        lambda b: b[1].update(upper=float("inf")),
        lambda b: b[1].update(lower_inclusive=1),
        lambda b: b[1].update(upper=20),
        lambda b: b[1].update(label="unknown"),
        lambda b: b[1].update(score=0.75),
        lambda b: b[3].update(upper_inclusive=True),
    ],
)
def test_overlapping_or_invalid_intervals_are_rejected(mutation):
    unit, policy = setup()
    mutation(policy["harmonization"]["reviewed_adaptation"]["intervals"])
    params, used, unresolved = compile_case(unit, policy)
    assert not params and not used and unresolved


@pytest.mark.parametrize(
    "field,value", [("pool_id", "shared"), ("compatibility_approved", True)]
)
def test_reviewed_adaptations_cannot_automatically_pool(field, value):
    unit, policy = setup()
    policy["harmonization"][field] = value
    params, used, unresolved = compile_case(unit, policy)
    assert not params and not used
    assert unresolved == [("reviewed", "reviewed_adaptation_pooling_not_supported")]


def test_boolean_scores_and_ranks_are_rejected():
    for key in ("class_scores", "ordinal_scale"):
        unit, policy = setup()
        if key == "class_scores":
            policy["harmonization"][key]["high"] = True
        else:
            policy[key] = json.dumps({"high": True})
        params, used, unresolved = compile_case(unit, policy)
        assert not params and not used and unresolved


def test_existing_labelled_ranges_keep_original_boundary_behavior():
    unit, policy = setup()
    unit.relationship = {
        "unit": "cm",
        "classes": [
            {"range": "0-30", "label": "high"},
            {"range": "30-80", "label": "moderate"},
        ],
    }
    policy.update(encoding="labelled_ranges", field="classes", harmonization={})
    params, used, unresolved = compile_case(unit, policy)
    assert used and not unresolved
    assert np.isnan(evaluate(params, [30])).all()


def test_missing_adaptation_and_selection_only_evidence_are_rejected():
    unit, policy = setup()
    policy["harmonization"].pop("reviewed_adaptation")
    params, used, unresolved = compile_case(unit, policy)
    assert not params and not used
    assert unresolved == [("reviewed", "reviewed_adaptation_required")]
    unit, policy = setup()
    unit.evidence_type = "ml_importance"
    params, used, unresolved = compile_case(unit, policy)
    assert not params and not used
    assert unresolved == [("reviewed", "selection_only")]


def test_policy_input_unit_cannot_change_after_review():
    unit, policy = setup()
    policy["input_unit"] = "m"
    params, used, unresolved = compile_case(unit, policy)
    assert not params and not used
    assert unresolved == [("reviewed", "invalid_or_stale_reviewed_adaptation")]
