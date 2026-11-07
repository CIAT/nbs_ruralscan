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

import argparse
import csv as _csv_mod
import hashlib
import io
import json
import os
import threading
from dataclasses import replace
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from nbs_ruralscan.ingest.integrity import validate_source_id
from nbs_ruralscan.ingest.source_publication import SourceSnapshot
from nbs_ruralscan.schema_tools.publication import PublicationRecoveryError

from . import clarifications, review_local

_COMPILER_ROOT = Path(__file__).resolve().parents[3]
ROOT = _COMPILER_ROOT
DOCS = ROOT / "docs"
STORE = ROOT / "pipeline" / "review" / "decisions.json"
CACHE = ROOT / ".cache" / "corpus"
# Serialize this server process's preview cache misses; other processes remain
# independent writers and are protected by publication drift checks.
_HYDRATION_LOCK = threading.RLock()
# One in-process lock covers requests that read or change linked review state.
_STORE_LOCK = clarifications.LOCK


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


def _source_field_input(
    source_id: str, field: str, sources: Path
) -> tuple[str, SourceSnapshot]:
    """Bind the selected field to unchanged source-register bytes."""
    snapshot = SourceSnapshot.capture([sources])
    state = snapshot.states[0]
    if state is None:
        return "", snapshot
    raw = sources.read_bytes()
    if hashlib.sha256(raw).hexdigest() != state[0]:
        raise ValueError("Source register changed while reading")
    snapshot.assert_unchanged()
    rows = _csv_mod.DictReader(io.StringIO(raw.decode("utf-8"), newline=""))
    for row in rows:
        if row.get("source_id") == source_id:
            return (row.get(field) or "").strip(), snapshot
    return "", snapshot


