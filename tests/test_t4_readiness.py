"""Implementation readiness must not grant spatial execution authorization."""

from copy import deepcopy
from pathlib import Path
import pytest
from nbs_ruralscan.recipe.developer_contract import build_contract
from nbs_ruralscan.recipe.readiness import assess

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def contract():
    return build_contract(ROOT)["contract"]


def test_partition_accounts_for_every_row_and_first_pass_gate(contract):
    assert contract["summary"]["implementation_readiness"] == {
        "defined": 9,
        "provisional": 2,
        "blocked": 15,
        "reference_only": 12,
    }
    assert (
        sum(contract["summary"]["implementation_readiness"].values())
        == len(contract["rows"])
        == 38
    )
    (policy,) = contract["run_contract"]["approved_policies"]
    assert policy["implementation_readiness"] == {"defined": 3, "provisional": 2}
    assert all(not r["readiness"]["execution_ready"] for r in contract["rows"])
    assert not policy["execution_ready"]


def test_approved_function_is_recognized_without_mutating_selection(contract):
    slope = next(
        r
        for r in contract["rows"]
        if r["rule_id"] == "agroforestry__planted_silvoarable__slope"
    )
    assert slope["function_id"] is None
    assert slope["readiness"]["function_basis"] == "approved_policy"
    assert (
        slope["readiness"]["effective_function_id"]
        == "pool:india_planted_scoping__slope"
    )
    changed = deepcopy(slope)
    changed["approved_policy"]["function_verified"] = False
    assert assess(changed)["state"] == "blocked"
    assert assess(changed)["effective_function_id"] is None


def test_soil_assumptions_and_partial_sources_stay_qualified(contract):
    soil = deepcopy(
        next(
            r
            for r in contract["rows"]
            if r["rule_id"] == "agroforestry__planted_silvoarable__soil_ph"
        )
    )
    assert soil["readiness"]["state"] == "provisional"
    assert soil["readiness"]["proposal_ids"] == ["planted_topsoil_0_30_v1"]
    assert soil["readiness"]["source_input_limit_ids"]
    for option in soil["function_options"]:
        option["completeness"]["status"] = "partial"
    assert assess(soil)["state"] == "blocked"


def test_explicit_alternative_does_not_inherit_policy_proposal(contract):
    row = deepcopy(
        next(
            r
            for r in contract["rows"]
            if r["rule_id"] == "agroforestry__planted_silvoarable__soil_ph"
        )
    )
    alternative = next(
        o
        for o in row["function_options"]
        if o["function_id"] != row["approved_policy"]["function_id"]
    )
    row["function_id"] = alternative["function_id"]
    readiness = assess(row)
    assert readiness["function_basis"] == "explicit_response_selection"
    assert readiness["effective_function_id"] == alternative["function_id"]
    assert readiness["proposal_ids"] == []
    assert set(readiness["source_input_limit_ids"]) <= set(alternative["evidence_ids"])


def test_references_and_placeholders_not_promoted(contract):
    for row in contract["rows"]:
        if row["role"] == "reference_only":
            assert row["readiness"]["state"] == "reference_only"
            assert not row["readiness"]["next_actions"]
        if row["role"] == "operational_scenario":
            assert row["readiness"]["state"] == "blocked"
            assert "placeholders" in row["readiness"]["reason"]


def test_legal_contract_is_implementable_but_not_permission(contract):
    row = next(r for r in contract["rows"] if r["role"] == "hard_exclusion")
    assert row["readiness"]["state"] == "defined"
    assert row["readiness"]["function_basis"] == "authored_mask_contract"
    assert any(a["owner"] == "Target team" for a in row["readiness"]["next_actions"])
    assert not row["readiness"]["execution_ready"]


def test_recipe_host_design_is_not_reported_as_new_user_selection(contract):
    gates = [r for r in contract["rows"] if r["role"] == "eligibility_gate"]
    assert all(r["readiness"]["function_basis"] == "recipe_host_design" for r in gates)
    assert all(r["selection_decision"] is None for r in gates)
