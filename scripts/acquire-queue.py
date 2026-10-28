#!/usr/bin/env python3
"""Acquire pending acquisition-queue rows into the corpus cache AND the SharePoint mirror.

Deterministic, two passes, no LLM:

1. direct: the row's ``url`` via ``nbs_ruralscan.ingest.acquire`` (PDF only; size + text-layer checked)
2. fallbacks for what failed: Unpaywall ``url_for_pdf`` locations (by DOI), a ``citation_pdf_url``
   meta tag or the first ``.pdf`` link on the landing page, and an optional Internet Archive map

Each success copies the PDF to the OneDrive mirror of the SharePoint library
(``…/library/<subdir>/<source_id>.pdf``), sets ``status=acquired`` + ``target_library_path``,
and flags scanned PDFs ``needs_ocr``. Rows flagged ``HUMAN CHECK`` (ResearchGate-only) or without
a usable URL/DOI are left for the human acquirer with an explicit blocker.

    python3 scripts/acquire-queue.py --date 2026-10-05 --nbs water_harvesting_conservation \
        --library-subdir 3_Water_Harvesting [--wayback map.json]
"""

from __future__ import annotations

import argparse
import csv
import json
import io
import os
import pathlib
import re
import time
import tempfile

from nbs_ruralscan.ingest.acquire import AcquireError, acquire
from nbs_ruralscan.ingest.integrity import (
    atomic_write,
    copy_immutable,
    pdf_title_error,
    validate_source_id,
)
from urllib.parse import urljoin

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "corpus"
LIB_ROOT = pathlib.Path(
    os.environ.get("NBS_LIBRARY_ROOT")
    or pathlib.Path.home()
    / "Library/CloudStorage/OneDrive-CGIAR/ClimateActionNetZero/1_Projects"
)
LIB_REL = "D591_Rural-Scan_NBS/2_Technical_&_Data/library"
UA = {
    "User-Agent": "Mozilla/5.0 (Macintosh) nbs-ruralscan evidence pipeline (p.steward@cgiar.org)"
}


def _acquire(
    sid: str,
    url: str,
    dest: pathlib.Path,
    citation: str | None = None,
    identity_holds: list[str] | None = None,
) -> bool:
    # A failed retry must never destroy an existing source. Acquire into an isolated
    # directory and validate with the PDF parser before promoting the artifact.
    import fitz

    def identity_matches(path: pathlib.Path) -> bool:
        problem = pdf_title_error(path, citation) if citation is not None else None
        if problem and identity_holds is not None:
            identity_holds.append(f"{url}: {problem}")
        return problem is None

    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        if dest.exists():
            if not identity_matches(dest):
                return False
            acquire(sid, url, kind="pdf", corpus_dir=dest.parent)
            with fitz.open(dest) as doc:
                return doc.page_count > 0
        with tempfile.TemporaryDirectory(dir=dest.parent) as tmp:
            result = acquire(sid, url, kind="pdf", corpus_dir=tmp)
            if result.artifact_path is None or result.meta_path is None:
                return False
            with fitz.open(result.artifact_path) as doc:
                if doc.page_count == 0:
                    return False
            if not identity_matches(result.artifact_path):
                return False
            result.artifact_path.replace(dest)
            result.meta_path.replace(dest.with_suffix(".meta.json"))
        return True
    except (AcquireError, ValueError, RuntimeError, OSError):
        return False


