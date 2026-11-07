#!/usr/bin/env python3
"""File PDFs downloaded by a person (or a browser session) into the corpus and the library.

    python3 scripts/intake-downloads.py [--dir ~/Downloads] [--dry-run] [--keep]

Looks for `<source_id>.pdf` files whose name matches an acquisition-queue row. For each:

1. **Identity check** — the citation's title must appear on the PDF's opening pages (the same
   token-coverage test as `verify_metadata.py verify-titles`; a body-only match is held for manual chapter/reference disambiguation). A mismatch is left where it is and reported: a wrong
   file must never reach the corpus (catalogue: DOI ↔ citation, trust anchor = title).
2. **Filing** — copies the PDF to `.cache/corpus/<source_id>.pdf` and to the SharePoint
   library through its OneDrive mirror at the row's `target_library_path` (library root
   from `NBS_LIBRARY_ROOT` or the default Mac mount, as `hydrate-corpus.py`).
3. **Queue** — sets `status = acquired`, `title_verified = true`, clears the blocker and
   appends an acquisition note. Extraction still refuses a DOI-bearing row until
   `verify_metadata.py verify` has stamped `doi_verified`.

The processed download is moved to `<dir>/nbs_ingested/` unless `--keep`. Nothing is
downloaded here: this only files what a human already fetched.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nbs_ruralscan.ingest import download_intake as intake  # noqa: E402
from nbs_ruralscan.ingest.integrity import atomic_write, copy_immutable  # noqa: E402
from nbs_ruralscan.ingest.download_intake import title_check as title_check  # noqa: E402

QUEUE = ROOT / "pipeline" / "acquisition_queue.csv"
CORPUS = ROOT / ".cache" / "corpus"
_spec = importlib.util.spec_from_file_location(
    "hydrate", ROOT / "scripts" / "hydrate-corpus.py"
)
assert _spec and _spec.loader
_H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_H)


def main(argv: list[str] | None = None) -> int:
    return intake.main(
        argv,
        paths=intake.DownloadIntakePaths(
            QUEUE, CORPUS, Path.home() / "Downloads", _H.library_root()
        ),
        title_checker=title_check,
        copy_file=copy_immutable,
        write_queue=atomic_write,
        today=date.today().isoformat(),
    )


if __name__ == "__main__":
    raise SystemExit(main())
