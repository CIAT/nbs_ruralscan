#!/usr/bin/env python3
"""Hydrate .cache/corpus/ from the shared SharePoint library (OneDrive mirror).

The QA/QC review server renders table screengrabs (/api/crop) and inline PDFs
(/api/pdf) from `.cache/corpus/<source_id>.pdf`, which is gitignored. A fresh
clone has an empty cache, so previews 404 for everyone but whoever extracted the
evidence. Every registered PDF, though, is uploaded to the SharePoint library and
its path stored in SRC_source_register.library_path; reviewers sync that library
locally via OneDrive. This script copies each registered PDF from the local
OneDrive mirror into `.cache/corpus/` in one pass.

Usage:
    python3 scripts/hydrate-corpus.py

The library root defaults to Pete's CGIAR OneDrive mount; override with the
NBS_LIBRARY_ROOT env var if your OneDrive folder name differs, e.g.:
    NBS_LIBRARY_ROOT="$HOME/OneDrive - CGIAR/ClimateActionNetZero/1_Projects" \
        python3 scripts/hydrate-corpus.py
"""

from __future__ import annotations

import csv
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "corpus"
SRC_CSV = ROOT / "schema" / "registers" / "SRC_source_register.csv"


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


def main() -> int:
    root = library_root()
    if root is None:
        print(
            "NBS_LIBRARY_ROOT is unset and the default OneDrive path was not found.\n"
            "Set it to your local mirror of the SharePoint .../1_Projects/ folder, e.g.:\n"
            '    NBS_LIBRARY_ROOT="$HOME/OneDrive - CGIAR/ClimateActionNetZero/1_Projects" \\\n'
            "        python3 scripts/hydrate-corpus.py"
        )
        return 0
    if not SRC_CSV.exists():
        print(f"SRC register not found: {SRC_CSV}")
        return 0

    CACHE.mkdir(parents=True, exist_ok=True)

    copied = 0
    already = 0
    no_path = 0
    missing: list[str] = []

    with SRC_CSV.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            sid = (r.get("source_id") or "").strip()
            lib_path = (r.get("library_path") or "").strip()
            if not sid:
                continue
            if not lib_path:
                no_path += 1
                continue
            cached = CACHE / (sid + ".pdf")
            if cached.exists():
                already += 1
                continue
            src_pdf = root / lib_path
            if not src_pdf.exists():
                missing.append(sid)
                continue
            try:
                shutil.copy2(src_pdf, cached)
                copied += 1
            except Exception as e:  # noqa: BLE001
                print(f"  ! failed to copy {sid}: {e}")
                missing.append(sid)

    print(f"library root : {root}")
    print(f"copied       : {copied}")
    print(f"already cached: {already}")
    print(f"no library_path: {no_path}")
    print(f"missing from library: {len(missing)}")
    if missing:
        for sid in missing:
            print(f"  - {sid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
