"""Build the gitignored ingestion cache over a folder of PDFs (process-once).

CLI:
    uv run python -m nbs_ruralscan.ingest.build <pdf_dir> [--cache .cache/ingest] [--no-tables]

Skips PDFs already cached with the same content hash. Born-digital PDFs need no OCR;
scanned pages are flagged in each index's ``needs_ocr_pages``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .cache import load_index, save_index
from .pdf import build_index


def build_cache(
    pdf_dir: str | Path,
    cache_dir: str | Path = ".cache/ingest",
    *,
    with_tables: bool = True,
) -> list[str]:
    """Ingest every PDF in ``pdf_dir`` into the cache. Returns the source_ids built."""
    pdf_dir = Path(pdf_dir)
    built: list[str] = []
    for pdf in sorted(pdf_dir.glob("*.pdf")):
        sid = pdf.stem
        existing = load_index(sid, cache_dir)
        try:
            idx = build_index(pdf, source_id=sid, with_tables=with_tables)
        except Exception as e:  # keep going across a corpus
            print(f"  SKIP {sid[:50]} — {type(e).__name__}: {e}")
            continue
        if existing and existing.sha1 == idx.sha1:
            print(f"  cached {sid[:50]}")
            continue
        save_index(idx, cache_dir)
        flag = f" · needs-OCR pp.{idx.needs_ocr_pages}" if idx.needs_ocr_pages else ""
        print(f"  built  {sid[:50]} — {idx.n_pages}p · {len(idx.tables)} tables{flag}")
        built.append(sid)
    return built


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the doc-ingestion cache.")
    ap.add_argument("pdf_dir")
    ap.add_argument("--cache", default=".cache/ingest")
    ap.add_argument("--no-tables", action="store_true")
    args = ap.parse_args()
    built = build_cache(args.pdf_dir, args.cache, with_tables=not args.no_tables)
    print(f"\nDone — {len(built)} new/updated indexes in {args.cache}")


if __name__ == "__main__":
    main()
