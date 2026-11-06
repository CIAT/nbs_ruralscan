#!/usr/bin/env python3
"""Hydrate source artifacts from selected records, library and source adapters.

Existing defaults and --queue/--nbs behavior remain. --root, --corpus-dir,
--library-root and --archive-dir select independent inputs and storage.
--dry-run fetches/checks privately without publishing selected corpus files.
"""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nbs_ruralscan.ingest import hydration  # noqa: E402

CACHE = ROOT / ".cache/corpus"
SRC_CSV = ROOT / "schema/registers/SRC_source_register.csv"
QUEUE_CSV = ROOT / "pipeline/acquisition_queue.csv"
_SNAPSHOT_EXTS = hydration._SNAPSHOT_EXTS
library_root = hydration.library_root
_github_raw = hydration._github_raw
_fetch = hydration._fetch


def _cached(sid):
    return hydration._cached(CACHE, sid)


def _paths(root):
    return hydration.HydrationPaths(
        SRC_CSV, QUEUE_CSV, CACHE, ROOT / "methodology/audits", root
    )


def hydrate_queue(root, nbs):
    result = hydration.run_hydration(
        _paths(root), queue_only=True, nbs=nbs, fetch=_fetch
    )
    print(result.report, end="")


def main(argv=None):
    return hydration.main(argv, paths=_paths(library_root()), fetch=_fetch)


if __name__ == "__main__":
    raise SystemExit(main())
