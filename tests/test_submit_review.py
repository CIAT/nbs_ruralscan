"""Consensus reduction for the headless review-submit path (scripts/submit-review.sh)."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from nbs_ruralscan.schema_tools import submit_review as submit
from nbs_ruralscan.schema_tools.submit_review import consensus_decisions


def test_agreeing_reviewers_apply_with_merged_reason_and_reviewers():
    store = {
        "e1": {
            "alice": {"decision": "drop", "reason": "off_scope"},
            "bob": {"decision": "drop", "reason": "wrong_table"},
        }
    }
    decisions, conflicts = consensus_decisions(store)
    assert conflicts == []
    assert decisions["e1"]["decision"] == "drop"
    assert decisions["e1"]["reviewer"] == "alice,bob"
    assert decisions["e1"]["reason"] == "off_scope;wrong_table"


def test_disagreement_is_a_conflict_not_applied():
    store = {"e1": {"alice": {"decision": "ok"}, "bob": {"decision": "drop"}}}
    decisions, conflicts = consensus_decisions(store)
    assert decisions == {}
    assert conflicts == ["e1"]


def test_single_reviewer_applies():
    store = {"e1": {"alice": {"decision": "ok", "reason": "confirmed_pass"}}}
    decisions, conflicts = consensus_decisions(store)
    assert list(decisions) == ["e1"]
    assert conflicts == []


def test_empty_decision_ignored():
    store = {"e1": {"alice": {"decision": ""}}, "e2": {"bob": {}}}
    decisions, conflicts = consensus_decisions(store)
    assert decisions == {} and conflicts == []


@pytest.fixture
def shipping_repo(tmp_path, monkeypatch):
    """Real Git checkout and local bare origin; only replay and GitHub are simulated."""
    root = tmp_path / "repo"
    origin = tmp_path / "origin.git"
    root.mkdir()

    def git(*args, cwd=root):
        return subprocess.run(
            ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
        ).stdout.strip()

    git("init", "--bare", str(origin))
    git("init", "-b", "main")
    git("config", "user.name", "Test Reviewer")
    git("config", "user.email", "review@example.test")
    (root / ".gitignore").write_text(".cache/\npipeline/review/\n")
    ev = root / "schema/registers/EV_evidence_register.csv"
    ev.parent.mkdir(parents=True)
    ev.write_text("original\n")
    (root / "application.py").write_text("original\n")
    git("add", ".")
    git("commit", "-m", "fixture")
    git("remote", "add", "origin", str(origin))
    git("push", "-u", "origin", "main")
    (root / ".cache/corpus").mkdir(parents=True)
    (root / ".cache/corpus/source.txt").write_text("source")
    store = root / "pipeline/review/decisions.json"
    store.parent.mkdir(parents=True)
    store.write_text('{"saved":"untouched"}')
    (root / "application.py").write_text("user edits\n")
    calls = []
    real_run = subprocess.run
    mode = {"replay": "change", "fail_push": False}

    def run(args, **kwargs):
        cwd = Path(kwargs.get("cwd", root))
        calls.append(args)
        if args[0] == sys.executable:
            assert (
                cwd / "pipeline/review/decisions.json"
            ).read_bytes() == store.read_bytes()
            assert (cwd / ".cache/corpus/source.txt").read_text() == "source"
            if mode["replay"] == "fail":
                return subprocess.CompletedProcess(args, 1, "", "provenance failure")
            if mode["replay"] == "change":
                (cwd / "schema/registers/EV_evidence_register.csv").write_text(
                    "reviewed\n"
                )
                (cwd / "application.py").write_text("must never ship\n")
            if mode["replay"] == "actual":
                submit.replay(cwd)
            return subprocess.CompletedProcess(args, 0, "replayed", "")
        if args[0] == "gh":
            output = (
                "https://github.com/test/repo/pull/1"
                if args[1:3] == ["pr", "create"]
                else ""
            )
            return subprocess.CompletedProcess(args, 0, output, "")
        return real_run(args, **kwargs)

    monkeypatch.setattr(submit.subprocess, "run", run)
    return root, git, calls, mode


def test_ship_preserves_live_work_and_stages_only_allowlist(shipping_repo):
    root, git, calls, mode = shipping_repo
    assert submit.ship("alice", auto=True, root=root) == 0
    assert git("branch", "--show-current") == "main"
    assert (root / "application.py").read_text() == "user edits\n"
    assert (
        root / "schema/registers/EV_evidence_register.csv"
    ).read_text() == "original\n"
    assert (
        root / "pipeline/review/decisions.json"
    ).read_text() == '{"saved":"untouched"}'
    branch = next(c[-1] for c in calls if c[:3] == ["git", "push", "-u"])
    assert (
        git("diff", "--name-only", "main", branch)
        == "schema/registers/EV_evidence_register.csv"
    )
    assert any("--auto" in c for c in calls if c[:3] == ["gh", "pr", "merge"])
    assert not (root / ".cache/review-submit.lock").exists()


def test_ship_noop_does_not_push_or_open_pr(shipping_repo):
    root, git, calls, mode = shipping_repo
    mode["replay"] = "noop"
    assert submit.ship("alice", root=root) == 0
    assert not any(
        c[:2] == ["git", "push"] or c[:3] == ["gh", "pr", "create"] for c in calls
    )
    assert len(git("worktree", "list").splitlines()) == 1


def test_first_clarification_history_is_submitted_and_local_event_survives(
    shipping_repo,
):
    root, git, calls, mode = shipping_repo
    mode["replay"] = "actual"
    review = root / "pipeline/review"
    (review / "decisions.json").write_text("{}")
    event = {"issue_id": "question", "date": "2026-11-07", "note": "First reply"}
    pending = review / "clarifications.json"
    pending.write_text(json.dumps([event]))
    before = pending.read_bytes()
    assert submit.ship("alice", root=root) == 0
    branch = next(c[-1] for c in calls if c[:3] == ["git", "push", "-u"])
    assert json.loads(
        git("show", f"{branch}:pipeline/metrics/clarification_log.json")
    ) == [event]
    assert (
        git("diff", "--name-only", "main", branch)
        == "pipeline/metrics/clarification_log.json"
    )
    assert pending.read_bytes() == before


def test_ship_real_replay_preserves_newer_main_rows(shipping_repo):
    root, git, calls, mode = shipping_repo
    mode["replay"] = "actual"
    ev = root / "schema/registers/EV_evidence_register.csv"
    header = "evidence_id,source_id,attribution,review_state,reviewer_ok\n"
    ev.write_text(header + "e1,s1,original,,false\n")
    git("add", str(ev))
    git("commit", "-m", "review fixture")
    git("push", "origin", "main")
    stale_head = git("rev-parse", "HEAD")
    git("switch", "-c", "newer-main")
    ev.write_text(ev.read_text() + "remote-only,s2,new record,,true\n")
    git("add", str(ev))
    git("commit", "-m", "new evidence")
    git("push", "origin", "HEAD:main")
    git("switch", "main")
    store = root / "pipeline/review/decisions.json"
    store.write_text(json.dumps({"e1": {"alice": {"decision": "drop"}}}))
    before = ev.read_bytes(), store.read_bytes()

    assert submit.ship("alice", root=root) == 0

    branch = next(c[-1] for c in calls if c[:3] == ["git", "push", "-u"])
    shipped = git("show", f"{branch}:schema/registers/EV_evidence_register.csv")
    assert "remote-only,s2,new record,,true" in shipped
    assert "dropped" in shipped
    assert git("rev-parse", "HEAD") == stale_head
    assert (ev.read_bytes(), store.read_bytes()) == before
    assert (root / "application.py").read_text() == "user edits\n"


def test_ship_failed_gate_preserves_recovery_checkout(shipping_repo):
    root, git, calls, mode = shipping_repo
    mode["replay"] = "fail"
    with pytest.raises(RuntimeError, match="provenance failure"):
        submit.ship("alice", root=root)
    assert not any(c[:2] == ["git", "push"] for c in calls)
    assert len(git("worktree", "list").splitlines()) == 2
    assert (root / "pipeline/review/decisions.json").exists()
    assert not (root / ".cache/review-submit.lock").exists()
    # Test-owned failed checkout cleanup.
    checkout = next(c[-2] for c in calls if c[:3] == ["git", "worktree", "add"])
    git("worktree", "remove", "--force", checkout)


def test_ship_refuses_concurrent_submission(shipping_repo):
    root, git, calls, mode = shipping_repo
    (root / ".cache/review-submit.lock").touch()
    with pytest.raises(RuntimeError, match="Another submission"):
        submit.ship("alice", root=root)
    assert not any(c[:3] == ["git", "worktree", "add"] for c in calls)


def test_ship_rejects_unsafe_handle_before_commands(tmp_path):
    with pytest.raises(ValueError, match="GitHub handle"):
        submit.ship("../bad", root=tmp_path)


def test_ship_without_symlink_privilege(shipping_repo, monkeypatch):
    root, git, calls, mode = shipping_repo

    def denied(*args, **kwargs):
        raise OSError("Windows symlink privilege unavailable")

    monkeypatch.setattr(Path, "symlink_to", denied)
    assert submit.ship("alice", root=root) == 0
    assert (root / ".cache/corpus/source.txt").read_text() == "source"


def test_cli_routes_ship_arguments(monkeypatch):
    calls = []
    monkeypatch.setattr(
        sys,
        "argv",
        ["submit_review", "--ship", "alice", "--title", "qaqc: batch", "--auto"],
    )
    monkeypatch.setattr(submit, "ship", lambda *args: calls.append(args) or 0)
    assert submit.cli() == 0
    assert calls == [("alice", "qaqc: batch", True)]
