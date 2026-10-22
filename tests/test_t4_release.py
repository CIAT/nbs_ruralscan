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
    assert 'data-operational="true"' in page
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
    assert "<th>Weighting</th>" in page
    assert "Equal numeric default: 0.2" in page
    assert "equal-hierarchy reference" in page
    assert "plots/agroforestry__cross_family__slope.svg" in page
    assert "planting versus natural retention/regeneration not established" in page
    assert "Alley cropping" in page
    assert (tmp_path / "practice_vocabulary.csv").exists()
