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
