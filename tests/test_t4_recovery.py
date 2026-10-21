"""Recovery regressions: source omissions, continuations and review boundaries."""

import copy
import csv
import json
from pathlib import Path
import shutil

import pytest

from nbs_ruralscan.recipe.numeric_bands import join_continuations
from nbs_ruralscan.schema_tools.t4_coverage import check

ROOT = Path(__file__).resolve().parents[1]


def profiles(path):
    result = {}
    for row in csv.DictReader(path.open()):
        for profile in json.loads(row["relationship_params"]).get("profiles", []):
            result[profile["profile_id"]] = profile
    return result


def test_recovered_evidence_preserves_approval_and_one_source_vote():
    live = profiles(ROOT / "schema/recipes/agroforestry/T4_suitability_mappings.csv")
    draft = profiles(
        ROOT
        / "pipeline/t4_audit/agroforestry/final_audit/draft/T4_suitability_mappings.csv"
    )
    assert len(live["ev_T4_slope_chuma21_1"]["intervals"]) == 3
    assert len(live["ev_T4_soc_haile2024_1"]["intervals"]) == 2
    assert len(draft["ev_T4_soc_haile2024_1"]["intervals"]) == 4
    assert draft["ev_T4_soc_haile2024_1"]["page_locators"] == {
        "ev_T4_soc_haile2024_1": 5,
        "ev_T4_soc_haile2024_continuation": 6,
    }
    assert "ev_T4_soc_haile2024_continuation" not in draft
    evidence = {
        r["evidence_id"]: r
        for r in csv.DictReader(
            (ROOT / "schema/registers/EV_evidence_register.csv").open()
        )
    }
    elevation = evidence["ev_T4_elevation_chuma2021_recovery"]
    assert ("ev_T4_elevation_chuma2021_recovery" in live) == (
        elevation["reviewer_ok"].lower() == "true"
        and elevation["review_state"] != "dropped"
    )
    assert len(draft["ev_T4_elevation_chuma2021_recovery"]["intervals"]) == 5


@pytest.mark.parametrize(
    "mismatch", ["source_id", "variable", "unit", "context_id", "system_id", "pool_id"]
)
def test_continuations_reject_incompatible_context(mismatch):
    base = profiles(ROOT / "schema/recipes/agroforestry/T4_suitability_mappings.csv")[
        "ev_T4_soc_haile2024_1"
    ]
    part = copy.deepcopy(base)
    part.update(
        profile_id="part", evidence_id="part", continuation_of=base["profile_id"]
    )
    part[mismatch] = "different"
    _, rejected = join_continuations([base, part])
    assert rejected == [("part", "incompatible_or_missing_table_continuation")]


def test_continuation_rejects_overlapping_table():
    base = profiles(ROOT / "schema/recipes/agroforestry/T4_suitability_mappings.csv")[
        "ev_T4_soc_haile2024_1"
    ]
    part = copy.deepcopy(base)
    part.update(
        profile_id="part", evidence_id="part", continuation_of=base["profile_id"]
    )
    _, rejected = join_continuations([base, part])
    assert rejected == [("part", "overlapping_table_continuation")]


@pytest.fixture
def coverage_tree(tmp_path):
    for path in [
        "pipeline/t4_audit/agroforestry",
        "pipeline/metrics",
        "schema/registers",
        "schema/lookups",
        "schema/recipes/agroforestry",
        "reference/stocktake",
        "docs/review/img",
    ]:
        shutil.copytree(ROOT / path, tmp_path / path)
    for file in (
        "docs/dashboard.html",
        "src/nbs_ruralscan/schema_tools/review_server.py",
    ):
        (tmp_path / file).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / file, tmp_path / file)
    return tmp_path


def test_coverage_gate_passes():
    assert check(ROOT) == []


@pytest.mark.parametrize("filename", ["table_inventory.json", "review_followups.json"])
def test_missing_tracked_evidence_fails(coverage_tree, filename):
    if filename == "review_followups.json":
        (coverage_tree / "pipeline/t4_audit/agroforestry" / filename).write_text("{}")
    else:
        path = coverage_tree / "schema/lookups/t4_numeric_compilation_policy.csv"
        rows = list(csv.DictReader(path.open()))
        with path.open("w") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(
                row for row in rows if row["evidence_id"] != "ev_T4_slope_chuma21_1"
            )
    assert check(coverage_tree)


