"""Title-identity guards in verify_metadata (2026-10-29: Donato 2012 cached for Bock 1978)."""

from nbs_ruralscan.schema_tools import verify_metadata as V

T = "A Comparison of Planting and Natural Succession After a Forest Fire in the Northern Sierra Nevada"


def test_title_in_reference_list_is_not_identity():
    page = (
        "Discussion ... References\nBock, J.H. & Bock, C.E. (1978) "
        + T
        + ". J. Appl. Ecol. 15"
    )
    assert V._cited_not_titled(T, page)


def test_title_as_chapter_heading_is_identity():
    page = "Chapter 9\n" + T + "\nJ.H. Bock\nAbstract. Planting after fire ..."
    assert not V._cited_not_titled(T, page)


def test_hand_confirmed_marker_constant():
    assert V.HAND_CONFIRMED == "[title: confirmed by hand]"
