"""Direct review callers must publish coherent records without touching live defaults."""

import csv
import importlib.util
import io
import json
from pathlib import Path

import pytest

from nbs_ruralscan.schema_tools import generate, publication, review
from nbs_ruralscan.schema_tools import review_server as server


def snapshot(root):
    files = review.ReviewFiles.from_root(root)
    files.evidence.parent.mkdir(parents=True)
    files.log.parent.mkdir(parents=True)
    files.evidence.write_text(
        "evidence_id,source_id,variable,use_role,attribution,review_state,reviewer_ok\n"
        "one,paper,slope,structural_suitability,[VERIFY-FLAG mismatch: value],,false\n"
        "two,paper,slope,structural_suitability,untouched,,false\n"
    )
    store = root / "pipeline/review/decisions.json"
    store.parent.mkdir(parents=True)
    store.write_text(
        json.dumps(
            {
                "one": {"alice": {"decision": "ok", "reason": "confirmed_pass"}},
                "two": {"alice": {"decision": "ok"}, "bob": {"decision": "drop"}},
            }
        )
    )
    (root / "pipeline/review/clarifications.json").write_text("[]\n")
    return files, store


def tree(root):
    return {
        str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()
    }


def events(files):
    if not files.log.exists():
        return []
    with files.log.open(newline="") as stream:
        return list(csv.DictReader(stream))


def post(route, data=None):
    payload = json.dumps(data or {}).encode()
    handler = server.Handler.__new__(server.Handler)
    handler.path = route
    handler.headers = {"Content-Length": str(len(payload))}
    handler.rfile = io.BytesIO(payload)
    replies = []
    handler._json = lambda code, body: replies.append((code, body))
    handler.do_POST()
    return replies[0]


@pytest.fixture
def endpoint(tmp_path, monkeypatch):
    root = tmp_path / "selected"
    files, store = snapshot(root)
    live, _ = snapshot(tmp_path / "live")
    live_before = tree(tmp_path / "live")
    monkeypatch.setattr(server, "ROOT", root)
    monkeypatch.setattr(server, "STORE", store)
    monkeypatch.setattr(
        server, "_pipeline_text_files", lambda: [files.evidence, files.log]
    )
    monkeypatch.setattr(review, "EV", live.evidence)
    monkeypatch.setattr(review, "LOG", live.log)
    builds = []
    monkeypatch.setattr(generate, "generate", lambda p: builds.append(("full", p)))
    monkeypatch.setattr(
        generate, "refresh_review_state", lambda p: builds.append(("refresh", p))
    )
    yield root, files, store, builds
    assert tree(tmp_path / "live") == live_before


def test_apply_preserves_response_conflicts_and_repeat_dedup(endpoint):
    root, files, store, builds = endpoint
    status, result = post("/api/apply")
    assert status == 200
    assert result == {
        "ok": 1,
        "dropped": 0,
        "queried": 0,
        "reclassified": 0,
        "rows": 2,
        "reasons": {"confirmed_pass": 1},
        "conflicts": [
            {"evidence_id": "two", "reviews": {"alice": "ok", "bob": "drop"}}
        ],
    }
    saved = json.loads(store.read_text())
    assert saved["one"]["alice"]["applied"] is True
    assert "applied" not in saved["two"]["alice"]
    before = tree(root)
    status, result = post("/api/apply")
    assert status == 200 and result["ok"] == 0
    assert tree(root) == before
    assert len(events(files)) == 1
    assert builds == [("full", root / "schema")] * 2


@pytest.mark.parametrize(
    "store_data", [{}, {"two": {"a": {"decision": "ok"}, "b": {"decision": "drop"}}}]
)
def test_no_agreement_is_noop(endpoint, store_data):
    root, _, store, builds = endpoint
    store.write_text(json.dumps(store_data))
    before = tree(root)
    status, result = post("/api/apply")
    assert status == 200 and result["applied"] == 0
    assert tree(root) == before and builds == []


def test_reopen_keeps_other_reviewers_and_challenge_keeps_conflict(endpoint):
    _, files, store, builds = endpoint
    status, result = post("/api/reopen", {"evidence_id": "two", "reviewer": "alice"})
    assert (status, result) == (200, {"ok": True, "reopened": 1})
    assert json.loads(store.read_text())["two"] == {"bob": {"decision": "drop"}}
    status, result = post(
        "/api/challenge", {"evidence_id": "two", "reviewer": "alice", "decision": "ok"}
    )
    assert status == 200 and result["conflict"] is True and result["reopened"] == 1
    assert [e["decision"] for e in events(files)] == ["reopen", "reopen"]
    assert len(builds) == 2


