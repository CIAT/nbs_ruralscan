"""check_numbers tests."""

from __future__ import annotations

from nbs_ruralscan.schema_tools import check_numbers as cn


def test_provenance_tokens_are_not_numbers():
    rel = (
        '{"direction": "positive", "source_scale_value": "-1", "outcome_raw": '
        '"WOCAT impacts_ecological_climate.flood_impacts rated -1 on the \u22123\u2026+3 scale", '
        '"note": "superseded_by=ev_crop_yield_castle21s_1; prose-review backlog 2026-10-06"}'
    )
    assert cn._rel_nums(rel) == {"1"}  # the rating itself still has to be in the quote
    assert "2026" not in cn._rel_nums('{"note": "run 2026-10-04"}')
    assert (
        cn._rel_nums('{"outcome_raw": "WOCAT QT 6.3: copes well with drought"}')
        == set()
    )
    # publication years and real values still count
    assert "2021" in cn._rel_nums('{"note": "Castle 2021 pooled estimate"}')
    assert "1" in cn._rel_nums('{"outcome_raw": "1 fallen tree, 3 defoliated"}')


def test_nums_reads_fraction_words_ligatures_and_linebroken_thousands():
    """2026-10-21 retro: three provenance gaps the primaries-round lanes hit."""
    from nbs_ruralscan.schema_tools.check_numbers import _nums

    assert "4.5" in _nums("four and one-half or more times")
    assert {"5", "7"} <= _nums("ﬁve to seven times higher")
    assert "25000" in _nums("BDT 20,000-25,\n000 per year")


def test_half_rule_does_not_fire_on_alternation_keys():
    """'twice' or 'double' alone must not yield 2.5 (ungrouped alternation bug, 2026-10-22)."""
    from nbs_ruralscan.schema_tools.check_numbers import _nums

    assert "2.5" not in _nums("yield about twice that of the controls")
    assert "2.5" not in _nums("a double-basin masonry check dam")
    assert "4.5" in _nums("four and one-half or more times")
