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

import csv as _csv_mod
import json
import os
import shutil
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOCS = ROOT / "docs"
STORE = ROOT / "pipeline" / "review" / "decisions.json"
CACHE = ROOT / ".cache" / "corpus"


# Local OneDrive mirror of the SharePoint library. SRC.library_path is relative to
# .../ClimateActionNetZero/1_Projects/ (e.g. "D591_Rural-Scan_NBS/2_Technical_&_Data/library/<nbs>/x.pdf").
# Per-user OneDrive folder name varies → override with NBS_LIBRARY_ROOT.
def _library_root() -> Path | None:
    env = os.environ.get("NBS_LIBRARY_ROOT")
    if env:
        return Path(env).expanduser()
    # best-effort default: Pete's CGIAR OneDrive mount
    default = (
        Path.home()
        / "Library/CloudStorage/OneDrive-CGIAR/ClimateActionNetZero/1_Projects"
    )
    return default if default.exists() else None


def _src_field(source_id: str, field: str) -> str:
    """Look up one field for a source_id from the SRC register CSV."""
    src_csv = ROOT / "schema" / "registers" / "SRC_source_register.csv"
    if not src_csv.exists():
        return ""
    with src_csv.open(newline="", encoding="utf-8") as f:
        for r in _csv_mod.DictReader(f):
            if r.get("source_id") == source_id:
                return (r.get(field) or "").strip()
    return ""


def _github_raw_url(blob_url: str) -> str | None:
    # https://github.com/<owner>/<repo>/blob/<ref>/<path...>  ->
    # https://raw.githubusercontent.com/<owner>/<repo>/<ref>/<path...>
    import re as _re

    m = _re.match(
        r"^https://github\.com/([^/]+)/([^/]+)/blob/(.+)$", (blob_url or "").strip()
    )
    if not m:
        return None
    return f"https://raw.githubusercontent.com/{m.group(1)}/{m.group(2)}/{m.group(3)}"


