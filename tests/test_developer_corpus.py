"""Developer exports must genuinely recompile reviewed evidence, never mutate it."""

import csv
import json
from pathlib import Path
import shutil

import pytest

from nbs_ruralscan.recipe.developer_corpus import rebuild

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def corpus(tmp_path):
    for name in (
        "schema/registers",
        "schema/lookups",
        "schema/recipes/agroforestry",
        "src/nbs_ruralscan/recipe",
    ):
        shutil.copytree(
            ROOT / name, tmp_path / name, ignore=shutil.ignore_patterns("__pycache__")
        )
    for name in (
        "scripts/synthesise-recipe.py",
        "src/nbs_ruralscan/schema_tools/generate.py",
    ):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, path)
    return tmp_path


def edit_csv(path, edit):
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields, rows = reader.fieldnames, list(reader)
    edit(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        assert fields is not None
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def test_rebuild_reproduces_audited_rules_and_accounts_for_omitted_evidence(corpus):
    before = {
        p.relative_to(corpus): p.read_bytes() for p in corpus.rglob("*") if p.is_file()
    }
    first = rebuild(corpus, "agroforestry")
    second = rebuild(corpus, "agroforestry")
    assert first == second
    after = {
        p.relative_to(corpus): p.read_bytes() for p in corpus.rglob("*") if p.is_file()
    }
    assert before == after
    report = first["synthesis_report"]
    relevant = {
        r["evidence_id"]
        for r in first["evidence"]
        if r["use_role"] in {"structural_suitability", "operational_risk"}
    }
    assert {r["evidence_id"] for r in report["evidence_dispositions"]} == relevant
    assert any(not r["compiled_mapping_ids"] for r in report["evidence_dispositions"])
    assert report["audited_recipe_matches"]
    slope = next(
        r
        for r in first["rows"]
        if r["mapping_id"] == "agroforestry__planted_silvoarable__slope"
    )
    params = json.loads(slope["relationship_params"])
    assert params["threshold"] == 19.3
    assert (
        params["harmonization"]["pools"][0]["pool_id"] == "india_planted_scoping__slope"
    )


def test_audited_profile_drift_blocks_export(corpus):
    def change(rows):
        row = next(r for r in rows if r["variable"] == "ndvi")
        params = json.loads(row["relationship_params"])
        params["profiles"][0]["intervals"][0]["score"] = 0.123
        row["relationship_params"] = json.dumps(params)

    edit_csv(corpus / "schema/recipes/agroforestry/T4_suitability_mappings.csv", change)
    with pytest.raises(ValueError, match="does not reproduce.*cross_family__ndvi"):
        rebuild(corpus, "agroforestry")


def test_changed_approval_cannot_silently_reuse_stale_profile(corpus):
    def change(rows):
        row = next(r for r in rows if r["evidence_id"] == "ev_T4_canopy_ahmad2018_1")
        row["reviewer_ok"] = "false"

    edit_csv(corpus / "schema/registers/EV_evidence_register.csv", change)
    with pytest.raises(ValueError, match="does not reproduce"):
        rebuild(corpus, "agroforestry")


def test_unassigned_new_evidence_is_accounted_even_without_compiled_row(corpus):
    def change(rows):
        row = dict(
            next(r for r in rows if r["evidence_id"] == "ev_T4_canopy_ahmad2018_1")
        )
        row.update(
            evidence_id="test_unassigned_t4",
            suitability_family_id="",
            reviewer_ok="false",
        )
        rows.append(row)

    edit_csv(corpus / "schema/registers/EV_evidence_register.csv", change)
    output = rebuild(corpus, "agroforestry")
    item = next(
        r
        for r in output["synthesis_report"]["evidence_dispositions"]
        if r["evidence_id"] == "test_unassigned_t4"
    )
    assert item["disposition"] == "no_suitability_family"
    assert item["compiled_mapping_ids"] == []