def test_missing_stocktake_source_fails(coverage_tree):
    path = (
        coverage_tree
        / "pipeline/t4_audit/agroforestry/stocktake_coverage_2026-10-20.csv"
    )
    rows = list(csv.DictReader(path.open()))
    with path.open("w") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows[1:])
    assert any("Unaccounted stocktake" in error for error in check(coverage_tree))


def test_wrong_class_count_is_an_explicit_compiler_hold():
    from nbs_ruralscan.recipe.evidence import load_units
    from nbs_ruralscan.recipe.numeric_bands import compile_bands

    unit = next(
        u
        for u in load_units(ROOT / "schema/registers/EV_evidence_register.json")
        if u.evidence_id == "ev_T4_slope_chuma21_1"
    )
    policy = next(
        r
        for r in csv.DictReader(
            (ROOT / "schema/lookups/t4_numeric_compilation_policy.csv").open()
        )
        if r["evidence_id"] == unit.evidence_id
    )
    hp = json.loads(policy["harmonization"])
    hp["expected_class_count"] = 4
    policy["harmonization"] = hp
    result, used, unresolved = compile_bands(
        [unit], {unit.evidence_id: policy}, "%", {}
    )
    assert not result and not used
    assert unresolved == [(unit.evidence_id, "incomplete_source_class_table")]


def test_orphan_continuation_cannot_become_independent_vote():
    part = profiles(ROOT / "schema/recipes/agroforestry/T4_suitability_mappings.csv")[
        "ev_T4_soc_haile2024_1"
    ]
    part["continuation_of"] = "missing_parent"
    result, rejected = join_continuations([part])
    assert not result
    assert rejected[0][1] == "incompatible_or_missing_table_continuation"


@pytest.mark.parametrize(
    "defect", ["missing_unit", "missing_page", "screened_only", "wrong_lane"]
)
def test_five_source_extraction_cannot_silently_regress(coverage_tree, defect):
    path = coverage_tree / "pipeline/t4_audit/agroforestry/five_source_extraction.json"
    inventory = json.loads(path.read_text())
    source = inventory["sources"]["ellis_2000"]
    if defect == "missing_page":
        source["pages_inspected"].pop()
    elif defect == "screened_only":
        source["main_paper_status"] = "screened"
    else:
        path_ev = coverage_tree / "schema/registers/EV_evidence_register.csv"
        rows = list(csv.DictReader(path_ev.open()))
        eid = source["evidence_ids"][0]
        if defect == "missing_unit":
            rows = [r for r in rows if r["evidence_id"] != eid]
        else:
            next(r for r in rows if r["evidence_id"] == eid)["use_role"] = (
                "structural_suitability"
            )
        with path_ev.open("w") as stream:
            writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    path.write_text(json.dumps(inventory))
    assert check(coverage_tree)


def test_nath_reported_slope_domain_is_finite():
    import numpy as np
    from nbs_ruralscan.runtime.numeric import evaluate_numeric

    rows = list(
        csv.DictReader(
            (ROOT / "schema/recipes/agroforestry/T4_suitability_mappings.csv").open()
        )
    )
    row = next(
        r
        for r in rows
        if "ev_t4_slope_nath21_01" in json.loads(r["evidence_ids"] or "[]")
    )
    result = evaluate_numeric(
        row, [-1, 0, 2, 20, 30, 44, 45], profile_id="ev_t4_slope_nath21_01"
    )
    assert np.isnan(result[0]) and np.isnan(result[-1])
    assert result[1] == pytest.approx(0.9)
    assert result[2] == pytest.approx(0.9)
    assert np.isnan(result[3])  # Source class boundary remains ambiguous.
    assert result[4] == 0 and result[5] == 0


def test_ahmad_ndvi_is_not_canopy_and_retains_source_classes():
    from nbs_ruralscan.runtime.numeric import evaluate_numeric

    evidence = {
        r["evidence_id"]: r
        for r in csv.DictReader(
            (ROOT / "schema/registers/EV_evidence_register.csv").open()
        )
    }
    unit = evidence["ev_T4_canopy_ahmad2018_1"]
    assert unit["variable"] == "ndvi"
    assert unit["reviewer_ok"] == "true"
    assert "Namita-J" in unit["attribution"]
    rows = list(
        csv.DictReader(
            (ROOT / "schema/recipes/agroforestry/T4_suitability_mappings.csv").open()
        )
    )
    row = next(
        r for r in rows if unit["evidence_id"] in json.loads(r["evidence_ids"] or "[]")
    )
    assert row["variable"] == "ndvi"
    assert row["dataset_id"] == "mod13q1_ndvi"
    assert evaluate_numeric(
        row, [0.1, 0.3, 0.6], profile_id=unit["evidence_id"]
    ).tolist() == [0.25, 0.5, 0.75]