def _candidates(r: dict, wayback: dict) -> list[str]:
    out: list[str] = []
    if r["source_id"] in wayback:
        out.append(wayback[r["source_id"]])
    if r.get("doi") and r.get("doi_verified") == "true":
        try:
            u = requests.get(
                f"https://api.unpaywall.org/v2/{r['doi']}?email=p.steward@cgiar.org",
                timeout=30,
            ).json()
            locs = (
                [u.get("best_oa_location")] if u.get("best_oa_location") else []
            ) + (u.get("oa_locations") or [])
            for loc in locs:
                if loc and loc.get("url_for_pdf") and loc["url_for_pdf"] not in out:
                    out.append(loc["url_for_pdf"])
        except Exception:
            pass
    for url in [r.get("url", "")] + list(out):
        if not url or url.lower().endswith(".pdf"):
            continue
        try:
            h = requests.get(url, headers=UA, timeout=40, allow_redirects=True)
            if "html" not in h.headers.get("content-type", ""):
                continue
            m = re.search(
                r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)',
                h.text,
                re.I,
            ) or re.search(
                r'content=["\']([^"\']+)["\'][^>]+name=["\']citation_pdf_url["\']',
                h.text,
                re.I,
            )
            links = (
                [m.group(1)]
                if m
                else re.findall(r'href=["\']([^"\']+\.pdf[^"\']*)', h.text, re.I)[:3]
            )
            for link in links:
                full = urljoin(h.url, link)
                if full not in out:
                    out.append(full)
        except Exception:
            pass
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--date", required=True)
    ap.add_argument("--nbs", required=True)
    ap.add_argument("--library-subdir", required=True)
    ap.add_argument("--wayback", default="")

    ap.add_argument(
        "--all-dates",
        action="store_true",
        help="retry every pending row of the NbS regardless of date_added (OA-recovery pass)",
    )
    a = ap.parse_args(argv)
    wayback = json.loads(pathlib.Path(a.wayback).read_text()) if a.wayback else {}
    library = (LIB_ROOT / LIB_REL).resolve()
    mirror = library / a.library_subdir
    if not mirror.resolve().is_relative_to(library):
        ap.error("library subdirectory escapes the team library")
    if not mirror.is_dir():
        ap.error(f"library mirror missing: {mirror}")
    qp = ROOT / "pipeline" / "acquisition_queue.csv"
    rows = list(csv.DictReader(open(qp, newline="", encoding="utf-8")))
    cols = list(rows[0].keys())
    import fitz  # noqa: WPS433

    log: list[tuple[str, str, str]] = []
    for r in rows:
        if (
            (r["date_added"] != a.date and not a.all_dates)
            or r["status"] != "pending"
            or a.nbs not in {token.strip() for token in r["nbs_id"].split("|")}
        ):
            continue
        sid = r["source_id"]
        try:
            validate_source_id(sid)
        except ValueError as exc:
            log.append((sid, "fail", str(exc)))
            continue
        if "HUMAN CHECK" in (r["blocker"] or "") or "paywalled (verified" in (
            r["blocker"] or ""
        ):
            log.append((sid, "skip", "human / verified paywalled"))
            continue
        dest = CACHE / f"{sid}.pdf"
        url = (r["url"] or "").strip()
        got = None
        identity_holds: list[str] = []
        citation = r.get("citation", "")
        if url and not (
            url.startswith("https://doi.org/") and "researchgate" not in url
        ):
            if _acquire(sid, url, dest, citation, identity_holds):
                got = url
        if not got:
            for cand in _candidates(r, wayback):
                if _acquire(sid, cand, dest, citation, identity_holds):
                    got = cand
                    break
                time.sleep(0.5)
        if not got:
            if identity_holds:
                r["blocker"] = "document identity hold — " + "; ".join(
                    dict.fromkeys(identity_holds)
                )
                log.append((sid, "fail", r["blocker"]))
                continue
            reason = (
                "no URL/DOI route"
                if not (url or r.get("doi"))
                else "no candidate URL yielded a PDF (landing page / 403 / no Unpaywall copy)"
            )
            r["blocker"] = (
                r["blocker"]
                or f"tool acquisition failed — {reason}; human browser download / OA web-search recovery"
            )
            log.append((sid, "fail", reason))
            continue
        identity_problem = pdf_title_error(dest, r.get("citation", ""))
        if identity_problem:
            r["blocker"] = f"document identity hold — {identity_problem}"
            log.append((sid, "fail", r["blocker"]))
            continue
        try:
            with fitz.open(dest) as d:
                txt = "".join(d[i].get_text() for i in range(min(3, len(d))))
                npages = len(d)
        except Exception as e:  # noqa: BLE001
            log.append((sid, "fail", f"unreadable PDF: {e}"))
            continue
        ocr = len(txt.strip()) < 200
        try:
            copy_immutable(dest, mirror / f"{sid}.pdf")
        except OSError as exc:
            r["blocker"] = f"library copy held — {exc}"
            log.append((sid, "fail", r["blocker"]))
            continue
        r["status"] = "acquired"
        r["target_library_path"] = f"{LIB_REL}/{a.library_subdir}/{sid}.pdf"
        r["url"] = got
        if ocr:
            r["blocker"] = "needs_ocr (scanned PDF, no text layer)"
        r["note"] = (
            r["note"]
            + f"; acquired {a.date} by acquire-queue.py ({npages} pp{', NO TEXT LAYER' if ocr else ''}) → cache + SharePoint mirror"
        ).strip("; ")
        log.append((sid, "ok", f"{npages} pp{' OCR' if ocr else ''}"))
        time.sleep(1.0)
    buffer = io.StringIO(newline="")
    w = csv.DictWriter(buffer, fieldnames=cols, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    atomic_write(qp, buffer.getvalue().encode("utf-8"))
    from collections import Counter

    print(Counter(s for _, s, _ in log))
    for sid, s, m in log:
        if s != "ok":
            print(f"  [{s}] {sid}: {m}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