def _ensure_code_snapshot(source_id: str) -> Path | None:
    """Return a local cached text snapshot for a code source_id, fetching from
    GitHub raw (commit-pinned SRC.url blob URL) on cache miss."""
    # already cached? (.txt / .html / .md — match the existing resolution order)
    for ext in (".txt", ".html", ".md"):
        p = CACHE / (source_id + ext)
        if p.exists():
            return p
    # not cached -> try GitHub raw from SRC.url (commit-pinned blob URL)
    url = _src_field(source_id, "url")
    raw = _github_raw_url(url)
    if not raw:
        return None
    import urllib.request

    req = urllib.request.Request(
        raw, headers={"User-Agent": "nbs-ruralscan-review-server"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status != 200:
                return None
            data = resp.read(4_000_000)  # 4 MB cap
    except Exception:
        return None
    try:
        CACHE.mkdir(parents=True, exist_ok=True)
        dest = CACHE / (source_id + ".txt")
        dest.write_bytes(data)
        return dest
    except Exception:
        return None


def _resolve_pdf(source_id: str) -> Path | None:
    """Return a local cached PDF for source_id, hydrating from the OneDrive library on cache miss."""
    cached = CACHE / (source_id + ".pdf")
    if cached.exists():
        return cached
    lib_path = _src_field(source_id, "library_path")
    if not lib_path:
        return None
    root = _library_root()
    if not root:
        return None
    # library_path may be posix-style with & etc.; join verbatim
    src_pdf = root / lib_path
    if not src_pdf.exists():
        return None
    try:
        CACHE.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_pdf, cached)
        return cached
    except Exception:
        return None


def render_region_png(
    pdf_path: Path, quote: str, page: int | None, rot: int = 0
) -> bytes | None:
    """Render a highlighted page-region screengrab (PNG bytes) around ``quote`` on ``page``.

    Opens the PDF, searches for the quote span, computes a clip rect (preferring the
    detected table bbox incl. its header row, falling back to a band around the hits or
    the whole page), auto-detects a sideways/rotated table, draws amber highlight annots
    over the located quote rects, and renders to PNG. A search miss with no clip is fine
    (whole page). Returns ``None`` only on a hard failure (no such file / no page / render
    error). ``rot`` (0/90/180/270) forces a rotation override; 0 = auto-detect.
    """
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(str(pdf_path))
        if len(doc) == 0:
            doc.close()
            return None
        pno = page if (page and page > 0) else 1
        pg = doc[max(0, min(pno - 1, len(doc) - 1))]
        q = " ".join((quote or "").split())
        # locate the WHOLE quote span: search several snippets across it and union
        # all hit rects (a table quote spans caption -> header -> data rows).
        rects = []
        for i in range(0, max(1, len(q)), 38):
            snip = q[i : i + 30].strip()
            if len(snip) >= 8:
                rects += pg.search_for(snip)
        clip = None
        # 1) prefer the FULL detected table bbox (includes its column-header row,
        #    which a quote deep in the table sits far below).
        if rects:
            try:
                for t in pg.find_tables().tables or []:
                    tb = fitz.Rect(t.bbox)
                    if any(tb.intersects(r) for r in rects):
                        clip = tb + (-10, -14, 10, 10)  # small pad incl header
                        break
            except Exception:  # noqa: BLE001
                clip = None
        # 2) fallback: a band around the quote, reaching well up for the header.
        if clip is None and rects:
            y0 = max(0, min(r.y0 for r in rects) - 230)
            y1 = min(pg.rect.height, max(r.y1 for r in rects) + 60)
            clip = fitz.Rect(0, y0, pg.rect.width, y1)
        elif clip is None:
            clip = pg.rect  # whole page
        clip = clip & pg.rect  # keep within the page
        # Guard against a too-small crop: a narrow cell hit (e.g. "CUADRO 4" with no
        # caption) yields an unreviewable thumbnail. Widen to a full-width band around
        # the hits (or the whole page) so the reviewer gets context. (2026-06-23 inab.)
        if clip.width < pg.rect.width * 0.45 or clip.height < 90:
            if rects:
                y0 = max(0, min(r.y0 for r in rects) - 260)
                y1 = min(pg.rect.height, max(r.y1 for r in rects) + 120)
                clip = fitz.Rect(0, y0, pg.rect.width, y1) & pg.rect
            else:
                clip = pg.rect
        # Detect a rotated (sideways) table so we can render it upright. Wide
        # landscape tables on a portrait page have vertical writing direction.
        det_rot = 0
        try:
            td = pg.get_text("dict", clip=clip)
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
                det_rot = 90 if ysign < 0 else 270
        except Exception:  # noqa: BLE001
            det_rot = 0
        # an explicit rot override wins (manual correction)
        use_rot = rot if rot in (0, 90, 180, 270) and rot else det_rot
        # render at higher resolution (~2600px on the long edge) for readability
        long_edge = max(clip.width, clip.height, 1.0)
        scale = max(1.5, min(4.0, 2600.0 / long_edge))
        mat = fitz.Matrix(scale, scale)
        if use_rot:
            mat = mat.prerotate(use_rot)
        # highlight the located quote span(s) so the reviewer sees the exact
        # passage inside the rendered region (rendered into the pixmap directly).
        if rects:
            try:
                for _hr in rects:
                    _an = pg.add_highlight_annot(_hr)
                    _an.set_colors(stroke=(1.0, 0.86, 0.24))  # amber
                    _an.update()
            except Exception:  # noqa: BLE001
                pass
        pix = pg.get_pixmap(matrix=mat, clip=clip)
        data = pix.tobytes("png")
        doc.close()
        return data
    except Exception:  # noqa: BLE001
        return None


def _load() -> dict:
    if STORE.exists():
        raw = STORE.read_bytes()
        try:
            return json.loads(raw.decode("utf-8"))
        except UnicodeDecodeError:
            # decisions.json is gitignored (per-reviewer, local) so `git restore` can't fix a
            # stray Windows-1252 byte in it. Self-heal: re-decode cp1252 → rewrite UTF-8.
            try:
                txt = raw.decode("cp1252")
                STORE.write_text(txt, encoding="utf-8")
                print(
                    "⚠  decisions.json had a non-UTF-8 byte — re-encoded cp1252→UTF-8 in place."
                )
                return json.loads(txt)
            except Exception:
                return {}
        except Exception:
            return {}
    return {}


def _save(d: dict) -> None:
    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps(d, indent=2), encoding="utf-8")


