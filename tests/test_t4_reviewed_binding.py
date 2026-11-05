"""Reviewed matching-input holds survive recipe and family-output regeneration."""

from copy import deepcopy
import csv
import json

import pytest

from nbs_ruralscan.recipe.family import FamilyResult
from nbs_ruralscan.recipe.t4_build import T4BuildInputs, write_recipe


def case(tmp_path):
    evidence = tmp_path / "evidence.csv"
    evidence.write_text("evidence_id,review_state,reviewer_ok\n")
    inputs = T4BuildInputs(
        evidence=evidence,
        sources=evidence,
        ontology=evidence,
        crop_scope_policy=evidence,
        numeric_policy=evidence,
        audited_recipe=tmp_path / "no-existing-recipe.csv",
    )
    rows = {}
    for family in ("scoped", "ordinary"):
        rows[family] = FamilyResult(
            family=family,
            corpus_n=None,
            rows=[
                dict(
                    mapping_id=family + "__distance",
                    variable="distance",
                    dataset_id="generic_proxy",
                    suitability_dimension="biophysical_constraint",
                    relationship_type="piecewise",
                    relationship_params={"profiles": [{"profile_id": family}]},
                    justification="Reconciled from evidence.",
                    evidence_ids=[family + "_evidence"],
                )
            ],
        )
    vont = [
        {
            "canonical_variable_id": "distance",
            "candidate_dataset_ids": '["generic_proxy"]',
        }
    ]
    return inputs, rows, vont


def read(output):
    with (output / "T4_suitability_mappings.csv").open() as f:
        return {r["suitability_family_id"]: r for r in csv.DictReader(f)}


def test_reviewed_binding_hold_preserves_unrelated_rows_and_caller_state(tmp_path):
    inputs, results, vont = case(tmp_path)
    write_recipe(
        "example", results, vont, inputs=inputs, output_dir=tmp_path / "baseline"
    )
    profile = results["scoped"].rows[0]["relationship_params"]["profiles"][0]
    profile["reviewed_adaptation"] = {
        "dataset_binding": {
            "status": "requires_matching_input",
            "reason": "Measure distance to both required habitat features, not stream proxy.",
        },
    }
    original = deepcopy(results)
    write_recipe("example", results, vont, inputs=inputs, output_dir=tmp_path / "held")
    actual, baseline = read(tmp_path / "held"), read(tmp_path / "baseline")
    assert actual["ordinary"] == baseline["ordinary"]
    assert actual["ordinary"]["dataset_id"] == "generic_proxy"
    assert actual["scoped"]["dataset_id"] == ""
    assert (
        "requires matching input: Measure distance" in actual["scoped"]["justification"]
    )
    family_rows = json.loads((tmp_path / "held/T4_scoped.json").read_text())
    assert family_rows[0]["dataset_id"] == ""
    assert family_rows[0]["justification"] == actual["scoped"]["justification"]
    assert results == original
    assert (tmp_path / "held/T4_ordinary.json").read_bytes() == (
        tmp_path / "baseline/T4_ordinary.json"
    ).read_bytes()


@pytest.mark.parametrize(
    "binding",
    [
        None,
        {},
        {"status": "requires_matching_input", "reason": " "},
        {"status": "ready", "reason": "no"},
    ],
)
def test_malformed_declared_binding_hold_cannot_silently_fallback(tmp_path, binding):
    inputs, results, vont = case(tmp_path)
    results["scoped"].rows[0]["relationship_params"]["profiles"][0][
        "reviewed_adaptation"
    ] = {"dataset_binding": binding}
    with pytest.raises(ValueError, match="Invalid reviewed dataset binding"):
        write_recipe(
            "example", results, vont, inputs=inputs, output_dir=tmp_path / "out"
        )


def test_ordinary_profile_metadata_does_not_create_binding_policy(tmp_path):
    inputs, results, vont = case(tmp_path)
    results["scoped"].rows[0]["relationship_params"]["profiles"][0][
        "dataset_binding"
    ] = {"status": "requires_matching_input", "reason": "Not a reviewed adaptation"}
    write_recipe("example", results, vont, inputs=inputs, output_dir=tmp_path / "out")
    assert read(tmp_path / "out")["scoped"]["dataset_id"] == "generic_proxy"
