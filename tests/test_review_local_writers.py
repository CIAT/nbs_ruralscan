"""Exercise review HTTP transactions against an isolated working directory."""

import csv
import hashlib
import io
import json
import multiprocessing
import os
import shutil
import sqlite3
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

import pytest

from nbs_ruralscan.schema_tools import clarifications
from nbs_ruralscan.schema_tools import review_server as server


def test_dashboard_retains_drafts_on_review_server_failure():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for the dashboard behavior tests")
    subprocess.run(
        [node, "--test", "tests/js/review_state_recovery.test.cjs"],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
    )


def request(route, data=None):
    handler = server.Handler.__new__(server.Handler)
    handler.path = route
    replies = []
    handler._json = lambda code, body: replies.append((code, body))
    if data is None:
        handler.do_GET()
    else:
        body = json.dumps(data).encode()
        handler.headers = {"Content-Length": str(len(body))}
        handler.rfile = io.BytesIO(body)
        handler.do_POST()
    assert len(replies) == 1
    return replies[0]


@pytest.fixture
def store(tmp_path, monkeypatch):
    for variable in ("HOME", "USERPROFILE"):
        monkeypatch.setenv(variable, str(tmp_path / "reviewer-home"))
    target = tmp_path / "pipeline/review/decisions.json"
    target.parent.mkdir(parents=True)
    monkeypatch.setattr(server, "ROOT", tmp_path)
    monkeypatch.setattr(server, "STORE", target)
    return target


def fail_after_replace(monkeypatch, target):
    """Raise once after the selected output has changed on disk."""
    replace = os.replace
    failures = []

    def interrupt(src, dst):
        replace(src, dst)
        if Path(dst) == target and not failures:
            failures.append(target)
            raise OSError("injected installation failure")

    monkeypatch.setattr(os, "replace", interrupt)
    return failures


def test_missing_store_then_valid_cp1252_store(store):
    assert request("/api/state") == (200, {"decisions": {}})
    assert not store.exists()
    original = {"one": {"alice": {"decision": "query", "note": "Reviewer’s café"}}}
    store.write_bytes(json.dumps(original, ensure_ascii=False).encode("cp1252"))
    assert request("/api/state") == (200, {"decisions": original})
    assert json.loads(store.read_bytes().decode("utf-8")) == original


@pytest.mark.parametrize(
    "raw",
    [
        b'{"one":{} }extra',
        '{"one":{ "note":"Reviewer’s café"'.encode("cp1252"),
        b'{"one": {"alice": ["keep"]}}',
        b"[]",
    ],
)
def test_unreadable_decisions_never_look_empty_or_get_overwritten(store, raw):
    store.write_bytes(raw)
    backup = store.with_name("decisions.bak.json")
    backup.write_bytes(b"previous backup")
    for route, data in (
        ("/api/state", None),
        ("/api/decision", {"evidence_id": "two", "reviewer": "bob", "decision": "ok"}),
        ("/api/clear", {"reviewer": "*"}),
    ):
        status, result = request(route, data)
        assert status >= 400 and result.get("error")
        assert store.read_bytes() == raw
        assert backup.read_bytes() == b"previous backup"


def review_entries():
    return {
        "one": {"alice": {"decision": "query"}, "bob": {"decision": "ok"}},
        "two": {"alice": {"decision": "ok", "applied": True}},
        "three": {"alice": {"decision": "ok", "applied": "true"}},
        "four": {"alice": {"decision": "drop", "applied": False}},
    }


def test_clear_scopes_pending_entries_and_keeps_the_entire_backup(store):
    original = review_entries()
    store.write_text(json.dumps(original), encoding="utf-8")
    backup = store.with_name("decisions.bak.json")
    backup.write_text("earlier backup", encoding="utf-8")
    before = store.read_bytes()
    assert request("/api/clear", {"reviewer": "   "})[0] == 400
    assert backup.read_bytes() == b"earlier backup"
    assert store.read_bytes() == before
    assert request("/api/clear", {"reviewer": " alice "}) == (
        200,
        {"ok": True, "cleared_for": "alice", "cleared": 2},
    )
    remaining = json.loads(store.read_text())
    assert remaining == {
        "one": {"bob": original["one"]["bob"]},
        "two": original["two"],
        "three": original["three"],
    }
    assert json.loads(backup.read_text()) == original
    assert request("/api/clear", {"reviewer": "*"}) == (
        200,
        {"ok": True, "cleared_for": "ALL"},
    )
    assert json.loads(store.read_text()) == {}
    assert json.loads(backup.read_text()) == remaining


