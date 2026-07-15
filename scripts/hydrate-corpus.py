#!/usr/bin/env python3
"""Hydrate .cache/corpus/ so a fresh clone can preview + Apply.

`.cache/corpus/` is gitignored, so a fresh clone has none of the source artifacts the
QA/QC review server needs — screengrabs/PDF previews 404 AND Apply's provenance guardrail
fails (it verifies every quote against the cached artifact). This script fetches them all:

* **PDFs** (`SRC.library_path`) — copied from the local OneDrive mirror of the SharePoint
  library. Needs `NBS_LIBRARY_ROOT` (or the default Mac mount).
* **Code / web sources** (`SRC.url`, `source_category=tool` or `source_kind=website`) — a
  snapshot fetched from the URL: a GitHub `/blob/` link -> raw text `.txt`; any other page
  -> `.html`. These have NO `library_path`, so the PDF pass alone leaves them missing and
  Apply blocks on them (#191, e.g. the saraheb3 GEE tool sources).

Usage:
    python3 scripts/hydrate-corpus.py

The library root defaults to Pete's CGIAR OneDrive mount; override with NBS_LIBRARY_ROOT if
your OneDrive folder name differs (e.g. on Windows):
    NBS_LIBRARY_ROOT="$HOME/OneDrive - CGIAR/ClimateActionNetZero/1_Projects" \
        python3 scripts/hydrate-corpus.py
Code/web hydration runs even without a library root (it only needs network).
"""

from __future__ import annotations

import csv
import os
import re
import shutil
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "corpus"
SRC_CSV = ROOT / "schema" / "registers" / "SRC_source_register.csv"
_SNAPSHOT_EXTS = (".pdf", ".txt", ".html", ".md")


def library_root() -> Path | None:
    """Resolve the local OneDrive mirror of the SharePoint .../1_Projects/ folder."""
    env = os.environ.get("NBS_LIBRARY_ROOT")
    if env:
        return Path(env).expanduser()
    default = (
        Path.home()
        / "Library/CloudStorage/OneDrive-CGIAR/ClimateActionNetZero/1_Projects"
    )
    return default if default.exists() else None


def _github_raw(url: str) -> str | None:
    """github.com/<o>/<r>/blob/<ref>/<path> -> raw.githubusercontent.com/<o>/<r>/<ref>/<path>."""
    m = re.match(
        r"^https://github\.com/([^/]+)/([^/]+)/blob/(.+)$", (url or "").strip()
    )
    return (
        f"https://raw.githubusercontent.com/{m.group(1)}/{m.group(2)}/{m.group(3)}"
        if m
        else None
    )


def _fetch(url: str) -> bytes | None:
    """Fetch a URL (4 MB cap); None on any failure."""
    req = urllib.request.Request(url, headers={"User-Agent": "nbs-ruralscan-hydrate"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            if resp.status != 200:
                return None
            return resp.read(4_000_000)
    except Exception:  # noqa: BLE001
        return None


def _cached(sid: str) -> bool:
    return any((CACHE / (sid + ext)).exists() for ext in _SNAPSHOT_EXTS)


def main() -> int:
    if not SRC_CSV.exists():
        print(f"SRC register not found: {SRC_CSV}")
        return 0
    CACHE.mkdir(parents=True, exist_ok=True)
    root = library_root()

    with SRC_CSV.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    pdf_copied = pdf_already = code_fetched = code_already = skipped = 0
    pdf_missing: list[str] = []
    code_failed: list[str] = []

    for r in rows:
        sid = (r.get("source_id") or "").strip()
        if not sid:
            continue
        lib_path = (r.get("library_path") or "").strip()
        url = (r.get("url") or "").strip()
        kind = (r.get("source_kind") or "").strip().lower()
        cat = (r.get("source_category") or "").strip().lower()

        if lib_path:  # PDF from the SharePoint/OneDrive library
            if (CACHE / (sid + ".pdf")).exists():
                pdf_already += 1
                continue
            if root is None:
                pdf_missing.append(f"{sid} (set NBS_LIBRARY_ROOT)")
                continue
            src_pdf = root / lib_path
            if not src_pdf.exists():
                pdf_missing.append(sid)
                continue
            try:
                shutil.copy2(src_pdf, CACHE / (sid + ".pdf"))
                pdf_copied += 1
            except Exception as e:  # noqa: BLE001
                print(f"  ! failed to copy {sid}: {e}")
                pdf_missing.append(sid)
        elif url and (
            cat == "tool" or kind in ("website", "github")
        ):  # code/web snapshot
            if _cached(sid):
                code_already += 1
                continue
            raw = _github_raw(url)
            data = _fetch(raw or url)
            if not data:
                code_failed.append(sid)
                continue
            (CACHE / (sid + (".txt" if raw else ".html"))).write_bytes(data)
            code_fetched += 1
        else:
            skipped += (
                1  # no artifact source (e.g. a PDF not yet uploaded to the library)
            )

    print(f"library root       : {root}")
    print(f"PDF copied         : {pdf_copied}")
    print(f"PDF already cached  : {pdf_already}")
    print(f"code/web fetched    : {code_fetched}")
    print(f"code/web cached     : {code_already}")
    print(f"no artifact source  : {skipped}")
    if pdf_missing:
        print(f"PDF missing from library: {len(pdf_missing)}")
        for sid in pdf_missing:
            print(f"  - {sid}")
    if code_failed:
        print(
            f"code/web fetch FAILED: {len(code_failed)} (check the SRC.url / network)"
        )
        for sid in code_failed:
            print(f"  - {sid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
