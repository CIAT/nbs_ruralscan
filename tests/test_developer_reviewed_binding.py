"""Reviewed input requirements survive developer export and function selection."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from nbs_ruralscan.recipe import developer_contract as dc
from nbs_ruralscan.runtime.binding import Binding

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def wetland():
    return dc.build_contract(ROOT, nbs="wetland_management", country="NLD")


def profile_rows(result):
    return [
        r
        for r in result["contract"]["rows"]
        if r["function_options"] and r["role"] == "suitability_score"
    ]


def assert_input_held(row):
    dataset = row["dataset"]
    assert dataset["needs_upload"] is True
    assert dataset["matching_input_required"] is True
    assert dataset["hold_reason"]
    for key in (
        "dataset_id",
        "asset",
        "binding_id",
        "preferred_binding_id",
        "band",
        "documented_input",
    ):
        assert dataset[key] is None
    assert dataset["prompt"] in row["blockers"]
    assert row["status"] == "blocked"


def test_all_four_wetland_profiles_preserve_source_and_input_holds(wetland):
    rows = profile_rows(wetland)
    assert len(rows) == 4
    originals = {
        r["mapping_id"]: json.loads(r["relationship_params"])["profiles"][0]
        for r in dc.read_csv(
            ROOT / "schema/recipes/wetland_management/T4_suitability_mappings.csv"
        )
    }
    for row in rows:
        assert_input_held(row)
        assert len(row["function_options"]) == 1
        option = row["function_options"][0]
        original = originals[row["rule_id"]]
        for key in ("reviewed_adaptation", "source_relationship"):
            assert option[key] == original[key]
        assert (
            option["reviewed_adaptation"]["dataset_binding"]["reason"]
            == row["dataset"]["hold_reason"]
        )
        assert option["reviewed_adaptation"]["reviewer"]
        assert option["reviewed_adaptation"]["decision_ref"]


@pytest.mark.parametrize(
    "rule_id",
    [
        "wetland_management__creation__distance_to_waterbody",
        "wetland_management__restoration_rewetting__distance_to_waterbody",
        "wetland_management__peatland__water_table_depth",
    ],
)
def test_selected_response_cannot_release_matching_input_hold(wetland, rule_id):
    row = next(r for r in profile_rows(wetland) if r["rule_id"] == rule_id)
    option = row["function_options"][0]
    selection = {
        "contract_version": dc.VERSION,
        "selections": {
            row["rule_id"]: {
                "function_id": option["function_id"],
                "function_fingerprint": option["fingerprint"],
                "target_system": row["system"],
                "applicability_country": "NLD",
                "applicability_note": "Test explicit selection only; no input validation.",
                "decision_reference": "test-reviewed-function-selection",
            }
        },
    }
    result = dc.build_contract(
        ROOT, nbs="wetland_management", country="NLD", selection=selection
    )
    selected = next(
        r for r in result["contract"]["rows"] if r["rule_id"] == row["rule_id"]
    )
    assert selected["function_id"] == option["function_id"]
    assert selected["applicability_status"] == "explicit_decision_recorded"
    assert_input_held(selected)


@pytest.mark.parametrize("carrier", ["row", "params", "profile"])
@pytest.mark.parametrize(
    "requirement",
    [
        None,
        {},
        True,
        {"status": "ready", "reason": "No"},
        {"status": "requires_matching_input", "reason": ""},
        {"status": "requires_matching_input", "reason": True},
    ],
)
def test_malformed_row_or_profile_hold_is_rejected(carrier, requirement):
    params = {"profiles": [{}]}
    row = {"relationship_params": params}
    destination = (
        row
        if carrier == "row"
        else params
        if carrier == "params"
        else params["profiles"][0]
    )
    destination["reviewed_adaptation"] = {"dataset_binding": requirement}
    with pytest.raises(ValueError, match="Invalid reviewed dataset binding"):
        dc._matching_input_requirement(row)


@pytest.mark.parametrize("carrier", ["row", "params", "profile"])
def test_explicit_row_or_profile_hold_blocks_catalog_fallback(carrier):
    requirement = {
        "status": "requires_matching_input",
        "reason": "Requires matched measurement.",
    }
    params = {"profiles": [{}]}
    row = {"relationship_params": params}
    destination = (
        row
        if carrier == "row"
        else params
        if carrier == "params"
        else params["profiles"][0]
    )
    destination["reviewed_adaptation"] = {"dataset_binding": requirement}
    binding = Binding(
        binding_id="global",
        variable="distance",
        scope_type="global",
        scope_id="",
        dataset_id="proxy",
        preference_rank=1,
        status="catalogued",
        fitness_note="Generic proxy",
    )
    catalog = {"proxy": {"gee_asset_id": "asset/proxy"}}
    args = ("distance", "proxy", [binding], catalog, {}, set())
    ordinary = dc._binding(*args)
    explicit_none = dc._binding(*args, matching_input=None)
    assert ordinary == explicit_none
    assert ordinary["dataset_id"] == "proxy" and ordinary["asset"] == "asset/proxy"
    assert "matching_input_required" not in ordinary
    held = dc._binding(*args, matching_input=dc._matching_input_requirement(row))
    assert held["dataset_id"] is None and held["asset"] is None
    assert held["needs_upload"] is True and held["hold_reason"] == requirement["reason"]


def test_ordinary_option_payload_and_fingerprint_unchanged_without_metadata():
    params = {
        "profiles": [
            {
                "profile_id": "example",
                "source_id": "source",
                "unit": "m",
                "intervals": [],
                "evidence_id": "ev",
                "origin_id": "source",
            }
        ]
    }
    row = {
        "relationship_params": params,
        "suitability_family_id": "family",
        "relationship_type": "piecewise",
        "mapping_id": "mapping",
        "evidence_ids": ["ev"],
    }
    original = deepcopy(row)
    options = dc._options(row, {}, {}, [])
    assert row == original
    option = options[0]
    assert "reviewed_adaptation" not in option and "source_relationship" not in option
    expected = {
        k: v
        for k, v in option.items()
        if k not in {"reviewed_adaptation", "source_relationship"}
    }
    assert dc.fingerprint(option) == dc.fingerprint(expected)
    assert dc._matching_input_requirement(row) is None


def test_approved_water_holds_block_even_a_catalogued_override():
    recipe = ROOT / "schema/recipes/water_harvesting_conservation"
    held = [
        r
        for r in dc.read_csv(recipe / "T4_suitability_mappings.csv")
        if dc._matching_input_requirement(r)
    ]
    assert len(held) == 4
    for row in held:
        assert row["dataset_id"] == ""
        requirement = dc._matching_input_requirement(row)
        approval = json.loads(row["relationship_params"])["reviewed_adaptation"][
            "dataset_binding"
        ]
        assert approval["scope"] == row["mapping_id"]
        assert (ROOT / approval["decision_ref"]).is_file()
        override = Binding(
            "test", row["variable"], "global", "", "proxy", 1, "catalogued"
        )
        result = dc._binding(
            row["variable"],
            "proxy",
            [override],
            {"proxy": {"gee_asset_id": "asset"}},
            {},
            set(),
            matching_input=requirement,
        )
        assert result["dataset_id"] is None and result["asset"] is None
        assert result["needs_upload"] and result["matching_input_required"]
        family = json.loads(
            (recipe / f"T4_{row['suitability_family_id']}.json").read_text()
        )
        published = next(r for r in family if r["mapping_id"] == row["mapping_id"])
        assert published["dataset_id"] == ""
        assert dc._matching_input_requirement(published) == requirement
