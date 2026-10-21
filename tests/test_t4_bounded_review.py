import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "bounded", ROOT / "scripts/check-t4-bounded-review.py"
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
AUDIT = ROOT / "pipeline/t4_audit/agroforestry/bounded_review_2026-10-21"


def test_live_t4_and_recovered_sources_have_review_coverage():
    assert MOD.check(ROOT, AUDIT) == []


def test_missing_live_source_is_detected(tmp_path):
    manifest = json.loads((AUDIT / "manifest.json").read_text())
    manifest["expected_source_ids"].remove("nath_2021")
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    assert any("Live T4 source absent" in e for e in MOD.check(ROOT, tmp_path))


def test_human_approval_drift_is_detected(tmp_path):
    manifest = json.loads((AUDIT / "manifest.json").read_text())
    eid = next(iter(manifest["existing_approval_snapshot"]))
    manifest["existing_approval_snapshot"][eid]["reviewer_ok"] = "invented"
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    assert any(
        "Existing human review state changed" in e for e in MOD.check(ROOT, tmp_path)
    )
