"""Local QA/QC review server — make verify-flag review a click, not a CSV dance.

Serves the dashboard from ``docs/`` AND exposes a tiny JSON API so the QA/QC tab's
ok/drop buttons write decisions directly and an "Apply & rebuild" button runs the
pipeline. The public GitHub-Pages dashboard stays static + read-only; this is a LOCAL
tool you run while doing QAQC. The page auto-detects the API (GET /api/health) and
upgrades the buttons; without it, it falls back to the download-CSV flow.

Run:  uv run python3 -m nbs_ruralscan.schema_tools.review_server   # http://localhost:8765
Endpoints:
  GET  /api/health                      -> {ok:true}
  GET  /api/state                       -> {decisions:{id:dec}}
  POST /api/decision {evidence_id,decision,reviewer}  -> record one decision
  POST /api/apply    {reviewer}         -> apply all decisions -> regenerate/re-gate
"""

from __future__ import annotations

import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOCS = ROOT / "docs"
STORE = ROOT / "pipeline" / "review" / "decisions.json"


def _load() -> dict:
    if STORE.exists():
        try:
            return json.loads(STORE.read_text())
        except Exception:
            return {}
    return {}


def _save(d: dict) -> None:
    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps(d, indent=2))


class Handler(SimpleHTTPRequestHandler):
    def _json(self, code: int, obj: dict) -> None:
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        if self.path == "/api/health":
            return self._json(200, {"ok": True})
        if self.path == "/api/state":
            return self._json(200, {"decisions": _load()})
        if self.path.startswith("/api/pdf"):
            from urllib.parse import urlparse, parse_qs
            import re as _re
            sid = parse_qs(urlparse(self.path).query).get("sid", [""])[0]
            if not _re.fullmatch(r"[A-Za-z0-9_]+", sid or ""):
                return self._json(400, {"error": "bad sid"})
            pdf = ROOT / ".cache" / "corpus" / (sid + ".pdf")
            if not pdf.exists():
                return self._json(404, {"error": "no cached pdf"})
            data = pdf.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        return super().do_GET()

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            return self._json(400, {"error": "bad json"})

        if self.path == "/api/decision":
            # store is nested: {evidence_id: {reviewer: {decision, reason, note}}} — one per person.
            eid = payload.get("evidence_id")
            dec = payload.get("decision", "")
            rev = (payload.get("reviewer") or "reviewer").strip() or "reviewer"
            if not eid:
                return self._json(400, {"error": "evidence_id required"})
            store = _load()
            byrev = store.setdefault(eid, {})
            if dec in ("", None):
                byrev.pop(rev, None)
            else:
                byrev[rev] = {"decision": dec, "reason": payload.get("reason", ""), "note": payload.get("note", "")}
            if not byrev:
                store.pop(eid, None)
            _save(store)
            decided = sum(1 for e in store.values() for r in e.values() if r.get("decision"))
            return self._json(200, {"ok": True, "decided": decided})

        if self.path == "/api/apply":
            store = _load()
            if not store:
                return self._json(200, {"applied": 0, "message": "no decisions"})
            from nbs_ruralscan.schema_tools.review import apply_decisions
            from nbs_ruralscan.schema_tools.generate import generate

            # CONSENSUS: only apply a flag when every reviewer who decided it AGREES.
            decisions, conflicts = {}, []
            for eid, byrev in store.items():
                decs = {rv: v for rv, v in byrev.items() if (v.get("decision") or "").strip()}
                if not decs:
                    continue
                vals = set(v["decision"] for v in decs.values())
                if len(vals) == 1:
                    decisions[eid] = {
                        "decision": next(iter(vals)),
                        "reason": ";".join(sorted({v.get("reason", "") for v in decs.values() if v.get("reason")})),
                        "note": " | ".join(v.get("note", "") for v in decs.values() if v.get("note")),
                        "reviewer": ",".join(sorted(decs.keys())),
                    }
                else:
                    conflicts.append({"evidence_id": eid, "reviews": {rv: v["decision"] for rv, v in decs.items()}})
            if not decisions:
                return self._json(200, {"applied": 0, "ok": True, "conflicts": conflicts, "message": "no consensus units to apply"})
            try:
                res = apply_decisions(decisions, "consensus")
                generate(ROOT / "schema")
            except Exception as e:  # noqa: BLE001
                return self._json(500, {"error": str(e)})
            for eid in decisions:
                store.pop(eid, None)  # keep conflicts pending for discussion
            _save(store)
            return self._json(200, {"ok": True, **res, "conflicts": conflicts})

        if self.path == "/api/clear":
            # Reset to-review. Scoped to ONE reviewer by default (you can't wipe others'
            # pending work); a full wipe requires reviewer="*". Always backs up first.
            rev = (payload.get("reviewer") or "").strip()
            store = _load()
            if STORE.exists():
                (STORE.parent / "decisions.bak.json").write_text(STORE.read_text())
            if rev and rev != "*":
                for eid in list(store):
                    store[eid].pop(rev, None)
                    if not store[eid]:
                        store.pop(eid, None)
                _save(store)
                return self._json(200, {"ok": True, "cleared_for": rev})
            if rev == "*":
                _save({})
                return self._json(200, {"ok": True, "cleared_for": "ALL"})
            return self._json(400, {"error": "reviewer required (use '*' to clear all)"})

        return self._json(404, {"error": "not found"})

    def log_message(self, *a):  # quieter
        pass


def main() -> int:
    import sys

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    handler = partial(Handler, directory=str(DOCS))
    srv = ThreadingHTTPServer(("127.0.0.1", port), handler)
    print(f"QA/QC review server → http://localhost:{port}/dashboard.html  (Ctrl-C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