def test_coded_feedback_without_keywords_is_tracked():
    from nbs_ruralscan.schema_tools.t4_coverage import (
        FOLLOWUP_REASONS,
        check_review_followups,
    )

    evidence = {"unit": {"use_role": "structural_suitability"}}
    row = dict(evidence_id="unit", reviewer="human", note="", reason="")
    for reason in FOLLOWUP_REASONS:
        row["reason"] = reason
        assert check_review_followups([row], evidence, {}) == [
            "Untracked review follow-up: unit"
        ]
    evidence["unit"]["use_role"] = "effect"
    assert check_review_followups([row], evidence, {}) == []
    row["reviewer"] = "codex"
    evidence["unit"]["use_role"] = "structural_suitability"
    assert check_review_followups([row], evidence, {}) == []


def test_resolution_requires_existing_evidence_and_unchanged_corrective_field():
    import hashlib
    from nbs_ruralscan.schema_tools.t4_coverage import (
        check_review_followups,
        followup_key,
    )

    evidence = {"unit": {"use_role": "operational_risk", "review_state": "active"}}
    item = dict(
        evidence_id="unit",
        reviewer="human",
        note="Wrong destination",
        status="resolved",
        resolution="Routed to operational risk",
        resolution_evidence_ids=["unit"],
        resolution_checks=[
            {
                "evidence_id": "unit",
                "field": "use_role",
                "sha256": hashlib.sha256(b"operational_risk").hexdigest(),
            }
        ],
    )
    followups = {followup_key(item): item}
    assert check_review_followups([], evidence, followups) == []
    evidence["unit"]["use_role"] = "structural_suitability"
    assert any(
        "corrective field changed" in x
        for x in check_review_followups([], evidence, followups)
    )
    item["resolution_evidence_ids"] = ["nonexistent"]
    assert any(
        "lacks valid evidence" in x
        for x in check_review_followups([], evidence, followups)
    )
    item["resolution_checks"] = []
    assert any(
        "lacks corrective field checks" in x
        for x in check_review_followups([], evidence, followups)
    )
    item["status"] = "quarantined"
    assert any(
        "quarantine no longer holds" in x
        for x in check_review_followups([], evidence, followups)
    )
    evidence["unit"]["review_state"] = "dropped"
    assert check_review_followups([], evidence, followups) == []


def test_caption_resolution_reopens_when_display_code_changes(coverage_tree):
    path = coverage_tree / "docs/dashboard.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "docs/dashboard.html", path)
    server = "src/nbs_ruralscan/schema_tools/review_server.py"
    (coverage_tree / server).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / server, coverage_tree / server)
    assert check(coverage_tree) == []
    path.write_text(path.read_text().replace("&full=1", "&full=0"))
    assert any("display artifact changed" in x for x in check(coverage_tree))


def test_answered_source_questions_do_not_become_general_numeric_curves():
    evidence = {
        r["evidence_id"]: r
        for r in csv.DictReader(
            (ROOT / "schema/registers/EV_evidence_register.csv").open()
        )
    }
    live = profiles(ROOT / "schema/recipes/agroforestry/T4_suitability_mappings.csv")
    ids = {
        "ev_dist_settlement_qual_singh26",
        "ev_t4_slope_kizir_2",
        "ev_T4_slope_haris2021_2",
        "ev_T4_soildrainage_haris2021_1",
    }
    assert not ids.intersection(live)
    settlement = evidence["ev_dist_settlement_qual_singh26"]
    assert settlement["use_role"] == "operational_risk"
    assert (
        json.loads(settlement["relationship"])["shape"] == "monotonic_decreasing_linear"
    )
    slope = evidence["ev_T4_slope_haris2021_2"]
    assert slope["claim_scope"] == "species_specific"
    assert slope["taxon"] == "Falcataria moluccana"
    drainage = json.loads(evidence["ev_T4_soildrainage_haris2021_1"]["relationship"])
    assert drainage == {"land_capability_class": "IVd", "limitation": "drainage"}