def _git_version() -> dict:
    """Local HEAD vs origin/main, for the dashboard 'new version — pull' banner (#191).

    `git ls-remote` reads the remote tip without a full fetch (~1s). `behind` is true only
    when the remote main commit is NOT already in local history (the reviewer is missing
    commits) — so being AHEAD (unpushed work) or up-to-date does not trigger it. Any git
    failure (no network, detached, not a clone) reports `known=false` and never raises.
    """
    import subprocess

    def _run(args: list[str]) -> tuple[int, str]:
        try:
            p = subprocess.run(
                args,
                cwd=str(ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=8,
            )
            return p.returncode, p.stdout.strip()
        except Exception:  # noqa: BLE001
            return 1, ""

    _, local = _run(["git", "rev-parse", "HEAD"])
    rc, out = _run(["git", "ls-remote", "origin", "refs/heads/main"])
    remote = out.split()[0] if (rc == 0 and out) else ""
    behind = False
    if local and remote and local != remote:
        # remote tip already in our history? if not (or we don't have it), we're behind.
        anc, _ = _run(["git", "merge-base", "--is-ancestor", remote, "HEAD"])
        behind = anc != 0
    return {
        "local": local[:12],
        "remote": remote[:12],
        "behind": behind,
        "known": bool(local and remote),
    }


def _resolve_bash() -> str | None:
    """Locate a bash interpreter for /api/submit. On Windows `bash` is usually not on PATH
    even when Git for Windows (which bundles it) is installed, so `subprocess.run(["bash",...])`
    fails with WinError 2 (the submit step Namita hit). Fall back to the standard Git install
    locations. Returns the executable path, or None if none is found."""
    found = shutil.which("bash")
    if found:
        return found
    candidates: list[Path] = []
    for base in (
        os.environ.get("ProgramFiles"),
        os.environ.get("ProgramFiles(x86)"),
        os.environ.get("LOCALAPPDATA"),
    ):
        if base:
            b = Path(base)
            candidates += [
                b / "Git" / "bin" / "bash.exe",
                b / "Git" / "usr" / "bin" / "bash.exe",
                b / "Programs" / "Git" / "bin" / "bash.exe",
            ]
    return next((str(c) for c in candidates if c.exists()), None)


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
        if self.path == "/api/version":
            return self._json(200, _git_version())
        if self.path == "/api/state":
            return self._json(200, {"decisions": _load()})
        if self.path == "/api/gaps":
            gaps_csv = ROOT / "pipeline" / "metrics" / "gaps.csv"
            rows = []
            if gaps_csv.exists():
                with gaps_csv.open(newline="", encoding="utf-8") as f:
                    rows = list(_csv_mod.DictReader(f))
            return self._json(200, {"gaps": rows})
        if self.path.startswith("/api/code"):
            # return the CODE lines around a file_line locator (tool/methodology sources).
            from urllib.parse import urlparse, parse_qs
            import csv as _csv
            import re as _re

            qs = parse_qs(urlparse(self.path).query)
            eid = qs.get("eid", [""])[0]
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
            if (row.get("locator_type") or "").strip() != "file_line":
                return self._json(400, {"error": "not a code (file_line) source"})
            loc = (row.get("locator") or "").strip()
            # path is everything before the last ':L'; the line spec follows it.
            path = loc
            target_start = 1
            target_end = 1
            idx = loc.rfind(":L")
            if idx >= 0:
                path = loc[:idx]
                spec = loc[idx + 2 :]
                m = _re.match(r"(\d+)(?:\s*-\s*(\d+))?", spec)
                if m:
                    target_start = int(m.group(1))
                    target_end = int(m.group(2)) if m.group(2) else target_start
            if target_end < target_start:
                target_start, target_end = target_end, target_start
            # resolve the cached text snapshot (.txt -> .html -> .md), fetching
            # from GitHub raw at the commit-pinned SRC.url on cache miss.
            sid = row["source_id"]
            snap = _ensure_code_snapshot(sid)
            if snap is None:
                return self._json(
                    404,
                    {
                        "error": "no cached snapshot and GitHub fetch failed "
                        "(offline, or SRC.url not a github blob URL)"
                    },
                )
            text = snap.read_text(encoding="utf-8", errors="replace")
            lines = text.split("\n")
            nlines = len(lines)
            try:
                ctx = int(qs.get("ctx", ["14"])[0])
            except ValueError:
                ctx = 14
            ctx = max(0, min(80, ctx))
            if target_start > nlines:
                target_start = min(target_start, nlines)
            if target_end > nlines:
                target_end = nlines
            window_start = max(1, target_start - ctx)
            window_end = min(nlines, target_end + ctx)
            out_lines = [
                {"n": i, "text": lines[i - 1]}
                for i in range(window_start, window_end + 1)
            ]
            # language guess
            pl = path.lower()
            if pl.endswith(".py"):
                lang = "python"
            elif pl.endswith((".r",)):
                lang = "r"
            elif pl.endswith((".js",)):
                lang = "javascript"
            else:
                looks_js = bool(_re.search(r"\bvar\b|\bfunction\b", text))
                lang = "javascript" if looks_js else "text"
            return self._json(
                200,
                {
                    "ok": True,
                    "path": path,
                    "commit": (row.get("commit_sha") or "").strip(),
                    "lang": lang,
                    "start": window_start,
                    "end": window_end,
                    "target_start": target_start,
                    "target_end": target_end,
                    "n_lines": nlines,
                    "lines": out_lines,
                },
            )
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
            pdf = _resolve_pdf(row["source_id"])
            if not pdf:
                return self._json(
                    404,
                    {
                        "error": "no cached pdf; set NBS_LIBRARY_ROOT or hydrate the corpus (scripts/hydrate-corpus.py)"
                    },
                )
            pno = int(row["page"]) if (row.get("page") or "").isdigit() else None
            _rq = parse_qs(urlparse(self.path).query).get("rot", [""])[0]
            rot = int(_rq) if _rq in ("0", "90", "180", "270") else 0
            try:
                data = render_region_png(pdf, row.get("quote") or "", pno, rot)
            except Exception as e:  # noqa: BLE001
                return self._json(500, {"error": f"crop failed: {e}"})
            if data is None:
                return self._json(
                    500, {"error": "crop failed: could not render region"}
                )
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
            pdf = _resolve_pdf(sid)
            if not pdf:
                return self._json(
                    404,
                    {
                        "error": "no cached pdf; set NBS_LIBRARY_ROOT or hydrate the corpus (scripts/hydrate-corpus.py)"
                    },
                )
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
                entry = {
                    "decision": dec,
                    "reason": payload.get("reason", ""),
                    "note": payload.get("note", ""),
                }
                # reclassify (species/crop) carries the target claim_scope + taxon
                if payload.get("taxon"):
                    entry["taxon"] = str(payload.get("taxon")).strip()
                if payload.get("claim_scope"):
                    entry["claim_scope"] = str(payload.get("claim_scope")).strip()
                byrev[rev] = entry
            if not byrev:
                store.pop(eid, None)
            _save(store)
            decided = sum(
                1 for e in store.values() for r in e.values() if r.get("decision")
            )
            return self._json(200, {"ok": True, "decided": decided})

        if self.path == "/api/gap":
            # Report MISSING evidence — a variable/figure/table a reviewer expected but that was
            # never extracted. Appended to the in-repo gaps register so it's tracked + queryable
            # and can feed a re-extraction sweep. Not an EV row (there's no source quote yet).
            import datetime as _dt

            cols = [
                "gap_id",
                "date",
                "reporter",
                "nbs_id",
                "suitability_family_id",
                "table",
                "source_id",
                "location",
                "variable",
                "note",
                "status",
            ]
            g = payload or {}
            variable = (g.get("variable") or "").strip()
            note = (g.get("note") or "").strip()
            if not (variable or note):
                return self._json(
                    400, {"error": "a gap needs at least a variable or a note"}
                )
            gaps_csv = ROOT / "pipeline" / "metrics" / "gaps.csv"
            gaps_csv.parent.mkdir(parents=True, exist_ok=True)
            existing = []
            if gaps_csv.exists():
                with gaps_csv.open(newline="", encoding="utf-8") as f:
                    existing = list(_csv_mod.DictReader(f))
            row = {c: "" for c in cols}
            row.update(
                {
                    "gap_id": f"gap_{len(existing) + 1:04d}",
                    "date": _dt.date.today().isoformat(),
                    "reporter": (g.get("reporter") or "reviewer").strip(),
                    "nbs_id": (g.get("nbs_id") or "").strip(),
                    "suitability_family_id": (
                        g.get("suitability_family_id") or ""
                    ).strip(),
                    "table": (g.get("table") or "").strip(),
                    "source_id": (g.get("source_id") or "").strip(),
                    "location": (g.get("location") or "").strip(),
                    "variable": variable,
                    "note": note,
                    "status": "open",
                }
            )
            need_header = not gaps_csv.exists()
            with gaps_csv.open("a", newline="", encoding="utf-8") as f:
                w = _csv_mod.DictWriter(f, fieldnames=cols)
                if need_header:
                    w.writeheader()
                w.writerow(row)
            return self._json(200, {"ok": True, "gap_id": row["gap_id"]})

        if self.path == "/api/apply":
            # Preflight: scan every file the Apply path reads for a stray non-UTF-8 byte / CRLF
            # BEFORE apply_decisions + generate run — so the popup NAMES the offending file
            # (incl. gitignored .cache snapshots) instead of a cryptic 'codec can't decode 0xNN'.
            enc = integrity_problems(_pipeline_text_files())
            if enc:
                return self._json(
                    400,
                    {
                        "error": "Encoding/line-ending problem — fix these before Apply:\n"
                        + "\n".join(enc)
                    },
                )
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

        if self.path == "/api/submit":
            # Ship the reviewed decisions to main with no terminal: run the same vetted flow
            # as scripts/submit-review.sh (branch off latest main → replay decisions → regen →
            # commit registers → push → open PR → --auto squash-merge on green CI). This is a
            # LOCAL tool on the reviewer's machine, so it uses their git/gh auth.
            import re as _re
            import subprocess

            reviewer = (payload.get("reviewer") or "reviewer").strip() or "reviewer"
            title = (
                payload.get("title") or f"qaqc: review decisions ({reviewer})"
            ).strip()
            # Fail fast on interactive git/gh auth prompts (no TTY here → they'd otherwise
            # block up to the timeout). Disable every credential/askpass prompt.
            _env = {
                **os.environ,
                "GIT_TERMINAL_PROMPT": "0",
                "GIT_ASKPASS": "",
                "SSH_ASKPASS": "",
                "GCM_INTERACTIVE": "Never",
                "GH_NO_UPDATE_NOTIFIER": "1",
                "GH_PROMPT_DISABLED": "1",
            }
            bash = _resolve_bash()
            if not bash:
                return self._json(
                    500,
                    {
                        "ok": False,
                        "error": "Submit needs bash and none was found. Your decisions ARE "
                        "applied + saved locally. On Windows, install Git for Windows (it "
                        "bundles bash) then click Apply again, or run from Git Bash: "
                        "`bash scripts/submit-review.sh <your-handle> --auto`. "
                        "(A bash-free submit is the follow-up.)",
                    },
                )
            try:
                proc = subprocess.run(
                    [bash, "scripts/submit-review.sh", reviewer, title, "--auto"],
                    cwd=str(ROOT),
                    capture_output=True,
                    text=True,
                    env=_env,
                    stdin=subprocess.DEVNULL,
                    timeout=180,
                )
            except subprocess.TimeoutExpired:
                return self._json(
                    500,
                    {
                        "ok": False,
                        "error": "submit timed out (git/gh auth?). Decisions ARE applied locally. Check `gh auth status` and git push rights, then use scripts/submit-review.sh.",
                    },
                )
            except Exception as e:  # noqa: BLE001
                return self._json(500, {"ok": False, "error": str(e)})
            out = (proc.stdout + "\n" + proc.stderr).strip()
            m = _re.search(r"https://github\.com/\S+/pull/\d+", out)
            return self._json(
                200 if proc.returncode == 0 else 500,
                {
                    "ok": proc.returncode == 0,
                    "pr_url": m.group(0) if m else "",
                    "output": out[-4000:],
                },
            )

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


def _gitignored(p: Path) -> bool:
    """decisions.json + the local corpus cache are gitignored — `git restore` won't touch them."""
    s = str(p).replace("\\", "/")
    return p.name == "decisions.json" or "/.cache/" in s


def _pipeline_text_files() -> list[Path]:
    """Every text file the Apply path reads (apply_decisions + generate + the validate gate) —
    including the local / gitignored ones a `git restore` can't fix (the .cache/corpus
    snapshots the guardrail reads). A stray non-UTF-8 byte in ANY of these makes Apply fail
    with a cryptic 'utf-8 codec can't decode 0xNN'. decisions.json is excluded here because
    `_load` self-heals it; it's covered by the startup warning instead."""
    reg = ROOT / "schema" / "registers"
    files = [
        reg / "EV_evidence_register.csv",
        reg / "SRC_source_register.csv",
        reg / "VONT_variable_ontology.csv",
        reg / "FAM_family_registry.csv",
        reg / "BIND_dataset_binding.csv",
        reg / "TOOL_tool_registry.csv",
        reg / "SRCH_search_register.csv",
        ROOT / "pipeline" / "metrics" / "review_log.csv",
    ]
    files += sorted((ROOT / "methodology" / "discovery_logs").glob("*.md"))
    cache = ROOT / ".cache" / "corpus"
    if cache.exists():
        files += sorted(
            p for p in cache.iterdir() if p.suffix in {".txt", ".html", ".md"}
        )
    return files


def integrity_problems(targets: list[Path]) -> list[str]:
    """One problem string per non-UTF-8 / CRLF file (empty = all clean). The fix hint is
    path-aware: tracked files → `git restore`; gitignored (decisions.json / .cache) → re-encode,
    since restore can't reach them."""
    problems = []
    for p in targets:
        if not p.exists():
            continue
        try:
            rel = p.relative_to(ROOT)
        except ValueError:
            rel = p.name
        raw = p.read_bytes()
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as e:
            if _gitignored(p):
                fix = (
                    "re-encode it: uv run python -c \"import pathlib; q=pathlib.Path(r'"
                    f"{rel}'); q.write_text(q.read_bytes().decode('cp1252'), encoding='utf-8')\""
                )
            else:
                fix = f"git restore {rel}"
            problems.append(
                f"  ✗ {rel} — NOT valid UTF-8 (byte 0x{raw[e.start]:02x} at position {e.start}); "
                f"a stray Windows-1252 byte. Fix: {fix}"
            )
        else:
            if b"\r\n" in raw and not _gitignored(p):
                problems.append(
                    f"  ✗ {rel} — has CRLF line endings (Windows). "
                    f"Fix: git restore {rel}  (or set: git config core.autocrlf false)"
                )
    return problems


def _startup_integrity_check() -> None:
    """Warn loudly at startup if a register CSV is non-UTF-8 or CRLF — the recurring
    Windows failure (#90/#104/#118/#123): a stray cp1252 byte or CRLF working copy makes
    'Apply decisions & rebuild' fail with a cryptic 'utf-8 codec can't decode 0xe7'. This
    catches it BEFORE any click, names the file, and gives the one-line fix. The server
    itself never writes these CSVs on startup — a 'modified' git diff is git autocrlf
    converting line endings on checkout, not the server."""
    problems = integrity_problems(_pipeline_text_files() + [STORE])
    if problems:
        print("\n" + "=" * 78)
        print("⚠  REGISTER ENCODING/LINE-ENDING PROBLEM — Apply will fail until fixed:")
        print("\n".join(problems))
        print(
            "\nYour LOCAL copy diverged from the committed (clean UTF-8/LF) register — a\n"
            "Windows cp1252/CRLF artefact, not the server. The committed files are clean;\n"
            "the fixes above re-sync them. Decisions live in pipeline/review/decisions.json,\n"
            "so `git restore` loses no review work. Also set: git config core.autocrlf false"
        )
        print("=" * 78 + "\n")
    else:
        print("✓ register integrity OK (UTF-8, LF).")


def main() -> int:
    import sys

    # Windows cp1252 stdout can't encode the ⚠ ✓ ✗ → ═ glyphs the startup prints use, so
    # print() raises UnicodeEncodeError and the process exits 1 BEFORE binding the port —
    # the server never starts (#189). Force UTF-8 on the streams first (best-effort: a
    # redirected pipe may not be reconfigurable).
    for _stream in (sys.stdout, sys.stderr):
        _reconfig = getattr(_stream, "reconfigure", None)
        if _reconfig is not None:
            try:
                _reconfig(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass

    _startup_integrity_check()
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
