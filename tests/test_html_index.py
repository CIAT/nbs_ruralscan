"""Tests for HTML → DocIndex builder (html.py) and build_index dispatch."""

from __future__ import annotations

from pathlib import Path

import pytest

from nbs_ruralscan.ingest.html import build_html_index
from nbs_ruralscan.ingest.pdf import build_index
from nbs_ruralscan.ingest.retrieve import retrieve


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

_SIMPLE_HTML = b"""
<!DOCTYPE html>
<html>
  <head><title>Agroforestry Review</title></head>
  <body>
    <h1>Introduction</h1>
    <p>Agroforestry systems improve soil organic matter and reduce runoff.</p>
    <h2>Methods</h2>
    <p>Slope of terrain was measured at 15% gradient.</p>
    <h3>Study Site</h3>
    <p>Sites were selected in humid tropics with annual rainfall over 1200 mm.</p>
    <h2>Results</h2>
    <p>Tree canopy cover reached 35% after three years.</p>
  </body>
</html>
"""

_FLAT_HTML = b"""
<!DOCTYPE html>
<html>
  <body>
    <p>A flat page with no headings.  Rainfall is 800 mm per year.</p>
    <p>Soil drainage was well-drained throughout.</p>
  </body>
</html>
"""

_BOILERPLATE_HTML = b"""
<!DOCTYPE html>
<html>
  <body>
    <nav>Navigation links</nav>
    <header>Site header</header>
    <h1>Content Section</h1>
    <p>Slope limit is 30 degrees.</p>
    <footer>Footer text</footer>
    <script>alert('hi');</script>
    <style>body { color: red; }</style>
  </body>
</html>
"""


def _write_html(tmp_path: Path, name: str, content: bytes) -> Path:
    p = tmp_path / name
    p.write_bytes(content)
    return p


# ---------------------------------------------------------------------------
# build_html_index: structure
# ---------------------------------------------------------------------------


def test_sections_parsed_from_headings(tmp_path):
    """h1–h4 headings become Section entries."""
    path = _write_html(tmp_path, "test.html", _SIMPLE_HTML)
    idx = build_html_index(path)
    titles = [s.title for s in idx.sections]
    assert any("Introduction" in t for t in titles)
    assert any("Methods" in t for t in titles)
    assert any("Results" in t for t in titles)
    assert any("Study Site" in t for t in titles)  # h3 sub-heading


def test_pages_non_empty(tmp_path):
    """pages list must be non-empty and each page must have some text."""
    path = _write_html(tmp_path, "test.html", _SIMPLE_HTML)
    idx = build_html_index(path)
    assert idx.n_pages >= 1
    assert len(idx.pages) == idx.n_pages
    assert all(p.strip() for p in idx.pages), "every page should have text"


def test_n_pages_matches_h1h2_count(tmp_path):
    """Number of pages equals number of h1/h2 headings (plus pre-heading prose if any)."""
    path = _write_html(tmp_path, "test.html", _SIMPLE_HTML)
    idx = build_html_index(path)
    # _SIMPLE_HTML has: Introduction (h1), Methods (h2), Results (h2) → 3 sections
    # pre-heading content is empty so exactly 3 pages
    assert idx.n_pages == 3


def test_flat_html_single_page(tmp_path):
    """An HTML file with no h1/h2 headings produces exactly one page."""
    path = _write_html(tmp_path, "flat.html", _FLAT_HTML)
    idx = build_html_index(path)
    assert idx.n_pages == 1
    assert len(idx.pages) == 1


def test_boilerplate_stripped(tmp_path):
    """nav, header, footer, script, style must not appear in page text."""
    path = _write_html(tmp_path, "bp.html", _BOILERPLATE_HTML)
    idx = build_html_index(path)
    full = "\n".join(idx.pages).lower()
    assert "navigation links" not in full
    assert "site header" not in full
    assert "footer text" not in full
    assert "alert(" not in full
    assert "color: red" not in full
    # Real content must survive
    assert "slope limit" in full


def test_source_id_default_is_stem(tmp_path):
    """source_id defaults to path.stem when not supplied."""
    path = _write_html(tmp_path, "SRC_042.html", _SIMPLE_HTML)
    idx = build_html_index(path)
    assert idx.source_id == "SRC_042"


def test_source_id_override(tmp_path):
    """Explicit source_id is used instead of stem."""
    path = _write_html(tmp_path, "some_file.html", _SIMPLE_HTML)
    idx = build_html_index(path, source_id="SRC_CUSTOM")
    assert idx.source_id == "SRC_CUSTOM"


def test_needs_ocr_pages_always_empty(tmp_path):
    """HTML documents never require OCR."""
    path = _write_html(tmp_path, "test.html", _SIMPLE_HTML)
    idx = build_html_index(path)
    assert idx.needs_ocr_pages == []


def test_sha1_set(tmp_path):
    """sha1 field must be populated and non-empty."""
    path = _write_html(tmp_path, "test.html", _SIMPLE_HTML)
    idx = build_html_index(path)
    assert idx.sha1 and len(idx.sha1) >= 8


# ---------------------------------------------------------------------------
# retrieve integration
# ---------------------------------------------------------------------------


def test_retrieve_returns_passage_for_present_term(tmp_path):
    """retrieve() on an HTML-built index returns a page-stamped passage for a present term."""
    path = _write_html(tmp_path, "test.html", _SIMPLE_HTML)
    idx = build_html_index(path)
    results = retrieve(idx, ["runoff"])
    assert len(results) >= 1
    assert any("runoff" in p.text.lower() for p in results)
    # page number must be a valid 1-based integer within n_pages
    for p in results:
        assert 1 <= p.page <= idx.n_pages


def test_retrieve_no_results_for_absent_term(tmp_path):
    """retrieve() returns empty list when the term is not in the document."""
    path = _write_html(tmp_path, "test.html", _SIMPLE_HTML)
    idx = build_html_index(path)
    assert retrieve(idx, ["cryosphere"]) == []


def test_retrieve_slope_with_numeric(tmp_path):
    """retrieve() surfaces the passage containing slope + threshold."""
    path = _write_html(tmp_path, "test.html", _SIMPLE_HTML)
    idx = build_html_index(path)
    results = retrieve(idx, ["slope"])
    assert any("15%" in p.text or "slope" in p.text.lower() for p in results)


def test_retrieve_section_heading_hit(tmp_path):
    """A term in a heading triggers a section passage."""
    path = _write_html(tmp_path, "test.html", _SIMPLE_HTML)
    idx = build_html_index(path)
    results = retrieve(idx, ["Methods"])
    section_hits = [p for p in results if p.kind == "section"]
    assert any("Methods" in p.text for p in section_hits)


# ---------------------------------------------------------------------------
# build_index dispatch
# ---------------------------------------------------------------------------


def test_build_index_dispatches_html(tmp_path):
    """build_index routes .html files to build_html_index (no PyMuPDF needed)."""
    path = _write_html(tmp_path, "doc.html", _FLAT_HTML)
    idx = build_index(path)
    assert idx.source_id == "doc"
    assert idx.n_pages >= 1


def test_build_index_dispatches_htm(tmp_path):
    """build_index routes .htm extension the same as .html."""
    path = _write_html(tmp_path, "doc.htm", _FLAT_HTML)
    idx = build_index(path)
    assert idx.n_pages >= 1


def test_build_index_unsupported_extension_raises(tmp_path):
    """build_index raises NotImplementedError for unknown extensions."""
    p = tmp_path / "doc.docx"
    p.write_bytes(b"fake")
    with pytest.raises(NotImplementedError, match=r"\.docx"):
        build_index(p)
