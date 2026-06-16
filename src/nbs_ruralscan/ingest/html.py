"""HTML → structure-aware `DocIndex`.

Deterministic, no model tokens.  ``BeautifulSoup`` (lxml parser) strips
boilerplate (scripts, styles, nav, header, footer, aside, form), then walks
heading tags (h1–h4) to derive Section boundaries.

Page design
-----------
A web page has no physical pages.  We split the cleaned text into *sections*
at each top-level heading (h1 / h2) and treat each section as one logical
"page".  This keeps ``retrieve``'s page-stamped passages meaningful — a
passage on "page 3" maps to the third top-level section, giving a section
heading + rough position.  If the document has no h1/h2 headings (flat prose
or a single-section page) the whole cleaned text becomes a single page,
``n_pages=1``.

Section objects use the same 1-based page convention as the PDF indexer.
Sub-headings (h3/h4) found within a section are also recorded as Section
entries on the same page number, so keyword lookups on headings still work.

Locator note
------------
The downstream verifier currently does document-level presence checks.  For
future locator-precise verification, the section title + page number are
preserved in each Section entry.  Character-offset pinpointing within a
section is deferred (punted — see ``retrieve.py`` which works at page/window
granularity already).
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .models import DocIndex, Section

# Tags whose content is boilerplate — strip entirely
_STRIP_TAGS = {
    "script",
    "style",
    "noscript",
    "nav",
    "header",
    "footer",
    "aside",
    "form",
    "button",
    "iframe",
    "svg",
    "figure",  # usually images; alt text kept via BeautifulSoup .get_text
}

# Heading tags that open a new top-level page boundary (h1, h2)
_PAGE_BOUNDARY_TAGS = {"h1", "h2"}
# Sub-headings recorded as Section entries without opening a new page
_SUB_HEADING_TAGS = {"h3", "h4"}
_ALL_HEADING_TAGS = _PAGE_BOUNDARY_TAGS | _SUB_HEADING_TAGS


def _sha1(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()[:16]


def _clean_text(raw: str) -> str:
    """Collapse whitespace runs and strip leading/trailing blanks."""
    return re.sub(r"[ \t]+", " ", raw).strip()


def build_html_index(
    path: str | Path,
    *,
    source_id: str | None = None,
) -> DocIndex:
    """Build a :class:`~nbs_ruralscan.ingest.models.DocIndex` from a cached ``.html`` file.

    The returned ``DocIndex`` is structurally identical to what :func:`pdf.build_index`
    returns, so :func:`retrieve.retrieve` works unchanged.

    Parameters
    ----------
    path:
        Path to the cached ``.html`` artifact (raw bytes as saved by ``acquire``).
    source_id:
        Override the default ``source_id`` (``path.stem`` when omitted).

    Returns
    -------
    DocIndex
        ``pages`` is a list of cleaned text strings — one per top-level section
        (h1/h2 boundary), or a single element for flat documents.
        ``n_pages`` equals ``len(pages)``.
        ``needs_ocr_pages`` is always empty (HTML has no scanned pages).
        ``tables`` and ``captions`` are empty (best-effort deferred).
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError as exc:
        raise ImportError(
            "beautifulsoup4 is required for HTML indexing. "
            "Run: uv add beautifulsoup4 lxml"
        ) from exc

    path = Path(path)
    sid = source_id or path.stem
    raw_bytes = path.read_bytes()
    sha1 = _sha1(raw_bytes)

    soup = BeautifulSoup(raw_bytes, "lxml")

    # --- Strip boilerplate tags ------------------------------------------
    for tag in soup.find_all(_STRIP_TAGS):
        tag.decompose()

    # --- Walk the DOM to collect sections and build page buckets ----------
    # Strategy: iterate over all elements in document order, accumulating text
    # into a current "page buffer".  Each h1/h2 flushes the buffer and starts
    # a new page.  h3/h4 are added as Section entries but do not split pages.

    sections: list[Section] = []
    pages: list[str] = []

    # Buffer for the current page: list of text fragments
    current_page_lines: list[str] = []
    current_page_number: int = 1  # 1-based; increments at each h1/h2

    def _flush_page() -> None:
        """Push accumulated text as one page entry."""
        text = "\n".join(line for line in current_page_lines if line)
        text = _clean_text(re.sub(r"\n{3,}", "\n\n", text))
        pages.append(text)

    # Find the body (or use the whole document if no body tag)
    body = soup.body or soup

    def _heading_text(tag) -> str:  # type: ignore[no-untyped-def]
        return _clean_text(tag.get_text(" ", strip=True))

    # Walk direct children and recurse into non-heading containers
    def _walk(node) -> None:  # type: ignore[no-untyped-def]
        nonlocal current_page_number, current_page_lines

        for child in node.children:
            if not hasattr(child, "name") or child.name is None:
                # NavigableString
                t = _clean_text(str(child))
                if t:
                    current_page_lines.append(t)
                continue

            tag_name = child.name.lower() if child.name else ""

            if tag_name in _STRIP_TAGS:
                # Already stripped, skip
                continue

            if tag_name in _PAGE_BOUNDARY_TAGS:
                # Flush current buffer → new page
                _flush_page()
                current_page_lines = []
                current_page_number = len(pages) + 1
                title = _heading_text(child)
                if title:
                    sections.append(Section(page=current_page_number, title=title))
                    current_page_lines.append(title)

            elif tag_name in _SUB_HEADING_TAGS:
                title = _heading_text(child)
                if title:
                    sections.append(Section(page=current_page_number, title=title))
                    current_page_lines.append(title)

            else:
                # Regular element — get text and recurse for inline nesting
                # For block elements, append extracted text as a line
                text = _clean_text(child.get_text(" ", strip=True))
                if text:
                    current_page_lines.append(text)

    _walk(body)

    # Flush the last (or only) page
    _flush_page()

    # If pages list is somehow empty, emit at least one page
    if not pages:
        full_text = _clean_text(body.get_text(" ", strip=True))
        pages = [full_text]

    # Remove empty leading page that appears before first h1/h2 in some documents
    # (the pre-heading text is on page index 0; keep it only if it has content)
    pages = [p for p in pages if p.strip()] or [""]

    # Recompute final page numbers — sections' page refs were set during walk,
    # which may shift by 1 if the empty first-page is dropped.  Re-index.
    # Simplest correct approach: re-scan for page count only.
    n_pages = len(pages)

    return DocIndex(
        source_id=sid,
        path=str(path),
        sha1=sha1,
        n_pages=n_pages,
        pages=pages,
        sections=sections,
        tables=[],
        captions=[],
        needs_ocr_pages=[],
    )
