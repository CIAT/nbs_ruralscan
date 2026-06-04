"""PDF → structure-aware `DocIndex`.

Deterministic, no model tokens. PyMuPDF for fast page text + caption/section
detection; pdfplumber for tables — ruled-line first, then a **text-layout fallback**
for borderless tables (targeted to pages that announce a "Table N", so prose isn't
turned into fake tables). Each table is linked to its nearest caption. Pages with
little/no extractable text are flagged ``needs_ocr``; `render_page_png` exposes a
single page image for a targeted figure-vision pass when a threshold lives only in a
figure (born-digital papers need neither).
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
_HAS_NUMBER = re.compile(r"\d")

_MIN_CHARS_PER_PAGE = 80  # below this → likely scanned/needs OCR
_TEXT_TABLE_SETTINGS = {
    "vertical_strategy": "text",
    "horizontal_strategy": "text",
    "min_words_vertical": 2,
    "min_words_horizontal": 1,
}


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


def _clean_rows(raw: list[list]) -> list[list[str]]:
    return [
        [("" if c is None else str(c).strip()) for c in row]
        for row in raw
        if any(c not in (None, "") for c in row)
    ]


def _keep(rows: list[list[str]], *, require_numeric: bool) -> bool:
    if len(rows) < 2 or len(rows[0]) > 40:
        return False
    if require_numeric:
        return any(_HAS_NUMBER.search(c) for row in rows for c in row)
    return True


def _extract_tables(path: Path, text_fallback_pages: set[int]) -> list[TableBlock]:
    """Ruled-line tables first; text-layout fallback only on pages that announce a table."""
    try:
        import pdfplumber
    except ImportError:
        return []
    blocks: list[TableBlock] = []
    try:
        with pdfplumber.open(str(path)) as pdf:
            for pno, page in enumerate(pdf.pages, start=1):
                found = False
                for tbl in page.extract_tables() or []:
                    rows = _clean_rows(tbl)
                    if _keep(rows, require_numeric=False):
                        blocks.append(TableBlock(page=pno, rows=rows))
                        found = True
                if not found and pno in text_fallback_pages:
                    for tbl in page.extract_tables(_TEXT_TABLE_SETTINGS) or []:
                        rows = _clean_rows(tbl)
                        if _keep(rows, require_numeric=True):  # stricter for borderless
                            blocks.append(TableBlock(page=pno, rows=rows))
    except Exception:
        return blocks
    return blocks


def _link_captions(tables: list[TableBlock], captions: list[Caption]) -> None:
    """Attach each table to a table-caption on the same page (in order)."""
    by_page: dict[int, list[Caption]] = {}
    for c in captions:
        if c.kind == "table":
            by_page.setdefault(c.page, []).append(c)
    used: dict[int, int] = {}
    for t in tables:
        caps = by_page.get(t.page)
        if caps:
            i = min(used.get(t.page, 0), len(caps) - 1)
            t.caption, t.label = caps[i].text, caps[i].label
            used[t.page] = i + 1


def render_page_png(path: str | Path, page: int, *, dpi: int = 150) -> bytes:
    """Render one page (1-based) to PNG bytes — for a *targeted* figure-vision pass."""
    import fitz

    doc = fitz.open(str(path))
    try:
        return doc[page - 1].get_pixmap(dpi=dpi).tobytes("png")
    finally:
        doc.close()


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

    tables: list[TableBlock] = []
    if with_tables:
        table_pages = {c.page for c in captions if c.kind == "table"}
        tables = _extract_tables(path, table_pages)
        _link_captions(tables, captions)

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