@pytest.mark.parametrize("reviewed_conflict", [False, True])
def test_challenge_without_reopen_only_saves_call(endpoint, reviewed_conflict):
    _, files, store, builds = endpoint
    target = "two" if reviewed_conflict else "one"
    status, result = post(
        "/api/challenge",
        {
            "evidence_id": target,
            "reviewer": "alice",
            "decision": "ok",
            "reviewed_conflict": reviewed_conflict,
        },
    )
    assert status == 200 and result["reopened"] == 0
    assert result["conflict"] == reviewed_conflict
    assert json.loads(store.read_text())[target]["alice"]["applied"] is False
    assert events(files) == [] and builds == []


ROUTES = [
    ("/api/apply", {}),
    ("/api/reopen", {"evidence_id": "one", "reviewer": "alice"}),
    ("/api/challenge", {"evidence_id": "one", "reviewer": "bob", "decision": "drop"}),
]


@pytest.mark.parametrize("route,payload", ROUTES)
@pytest.mark.parametrize(
    "failure", ["audit_write", "store_write", "second_install", "third_install"]
)
def test_endpoint_failed_record_write_restores_all_records(
    endpoint, monkeypatch, route, payload, failure
):
    root, files, store, builds = endpoint
    before = tree(root)
    original_open, original_replace = Path.open, publication.os.replace

    def failing_open(path, mode="r", *args, **kwargs):
        if failure == "audit_write" and path.name == "review_log.csv" and mode == "a":
            raise OSError("audit write failed")
        if (
            failure == "store_write"
            and path.name.startswith("decisions.json.tmp.")
            and mode == "w"
        ):
            raise OSError("decision save failed")
        return original_open(path, mode, *args, **kwargs)

    target = files.log if failure == "second_install" else store
    fired = False

    def failing_replace(source, destination):
        nonlocal fired
        if failure.endswith("install") and Path(destination) == target and not fired:
            fired = True
            raise OSError("record installation failed")
        return original_replace(source, destination)

    monkeypatch.setattr(Path, "open", failing_open)
    monkeypatch.setattr(publication.os, "replace", failing_replace)
    status, result = post(route, payload)
    assert status == 500 and "failed" in result["error"]
    assert (
        "records_saved" not in result
    )  # recovery/cleanup failures may be indeterminate
    assert tree(root) == before and builds == []


@pytest.mark.parametrize("route,payload", ROUTES)
def test_failed_rebuild_keeps_coherent_records_and_explains_retry(
    endpoint, monkeypatch, route, payload
):
    root, files, store, _ = endpoint

    def fail(_):
        raise RuntimeError("producer failed")

    name = "generate" if route == "/api/apply" else "refresh_review_state"
    monkeypatch.setattr(generate, name, fail)
    status, result = post(route, payload)
    assert status == 500 and result["records_saved"] and result["rebuild_required"]
    assert "without repeating Reopen or Challenge" in result["error"]
    assert name in result["error"] and "producer failed" in result["error"]
    assert len(events(files)) == 1
    saved = json.loads(store.read_text())
    if route == "/api/apply":
        assert saved["one"]["alice"]["applied"] is True
        monkeypatch.setattr(generate, name, lambda _: None)
        assert post(route, payload)[0] == 200
        assert len(events(files)) == 1
    elif route == "/api/reopen":
        assert "one" not in saved
    else:
        assert saved["one"]["bob"]["decision"] == "drop"
    assert (root / "pipeline/review/clarifications.json").read_text() == "[]\n"


@pytest.mark.parametrize("operation", ["apply", "reopen"])
def test_public_record_mutators_protect_audit_failure(tmp_path, monkeypatch, operation):
    files, _ = snapshot(tmp_path)
    before = tree(tmp_path)
    original = Path.open

    def fail(path, mode="r", *args, **kwargs):
        if path.name == "review_log.csv" and mode == "a":
            raise OSError("audit failed")
        return original(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fail)
    with pytest.raises(OSError, match="audit failed"):
        if operation == "apply":
            review.apply_decisions({"one": "ok"}, files=files)
        else:
            review.reopen_units(["one"], files=files)
    assert tree(tmp_path) == before