@pytest.mark.parametrize("target", ["decisions.json", "decisions.bak.json"])
def test_clear_restores_decisions_and_previous_backup_on_failure(
    store, monkeypatch, target
):
    store.write_text(json.dumps(review_entries(), indent=4), encoding="utf-8")
    backup = store.with_name("decisions.bak.json")
    backup.write_bytes(b'{"previous": {}}\n')
    before = {p: p.read_bytes() for p in (store, backup)}
    failures = fail_after_replace(monkeypatch, store.with_name(target))
    status, body = request("/api/clear", {"reviewer": "alice"})
    assert failures and status >= 400 and body.get("error")
    assert {p: p.read_bytes() for p in before} == before


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def questions(tmp_path, store):
    paths = clarifications.ClarificationPaths.from_root(tmp_path)
    evidence = dict(
        evidence_id="one",
        nbs_id="agroforestry",
        use_role="structural_suitability",
        review_state="",
        source_id="paper",
        variable="slope",
        page="2",
        quote="Lower slopes preferred",
        claim_scope="practice_technology",
        relationship="{}",
        reviewer_ok="false",
    )
    write_csv(paths.evidence, [evidence])
    reviews = [
        dict(
            evidence_id="one",
            reviewer=name,
            decision="query",
            note=note,
            reason="unclear",
        )
        for name, note in (("alice", "Explain direction"), ("bob", "Explain scope"))
    ]
    write_csv(paths.review_log, reviews)
    paths.followups.parent.mkdir(parents=True)
    check = dict(
        evidence_id="one",
        field="quote",
        sha256=hashlib.sha256(evidence["quote"].encode()).hexdigest(),
    )
    paths.followups.write_text(
        json.dumps(
            {
                r["reviewer"]: dict(
                    evidence_id="one",
                    reviewer=r["reviewer"],
                    note=r["note"],
                    status="resolved",
                    resolution="The relationship is qualitative.",
                    resolution_checks=[check],
                )
                for r in reviews
            }
        )
    )
    paths.pending.write_text('[{"issue_id": "historic", "date": "2026-01-01"}]\n')
    store.write_text(json.dumps({"unrelated": {"bob": {"decision": "ok"}}}))
    issues = clarifications.build(paths)
    assert [g["status"] for g in issues] == ["answer_ready", "answer_ready"]
    ids = [g["id"] for g in issues]
    payload = dict(
        evidence_id="one",
        reviewer="carol",
        decision="query",
        note="Please cite the passage.",
        answered_issue_ids=[*ids, ids[0], "unknown"],
    )
    return paths, ids, payload


@pytest.mark.parametrize("encoding", ["utf-8", "cp1252"])
def test_new_query_publishes_one_reply_per_answer_and_keeps_prior_state(
    questions, encoding
):
    paths, ids, payload = questions
    old = {"bob": {"decision": "ok", "note": "Reviewer’s café"}}
    paths.decisions.write_bytes(
        json.dumps({"unrelated": old}, ensure_ascii=False).encode(encoding)
    )
    status, result = request("/api/decision", payload)
    assert status == 200 and result == {"ok": True, "decided": 2}
    decisions = json.loads(paths.decisions.read_text())
    assert decisions["unrelated"] == old
    assert decisions["one"]["carol"]["note"] == payload["note"]
    historic, *replies = json.loads(paths.pending.read_text())
    assert historic["issue_id"] == "historic"
    assert sorted(r["issue_id"] for r in replies) == sorted(ids)
    assert all(
        r["action"] == "reply"
        and r["evidence_ids"] == ["one"]
        and r["reviewer"] == "carol"
        and r["note"] == payload["note"]
        for r in replies
    )


