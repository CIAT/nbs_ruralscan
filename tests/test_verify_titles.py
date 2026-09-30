from nbs_ruralscan.schema_tools.verify_metadata import (
    TITLE_THRESH,
    _title_coverage,
    _title_of,
)


def test_title_of_extracts_title_segment():
    c = "Critchley, W.; Siegert, K. (1991). Water harvesting: a manual for the design and construction of water harvesting schemes. FAO, Rome."
    assert _title_of(c).startswith("Water harvesting: a manual")
    assert "FAO" not in _title_of(c)


def test_title_of_falls_back_to_whole_citation():
    assert _title_of("Untitled grey report") == "Untitled grey report"


def test_coverage_passes_when_title_is_on_the_cover():
    title = "Global guidelines for the restoration of degraded forests and landscapes in drylands"
    cover = "FAO FORESTRY PAPER 175 Global guidelines for the restoration of degraded forests and landscapes in drylands Building resilience"
    assert _title_coverage(title, cover) >= TITLE_THRESH


def test_coverage_fails_on_the_wrong_document():
    title = "Contour ridges for water harvesting in semi-arid Zimbabwe"
    wrong = "A multiplier-based method of generating stochastic areal rainfall from point rainfalls"
    assert _title_coverage(title, wrong) < TITLE_THRESH
