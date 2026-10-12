"""check_quote — narrow AND over-wide quotes (ruleset v1.6.8)."""

from __future__ import annotations

from nbs_ruralscan.schema_tools import check_quote as cq


def test_short_quote_is_flagged():
    assert cq._fragment("30-40 pt") == f"<{cq.MIN_WORDS}w"


def test_full_sentence_passes():
    assert (
        cq._fragment(
            "Zai pits gave 300 to 400 kg of sorghum in a year of low rainfall on land that otherwise yielded nothing at all."
        )
        is None
    )


def test_whole_table_is_flagged():
    q = "Table 2. " + " ".join(f"row{i} value {i}" for i in range(cq.MAX_WORDS))
    why = cq._fragment(q)
    assert why and "whole table" in why


def test_translated_quote_gets_double_budget():
    body = "Les terres terrassees ont produit des rendements superieurs " * 10
    q = (
        "Resultat: "
        + body
        + " (English: Terraced land produced higher yields "
        + body
        + ")"
    )
    assert len(q.split()) > cq.MAX_WORDS
    assert cq._fragment(q) is None
