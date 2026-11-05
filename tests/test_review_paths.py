"""Relocated replay must never use the compiler checkout's mutable records."""

import csv
import json
import os
from pathlib import Path

import pytest
from nbs_ruralscan.schema_tools import review, submit_review as submit


def snapshot(root: Path, *, action="ok") -> Path:
    files = review.ReviewFiles.from_root(root)
    files.evidence.parent.mkdir(parents=True)
    files.log.parent.mkdir(parents=True)
    files.evidence.write_text(
        "evidence_id,source_id,attribution,review_state,reviewer_ok,claim_scope,taxon\n"
        "e1,s1,[VERIFY-FLAG mismatch: value] note,,false,practice_technology,\n"
        "e2,s2,untouched,,false,practice_technology,\n"
        "e3,s3,old,dropped,false,practice_technology,\n"
        "e4,s4,new on main,,true,practice_technology,\n"
    )
    store = root / "pipeline/review/decisions.json"
    store.parent.mkdir(parents=True)
    store.write_text(
        json.dumps(
            {
                "e1": {"alice": {"decision": action, "note": "checked"}},
                "e2": {"alice": {"decision": "ok"}, "bob": {"decision": "drop"}},
                "e3": {
                    "alice": {
                        "decision": "reclassify",
                        "claim_scope": "crop_specific",
                        "taxon": "Test crop",
                    }
                },
            }
        )
    )
    shared = {"date": "2026-01-01", "issue_id": "one", "note": "existing"}
    local = {"date": "2026-01-02", "issue_id": "two", "note": "new clarification"}
    (root / "pipeline/metrics/clarification_log.json").write_text(json.dumps([shared]))
    (root / "pipeline/review/clarifications.json").write_text(
        json.dumps([shared, local])
    )
    return root


def tree(root: Path) -> dict:
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in root.rglob("*")
        if p.is_file()
    }


def rows(root: Path) -> dict:
    with review.ReviewFiles.from_root(root).evidence.open(newline="") as f:
        return {r["evidence_id"]: r for r in csv.DictReader(f)}


def test_replay_isolated_interleaved_and_idempotent(tmp_path, monkeypatch):
    live = snapshot(tmp_path / "live")
    first = snapshot(tmp_path / "first")
    second = snapshot(tmp_path / "second", action="drop")
    live_before, first_before, second_before = tree(live), tree(first), tree(second)
    monkeypatch.setattr(submit, "ROOT", live)
    monkeypatch.setattr(review, "EV", review.ReviewFiles.from_root(live).evidence)
    monkeypatch.setattr(review, "LOG", review.ReviewFiles.from_root(live).log)
    monkeypatch.chdir(live)

    def forbidden(*args, **kwargs):
        pytest.fail("Replay-only must not build artifacts, run Git or submit anything")

    monkeypatch.setattr(submit, "generate", forbidden)
    monkeypatch.setattr(submit.subprocess, "run", forbidden)
    a = submit.replay(first)
    assert a.conflicts == ("e2",)
    assert a.clarification_count == 1
    assert a.applied is not None
    assert a.applied["ok"] == 1 and a.applied["reclassified"] == 1
    assert tree(second) == second_before
    first_after = tree(first)
    submit.replay(second)
    b = submit.replay(first)
    assert b.clarification_count == 0
    assert b.applied is not None
    assert b.applied["ok"] == b.applied["reclassified"] == 0
    assert tree(first) == first_after
    assert tree(live) == live_before
    for root, before in ((first, first_before), (second, second_before)):
        after = tree(root)
        assert {p for p in after if after[p] != before.get(p)} == {
            "schema/registers/EV_evidence_register.csv",
            "pipeline/metrics/review_log.csv",
            "pipeline/metrics/clarification_log.json",
        }
        assert rows(root)["e2"]["attribution"] == "untouched"
        assert rows(root)["e4"]["attribution"] == "new on main"
        assert rows(root)["e3"]["review_state"] == ""
        assert rows(root)["e3"]["claim_scope"] == "crop_specific"
        assert rows(root)["e3"]["taxon"] == "Test crop"
    assert rows(first)["e1"]["reviewer_ok"] == "true"
    assert rows(second)["e1"]["review_state"] == "dropped"


