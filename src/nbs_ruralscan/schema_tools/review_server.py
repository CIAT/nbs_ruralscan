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
            return json.loads(STORE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save(d: dict) -> None:
    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps(d, indent=2), encoding="utf-8")


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
        if self.path.startswith("/api/crop"):
            # render a page-region screengrab around an EV unit's quote (table view).
            from urllib.parse import urlparse, parse_qs
            import csv as _csv
            import re as _re

            eid = parse_qs(urlparse(self.path).query).get("eid", [""])[0]
            if not _re.fullmatch(r"[A-Za-z0-9_]+", eid or ""):
                return self._json(400, {"error": "bad eid"})
            ev_csv = ROOT / "schema" / "registers" / "EV_evidence_register.csv"
            row = None
            with ev_csv.open(newline="", encoding="utf-8") as f:
                for r in _csv.DictReader(f):
                    if r["evidence_id"] == eid:
                        row = r
                        break
            if not row:
                return self._json(404, {"error": "no such evidence_id"})
            pdf = ROOT / ".cache" / "corpus" / (row["source_id"] + ".pdf")
            if not pdf.exists():
                return self._json(404, {"error": "no cached pdf"})
            try:
                import fitz  # PyMuPDF

                doc = fitz.open(str(pdf))
                pno = int(row["page"]) if (row.get("page") or "").isdigit() else 1
                page = doc[max(0, min(pno - 1, len(doc) - 1))]
                quote = " ".join((row.get("quote") or "").split())
                # locate the WHOLE quote span: search several snippets across it and union
                # all hit rects (a table quote spans caption -> header -> data rows).
                rects = []
                for i in range(0, max(1, len(quote)), 38):
                    snip = quote[i : i + 30].strip()
                    if len(snip) >= 8:
                        rects += page.search_for(snip)
                clip = None
                # 1) prefer the FULL detected table bbox (includes its column-header row,
                #    which a quote deep in the table sits far below).
                if rects:
                    try:
                        for t in page.find_tables().tables or []:
                            tb = fitz.Rect(t.bbox)
                            if any(tb.intersects(r) for r in rects):
                                clip = tb + (-10, -14, 10, 10)  # small pad incl header
                                break
                    except Exception:  # noqa: BLE001
                        clip = None
                # 2) fallback: a band around the quote, reaching well up for the header.
                if clip is None and rects:
                    y0 = max(0, min(r.y0 for r in rects) - 230)
                    y1 = min(page.rect.height, max(r.y1 for r in rects) + 60)
                    clip = fitz.Rect(0, y0, page.rect.width, y1)
                elif clip is None:
                    clip = page.rect  # whole page
                clip = clip & page.rect  # keep within the page
                # Guard against a too-small crop: a narrow cell hit (e.g. "CUADRO 4" with no
                # caption) yields an unreviewable thumbnail. Widen to a full-width band around
                # the hits (or the whole page) so the reviewer gets context. (2026-06-23 inab.)
                if clip.width < page.rect.width * 0.45 or clip.height < 90:
                    if rects:
                        y0 = max(0, min(r.y0 for r in rects) - 260)
                        y1 = min(page.rect.height, max(r.y1 for r in rects) + 120)
                        clip = fitz.Rect(0, y0, page.rect.width, y1) & page.rect
                    else:
                        clip = page.rect
                # Detect a rotated (sideways) table so we can render it upright. Wide
                # landscape tables on a portrait page have vertical writing direction.
                rot = 0
                try:
                    td = page.get_text("dict", clip=clip)
                    vert = horiz = 0
                    ysign = 0.0
                    for b in td.get("blocks", []):
                        for ln in b.get("lines", []):
                            dx, dy = ln.get("dir", (1.0, 0.0))
                            if abs(dy) > abs(dx):
                                vert += 1
                                ysign += dy
                            else:
                                horiz += 1
                    if vert > horiz and vert > 0:
                        # dir (0,-1) reads bottom→top → rotate 90; (0,1) → 270
                        rot = 90 if ysign < 0 else 270
                except Exception:  # noqa: BLE001
                    rot = 0
                # an explicit ?rot= override from the client wins (manual correction)
                _rq = parse_qs(urlparse(self.path).query).get("rot", [""])[0]
                if _rq in ("0", "90", "180", "270"):
                    rot = int(_rq)
                # render at higher resolution (~2600px on the long edge) for readability
                long_edge = max(clip.width, clip.height, 1.0)
                scale = max(1.5, min(4.0, 2600.0 / long_edge))
                mat = fitz.Matrix(scale, scale)
                if rot:
                    mat = mat.prerotate(rot)
                pix = page.get_pixmap(matrix=mat, clip=clip)
                data = pix.tobytes("png")
                doc.close()
            except Exception as e:  # noqa: BLE001
                return self._json(500, {"error": f"crop failed: {e}"})
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
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
                byrev[rev] = {
                    "decision": dec,
                    "reason": payload.get("reason", ""),
                    "note": payload.get("note", ""),
                }
            if not byrev:
                store.pop(eid, None)
            _save(store)
            decided = sum(
                1 for e in store.values() for r in e.values() if r.get("decision")
            )
            return self._json(200, {"ok": True, "decided": decided})

        if self.path == "/api/apply":
            store = _load()
            if not store:
                return self._json(200, {"applied": 0, "message": "no decisions"})
            from nbs_ruralscan.schema_tools.review import apply_decisions
            from nbs_ruralscan.schema_tools.generate import generate

            # CONSENSUS: commit a flag when the reviewers who decided it AGREE; a
            # disagreement is a conflict (left pending). Applied decisions are NOT deleted
            # from the store — they persist as the review record so they can be viewed,
            # re-reviewed by others, and a later disagreeing review re-opens the conflict.
            decisions, conflicts = {}, []
            for eid, byrev in store.items():
                decs = {
                    rv: v
                    for rv, v in byrev.items()
                    if (v.get("decision") or "").strip()
                }
                if not decs:
                    continue
                vals = set(v["decision"] for v in decs.values())
                if len(vals) == 1:
                    decisions[eid] = {
                        "decision": next(iter(vals)),
                        "reason": ";".join(
                            sorted(
                                {
                                    v.get("reason", "")
                                    for v in decs.values()
                                    if v.get("reason")
                                }
                            )
                        ),
                        "note": " | ".join(
                            v.get("note", "") for v in decs.values() if v.get("note")
                        ),
                        "reviewer": ",".join(sorted(decs.keys())),
                    }
                else:
                    conflicts.append(
                        {
                            "evidence_id": eid,
                            "reviews": {rv: v["decision"] for rv, v in decs.items()},
                        }
                    )
            if not decisions:
                return self._json(
                    200,
                    {
                        "applied": 0,
                        "ok": True,
                        "conflicts": conflicts,
                        "message": "no agreed units to apply",
                    },
                )
            try:
                res = apply_decisions(decisions, "consensus")
                generate(ROOT / "schema")
            except Exception as e:  # noqa: BLE001
                return self._json(500, {"error": str(e)})
            for eid in decisions:  # mark applied; keep the record (history + re-review)
                for rv in store.get(eid, {}):
                    store[eid][rv]["applied"] = True
            _save(store)
            return self._json(200, {"ok": True, **res, "conflicts": conflicts})

        if self.path == "/api/challenge":
            # A reviewer records a decision on an already-applied unit. If it disagrees
            # with the existing decision(s), it's a conflict -> auto-reopen into AI-flagged
            # for consensus. If it agrees, just record it.
            eid = payload.get("evidence_id")
            dec = (payload.get("decision") or "").strip()
            rev = (payload.get("reviewer") or "reviewer").strip() or "reviewer"
            if not eid or dec not in ("ok", "drop"):
                return self._json(
                    400, {"error": "evidence_id + decision(ok|drop) required"}
                )
            store = _load()
            byrev = store.setdefault(eid, {})
            byrev[rev] = {
                "decision": dec,
                "reason": payload.get("reason", ""),
                "note": payload.get("note", ""),
                "applied": False,
            }
            decs = {
                r: v["decision"]
                for r, v in byrev.items()
                if (v.get("decision") or "").strip()
            }
            conflict = len(set(decs.values())) > 1
            _save(store)
            reopened = 0
            if conflict:
                from nbs_ruralscan.schema_tools.review import reopen_units
                from nbs_ruralscan.schema_tools.generate import generate

                try:
                    res = reopen_units([eid], rev)
                    generate(ROOT / "schema")
                    reopened = res.get("reopened", 0)
                except Exception as e:  # noqa: BLE001
                    return self._json(500, {"error": str(e)})
            return self._json(
                200,
                {
                    "ok": True,
                    "conflict": conflict,
                    "reopened": reopened,
                    "reviews": decs,
                },
            )

        if self.path == "/api/reopen":
            eids = payload.get("evidence_ids") or (
                [payload["evidence_id"]] if payload.get("evidence_id") else []
            )
            rev = (payload.get("reviewer") or "reviewer").strip() or "reviewer"
            if not eids:
                return self._json(400, {"error": "evidence_id(s) required"})
            from nbs_ruralscan.schema_tools.review import reopen_units
            from nbs_ruralscan.schema_tools.generate import generate

            try:
                res = reopen_units(eids, rev)
                generate(ROOT / "schema")
            except Exception as e:  # noqa: BLE001
                return self._json(500, {"error": str(e)})
            return self._json(200, {"ok": True, **res})

        if self.path == "/api/clear":
            # Reset to-review. Scoped to ONE reviewer by default (you can't wipe others'
            # pending work); a full wipe requires reviewer="*". Always backs up first.
            rev = (payload.get("reviewer") or "").strip()
            store = _load()
            if STORE.exists():
                (STORE.parent / "decisions.bak.json").write_text(
                    STORE.read_text(encoding="utf-8")
                )
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
            return self._json(
                400, {"error": "reviewer required (use '*' to clear all)"}
            )

        return self._json(404, {"error": "not found"})

    def log_message(self, *a):  # quieter  # ty: ignore[invalid-method-override]
        pass


def main() -> int:
    import sys

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    handler = partial(Handler, directory=str(DOCS))
    srv = ThreadingHTTPServer(("127.0.0.1", port), handler)
    print(
        f"QA/QC review server → http://localhost:{port}/dashboard.html  (Ctrl-C to stop)"
    )
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