@pytest.mark.parametrize("target", ["decisions", "pending"])
def test_new_query_rolls_back_both_replies_and_decision(questions, monkeypatch, target):
    paths, _, payload = questions
    before = {p: p.read_bytes() for p in (paths.decisions, paths.pending)}
    failures = fail_after_replace(monkeypatch, getattr(paths, target))
    status, body = request("/api/decision", payload)
    assert failures and status >= 400 and body.get("error")
    assert {p: p.read_bytes() for p in before} == before


def _submit_child(root, channel):
    """Run the real submission workflow, with isolated stand-ins for Git and GitHub."""
    from nbs_ruralscan.schema_tools import submit_review as submit

    pair_lock = submit.review_pair_lock
    connect = sqlite3.connect

    @contextmanager
    def observe_reservation():
        # A zero-timeout attempt proves contention without relying on a sleep.
        def no_wait(path, *, timeout):
            return connect(path, timeout=0)

        with (
            patch.object(sqlite3, "connect", no_wait),
            pytest.raises(OSError) as contention,
        ):
            with pair_lock():
                pass
        assert isinstance(contention.value.__cause__, sqlite3.OperationalError)
        assert "locked" in str(contention.value.__cause__).lower()
        channel.send("blocked during linked write")
        with pair_lock():
            yield

    def command(args, *, cwd, **kwargs):
        out = ""
        if args[:2] == ["git", "diff"]:
            out = "pipeline/metrics/clarification_log.json"
        elif args[:2] == ["git", "push"]:
            review = cwd / "pipeline/review"
            channel.send(
                tuple(
                    json.loads((review / name).read_bytes())
                    for name in ("decisions.json", "clarifications.json")
                )
            )
            assert channel.poll(15) and channel.recv() == "finish push"
        elif args[:3] == ["git", "worktree", "remove"]:
            shutil.rmtree(args[-1])
        return subprocess.CompletedProcess(args, 0, out, "")

    with (
        patch.object(submit, "review_pair_lock", observe_reservation),
        patch.object(submit.subprocess, "run", command),
    ):
        channel.send(submit.ship("carol", root=root))


def test_submission_reads_complete_linked_update_and_releases_before_push(
    tmp_path, questions, monkeypatch
):
    paths, ids, payload = questions
    (tmp_path / ".cache/corpus").mkdir(parents=True)
    first_installed, allow_second = threading.Event(), threading.Event()
    replace = os.replace

    def pause_between_targets(src, dest):
        replace(src, dest)
        if (
            Path(dest) in {paths.pending, paths.decisions}
            and not first_installed.is_set()
        ):
            first_installed.set()
            assert allow_second.wait(15)

    monkeypatch.setattr(os, "replace", pause_between_targets)
    ctx = multiprocessing.get_context("spawn")
    channel, child_channel = ctx.Pipe()
    child = ctx.Process(target=_submit_child, args=(tmp_path, child_channel))
    with ThreadPoolExecutor(max_workers=1) as pool:
        writer = pool.submit(request, "/api/decision", payload)
        try:
            assert first_installed.wait(10)
            child.start()
            child_channel.close()
            assert channel.poll(10) and channel.recv() == "blocked during linked write"
            allow_second.set()
            assert writer.result(timeout=10)[0] == 200
            assert channel.poll(10)
            submitted, events = channel.recv()
            assert submitted["one"]["carol"]["note"] == payload["note"]
            assert submitted["unrelated"] == {"bob": {"decision": "ok"}}
            assert [e["issue_id"] for e in events] == ["historic", *ids]
            # The submission is paused at push. Another linked save must finish now.
            edit = dict(payload, note="Please also check the appendix.")
            assert request("/api/decision", edit)[0] == 200
            channel.send("finish push")
            assert channel.poll(10) and channel.recv() == 0
            child.join(timeout=10)
            assert child.exitcode == 0
            live = json.loads(paths.decisions.read_bytes())
            assert live["one"]["carol"]["note"] == edit["note"]
            assert live["unrelated"] == submitted["unrelated"]
            live_events = json.loads(paths.pending.read_bytes())
            assert live_events[: len(events)] == events
            assert [(e["issue_id"], e["note"]) for e in live_events[len(events) :]] == [
                (issue_id, edit["note"]) for issue_id in ids
            ]
        finally:
            allow_second.set()
            if child.is_alive():
                child.terminate()
                child.join(timeout=10)
            child_channel.close()
            channel.close()


