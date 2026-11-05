"""Review-priority annotations remain independent of scientific/review state."""

import csv
import shutil
import subprocess
from pathlib import Path

import pytest

from nbs_ruralscan.schema_tools.review_notes import evidence_fingerprint
from nbs_ruralscan.schema_tools.review_priorities import load_review_priorities

ROOT = Path(__file__).resolve().parents[1]


def write_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def fixture(tmp_path):
    ev = dict(
        evidence_id="one",
        source_id="paper",
        page="3",
        quote="original",
        relationship="{}",
        context="{}",
        reviewer_ok="false",
        review_state="",
    )
    row = dict(
        batch_id="batch",
        batch_label="Review batch",
        priority="high",
        evidence_id="one",
        source_id="paper",
        page="3",
        reason="Inspect",
        decision_needed="Confirm meaning",
        requested_by="Pete",
        requested_date="2026-11-05",
        evidence_sha256=evidence_fingerprint(ev),
    )
    write_rows(tmp_path / "schema/registers/EV_evidence_register.csv", [ev])
    write_rows(tmp_path / "pipeline/review_priorities.csv", [row])
    return tmp_path, ev, row


def test_annotations_do_not_write_or_change_approval(fixture):
    root, ev, row = fixture
    before = {p: p.read_bytes() for p in root.rglob("*.csv")}
    assert load_review_priorities(root) == [dict(row, context_changed=False)]
    assert before == {p: p.read_bytes() for p in before}
    ev.update(reviewer_ok="true", review_state="dropped")
    write_rows(root / "schema/registers/EV_evidence_register.csv", [ev])
    assert load_review_priorities(root)[0]["context_changed"] is False


def test_semantic_changes_keep_request_but_warn(fixture):
    root, ev, _ = fixture
    ev["relationship"] = '{"abs_max":100}'
    write_rows(root / "schema/registers/EV_evidence_register.csv", [ev])
    assert load_review_priorities(root)[0]["context_changed"] is True


@pytest.mark.parametrize("change", ["duplicate", "missing", "empty", "invalid"])
def test_invalid_annotations_fail_build(fixture, change):
    root, _, row = fixture
    rows = [row]
    if change == "duplicate":
        rows.append(row.copy())
    elif change == "missing":
        row["evidence_id"] = "absent"
    elif change == "empty":
        row["decision_needed"] = ""
    else:
        row["priority"] = "approved"
    write_rows(root / "pipeline/review_priorities.csv", rows)
    with pytest.raises(ValueError):
        load_review_priorities(root)


def test_seed_has_exact_six_records():
    rows = [
        r
        for r in load_review_priorities(ROOT)
        if r["batch_id"] == "t4_wetland_live_mapping_review_20261105"
    ]
    assert len(rows) == 6
    assert all(r["priority"] == "high" for r in rows)
    assert {r["evidence_id"] for r in rows} == {
        "ev_wet_distance_to_waterbody_morenomateos10_1",
        "ev_wet_drainage_density_sumarga26_1",
        "ev_wet_water_table_depth_brouwer26_1",
        "ev_wet_groundwater_seepage_brouwer26_1",
        "ev_wet_site_area_russell97_1",
        "ev_wet_distance_to_waterbody_russell97_1",
    }


def test_priority_controls_and_queue_semantics():
    if not shutil.which("node"):
        pytest.skip("node is required for dashboard behavior tests")
    subprocess.run(["node", "tests/js/review_priority.test.cjs"], cwd=ROOT, check=True)
