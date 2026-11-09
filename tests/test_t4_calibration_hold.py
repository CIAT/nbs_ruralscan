"""Numerical holds survive regeneration and cannot become executable by selection."""

from copy import deepcopy
from dataclasses import replace
import csv
import json
from pathlib import Path

import pytest

from nbs_ruralscan.recipe import developer_contract as dc
from nbs_ruralscan.recipe.calibration_requirements import calibration_requirement
from nbs_ruralscan.recipe.family import FamilyResult
from nbs_ruralscan.recipe.t4_build import (
    T4BuildInputs,
    _preserve_mapping_review_holds,
    write_recipe,
)
from nbs_ruralscan.runtime.numeric import evaluate_numeric
from nbs_ruralscan.schema_tools.generate import _coerce

ROOT = Path(__file__).resolve().parents[1]
NBS = "water_harvesting_conservation"
MID = "water_harvesting__runoff_catchment__runoff_potential_index"
HOLD = {
    "status": "held",
    "reason": "Source input classes are not a calibrated response.",
}


def read(path):
    with path.open() as handle:
        return list(csv.DictReader(handle))


@pytest.mark.parametrize("selection", [{}, {"profile_id": "p"}, {"pool_id": "pool"}])
@pytest.mark.parametrize("serialized", [False, True])
def test_hold_blocks_numeric_paths_before_selection(selection, serialized):
    params = {
        "points": [[0, 0], [100, 1]],
        "profiles": [{"profile_id": "p", "intervals": []}],
        "harmonization": {"pools": [{"pool_id": "pool", "cells": []}]},
        "reviewed_adaptation": {"numerical_calibration": HOLD},
    }
    row = {
        "relationship_type": "piecewise",
        "relationship_params": json.dumps(params) if serialized else params,
    }
    with pytest.raises(ValueError, match="Numerical calibration held"):
        evaluate_numeric(row, [75, 80], **selection)
    assert dc._options(row, {}, {}, []) == []


@pytest.mark.parametrize(
    "hold",
    [None, {}, {"status": "ready", "reason": "x"}, {"status": "held", "reason": " "}],
)
def test_malformed_calibration_hold_fails_closed(hold):
    row = {
        "relationship_params": {"reviewed_adaptation": {"numerical_calibration": hold}}
    }
    with pytest.raises(ValueError, match="Invalid reviewed numerical calibration hold"):
        evaluate_numeric(row, [80])
    with pytest.raises(ValueError, match="Invalid reviewed numerical calibration hold"):
        dc._options(row, {}, {}, [])


