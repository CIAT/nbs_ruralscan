import io
import json
import threading
import time

from nbs_ruralscan.schema_tools import review_server as server


def test_post_serializes_read_modify_write(monkeypatch):
    state = {"count": 0}

    def handle(self):
        old = state["count"]
        time.sleep(0.005)
        state["count"] = old + 1

    monkeypatch.setattr(server.Handler, "_handle_post", handle)
    handlers = [server.Handler.__new__(server.Handler) for _ in range(12)]
    for handler in handlers:
        handler.path = "/api/decision"
    threads = [threading.Thread(target=h.do_POST) for h in handlers]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert state["count"] == 12


def test_reopen_clears_only_requesting_reviewers_saved_call(tmp_path, monkeypatch):
    from nbs_ruralscan.schema_tools import review, generate

    store = tmp_path / "decisions.json"
    store.write_text(
        json.dumps(
            {
                "one": {"Pete": {"decision": "ok"}, "Namita": {"decision": "ok"}},
                "two": {"Pete": {"decision": "ok"}},
            }
        )
    )
    monkeypatch.setattr(server, "STORE", store)
    monkeypatch.setattr(server, "ROOT", tmp_path)
    monkeypatch.setattr(review, "reopen_units", lambda *a: {"reopened": 1})
    refreshed = []
    monkeypatch.setattr(
        generate, "refresh_review_state", lambda path: refreshed.append(path)
    )
    payload = json.dumps({"evidence_ids": ["one"], "reviewer": "Pete"}).encode()
    h = server.Handler.__new__(server.Handler)
    h.path = "/api/reopen"
    h.headers = {"Content-Length": str(len(payload))}
    h.rfile = io.BytesIO(payload)
    results = []
    h._json = lambda status, data: results.append((status, data))
    h.do_POST()
    saved = json.loads(store.read_text())
    assert saved["one"] == {"Namita": {"decision": "ok"}}
    assert saved["two"] == {"Pete": {"decision": "ok"}}
    assert refreshed == [tmp_path / "schema"]
    assert results[0][0] == 200


def test_query_can_reopen_even_without_approval_flag(tmp_path, monkeypatch):
    import csv
    from nbs_ruralscan.schema_tools import review

    ev = tmp_path / "ev.csv"
    fields = ["evidence_id", "source_id", "reviewer_ok", "review_state", "attribution"]
    with ev.open("w") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerow(
            dict(
                evidence_id="one",
                source_id="paper",
                reviewer_ok="false",
                review_state="",
                attribution="query",
            )
        )
    log = tmp_path / "review.csv"
    monkeypatch.setattr(review, "EV", ev)
    monkeypatch.setattr(review, "LOG", log)
    assert review.reopen_units(["one"], "Pete")["reopened"] == 1
    rows = list(csv.DictReader(log.open()))
    assert rows[0]["decision"] == "reopen"
    assert rows[0]["reviewer"] == "Pete"


def test_repeat_conflict_review_saved_without_settling_conflict(tmp_path, monkeypatch):
    from nbs_ruralscan.schema_tools import review, generate

    store = tmp_path / "decisions.json"
    monkeypatch.setattr(server, "STORE", store)
    monkeypatch.setattr(server, "ROOT", tmp_path)
    monkeypatch.setattr(review, "reopen_units", lambda *a: {"reopened": 0})
    monkeypatch.setattr(generate, "refresh_review_state", lambda *a: None)
    for route in ("/api/decision", "/api/challenge"):
        store.write_text(
            json.dumps(
                {"one": {"Pete": {"decision": "drop"}, "Namita": {"decision": "ok"}}}
            )
        )
        payload = json.dumps(
            dict(
                evidence_id="one",
                reviewer="Pete",
                decision="drop",
                reason="off_scope",
                reviewed_conflict=True,
            )
        ).encode()
        h = server.Handler.__new__(server.Handler)
        h.path = route
        h.headers = {"Content-Length": str(len(payload))}
        h.rfile = io.BytesIO(payload)
        results = []
        h._json = lambda status, data: results.append((status, data))
        h.do_POST()
        saved = json.loads(store.read_text())["one"]
        assert results[0][0] == 200
        assert saved["Pete"]["reviewed_conflict_at"]
        assert saved["Pete"]["decision"] == "drop"
        assert saved["Namita"] == {"decision": "ok"}