def load_export_script():
    path = Path(__file__).resolve().parents[1] / "scripts/apply-review-export.py"
    spec = importlib.util.spec_from_file_location("apply_review_export", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_csv_batch_later_reviewer_failure_then_retry(tmp_path, monkeypatch):
    root = tmp_path / "selected"
    files, _ = snapshot(root)
    export = tmp_path / "export.csv"
    export.write_text(
        "evidence_id,decision,reason,reviewer,note,picos_flags\none,approve,,alice,checked,I;C\ntwo,reject,off_scope,bob,wrong,\n"
    )
    script = load_export_script()
    before = tree(root)
    apply = script.apply_decisions

    def fail(decisions, reviewer, **kwargs):
        if reviewer == "bob":
            raise RuntimeError("second reviewer failed")
        return apply(decisions, reviewer, **kwargs)

    monkeypatch.setattr(script, "apply_decisions", fail)
    with pytest.raises(RuntimeError, match="second reviewer"):
        script.main([str(export), "--root", str(root)])
    assert tree(root) == before
    monkeypatch.setattr(script, "apply_decisions", apply)
    script.main([str(export), "--root", str(root), "--dry-run"])
    assert tree(root) == before
    script.main([str(export), "--root", str(root)])
    log = events(files)
    assert [(e["decision"], e["reviewer"]) for e in log] == [
        ("ok", "alice"),
        ("drop", "bob"),
    ]
    assert log[0]["note"] == "checked [PICOS fails: I,C]"
    after = tree(root)
    script.main([str(export), "--root", str(root)])
    assert tree(root) == after


def test_worklist_explicit_root_export_and_apply(tmp_path, monkeypatch):
    root = tmp_path / "selected"
    files, _ = snapshot(root)
    monkeypatch.setattr(review, "EV", tmp_path / "never-read.csv")
    monkeypatch.setattr(review, "LOG", tmp_path / "never-write.csv")
    monkeypatch.setattr(review, "WORKLIST", tmp_path / "never-worklist.csv")
    assert review.main(["export", "--root", str(root)]) == 0
    worklist = root / "pipeline/review/flag_worklist.csv"
    with worklist.open() as stream:
        rows = list(csv.DictReader(stream))
    assert [r["evidence_id"] for r in rows] == ["one"]
    rows[0].update(decision="ok", reviewer="alice")
    with worklist.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    assert review.main(["apply", "--root", str(root)]) == 0
    assert events(files)[0]["reviewer"] == "alice"
    assert not review.LOG.exists()


def test_worklist_failed_replacement_preserves_existing_export(tmp_path, monkeypatch):
    files, _ = snapshot(tmp_path)
    worklist = tmp_path / "worklist.csv"
    worklist.write_text("old,work\nkeep,this\n")
    before = tree(tmp_path)
    original = publication.os.replace

    def fail(source, target):
        if Path(target) == worklist:
            raise OSError("export failed")
        return original(source, target)

    monkeypatch.setattr(publication.os, "replace", fail)
    with pytest.raises(OSError, match="export failed"):
        review.export(files=files, worklist=worklist)
    assert tree(tmp_path) == before


def test_interrupt_after_store_replacement_restores_existing_records(
    endpoint, monkeypatch
):
    root, files, store, _ = endpoint
    assert post("/api/apply")[0] == 200
    before = tree(root)
    original = publication.os.replace
    fired = False

    def interrupt(source, target):
        nonlocal fired
        result = original(source, target)
        if Path(target) == store and not fired:
            fired = True
            raise KeyboardInterrupt()
        return result

    monkeypatch.setattr(publication.os, "replace", interrupt)
    with pytest.raises(KeyboardInterrupt):
        post("/api/reopen", {"evidence_id": "one", "reviewer": "alice"})
    assert tree(root) == before
    assert len(events(files)) == 1


def test_recovery_error_retains_path_and_never_claims_rollback(endpoint, monkeypatch):
    root, files, _, _ = endpoint
    original = publication.os.replace
    replacements = 0

    def fail(source, target):
        nonlocal replacements
        if Path(target) in (files.evidence, files.log):
            replacements += 1
            if replacements >= 2:
                raise OSError("install or rollback failed")
        return original(source, target)

    monkeypatch.setattr(publication.os, "replace", fail)
    status, result = post("/api/apply")
    assert status == 500
    assert "ruralscan-publication-" in result["error"]
    assert "records_saved" not in result
    assert (
        json.loads((root / "pipeline/review/decisions.json").read_text())["one"][
            "alice"
        ].get("applied")
        is None
    )


@pytest.mark.parametrize("target_name", ["evidence", "log", "store"])
def test_endpoint_refuses_redirected_record_paths(endpoint, tmp_path, target_name):
    root, files, store, builds = endpoint
    target = {"evidence": files.evidence, "log": files.log, "store": store}[target_name]
    external = tmp_path / "external"
    external.write_bytes(
        target.read_bytes() if target.exists() else b"date,evidence_id\n"
    )
    target.unlink(missing_ok=True)
    target.symlink_to(external)
    before, external_before = tree(root), external.read_bytes()
    status, result = post("/api/reopen", {"evidence_id": "one", "reviewer": "alice"})
    assert status == 500 and "symlink" in result["error"]
    assert tree(root) == before and external.read_bytes() == external_before
    assert builds == []