def _ensure_code_snapshot(
    source_id: str, *, sources: Path | None = None, corpus: Path | None = None
) -> Path | None:
    """Return a local cached text snapshot for a code source_id, fetching from
    GitHub raw (commit-pinned SRC.url blob URL) on cache miss."""
    with _HYDRATION_LOCK:
        import urllib.request

        try:
            validate_source_id(source_id)
            corpus = Path(corpus) if corpus is not None else CACHE
            sources = (
                Path(sources)
                if sources is not None
                else ROOT / "schema/registers/SRC_source_register.csv"
            )
            # Keep the existing .txt/.html/.md precedence and guard every candidate.
            candidates = [
                corpus / (source_id + ext) for ext in (".txt", ".html", ".md")
            ]
            cached = SourceSnapshot.capture(candidates)
            for path, state in zip(candidates, cached.states):
                if state is not None:
                    return path
            dest = candidates[0]
            target = SourceSnapshot.capture([dest])
            if str(dest.resolve()).casefold() == str(sources.resolve()).casefold():
                return None
            url, registry = _source_field_input(source_id, "url", sources)
            raw = _github_raw_url(url)
            if not raw:
                return None
            req = urllib.request.Request(
                raw, headers={"User-Agent": "nbs-ruralscan-review-server"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status != 200:
                    return None
                data = resp.read(4_000_000)  # 4 MB cap

            def validate(stage):
                registry.assert_unchanged()
                cached.assert_unchanged()
                if (stage / dest.name).read_bytes() != data:
                    raise ValueError("Code snapshot differs from fetched bytes")

            target.publish({dest: data}, validate, create_only=True)
            return dest
        except PublicationRecoveryError:
            raise
        except Exception:
            return None


def _resolve_pdf(
    source_id: str,
    *,
    sources: Path | None = None,
    corpus: Path | None = None,
    library: Path | None = None,
) -> Path | None:
    """Return a local cached PDF for source_id, hydrating from the OneDrive library on cache miss."""
    with _HYDRATION_LOCK:
        try:
            validate_source_id(source_id)
            corpus = Path(corpus) if corpus is not None else CACHE
            sources = (
                Path(sources)
                if sources is not None
                else ROOT / "schema/registers/SRC_source_register.csv"
            )
            cached = corpus / (source_id + ".pdf")
            target = SourceSnapshot.capture([cached])
            if target.states[0] is not None:
                return cached
            if str(cached.resolve()).casefold() == str(sources.resolve()).casefold():
                return None
            lib_path, registry = _source_field_input(source_id, "library_path", sources)
            if not lib_path:
                return None
            root = Path(library) if library is not None else _library_root()
            if root is None:
                return None
            relative = Path(lib_path)
            if relative.is_absolute() or ".." in relative.parts or "\\" in lib_path:
                return None
            src_pdf = root / relative
            if not src_pdf.resolve().is_relative_to(root.resolve()):
                return None
            if str(src_pdf.resolve()).casefold() == str(cached.resolve()).casefold():
                return None
            source = SourceSnapshot.capture([src_pdf])
            state = source.states[0]
            if state is None:
                return None
            data = src_pdf.read_bytes()
            if hashlib.sha256(data).hexdigest() != state[0]:
                raise ValueError("Library PDF changed while reading")

            def validate(stage):
                registry.assert_unchanged()
                source.assert_unchanged()
                if (stage / cached.name).read_bytes() != data:
                    raise ValueError("Cached PDF differs from library bytes")

            target.publish({cached: data}, validate, create_only=True)
            return cached
        except PublicationRecoveryError:
            raise
        except Exception:
            return None


def render_region_png(
    pdf_path: Path,
    quote: str,
    page: int | None,
    rot: int = 0,
    *,
    full_page: bool = False,
) -> bytes | None:
    """Render a highlighted page-region screengrab (PNG bytes) around ``quote`` on ``page``.

    Opens the PDF, searches for the quote span, computes a clip rect (preferring the
    detected table bbox incl. its header row, falling back to a band around the hits or
    the whole page), auto-detects a sideways/rotated table, draws amber highlight annots
    over the located quote rects, and renders to PNG. A search miss with no clip is fine
    (whole page). Returns ``None`` only on a hard failure (no such file / no page / render
    error). ``full_page`` retains captions and both columns without cropping. ``rot`` (0/90/180/270) forces a rotation override; 0 = auto-detect.
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
        if full_page:
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


def _clarification_paths():
    return replace(
        clarifications.ClarificationPaths.from_root(ROOT),
        decisions=STORE,
        pending=STORE.with_name("clarifications.json"),
    )


def _load() -> dict:
    with _STORE_LOCK:
        return review_local.load_store(STORE)


def _decision_snapshot():
    snapshot = SourceSnapshot.capture([STORE])
    store, _ = review_local.read_decisions(STORE)
    snapshot.assert_unchanged()
    return store, snapshot


def _save(d: dict, *, path: Path) -> None:
    """Write the private decision copy for a staged register action."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".tmp.{os.getpid()}")
    tmp.write_text(json.dumps(d, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def _stage_review_action(mutate, snapshot):
    from nbs_ruralscan.schema_tools.review import ReviewFiles, stage_review_records

    def checked(files, staged_store):
        # Bind the consensus/reopen calculation to the bytes the publisher captured.
        snapshot.assert_unchanged()
        return mutate(files, staged_store)

    return stage_review_records(
        checked, files=ReviewFiles.from_root(ROOT), decision_store=STORE
    )


def _review_rebuild_error(error: Exception, *, full: bool) -> dict:
    import shlex

    method = "generate" if full else "refresh_review_state"
    script = (
        f"from nbs_ruralscan.schema_tools.generate import {method}; "
        f"{method}({str(ROOT / 'schema')!r})"
    )
    return {
        "error": (
            "Review records saved, but dashboard rebuilding failed. "
            "Keep any reported recovery copies and reconcile incomplete rollback first. "
            "Retry rebuilding without repeating Reopen or Challenge: "
            f"uv run python -c {shlex.quote(script)}\n{error}"
        ),
        "records_saved": True,
        "rebuild_required": True,
    }


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


def _corpus_readiness() -> dict:
    """Cache presence only: provenance validity is still checked when applying."""
    ev = ROOT / "schema" / "registers" / "EV_evidence_register.csv"
    if not ev.exists():
        return {"known": False, "error": "Evidence register unavailable"}
    with ev.open(newline="", encoding="utf-8") as stream:
        sources = sorted(
            {
                r["source_id"]
                for r in _csv_mod.DictReader(stream)
                if r.get("source_id") and r.get("use_role") != "dataset"
            }
        )
    missing = [
        sid
        for sid in sources
        if not any(
            (CACHE / f"{sid}{ext}").is_file() and (CACHE / f"{sid}{ext}").stat().st_size
            for ext in (".pdf", ".txt", ".html", ".md")
        )
    ]
    return {
        "known": True,
        "total": len(sources),
        "cached": len(sources) - len(missing),
        "missing": missing,
        "ready": not missing,
    }


class Handler(SimpleHTTPRequestHandler):
    def _json(self, code: int, obj: dict) -> None:
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        if self.path == "/api/clarifications":
            try:
                with _STORE_LOCK:
                    paths = _clarification_paths()
                    data = {
                        "issues": clarifications.build(paths),
                        "pending": len(clarifications.pending_events(paths)),
                    }
                return self._json(200, data)
            except (ValueError, OSError, PublicationRecoveryError) as exc:
                return self._json(500, {"error": str(exc)})
        if self.path == "/api/health":
            return self._json(200, {"ok": True})
        if self.path == "/api/readiness":
            return self._json(200, _corpus_readiness())
        if self.path == "/api/version":
            return self._json(200, _git_version())
        if self.path == "/api/state":
            try:
                return self._json(200, {"decisions": _load()})
            except (ValueError, OSError, PublicationRecoveryError) as exc:
                return self._json(500, {"error": str(exc)})
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
            requested_page = parse_qs(urlparse(self.path).query).get("page", [""])[0]
            if requested_page:
                if (
                    not requested_page.isdigit()
                    or not 1 <= int(requested_page) <= 10000
                ):
                    return self._json(400, {"error": "invalid PDF page"})
                import fitz

                with fitz.open(str(pdf)) as document:
                    if int(requested_page) > len(document):
                        return self._json(400, {"error": "PDF page out of range"})
                pno = int(requested_page)
            _rq = parse_qs(urlparse(self.path).query).get("rot", [""])[0]
            rot = int(_rq) if _rq in ("0", "90", "180", "270") else 0
            try:
                data = render_region_png(
                    pdf,
                    ""
                    if requested_page and str(pno) != row.get("page")
                    else row.get("quote") or "",
                    pno,
                    rot,
                    full_page=parse_qs(urlparse(self.path).query).get("full", [""])[0]
                    == "1",
                )
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
        # Serialize whole read-modify-write transactions, not only final file writes.
        try:
            if self.path in {
                "/api/decision",
                "/api/clarifications",
                "/api/challenge",
                "/api/reopen",
                "/api/apply",
                "/api/clear",
                "/api/gap",
            }:
                with _STORE_LOCK:
                    return self._handle_post()
            return self._handle_post()
        except review_local.InvalidRequest as exc:
            return self._json(400, {"error": str(exc)})
        except (ValueError, OSError, _csv_mod.Error, PublicationRecoveryError) as exc:
            return self._json(500, {"error": str(exc)})

    def _handle_post(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            return self._json(400, {"error": "bad json"})

        if not isinstance(payload, dict):
            return self._json(400, {"error": "request must be a JSON object"})

        if self.path == "/api/clarifications":
            event = clarifications.record(_clarification_paths(), payload)
            return self._json(200, {"event": event})

        if self.path == "/api/decision":
            return self._json(
                200, review_local.save_decision(_clarification_paths(), payload)
            )

        if self.path == "/api/gap":
            return self._json(
                200,
                review_local.report_gap(ROOT / "pipeline/metrics/gaps.csv", payload),
            )

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
            store, snapshot = _decision_snapshot()
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

            def apply_records(files, staged_store):
                res = apply_decisions(decisions, "consensus", files=files)
                for eid in decisions:  # keep history and other reviewers' calls
                    for rv in store.get(eid, {}):
                        store[eid][rv]["applied"] = True
                _save(store, path=staged_store)
                return res

            try:
                res = _stage_review_action(apply_records, snapshot)
            except Exception as e:  # noqa: BLE001
                return self._json(500, {"error": str(e)})
            try:
                generate(ROOT / "schema")
            except Exception as e:  # noqa: BLE001
                return self._json(500, _review_rebuild_error(e, full=True))
            return self._json(200, {"ok": True, **res, "conflicts": conflicts})

        if self.path == "/api/submit":
            # Ship the reviewed decisions to main with no terminal: run the same vetted flow
            # as scripts/submit-review.sh (branch off latest main → replay decisions → regen →
            # commit registers → push → open PR → --auto squash-merge on green CI). This is a
            # LOCAL tool on the reviewer's machine, so it uses their git/gh auth.
            import re as _re
            import subprocess

            review_local.validate_text_fields(payload, ("reviewer", "title"))
            if ROOT != _COMPILER_ROOT:
                return self._json(
                    409,
                    {
                        "ok": False,
                        "error": "Shipping uses the installed Git checkout. Run the server from the review checkout to submit its decisions.",
                    },
                )
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
            import sys

            try:
                proc = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "nbs_ruralscan.schema_tools.submit_review",
                        "--ship",
                        reviewer,
                        "--title",
                        title,
                        "--auto",
                    ],
                    cwd=str(ROOT),
                    capture_output=True,
                    text=True,
                    env=_env,
                    stdin=subprocess.DEVNULL,
                    timeout=900,
                )
            except subprocess.TimeoutExpired:
                return self._json(
                    500,
                    {
                        "ok": False,
                        "error": "submit timed out (git/gh auth?). Decisions ARE applied locally. Check `gh auth status` and git push rights, then retry submission. Check .cache/review-submit.lock only after confirming no submission is still running.",
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
            review_local.validate_text_fields(
                payload, ("evidence_id", "reviewer", "decision", "reason", "note")
            )
            eid = payload.get("evidence_id")
            dec = (payload.get("decision") or "").strip()
            rev = (payload.get("reviewer") or "reviewer").strip() or "reviewer"
            if not eid or dec not in ("ok", "drop"):
                return self._json(
                    400, {"error": "evidence_id + decision(ok|drop) required"}
                )
            store, snapshot = _decision_snapshot()
            byrev = store.setdefault(eid, {})
            byrev[rev] = {
                "decision": dec,
                "reason": payload.get("reason", ""),
                "note": payload.get("note", ""),
                "applied": False,
            }
            if payload.get("reviewed_conflict"):
                from datetime import datetime, timezone

                byrev[rev]["reviewed_conflict_at"] = datetime.now(
                    timezone.utc
                ).isoformat()
            decs = {
                r: v["decision"]
                for r, v in byrev.items()
                if (v.get("decision") or "").strip()
            }
            conflict = len(set(decs.values())) > 1
            reopened = 0
            if conflict and not payload.get("reviewed_conflict"):
                from nbs_ruralscan.schema_tools.review import reopen_units
                from nbs_ruralscan.schema_tools.generate import refresh_review_state

                def challenge_records(files, staged_store):
                    res = reopen_units([eid], rev, files=files)
                    _save(store, path=staged_store)
                    return res

                try:
                    res = _stage_review_action(challenge_records, snapshot)
                    reopened = res.get("reopened", 0)
                except Exception as e:  # noqa: BLE001
                    return self._json(500, {"error": str(e)})
                try:
                    refresh_review_state(ROOT / "schema")
                except Exception as e:  # noqa: BLE001
                    return self._json(500, _review_rebuild_error(e, full=False))
            else:
                snapshot.publish(
                    {STORE: json.dumps(store, indent=2).encode("utf-8")},
                    lambda _: snapshot.assert_unchanged(),
                )
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
            review_local.validate_text_fields(payload, ("evidence_id", "reviewer"))
            eids = payload.get("evidence_ids") or (
                [payload["evidence_id"]] if payload.get("evidence_id") else []
            )
            rev = (payload.get("reviewer") or "reviewer").strip() or "reviewer"
            if (
                not isinstance(eids, list)
                or not eids
                or not all(isinstance(eid, str) and eid.strip() for eid in eids)
            ):
                return self._json(400, {"error": "evidence_id(s) required"})
            from nbs_ruralscan.schema_tools.review import reopen_units
            from nbs_ruralscan.schema_tools.generate import refresh_review_state

            store, snapshot = _decision_snapshot()

            def reopen_records(files, staged_store):
                res = reopen_units(eids, rev, files=files)
                # Clear only this reviewer's saved call; other reviewers stay intact.
                for eid in eids:
                    if eid in store:
                        store[eid].pop(rev, None)
                        if not store[eid]:
                            store.pop(eid)
                _save(store, path=staged_store)
                return res

            try:
                res = _stage_review_action(reopen_records, snapshot)
            except Exception as e:  # noqa: BLE001
                return self._json(500, {"error": str(e)})
            try:
                refresh_review_state(ROOT / "schema")
            except Exception as e:  # noqa: BLE001
                return self._json(500, _review_rebuild_error(e, full=False))
            return self._json(200, {"ok": True, **res})

        if self.path == "/api/clear":
            return self._json(200, review_local.clear_decisions(STORE, payload))

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


def main(argv=None) -> int:
    import sys

    global ROOT, CACHE, DOCS, STORE
    parser = argparse.ArgumentParser(
        description="Serve a local Rural Scan review checkout."
    )
    parser.add_argument("port", nargs="?", type=int, default=8765)
    parser.add_argument(
        "--root",
        type=Path,
        default=_COMPILER_ROOT,
        help="Review data and dashboard checkout (default: installed checkout)",
    )
    args = parser.parse_args(argv)
    ROOT = args.root.expanduser().resolve()
    if not (ROOT / "schema").is_dir() or not (ROOT / "docs").is_dir():
        parser.error("review root must contain schema/ and docs/")
    CACHE = ROOT / ".cache/corpus"
    DOCS = ROOT / "docs"
    STORE = ROOT / "pipeline/review/decisions.json"

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
    port = args.port
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
