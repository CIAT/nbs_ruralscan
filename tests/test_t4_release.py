"""Release content must follow live CSVs without upgrading evidence or readiness."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "t4_release", ROOT / "scripts/release-t4-first-pass.py"
)
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


def test_release_is_exact_accounted_snapshot_with_dataset_differences(tmp_path):
    manifest = release.build(ROOT, tmp_path)
    live = ROOT / "schema/recipes/agroforestry/T4_suitability_mappings.csv"
    assert (tmp_path / live.name).read_bytes() == live.read_bytes()
    assert sum(manifest["row_counts"].values()) == len(release.read(live))
    assert manifest["unreconciled_records"] == []
    assert {"annual_precipitation", "mean_annual_temperature"} <= set(
        manifest["binding_differences"]
    )
    rows = release.read(tmp_path / "T4_review.csv")
    rainfall = next(r for r in rows if r["variable"] == "annual_precipitation")
    assert rainfall["global_binding_dataset"] == "chelsa_bioclim_v21_baseline"
    assert "reconcile" in rainfall["status"]
    legal = next(r for r in rows if r["kind"] == "Hard exclusion")
    assert "not executable" in legal["status"]
    assert "field_boundary_zone" in manifest["required_local_inputs"]
    page = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert 'data-module="M2b"' in page
    assert "pilot execution remain to validate" in page
    assert json.loads((tmp_path / "manifest.json").read_text()) == manifest


def test_release_preserves_evidence_states_and_does_not_invent_aliases(tmp_path):
    release.build(ROOT, tmp_path)
    evidence = {
        r["evidence_id"]: r
        for r in release.read(ROOT / "schema/registers/EV_evidence_register.csv")
    }
    for row in release.read(tmp_path / "evidence_accounting.csv"):
        assert row["reviewer_ok"] == evidence[row["evidence_id"]]["reviewer_ok"]
        assert row["review_state"] == evidence[row["evidence_id"]]["review_state"]
        if row["review_state"] == "dropped":
            assert row["disposition"] == "quarantined"
    ontology = {
        r["canonical_variable_id"]: r
        for r in release.read(ROOT / "schema/registers/VONT_variable_ontology.csv")
    }
    for row in release.read(tmp_path / "variables.csv"):
        assert row == ontology[row["canonical_variable_id"]]


def test_rule_view_separates_hierarchy_and_exposes_weights_and_scope(tmp_path):
    release.build(ROOT, tmp_path)
    page = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "<th>Theme</th><th>Variable group</th>" in page
    assert "<th>Studies using variable group</th>" in page
    assert "<th>Studies using variable</th>" in page
    assert (tmp_path / "inclusion_estimates.csv").exists()
    assert "<th>Weighting</th>" in page
    assert "Equal numeric default: 0.2" in page
    assert "equal-hierarchy reference" in page
    assert "plots/agroforestry__cross_family__slope.svg" in page
    assert "planting versus natural retention/regeneration not established" in page
    assert "Alley cropping" in page
    assert (tmp_path / "practice_vocabulary.csv").exists()


def test_operational_module_visible_and_evidence_only_rows_not_executable(tmp_path):
    manifest = release.build(ROOT, tmp_path)
    rows = release.read(tmp_path / "T4_review.csv")
    road = next(r for r in rows if r["variable"] == "distance_to_road")
    travel = next(r for r in rows if r["variable"] == "accessibility_travel_time")
    assert road["module"].startswith("M2b")
    assert road["kind"] == "Operational evidence (not configured)"
    assert road["weight_default"] == ""
    assert road["related_operational_evidence_ids"]
    assert travel["related_operational_evidence_ids"]
    assert travel["related_operational_sources"]
    assert "No verified model-use record" in travel["variable_inclusion"]
    assert manifest["operational_evidence_only_rows"] > 0
    assert (
        len(rows)
        == sum(manifest["row_counts"].values())
        + manifest["operational_evidence_only_rows"]
    )
    assert "distance_to_road" not in {
        r["variable"] for r in release.read(tmp_path / "T4_suitability_mappings.csv")
    }
    page = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert '<option value="all">All modules</option>' in page
    assert "<th>Module</th>" in page


def test_release_retains_original_source_holds_and_fingerprints(tmp_path):
    import hashlib

    manifest = release.build(ROOT, tmp_path)
    source = "pipeline/t4_audit/agroforestry/original_claim_followups_2026-10-23.json"
    expected = json.loads((ROOT / source).read_text())["items"]
    rows = release.read(tmp_path / "source_followups.csv")
    assert {r["reporting_evidence_id"] for r in rows} == {
        r["reporting_evidence_id"] for r in expected
    }
    for row, item in zip(rows, expected):
        assert row["status"] == item["status"]
        assert row["runtime_effect"] == item["runtime_effect"]
        assert row["next_action"] == item["next_action"]
    assert (
        manifest["input_sha256"][source]
        == hashlib.sha256((ROOT / source).read_bytes()).hexdigest()
    )
    assert (
        manifest["output_sha256"]["source_followups.csv"]
        == hashlib.sha256((tmp_path / "source_followups.csv").read_bytes()).hexdigest()
    )


def test_ndvi_study_use_review_and_numeric_support_are_distinct(tmp_path):
    release.build(ROOT, tmp_path)
    row = next(
        r for r in release.read(tmp_path / "T4_review.csv") if r["variable"] == "ndvi"
    )
    assert row["variable_inclusion"] == "3/10 studies (30.0%)"
    assert row["review_status"] == "All 3 have reviewed evidence of variable use"
    assert row["numeric_rule_studies"] == "1 study: ahmad_2018"
    page = (tmp_path / "index.html").read_text()
    assert "<th>Review status</th>" in page
    assert "<th>Studies supplying numeric rules</th>" in page
    assert "Reviewed: 3/10" not in page
