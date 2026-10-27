#!/usr/bin/env python3
"""File PDFs downloaded by a person (or a browser session) into the corpus and the library.

    python3 scripts/intake-downloads.py [--dir ~/Downloads] [--dry-run] [--keep]

Looks for `<source_id>.pdf` files whose name matches an acquisition-queue row. For each:

1. **Identity check** — the citation's title must appear on the PDF's opening pages (the same
   token-coverage test as `verify_metadata.py verify-titles`; a chapter inside a larger PDF
   is found by searching the body). A mismatch is left where it is and reported: a wrong
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

import argparse
import csv
import importlib.util
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nbs_ruralscan.schema_tools.verify_metadata import (  # noqa: E402
    TITLE_THRESH,
    _title_coverage,
    _title_of,
)

QUEUE = ROOT / "pipeline" / "acquisition_queue.csv"
CORPUS = ROOT / ".cache" / "corpus"
_spec = importlib.util.spec_from_file_location(
    "hydrate", ROOT / "scripts" / "hydrate-corpus.py"
)
assert _spec and _spec.loader
_H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_H)


def title_check(pdf: Path, citation: str) -> tuple[bool, str]:
    """(ok, where): the citation title on the opening pages, else anywhere in the body."""
    import fitz

    title = _title_of(citation)
    with fitz.open(pdf) as doc:
        head = " ".join(doc[i].get_text() for i in range(min(3, len(doc))))
        if _title_coverage(title, head) >= TITLE_THRESH:
            return True, "opening pages"
        prev = ""
        for i in range(min(len(doc), 500)):
            page = doc[i].get_text()
            if _title_coverage(title, prev + " " + page) >= TITLE_THRESH:
                return True, f"page {i + 1}"
            prev = page
    return False, f"title not found: {title[:80]}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--dir", default=str(Path.home() / "Downloads"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--keep", action="store_true", help="leave the downloads in place")
    a = ap.parse_args(argv)
    src_dir = Path(a.dir).expanduser()
    with QUEUE.open(newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        cols = list(rd.fieldnames or [])
        rows = list(rd)
    by_id = {r["source_id"]: r for r in rows}
    lib = _H.library_root()
    today = date.today().isoformat()
    done, bad, no_lib = [], [], []
    for pdf in sorted(src_dir.glob("*.pdf")):
        r = by_id.get(pdf.stem)
        if not r:
            continue
        ok, where = title_check(pdf, r.get("citation", ""))
        if not ok:
            bad.append(f"{pdf.name}: {where}")
            continue
        done.append(f"{pdf.name}: title on {where}")
        if a.dry_run:
            continue
        CORPUS.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf, CORPUS / f"{r['source_id']}.pdf")
        tgt = (r.get("target_library_path") or "").strip()
        if lib and tgt:
            dest = lib / tgt
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pdf, dest)
        else:
            no_lib.append(r["source_id"])
        r["status"] = "acquired"
        r["title_verified"] = "true"
        r["blocker"] = ""
        add = (
            f"acquired {today} from a human/browser download; title verified ({where})"
        )
        r["note"] = f"{r['note']} | {add}" if r.get("note") else add
        if not a.keep:
            moved = src_dir / "nbs_ingested"
            moved.mkdir(exist_ok=True)
            shutil.move(str(pdf), moved / pdf.name)
    if done and not a.dry_run:
        with QUEUE.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    print(f"filed {len(done)}" + (" (dry run)" if a.dry_run else ""))
    for d in done:
        print("  ok  ", d)
    for b in bad:
        print("  FAIL", b, "(left in place)")
    if no_lib:
        print(
            "  library copy skipped (no library root / target path):", ", ".join(no_lib)
        )
    if done and not a.dry_run:
        print(
            "next: python3 src/nbs_ruralscan/schema_tools/verify_metadata.py verify  (DOI rows)"
        )
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
