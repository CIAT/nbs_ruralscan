"""Tests for the vectorless retrieval and window-merging logic."""

from nbs_ruralscan.ingest.models import DocIndex, TableBlock
from nbs_ruralscan.ingest.retrieve import retrieve


def test_retrieve_no_matches():
    index = DocIndex(
        source_id="test_doc",
        path="test.pdf",
        sha1="abcdef123",
        n_pages=1,
        pages=["This is some random text about crops and weather."],
    )
    res = retrieve(index, ["slope"])
    assert len(res) == 0


def test_retrieve_separate_matches():
    index = DocIndex(
        source_id="test_doc",
        path="test.pdf",
        sha1="abcdef123",
        n_pages=1,
        pages=[
            "The slope of the landscape is 5%. "
            + "A lot of unrelated text goes here in the middle to make sure they do not overlap. "
            * 20
            + "Rainfall is 1200mm annually."
        ],
    )
    res = retrieve(index, ["slope", "rainfall"], window=100)
    assert len(res) == 2
    # Check that they retrieved different snippets
    texts = [p.text.lower() for p in res]
    assert any("slope" in t for t in texts)
    assert any("rainfall" in t for t in texts)


def test_retrieve_overlapping_matches_merged():
    """Matches that are close to each other should be merged into a single snippet."""
    index = DocIndex(
        source_id="test_doc",
        path="test.pdf",
        sha1="abcdef123",
        n_pages=1,
        pages=["The slope of the terrain should be a gentle slope to prevent erosion."],
    )
    # The term 'slope' occurs twice close to each other.
    # With a window of 80, the two windows will overlap heavily.
    res = retrieve(index, ["slope"], window=80)
    assert len(res) == 1
    # It should contain both occurrences in a single merged snippet.
    assert "gentle slope" in res[0].text
    assert "The slope" in res[0].text


def test_retrieve_ranking_by_score():
    """Verify that passages with numbers/units and co-occurring terms get ranked higher."""
    index = DocIndex(
        source_id="test_doc",
        path="test.pdf",
        sha1="abcdef123",
        n_pages=2,
        pages=[
            "This page mentions slope and rainfall.",  # multiple terms, but no numeric threshold
            "Here is the slope limit: 15% gradient.",  # term + numeric threshold
        ],
    )
    # Both pages are retrieved, but the second one should rank higher
    res = retrieve(index, ["slope", "rainfall"], window=100)
    assert len(res) == 2
    assert res[0].page == 2  # Has numeric threshold "15%"
    assert "15%" in res[0].text
    assert res[1].page == 1


def test_retrieve_smart_table_filtering():
    # Setup index with a table block that has:
    # Col 0: Crop (keep)
    # Col 1: Study Location (irrelevant, drop)
    # Col 2: Rainfall (has numeric cell with unit, keep)
    # Col 3: Slope limit (matches term 'slope', keep)
    table = TableBlock(
        page=1,
        rows=[
            ["Crop", "Study Location", "Rainfall", "Slope limit"],
            ["Alley cropping", "Humid tropics", "1200mm", "15%"],
            ["Silvopastoral", "Semiarid", "400mm", "8%"],
        ],
        label="Table 1",
    )
    index = DocIndex(
        source_id="test_doc",
        path="test.pdf",
        sha1="abcdef123",
        n_pages=1,
        pages=["Table 1 contains slope values."],
        tables=[table],
    )

    # Query for slope
    res = retrieve(index, ["slope"])
    table_passages = [p for p in res if p.kind == "table"]
    assert len(table_passages) == 1
    passage = table_passages[0]

    # Verify that Study Location (Col 1) is dropped, but other columns are preserved
    text_rows = passage.text.split("\n")
    assert text_rows[0] == "Crop | Rainfall | Slope limit"
    assert text_rows[1] == "Alley cropping | 1200mm | 15%"
    assert text_rows[2] == "Silvopastoral | 400mm | 8%"


def test_retrieve_smart_table_truncation():
    # Table with 15 rows (more than the max limit of 12)
    # Header matches "slope" so table is retrieved
    rows = [["Header Col 0", "Slope limit"]]
    for i in range(15):
        rows.append([f"Row {i}", "10%"])

    table = TableBlock(
        page=1,
        rows=rows,
        label="Table 1",
    )
    index = DocIndex(
        source_id="test_doc",
        path="test.pdf",
        sha1="abcdef123",
        n_pages=1,
        pages=["Table 1 contains values."],
        tables=[table],
    )

    res = retrieve(index, ["slope"])
    table_passages = [p for p in res if p.kind == "table"]
    assert len(table_passages) == 1
    passage = table_passages[0]

    text_rows = passage.text.split("\n")
    # Should be exactly 12 rows of data + 1 row of truncation indicator = 13 total lines
    assert len(text_rows) == 13
    assert "... [table truncated]" in text_rows[-1]


def _spec_table_index(n_rows: int = 15) -> DocIndex:
    """A siting SPECIFICATION table: one row per structure, one column per criterion.

    The "Soil type" column is non-numeric and its header does not name the search term,
    so the default filter drops it — which is exactly the column an extractor needs.
    """
    rows = [["Structure", "Slope limit", "Soil type"]]
    for i in range(n_rows):
        rows.append([f"Structure {i}", f"{i + 1}%", "Sandy clay loam"])
    return DocIndex(
        source_id="spec_doc",
        path="spec.pdf",
        sha1="abc",
        n_pages=1,
        pages=["Table 6 gives the adopted specifications."],
        tables=[TableBlock(page=1, rows=rows, label="Table 6")],
    )


def test_default_retrieval_prunes_and_truncates_spec_tables():
    """Baseline the defect the full_tables option exists for (2026-09 sweeps)."""
    (passage,) = [
        p for p in retrieve(_spec_table_index(), ["slope"]) if p.kind == "table"
    ]
    assert "Soil type" not in passage.text
    assert passage.text.endswith("... [table truncated]")


def test_full_tables_keeps_every_row_and_column():
    """Extraction opts in: the whole specification table comes through unpruned."""
    (passage,) = [
        p
        for p in retrieve(_spec_table_index(), ["slope"], full_tables=True)
        if p.kind == "table"
    ]
    lines = passage.text.split("\n")
    assert lines[0] == "Structure | Slope limit | Soil type"
    assert len(lines) == 16  # header + all 15 rows
    assert "[table truncated]" not in passage.text
    assert lines[-1] == "Structure 14 | 15% | Sandy clay loam"


def test_full_tables_threads_through_the_extraction_packager(tmp_path):
    from nbs_ruralscan.recipe.evidence import package_for_extraction_multi

    ev = tmp_path / "EV.csv"
    ev.write_text("evidence_id,source_id,variable\n", encoding="utf-8", newline="\n")
    bundle = package_for_extraction_multi(
        _spec_table_index(),
        [{"variable": "slope"}],
        ev_register=ev,
        full_tables=True,
    )
    tables = [p for p in bundle["passages"] if p["kind"] == "table"]
    assert tables and "Soil type" in tables[0]["text"]
    assert "[table truncated]" not in tables[0]["text"]
