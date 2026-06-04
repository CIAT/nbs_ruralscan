"""PDF → structure-aware `DocIndex`.

Deterministic, no model tokens. Uses PyMuPDF for fast page text + caption/section
detection, and pdfplumber for table extraction. Pages with little/no extractable
text are flagged ``needs_ocr`` (OCR itself is an optional, lazy step — born-digital
papers don't need it).
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .models import Caption, DocIndex, Section, TableBlock

# "Table 3", "Fig. 2", "Figure 12" + trailing caption text
_CAPTION_RE = re.compile(
    r"(?im)\b(?P<label>(?:fig(?:ure)?|table)\.?\s*\d+)\b[\s:.–\-]*(?P<text>.{0,180})"
)
# numbered headings ("3.1 Slope") or short Title-Case / ALL-CAPS lines
_HEADING_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)\s+([A-Z][^.\n]{2,70})\s*$")

_MIN_CHARS_PER_PAGE = 80  # below this → likely scanned/needs OCR


def _sha1(path: Path) -> str:
    h = hashlib.sha1()
    h.update(path.read_bytes())
    return h.hexdigest()[:16]


def _find_captions(text: str, page: int) -> list[Caption]:
    out: list[Caption] = []
    for m in _CAPTION_RE.finditer(text):
        label = re.sub(r"\s+", " ", m.group("label")).strip()
        kind = "figure" if label.lower().startswith("fig") else "table"
        cap = re.sub(r"\s+", " ", m.group("text")).strip()
        if cap:
            out.append(Caption(page=page, label=label, text=cap[:180], kind=kind))
    return out


def _find_sections(text: str, page: int) -> list[Section]:
    out: list[Section] = []
    for line in text.splitlines():
        m = _HEADING_RE.match(line)
        if m:
            out.append(Section(page=page, title=f"{m.group(1)} {m.group(2).strip()}"))
    return out


def _extract_tables(path: Path) -> list[TableBlock]:
    """Tables via pdfplumber (best-effort; pdfplumber is optional)."""
    try:
        import pdfplumber
    except ImportError:
        return []
    blocks: list[TableBlock] = []
    try:
        with pdfplumber.open(str(path)) as pdf:
            for pno, page in enumerate(pdf.pages, start=1):
                for tbl in page.extract_tables() or []:
                    rows = [
                        [("" if c is None else str(c).strip()) for c in row]
                        for row in tbl
                        if any(c not in (None, "") for c in row)
                    ]
                    if len(rows) >= 2:  # header + ≥1 row
                        blocks.append(TableBlock(page=pno, rows=rows))
    except Exception:
        return blocks
    return blocks


def build_index(
    path: str | Path, *, source_id: str | None = None, with_tables: bool = True
) -> DocIndex:
    """Build a `DocIndex` from a PDF. Requires PyMuPDF (``pymupdf``)."""
    import fitz  # PyMuPDF

    path = Path(path)
    sid = source_id or path.stem
    doc = fitz.open(str(path))
    pages: list[str] = []
    sections: list[Section] = []
    captions: list[Caption] = []
    needs_ocr: list[int] = []
    try:
        for pno in range(doc.page_count):
            text = doc[pno].get_text() or ""
            pages.append(text)
            if len(text.strip()) < _MIN_CHARS_PER_PAGE:
                needs_ocr.append(pno + 1)
                continue
            flat = re.sub(r"\n+", " ", text)
            captions.extend(_find_captions(flat, pno + 1))
            sections.extend(_find_sections(text, pno + 1))
        n_pages = doc.page_count
    finally:
        doc.close()

    tables = _extract_tables(path) if with_tables else []
    return DocIndex(
        source_id=sid,
        path=str(path),
        sha1=_sha1(path),
        n_pages=n_pages,
        pages=pages,
        sections=sections,
        tables=tables,
        captions=captions,
        needs_ocr_pages=needs_ocr,
    )