def test_explicit_reopen_retains_event_history(tmp_path):
    root = snapshot(tmp_path)
    submit.replay(root)
    files = review.ReviewFiles.from_root(root)
    assert review.reopen_units(["e1"], "alice", files=files) == {"reopened": 1}
    assert rows(root)["e1"]["reviewer_ok"] == "false"
    reapplied = submit.replay(root).applied
    assert reapplied is not None and reapplied["ok"] == 1
    with files.log.open(newline="") as f:
        events = [r for r in csv.DictReader(f) if r["evidence_id"] == "e1"]
    assert [r["decision"] for r in events] == ["ok", "reopen", "ok"]


def test_wrapper_rebuilds_selected_root_after_replay(tmp_path, monkeypatch):
    root = snapshot(tmp_path)
    builds = []

    def build(schema):
        assert rows(root)["e1"]["reviewer_ok"] == "true"
        assert (
            len(
                json.loads(
                    (root / "pipeline/metrics/clarification_log.json").read_text()
                )
            )
            == 2
        )
        builds.append(schema)

    monkeypatch.setattr(submit, "generate", build)
    assert submit.main(root=root) == 0
    assert builds == [root / "schema"]


def test_conflicts_only_do_not_rebuild(tmp_path, monkeypatch):
    root = snapshot(tmp_path)
    (root / "pipeline/review/decisions.json").write_text(
        json.dumps({"e1": {"a": {"decision": "ok"}, "b": {"decision": "drop"}}})
    )
    (root / "pipeline/review/clarifications.json").unlink()
    before = tree(root)
    monkeypatch.setattr(submit, "generate", lambda *a: pytest.fail("No rebuild needed"))
    assert submit.main(root=root) == 0
    assert tree(root) == before


@pytest.mark.parametrize(
    "destination",
    [
        "schema/registers/EV_evidence_register.csv",
        "pipeline/metrics/review_log.csv",
        "pipeline/metrics/clarification_log.json",
        "pipeline/metrics/clarification_log.tmp",
    ],
)
@pytest.mark.parametrize("link", ["symlink", "hardlink"])
def test_replay_refuses_redirected_writes_before_any_mutation(
    tmp_path, destination, link
):
    root = snapshot(tmp_path / "snapshot")
    external = tmp_path / "external"
    external.write_text("must remain untouched")
    target = root / destination
    target.unlink(missing_ok=True)
    if link == "symlink":
        target.symlink_to(external)
    else:
        os.link(external, target)
    before = tree(root)
    with pytest.raises(ValueError, match="symlink|independent file"):
        submit.replay(root)
    assert tree(root) == before
    assert external.read_text() == "must remain untouched"


def test_missing_register_does_not_publish_clarifications(tmp_path):
    root = snapshot(tmp_path)
    review.ReviewFiles.from_root(root).evidence.unlink()
    before = tree(root)
    with pytest.raises(ValueError, match="Evidence register missing"):
        submit.replay(root)
    assert tree(root) == before


def test_malformed_decisions_do_not_publish_clarifications(tmp_path):
    root = snapshot(tmp_path)
    (root / "pipeline/review/decisions.json").write_text("{broken")
    before = tree(root)
    with pytest.raises(ValueError):
        submit.replay(root)
    assert tree(root) == before


def test_cli_root_cannot_redirect_shipping(tmp_path, monkeypatch):
    monkeypatch.setattr(
        submit.sys, "argv", ["submit", "--root", str(tmp_path), "--ship", "alice"]
    )
    monkeypatch.setattr(submit, "ship", lambda *a: pytest.fail("Must not ship"))
    with pytest.raises(SystemExit) as exc:
        submit.cli()
    assert exc.value.code == 2


def test_cli_routes_local_root(tmp_path, monkeypatch):
    monkeypatch.setattr(submit.sys, "argv", ["submit", "--root", str(tmp_path)])
    calls = []
    monkeypatch.setattr(submit, "main", lambda **kwargs: calls.append(kwargs) or 0)
    assert submit.cli() == 0
    assert calls == [{"root": tmp_path}]
