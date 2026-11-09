#!/usr/bin/env python3
"""OCR adapter for scanned PDFs with no text layer (Pete 2026-11-07, decision F1).

    uv run python scripts/ocr-scan.py <source_id> [<source_id> ...] [--lang eng]

Rule (methodology/search_protocol.md §Scanned PDFs): OCR ONCE, store the result as the
artefact of record, never re-run. For each page without a usable text layer the page is
rendered at 300 dpi and Tesseract adds an invisible text layer under the page image; pages
that already carry text are copied unchanged. The OCR'd PDF goes to the team library as
`<source_id>_ocr.pdf` (the original scan stays there untouched) and replaces the local
corpus copy, so quotes are sliced from the OCR text and page locators match the scan.
The queue row's `target_library_path` is re-pointed and its note says OCR. Units extracted
from it carry `context.ocr_text = true`; a person checks a sample of their quotes against
the page image (review batch) before any is approved.
"""

from __future__ import annotations

import argparse
import csv
import io
import pathlib
import subprocess
import sys
import tempfile

import fitz

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nbs_ruralscan.ingest.integrity import copy_immutable  # noqa: E402

CACHE = ROOT / ".cache" / "corpus"
QUEUE = ROOT / "pipeline" / "acquisition_queue.csv"
MIN_TEXT = 50  # characters: below this a page counts as image-only


def _ocr_page(page, lang: str, dpi: int) -> bytes:
    """One page through the Tesseract CLI with full layout analysis (--psm 1), so
    two-column pages come out column by column. PyMuPDF's built-in OCR call interleaved
    the columns line by line (Bullock 2003, 2026-11-09), which made them unquotable."""
    with tempfile.TemporaryDirectory() as tmp:
        img = pathlib.Path(tmp) / "p.png"
        page.get_pixmap(dpi=dpi).save(img)
        base = pathlib.Path(tmp) / "out"
        subprocess.run(
            ["tesseract", str(img), str(base), "-l", lang, "--psm", "1", "pdf"],
            check=True,
            capture_output=True,
        )
        return (base.with_suffix(".pdf")).read_bytes()


def ocr_pdf(
    src: pathlib.Path, lang: str = "eng", dpi: int = 300, force: bool = False
) -> tuple[bytes, int, int]:
    doc = fitz.open(src)
    out = fitz.open()
    n_ocr = 0
    for page in doc:
        if not force and len(page.get_text().strip()) >= MIN_TEXT:
            out.insert_pdf(doc, from_page=page.number, to_page=page.number)
            continue
        out.insert_pdf(fitz.open("pdf", _ocr_page(page, lang, dpi)))
        n_ocr += 1
    return out.tobytes(garbage=3, deflate=True), len(doc), n_ocr


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source_ids", nargs="+")
    ap.add_argument("--lang", default="eng")
    ap.add_argument(
        "--force",
        action="store_true",
        help="OCR every page (a publisher banner can make an image page look like text)",
    )
    a = ap.parse_args(argv)
    lib_root = None
    spec = ROOT / "scripts" / "acquire-queue.py"
    import importlib.util

    s = importlib.util.spec_from_file_location("aq", spec)
    aq = importlib.util.module_from_spec(s)
    s.loader.exec_module(aq)
    lib_root = aq.LIB_ROOT
    rows = list(csv.DictReader(QUEUE.open(newline="", encoding="utf-8")))
    cols = list(rows[0].keys())
    by = {r["source_id"]: r for r in rows}
    for sid in a.source_ids:
        r = by.get(sid)
        if r is None:
            print(f"[skip] {sid}: not in queue")
            continue
        src = CACHE / f"{sid}.pdf"
        rel = r["target_library_path"]
        if not src.exists() or not rel:
            print(f"[skip] {sid}: no cached scan or library path")
            continue
        if rel.endswith("_ocr.pdf"):
            print(f"[skip] {sid}: already OCR'd (never re-run)")
            continue
        data, n_pages, n_ocr = ocr_pdf(src, a.lang, force=a.force)
        tmp = CACHE / f"{sid}.ocr.tmp"
        tmp.write_bytes(data)
        new_rel = rel[: -len(".pdf")] + "_ocr.pdf"
        copy_immutable(tmp, lib_root / new_rel)
        tmp.replace(src)
        r["target_library_path"] = new_rel
        r["blocker"] = ""
        r["note"] = (
            r["note"]
            + f" | OCR 2026-11-07 (scripts/ocr-scan.py, Tesseract {a.lang}, {n_ocr} of {n_pages} pages): artefact of record = {pathlib.Path(new_rel).name}; original scan kept in the library; units carry context.ocr_text=true and need a sampled human quote check"
        ).strip(" |")
        print(f"[ok] {sid}: {n_ocr}/{n_pages} pages OCR'd → {new_rel}")
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    QUEUE.write_text(buf.getvalue(), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
