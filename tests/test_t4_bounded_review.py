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


def test_documented_later_review_is_allowed_but_unlogged_approval_is_not():
    row = dict(
        evidence_id="unit",
        source_id="paper",
        reviewer_ok="true",
        review_state="",
        attribution="[reviewed 2026-10-22 by Pete]",
    )
    entry = dict(
        evidence_id="unit",
        source_id="paper",
        date="2026-10-22",
        reviewer="Pete",
        decision="ok",
    )
    old = {"reviewer_ok": "false", "review_state": ""}
    assert MOD.documented_review_transition(row, old, [entry], "2026-10-21")
    assert not MOD.documented_review_transition(row, old, [], "2026-10-21")
    assert not MOD.documented_review_transition(
        row, old, [dict(entry, reviewer="Other")], "2026-10-21"
    )
    assert not MOD.documented_review_transition(
        row, old, [entry, dict(entry, decision="flag")], "2026-10-21"
    )
    assert not MOD.documented_review_transition(row, old, [entry], "2026-10-23")


def test_drop_preserves_logged_approval_but_cannot_invent_it():
    old = {"reviewer_ok": "false", "review_state": ""}
    row = dict(
        evidence_id="unit",
        source_id="paper",
        reviewer_ok="true",
        review_state="dropped",
        attribution="[dropped 2026-11-09 by B] [reviewed 2026-10-23 by A]",
    )
    keep = dict(
        evidence_id="unit",
        source_id="paper",
        reviewer="A",
        date="2026-10-23",
        decision="ok",
    )
    drop = dict(keep, reviewer="B", date="2026-11-09", decision="drop")
    assert MOD.documented_review_transition(row, old, [keep, drop], "2026-10-21")
    assert not MOD.documented_review_transition(row, old, [drop], "2026-10-21")
    assert not MOD.documented_review_transition(
        row, old, [dict(keep, decision="flag"), drop], "2026-10-21"
    )
    assert not MOD.documented_review_transition(
        row, old, [keep, dict(keep, decision="reopen"), drop], "2026-10-21"
    )
