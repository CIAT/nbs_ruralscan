"""Relocated replay must never use the compiler checkout's mutable records."""

import csv
import json
import os
from pathlib import Path

import pytest
from nbs_ruralscan.schema_tools import publication, review, submit_review as submit


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


@pytest.mark.parametrize("failed_write", ["evidence", "audit", "clarification"])
def test_staging_write_failure_leaves_every_live_record_untouched(
    tmp_path, monkeypatch, failed_write
):
    root = snapshot(tmp_path / "snapshot")
    before = tree(root)
    original = Path.open
    names = {
        "evidence": "EV_evidence_register.csv",
        "audit": "review_log.csv",
        "clarification": "clarification_log.tmp",
    }

    def fail_write(path, mode="r", *args, **kwargs):
        if path.name == names[failed_write] and mode in {"w", "a"}:
            assert not path.is_relative_to(root)
            raise OSError(f"injected {failed_write} write failure")
        return original(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fail_write)
    with pytest.raises(OSError, match="injected"):
        submit.replay(root)
    assert tree(root) == before


@pytest.mark.parametrize(
    "failure,existing_audit",
    [
        ("second_replace", False),
        ("after_replace_interrupt", False),
        ("third_replace", True),
        ("after_third_interrupt", True),
    ],
)
def test_record_install_failure_restores_existing_and_removes_new_records(
    tmp_path, monkeypatch, failure, existing_audit
):
    root = snapshot(tmp_path / "snapshot")
    log = review.ReviewFiles.from_root(root).log
    if existing_audit:
        log.write_text(
            "date,evidence_id,source_id,verdict,decision,reason,note,reviewer\n"
            "2026-01-01,e4,s4,,ok,,,previous_reviewer\n"
        )
    before = tree(root)
    replace = publication.os.replace
    calls = 0

    def fail_install(source, target):
        nonlocal calls
        if Path(target).is_relative_to(root):
            calls += 1
            if failure == "second_replace" and calls == 2:
                raise OSError("record install failed")
            if failure == "after_replace_interrupt" and calls == 2:
                replace(source, target)
                raise KeyboardInterrupt("record install interrupted")
            if failure == "third_replace" and calls == 3:
                raise OSError("record install failed")
            if failure == "after_third_interrupt" and calls == 3:
                replace(source, target)
                raise KeyboardInterrupt("record install interrupted")
        replace(source, target)

    monkeypatch.setattr(publication.os, "replace", fail_install)
    with pytest.raises((OSError, KeyboardInterrupt), match="record install"):
        submit.replay(root)
    assert tree(root) == before
    assert log.exists() == existing_audit


def test_incomplete_record_rollback_preserves_recovery_copies(tmp_path, monkeypatch):
    root = snapshot(tmp_path / "snapshot")
    before = tree(root)
    replace = publication.os.replace
    calls = 0

    def fail_install_and_restore(source, target):
        nonlocal calls
        if Path(target).is_relative_to(root):
            calls += 1
            if calls >= 2:
                raise OSError("disk unavailable")
        replace(source, target)

    monkeypatch.setattr(publication.os, "replace", fail_install_and_restore)
    with pytest.raises(publication.PublicationRecoveryError) as caught:
        submit.replay(root)
    recovery = caught.value.recovery_dir
    manifest = json.loads((recovery / "manifest.json").read_text())
    assert manifest["output_root"] == str(root)
    ev = "schema/registers/EV_evidence_register.csv"
    assert (recovery / "before" / ev).read_bytes() == before[ev]
    assert (recovery / "artifacts" / ev).read_bytes() == (root / ev).read_bytes()
    assert manifest["previous"]["pipeline/metrics/review_log.csv"] is None
    for name in ("decisions.json", "clarifications.json"):
        path = "pipeline/review/" + name
        assert (root / path).read_bytes() == before[path]
    import shutil

    shutil.rmtree(recovery)


def test_unknown_evidence_id_does_not_create_empty_audit_log(tmp_path):
    root = snapshot(tmp_path)
    (root / "pipeline/review/decisions.json").write_text(
        json.dumps({"unknown": {"alice": {"decision": "ok"}}})
    )
    (root / "pipeline/review/clarifications.json").unlink()
    before = tree(root)
    result = submit.replay(root)
    assert result.applied is not None and result.applied["ok"] == 0
    assert tree(root) == before
    assert not review.ReviewFiles.from_root(root).log.exists()


def test_clarification_only_replay_can_create_history_without_other_records(tmp_path):
    local = tmp_path / "pipeline/review/clarifications.json"
    local.parent.mkdir(parents=True)
    events = [{"date": "2026-01-01", "issue_id": "one", "note": "reply"}]
    local.write_text(json.dumps(events))
    original = local.read_bytes()
    result = submit.replay(tmp_path)
    assert result.applied is None and result.clarification_count == 1
    assert (
        json.loads((tmp_path / "pipeline/metrics/clarification_log.json").read_text())
        == events
    )
    assert local.read_bytes() == original
    assert not review.ReviewFiles.from_root(tmp_path).log.exists()
    assert not review.ReviewFiles.from_root(tmp_path).evidence.exists()
    before = tree(tmp_path)
    assert not submit.replay(tmp_path).needs_rebuild
    assert tree(tmp_path) == before


def test_generator_failure_retains_successful_replay_and_explains_explicit_retry(
    tmp_path, monkeypatch, capsys
):
    root = snapshot(tmp_path)
    (root / "pipeline/review/decisions.json").unlink()
    evidence_before = review.ReviewFiles.from_root(root).evidence.read_bytes()
    attempts = []

    def fail_build(schema):
        attempts.append(schema)
        assert (
            len(
                json.loads(
                    (root / "pipeline/metrics/clarification_log.json").read_text()
                )
            )
            == 2
        )
        raise RuntimeError("artifact build failed")

    monkeypatch.setattr(submit, "generate", fail_build)
    with pytest.raises(RuntimeError, match="artifact build failed"):
        submit.main(root=root)
    assert "Retry generation explicitly" in capsys.readouterr().err
    assert review.ReviewFiles.from_root(root).evidence.read_bytes() == evidence_before
    assert submit.main(root=root) == 0
    assert attempts == [
        root / "schema"
    ]  # Duplicate events are not republished/rebuilt.


def test_staged_replay_does_not_overwrite_concurrent_record_edit(tmp_path, monkeypatch):
    root = snapshot(tmp_path)
    before = tree(root)
    apply = submit.apply_decisions
    log = review.ReviewFiles.from_root(root).log

    def concurrent(*args, **kwargs):
        result = apply(*args, **kwargs)
        log.write_text("another writer\n")
        return result

    monkeypatch.setattr(submit, "apply_decisions", concurrent)
    with pytest.raises(ValueError, match="changed during compilation"):
        submit.replay(root)
    assert log.read_text() == "another writer\n"
    after = tree(root)
    del after["pipeline/metrics/review_log.csv"]
    assert after == before
