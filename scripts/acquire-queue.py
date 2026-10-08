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
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time
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


def _acquire(sid: str, url: str, dest: pathlib.Path) -> bool:
    if dest.exists():
        dest.unlink()
    p = subprocess.run(
        [
            sys.executable,
            "-m",
            "nbs_ruralscan.ingest.acquire",
            sid,
            url,
            "--kind",
            "pdf",
        ],
        capture_output=True,
        text=True,
        timeout=180,
    )
    ok = p.returncode == 0 and dest.exists() and dest.stat().st_size >= 20000
    if not ok:
        dest.unlink(missing_ok=True)
    return ok


def _candidates(r: dict, wayback: dict) -> list[str]:
    out: list[str] = []
    if r["source_id"] in wayback:
        out.append(wayback[r["source_id"]])
    if r.get("doi"):
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
    mirror = LIB_ROOT / LIB_REL / a.library_subdir
    assert mirror.is_dir(), f"library mirror missing: {mirror}"
    qp = ROOT / "pipeline" / "acquisition_queue.csv"
    rows = list(csv.DictReader(open(qp, newline="", encoding="utf-8")))
    cols = list(rows[0].keys())
    import fitz  # noqa: WPS433

    log: list[tuple[str, str, str]] = []
    for r in rows:
        if (
            (r["date_added"] != a.date and not a.all_dates)
            or r["status"] != "pending"
            or r["nbs_id"] != a.nbs
        ):
            continue
        sid = r["source_id"]
        if "HUMAN CHECK" in (r["blocker"] or "") or "paywalled (verified" in (
            r["blocker"] or ""
        ):
            log.append((sid, "skip", "human / verified paywalled"))
            continue
        dest = CACHE / f"{sid}.pdf"
        url = (r["url"] or "").strip()
        got = None
        if url and not (
            url.startswith("https://doi.org/") and "researchgate" not in url
        ):
            if _acquire(sid, url, dest):
                got = url
        if not got:
            for cand in _candidates(r, wayback):
                if _acquire(sid, cand, dest):
                    got = cand
                    break
                time.sleep(0.5)
        if not got:
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
        try:
            d = fitz.open(dest)
            txt = "".join(d[i].get_text() for i in range(min(3, len(d))))
            npages = len(d)
        except Exception as e:  # noqa: BLE001
            dest.unlink(missing_ok=True)
            log.append((sid, "fail", f"unreadable PDF: {e}"))
            continue
        ocr = len(txt.strip()) < 200
        shutil.copy2(dest, mirror / f"{sid}.pdf")
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
    with open(qp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    from collections import Counter

    print(Counter(s for _, s, _ in log))
    for sid, s, m in log:
        if s != "ok":
            print(f"  [{s}] {sid}: {m}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
