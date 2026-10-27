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


def test_soil_input_proposal_is_scoped_unselected_and_thickness_weighted(built):
    policy = built["contract"]["run_contract"]["approved_policies"][0]
    assert not policy["criteria"][0]["input_proposals"]
    for criterion in policy["criteria"][1:]:
        (proposal,) = criterion["input_proposals"]
        assert proposal["layer_weights"] == pytest.approx([1 / 6, 1 / 3, 1 / 2])
        assert proposal["depth_cm"] == [0, 30]
        assert not proposal["selected"]
    assert not policy["execution_ready"]


@pytest.mark.parametrize(
    "mutation",
    ["gap", "overlap", "unsupported_depth", "nan", "activated", "renormalize"],
)
def test_invalid_soil_input_proposals_rejected(built, mutation):
    from nbs_ruralscan.recipe.run_policy import input_proposals

    row = deepcopy(
        next(
            r
            for r in built["contract"]["rows"]
            if r["variable"] == "soil_ph"
            and r["system"] == "agroforestry__planted_silvoarable"
        )
    )
    p = row["dataset"]["documented_input"]["scoping_proposals"][0]
    if mutation == "gap":
        p["layers_cm"][1][0] = 6
    if mutation == "overlap":
        p["layers_cm"][1][0] = 4
    if mutation == "unsupported_depth":
        p["layers_cm"] = [[0, 30]]
    if mutation == "nan":
        p["depth_cm"][1] = float("nan")
    if mutation == "activated":
        p["status"] = "approved"
    if mutation == "renormalize":
        p["missing_layers"] = "renormalize"
    with pytest.raises(ValueError, match="Invalid soil input proposal"):
        input_proposals(row, "planted_terrain_soil_v1")
    assert input_proposals(row, "another_policy") == []
    row["dataset"]["documented_input"] = None
    assert input_proposals(row, "planted_terrain_soil_v1") == []


def test_policy_names_scoped_host_and_legal_masks(built):
    policy = built["contract"]["run_contract"]["approved_policies"][0]
    gates = {g["rule_id"]: g for g in policy["gate_requirements"]}
    assert set(gates) == {
        "agro_planted_silvoarable_land_cover_gate",
        "agro_protected_areas_exclusion",
    }
    assert all(
        g["system"] == policy["system"] and not g["included_in_weighted_sum"]
        for g in gates.values()
    )
    legal = gates["agro_protected_areas_exclusion"]["input_contract"]
    assert legal["input_name"] == "excluded"
    assert legal["decision_status"] == "target_rules_required"
    row = next(
        r
        for r in built["contract"]["rows"]
        if r["rule_id"] == "agro_protected_areas_exclusion"
    )
    assert not row["function_options"]  # No fake numeric/legal category response.
    assert row["weight"]["configured_default"] == 0
    assert "threshold" not in row["declared_relationship"]["params"]
    assert not row["evidence_ids"]


@pytest.mark.parametrize("host", [True, False, None])
@pytest.mark.parametrize("excluded", [True, False, None])
def test_gate_truth_table_preserves_unknown_and_exclusion(built, host, excluded):
    policy = built["contract"]["run_contract"]["approved_policies"][0]
    values = {c["rule_id"]: 0.75 for c in policy["criteria"]}
    result = reference_scores(policy, values, host=host, excluded=excluded)
    expected = (
        "excluded"
        if excluded is True or host is False
        else "unknown"
        if host is None or excluded is None
        else "scored"
    )
    assert result["status"] == expected
    assert result["score"] == (0.75 if expected == "scored" else None)


@pytest.mark.parametrize("mutation", ["missing_legal", "wrong_scope"])
def test_gate_contract_cannot_silently_disappear_or_change_system(built, mutation):
    rows = deepcopy(built["contract"]["rows"])
    if mutation == "missing_legal":
        rows = [r for r in rows if r["role"] != "hard_exclusion"]
    else:
        next(r for r in rows if r["role"] == "hard_exclusion")["gate_input_contract"][
            "scope"
        ] = "another_system"
    with pytest.raises(ValueError, match="gate mappings|scope"):
        compile_policies(
            read_csv(ROOT / "schema/recipes/agroforestry/T4_run_policy.csv"), rows
        )


@pytest.mark.parametrize("category", ["Ia", "II", "Not Reported", 1])
def test_raw_protected_area_categories_are_not_legal_booleans(built, category):
    policy = built["contract"]["run_contract"]["approved_policies"][0]
    with pytest.raises(ValueError, match="Host and exclusion"):
        reference_scores(
            policy,
            {c["rule_id"]: 0.75 for c in policy["criteria"]},
            host=True,
            excluded=category,
        )