@pytest.mark.parametrize("missing_family", [False, True])
def test_calibration_hold_survives_empty_round_and_new_synthesis(
    tmp_path, missing_family
):
    inputs = T4BuildInputs.from_root(ROOT, NBS)
    held = next(r for r in read(inputs.audited_recipe) if r["mapping_id"] == MID)
    held.update(corpus_n="13", paper_support_pct="35.8")
    baseline = tmp_path / "baseline.csv"
    with baseline.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, list(held))
        writer.writeheader()
        writer.writerow(held)
    # This fixture represents a historical snapshot where the accepted CSV carried the hold.
    inputs = replace(
        inputs,
        audited_recipe=baseline,
        definition_index=None,
        authored_mappings=None,
        mapping_settings=None,
        review_holds=None,
    )
    family = held["suitability_family_id"]
    empty = (
        {} if missing_family else {family: FamilyResult(family=family, corpus_n=None)}
    )
    first = tmp_path / "first"
    vont = [
        {
            "canonical_variable_id": held["variable"],
            "candidate_dataset_ids": '["generic_proxy"]',
        }
    ]
    # The synthesis and serialization stages both enforce holds against the same snapshot.
    prepared = _preserve_mapping_review_holds(empty, [held])
    write_recipe(NBS, prepared, vont, inputs=inputs, output_dir=first)
    retained = read(first / "T4_suitability_mappings.csv")[0]
    assert retained["relationship_params"] == held["relationship_params"]
    assert retained["dataset_id"] == ""
    assert retained["corpus_n"] == retained["paper_support_pct"] == ""
    assert retained["evidence_ids"] == held["evidence_ids"]
    assert "no new numeric synthesis or approval" in retained["justification"]

    proposed = {k: _coerce(v) for k, v in held.items() if v != ""}
    proposed.update(
        relationship_type="piecewise",
        relationship_params={"points": [[0, 0], [100, 1]]},
        evidence_ids=["new_source"],
        n_sources=1,
        references=["New synthesis references must not relabel the retained sources"],
    )
    ordinary = deepcopy(proposed)
    ordinary.update(mapping_id="ordinary__runoff", suitability_family_id="ordinary")
    results = {
        family: FamilyResult(family=family, corpus_n=None, rows=[proposed]),
        "ordinary": FamilyResult(family="ordinary", corpus_n=None, rows=[ordinary]),
    }
    before = deepcopy(results)
    second = tmp_path / "second"
    write_recipe(
        NBS,
        results,
        vont,
        inputs=replace(inputs, audited_recipe=first / "T4_suitability_mappings.csv"),
        output_dir=second,
    )
    actual = {r["mapping_id"]: r for r in read(second / "T4_suitability_mappings.csv")}
    for key in (
        "relationship_type",
        "relationship_params",
        "evidence_ids",
        "n_sources",
        "uncertainty_pct",
    ):
        assert actual[MID][key] == retained[key]
    assert actual[MID]["dataset_id"] == ""
    assert actual[MID]["corpus_n"] == actual[MID]["paper_support_pct"] == ""
    assert (
        json.loads(actual["ordinary__runoff"]["relationship_params"])
        == ordinary["relationship_params"]
    )
    assert actual["ordinary__runoff"]["dataset_id"] == "generic_proxy"
    family_row = json.loads((second / f"T4_{family}.json").read_text())[0]
    assert calibration_requirement(family_row) == calibration_requirement(held)
    assert family_row["evidence_ids"] == json.loads(held["evidence_ids"])
    assert "references" not in family_row
    assert results == before
    with pytest.raises(ValueError, match="Numerical calibration held"):
        evaluate_numeric(family_row, [80])


def test_developer_contract_cannot_select_function_around_hold(monkeypatch):
    # Use a valid reviewed corpus to test the hold separately from evidence approval.
    corpus = dc.rebuild(ROOT, "wetland_management")
    row = next(
        r
        for r in corpus["rows"]
        if json.loads(r["relationship_params"]).get("profiles")
    )
    original_options = dc._options(
        row,
        {u["evidence_id"]: u for u in corpus["evidence"]},
        {s["source_id"]: s for s in corpus["sources"]},
        [],
    )
    assert original_options
    params = json.loads(row["relationship_params"])
    params.setdefault("reviewed_adaptation", {})["numerical_calibration"] = HOLD
    row["relationship_params"] = json.dumps(params)
    monkeypatch.setattr(dc, "rebuild", lambda *args: deepcopy(corpus))
    result = dc.build_contract(ROOT, nbs="wetland_management", country="NLD")
    contract_row = next(
        r for r in result["contract"]["rows"] if r["rule_id"] == row["mapping_id"]
    )
    assert contract_row["status"] == "blocked"
    assert contract_row["function_options"] == []
    assert contract_row["function_id"] is None
    assert any("Numerical calibration held" in b for b in contract_row["blockers"])
    assert contract_row["evidence_ids"] == json.loads(row["evidence_ids"])
    with pytest.raises(ValueError, match="Missing or stale function selection"):
        dc.build_contract(
            ROOT,
            nbs="wetland_management",
            country="NLD",
            selection={
                "contract_version": dc.VERSION,
                "selections": {
                    row["mapping_id"]: {
                        "function_id": original_options[0]["function_id"],
                        "function_fingerprint": "stale",
                    }
                },
            },
        )
