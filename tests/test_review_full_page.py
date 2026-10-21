"""Source context must survive quote matching and legacy committed crops."""

import fitz

from nbs_ruralscan.schema_tools.review_server import render_region_png


def test_full_page_retains_caption_and_both_columns(tmp_path):
    pdf = tmp_path / "source.pdf"
    doc = fitz.open()
    page = doc.new_page(width=600, height=900)
    page.insert_text((40, 50), "Table 2. Caption above the quote")
    page.insert_text((40, 820), "Quoted cell in left column")
    page.insert_text((350, 70), "Continuation in right column")
    doc.save(pdf)
    doc.close()
    quote = "Quoted cell in left column"
    full = fitz.Pixmap(render_region_png(pdf, quote, 1, full_page=True))
    crop = fitz.Pixmap(render_region_png(pdf, quote, 1))
    assert abs(full.width / full.height - 600 / 900) < 0.001
    assert crop.width / crop.height > full.width / full.height
    assert full.height >= 2500
