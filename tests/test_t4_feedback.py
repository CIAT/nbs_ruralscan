"""Presentation consolidation must preserve evidence scope and feedback identity."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "feedback", ROOT / "scripts/report-t4-bounded-review.py"
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def test_grouping_keeps_every_record_once_and_separates_depths():
    data = MOD.build_data()
    manifest = json.loads((MOD.AUDIT / "manifest.json").read_text())
    ids = [r["id"] for g in data["groups"] for r in g["records"]]
    assert sorted(ids) == sorted(manifest["new_evidence_ids"])
    assert len(ids) == len(set(ids))
    ph = next(g for g in data["groups"] if g["id"] == "soil_ph")
    assert {r["variable"] for r in ph["records"]} == {"soil_ph", "soil_ph_subsoil"}
    assert len({g["fingerprint"] for g in data["groups"]}) == len(data["groups"])


def test_comparison_preserves_species_scope_and_quarantine():
    data = MOD.build_data()
    records = [r for g in data["groups"] for r in g["records"]]
    assert all(
        r["scope"] == "species_specific"
        for r in records
        if r["source"] == "mushtaq_2023"
    )
    assert sum(r["state"] == "dropped" for r in records) == 1
    assert any(r["weights"].get("weight_conflict") for r in records)


def test_generated_page_matches_current_evidence_and_cannot_submit_approvals():
    page = (ROOT / "docs/review/t4-bounded-review.html").read_text()
    raw = page.split('<script id="review-data" type="application/json">', 1)[1].split(
        "</script>", 1
    )[0]
    assert json.loads(raw) == MOD.build_data()
    assert "/api/submit" not in page
    assert "/api/apply" not in page
    assert "t4_group_feedback_v1" in page


def test_every_source_page_has_a_rendered_image_and_claim_locator():
    data = MOD.build_data()
    for group in data["groups"]:
        for record in group["records"]:
            assert record["source_row"]
            assert int(record["page"]) in {p["page"] for p in record["source_pages"]}
            for page in record["source_pages"]:
                assert (ROOT / "docs" / page["image"].lstrip("/")).is_file()
    singh = next(
        r
        for g in data["groups"]
        for r in g["records"]
        if r["source"] == "singh_2026" and r["variable"] == "slope"
    )
    assert {4, 8} <= {p["page"] for p in singh["source_pages"]}