def test_gap_append_preserves_history_and_advances_past_existing_ids(tmp_path, store):
    gaps = tmp_path / "pipeline/metrics/gaps.csv"
    assert request("/api/gap", {"variable": "  ", "note": ""})[0] == 400
    assert not gaps.exists()
    assert request("/api/gap", {"variable": "slope"}) == (
        200,
        {"ok": True, "gap_id": "gap_0001"},
    )
    original = request("/api/gaps")[1]["gaps"][0]
    # A prior import has a discontinuous sequence.
    second = dict(original, gap_id="gap_0003", status="reviewed")
    write_csv(gaps, [original, second])
    note = "clarify, please\nincluding the annex"
    status, result = request("/api/gap", {"note": note, "reporter": "alice"})
    assert status == 200 and result["gap_id"] == "gap_0004"
    first, imported, latest = request("/api/gaps")[1]["gaps"]
    assert [first, imported] == [original, second]
    assert latest["note"] == note and latest["reporter"] == "alice"
    assert latest["status"] == "open"


def test_concurrent_gap_reports_keep_distinct_rows_and_identifiers(store):
    workers = 8
    start = threading.Barrier(workers)

    def report(index):
        start.wait(timeout=10)
        return request("/api/gap", {"variable": f"variable-{index}"})

    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(report, range(workers)))
    assert all(status == 200 for status, _ in results)
    rows = request("/api/gaps")[1]["gaps"]
    assert len(rows) == workers
    assert {r["variable"] for r in rows} == {f"variable-{i}" for i in range(workers)}
    assert {r["gap_id"] for r in rows} == {f"gap_{i + 1:04d}" for i in range(workers)}


def test_launcher_ports_all_local_writes_to_selected_root(tmp_path, monkeypatch):
    selected = tmp_path / "review checkout"
    (selected / "schema").mkdir(parents=True)
    (selected / "docs").mkdir()
    for name in ("ROOT", "DOCS", "CACHE", "STORE"):
        monkeypatch.setattr(server, name, tmp_path / "unused" / name)

    class ServerProbe:
        def __init__(self, address, handler):
            assert address == ("127.0.0.1", 9865)
            assert handler.func is server.Handler
            assert Path(handler.keywords["directory"]) == selected / "docs"

        def serve_forever(self):
            assert server.CACHE == selected / ".cache/corpus"
            assert (
                request("/api/decision", {"evidence_id": "one", "decision": "ok"})[0]
                == 200
            )
            assert request("/api/gap", {"note": "check appendix"})[0] == 200

    monkeypatch.setattr(server, "ThreadingHTTPServer", ServerProbe)
    assert server.main(["9865", "--root", str(selected)]) == 0
    assert (selected / "pipeline/review/decisions.json").is_file()
    assert (selected / "pipeline/metrics/gaps.csv").is_file()
    assert not (tmp_path / "unused").exists()


@pytest.mark.parametrize(
    ("route", "fields"),
    [
        ("/api/decision", {"decision": "flag", "reason": []}),
        ("/api/decision", {"decision": "ok", "note": {}}),
        ("/api/challenge", {"decision": "ok", "note": 20}),
        ("/api/challenge", {"decision": ["drop"]}),
        ("/api/reopen", {"evidence_ids": ["one", {}]}),
    ],
)
def test_bad_request_cannot_poison_saved_decisions(store, route, fields):
    original = b'{"old":{"reviewer":{"decision":"ok","other":[1]}}}'
    store.write_bytes(original)
    status, result = request(route, {"evidence_id": "one", **fields})
    assert status == 400 and result["error"]
    assert store.read_bytes() == original


def test_malformed_historical_note_stays_available_for_recovery(store):
    original = b'{"old":{"reviewer":{"decision":"flag","note":[]}}}'
    store.write_bytes(original)
    assert request("/api/state")[0] == 500
    assert request("/api/clear", {"reviewer": "*"})[0] == 500
    assert store.read_bytes() == original
    assert not store.with_name("decisions.bak.json").exists()
