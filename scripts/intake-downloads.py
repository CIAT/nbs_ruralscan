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

import argparse
import csv
import importlib.util
import hashlib
import io
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
from nbs_ruralscan.ingest.integrity import atomic_write, copy_immutable  # noqa: E402

QUEUE = ROOT / "pipeline" / "acquisition_queue.csv"
CORPUS = ROOT / ".cache" / "corpus"
_spec = importlib.util.spec_from_file_location(
    "hydrate", ROOT / "scripts" / "hydrate-corpus.py"
)
assert _spec and _spec.loader
_H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_H)


def title_check(pdf: Path, citation: str) -> tuple[bool, str]:
    """(ok, where): opening-page title match; body matches need identity review."""
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
                return (
                    False,
                    f"title only in body (page {i + 1}); could be a cited reference; verify chapter identity manually",
                )
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
    filed_downloads = []
    for pdf in sorted(src_dir.glob("*.pdf")):
        r = by_id.get(pdf.stem)
        if not r:
            continue
        try:
            ok, where = title_check(pdf, r.get("citation", ""))
        except (OSError, RuntimeError, ValueError) as exc:
            bad.append(f"{pdf.name}: unreadable PDF: {exc}")
            continue
        if not ok:
            bad.append(f"{pdf.name}: {where}")
            continue
        tgt = (r.get("target_library_path") or "").strip()
        if not lib or not tgt:
            no_lib.append(r["source_id"])
            continue
        dest = lib / tgt
        if not dest.resolve().is_relative_to(lib.resolve()):
            bad.append(f"{pdf.name}: library path escapes library root")
            continue
        digest = hashlib.sha256(pdf.read_bytes()).digest()
        archive = src_dir / "nbs_ingested" / pdf.name
        targets = [CORPUS / f"{r['source_id']}.pdf", dest]
        if not a.keep:
            targets.append(archive)
        if any(
            p.exists() and hashlib.sha256(p.read_bytes()).digest() != digest
            for p in targets
        ):
            bad.append(
                f"{pdf.name}: existing cache/library artifact differs; reconcile identity before replacement"
            )
            continue
        if a.dry_run:
            done.append(f"{pdf.name}: title on {where}")
            continue
        try:
            for target in targets:
                copy_immutable(pdf, target)
        except OSError as exc:
            bad.append(f"{pdf.name}: filing held: {exc}")
            continue
        done.append(f"{pdf.name}: title on {where}")
        r["status"] = "acquired"
        r["title_verified"] = "true"
        r["blocker"] = ""
        add = (
            f"acquired {today} from a human/browser download; title verified ({where})"
        )
        r["note"] = f"{r['note']} | {add}" if r.get("note") else add
        if not a.keep:
            filed_downloads.append(pdf)
    if done and not a.dry_run:
        buffer = io.StringIO(newline="")
        w = csv.DictWriter(buffer, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
        atomic_write(QUEUE, buffer.getvalue().encode("utf-8"))
        # Keep downloads available for a retry until queue persistence succeeds.
        for pdf in filed_downloads:
            pdf.unlink()
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
    return 1 if bad or no_lib else 0


if __name__ == "__main__":
    raise SystemExit(main())
