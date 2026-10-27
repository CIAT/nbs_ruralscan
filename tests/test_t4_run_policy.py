"""Approved policy semantics and adversarial configuration checks."""

from copy import deepcopy
from pathlib import Path

import pytest

from nbs_ruralscan.recipe.developer_contract import build_contract, read_csv
from nbs_ruralscan.recipe.run_policy import compile_policies, reference_scores

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def built():
    return build_contract(ROOT)


def test_approved_policy_is_not_geographic_transfer(built):
    contract = built["contract"]
    policy = contract["run_contract"]["approved_policies"][0]
    assert [c["weight"] for c in policy["criteria"]] == [0.5, 0.25, 0.25]
    assert all(c["function_verified"] for c in policy["criteria"])
    assert contract["target_country"] is None
    assert not policy["execution_ready"]
    assert policy["status"] == "approved_pending_target_and_inputs"
    assert all(r["weight"]["runtime_weight"] is None for r in contract["rows"])
    assert all(
        r["role"] == "suitability_score"
        for r in contract["rows"]
        if "approved_policy" in r
    )


@pytest.mark.parametrize(
    "values,expected",
    [([0.25, 0.9, 0.9], 0.575), ([0.9, 0.25, 0.25], 0.575), ([0.75, 0.5, 0.9], 0.725)],
)
def test_approved_weighted_examples(built, values, expected):
    policy = built["contract"]["run_contract"]["approved_policies"][0]
    scores = dict(zip((c["rule_id"] for c in policy["criteria"]), values))
    out = reference_scores(
        policy, scores, host=True, excluded=False, eligible_fraction=0.3
    )
    assert out["score"] == pytest.approx(expected)
    assert out["minimum"] == min(values)
    assert out["eligible_fraction"] == 0.3  # Never multiply score by host share.


def test_unknown_and_exclusion_states(built):
    policy = built["contract"]["run_contract"]["approved_policies"][0]
    scores: dict[str, float | None] = {c["rule_id"]: 0.75 for c in policy["criteria"]}
    scores[next(iter(scores))] = None
    assert (
        reference_scores(policy, scores, host=True, excluded=False)["status"]
        == "unknown"
    )
    assert (
        reference_scores(policy, scores, host=True, excluded=True)["status"]
        == "excluded"
    )
    scores = {k: 0 for k in scores}
    assert (
        reference_scores(policy, scores, host=True, excluded=False)["status"]
        == "scored"
    )
    assert reference_scores(policy, scores, host=None, excluded=False)["score"] is None
    assert reference_scores(policy, scores, host=True, excluded=None)["score"] is None
    assert (
        reference_scores(policy, scores, host=False, excluded=None)["status"]
        == "excluded"
    )
    with pytest.raises(ValueError, match="fixed criterion"):
        reference_scores(policy, {}, host=True, excluded=False)
    with pytest.raises(ValueError, match="Host and exclusion"):
        reference_scores(policy, scores, host=1, excluded=False)


@pytest.mark.parametrize(
    "mutation", ["weight", "group", "role", "duplicate", "aggregation"]
)
def test_invalid_policy_refused(built, mutation):
    rows = deepcopy(built["contract"]["rows"])
    records = read_csv(ROOT / "schema/recipes/agroforestry/T4_run_policy.csv")
    if mutation == "weight":
        records[0]["criterion_weight"] = "0.4"
    if mutation == "group":
        records[0]["variable_group"] = "edaphic"
    if mutation == "role":
        next(r for r in rows if r["rule_id"] == records[0]["rule_id"])["role"] = (
            "eligibility_gate"
        )
    if mutation == "duplicate":
        records.append(records[0].copy())
    if mutation == "aggregation":
        for r in records:
            r["aggregation"] = "unsupported"
    with pytest.raises(ValueError):
        compile_policies(records, rows)


def test_changed_function_is_held_not_replaced(built):
    records = read_csv(ROOT / "schema/recipes/agroforestry/T4_run_policy.csv")
    records[0]["function_fingerprint"] = "changed"
    policy = compile_policies(records, deepcopy(built["contract"]["rows"]))[0]
    assert policy["status"] == "blocked_function_changed"
    assert not policy["criteria"][0]["function_verified"]
    assert not policy["execution_ready"]


def test_country_filter_cannot_silently_reuse_approved_pool():
    result = build_contract(ROOT, evidence_countries=["Ethiopia"])
    policy = result["contract"]["run_contract"]["approved_policies"][0]
    assert policy["status"] == "blocked_function_changed"
    assert not any(c["function_verified"] for c in policy["criteria"])
