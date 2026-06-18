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
            eid = payload.get("evidence_id")
            dec = payload.get("decision", "")
            if not eid:
                return self._json(400, {"error": "evidence_id required"})
            store = _load()
            if dec in ("", None):
                store.pop(eid, None)
            else:
                store[eid] = {"decision": dec, "reviewer": payload.get("reviewer", "reviewer")}
            _save(store)
            return self._json(200, {"ok": True, "decided": len(store)})

        if self.path == "/api/apply":
            store = _load()
            if not store:
                return self._json(200, {"applied": 0, "message": "no decisions"})
            from nbs_ruralscan.schema_tools.review import apply_decisions
            from nbs_ruralscan.schema_tools.generate import generate

            decisions = {eid: v["decision"] for eid, v in store.items()}
            reviewer = next((v.get("reviewer") for v in store.values() if v.get("reviewer")), "reviewer")
            try:
                res = apply_decisions(decisions, reviewer)
                generate(ROOT / "schema")  # rebuild + re-gate (raises if a gate fails)
            except Exception as e:  # noqa: BLE001
                return self._json(500, {"error": str(e)})
            _save({})  # clear after successful apply
            return self._json(200, {"ok": True, **res})

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
