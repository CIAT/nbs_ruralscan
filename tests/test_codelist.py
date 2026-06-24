"""Tests for categorical code-list decoding (issue #102)."""

import pytest

from nbs_ruralscan.runtime import codelist

_SARAHEB3 = (
    "cropLandcover.lte(61).or(cropLandcover.gte(205).and(cropLandcover.lte(209)))"
    ".or((cropLandcover.gte(213)).and((cropLandcover.neq(215)).and(cropLandcover.neq(217))"
    ".and(cropLandcover.neq(218)).and(cropLandcover.neq(220)).and(cropLandcover.neq(223))))"
)


def test_load_and_decode():
    legend = codelist.load("cdl")
    assert legend[1] == "Corn"
    assert legend[215] == "Avocados"
    assert codelist.decode("cdl", [1, 5, 999]) == [
        (1, "Corn"),
        (5, "Soybeans"),
        (999, ""),  # unknown code → blank label, no crash
    ]


def test_cdl_mask_selects_annual_crops_not_trees():
    codes = codelist.codes_from_cdl_mask(_SARAHEB3)
    # annual crops in
    assert {1, 5, 61, 205, 241}.issubset(codes)
    # NOT pasture/forest/tree-crops/developed/water (the "not tree crops" intent)
    for excluded in (62, 63, 66, 71, 82, 83, 215, 217, 218, 220, 223):
        assert excluded not in codes, f"{excluded} should be excluded"


def test_summarise_lists_excluded_tree_crops():
    s = codelist.summarise_cdl_mask(_SARAHEB3)
    excluded = dict(s["excluded"])
    assert excluded == {
        215: "Avocados",
        217: "Pomegranates",
        218: "Nectarines",
        220: "Plums",
        223: "Apricots",
    }
    assert s["n_included"] == len(s["included"]) > 80


def test_mask_eval_is_sandboxed():
    # a predicate that doesn't translate to safe arithmetic must be refused, not eval'd
    with pytest.raises(ValueError):
        codelist.codes_from_cdl_mask("band.lte(5).or(__import__('os').system('x'))")


def test_scheme_routing():
    assert codelist.scheme_for(dataset="usda_cdl") == "cdl"
    assert (
        codelist.scheme_for(dataset="HWSD") == "hwsd_soil_quality"
    )  # case-insensitive
    assert codelist.scheme_for(variable="slope") is None


def test_expand_codes():
    assert codelist.expand_codes("1-4") == [1, 2, 3, 4]
    assert codelist.expand_codes("5-7") == [5, 6, 7]
    assert codelist.expand_codes("1,2,5") == [1, 2, 5]
    assert codelist.expand_codes("1-3,7") == [1, 2, 3, 7]
    assert codelist.expand_codes("") == []


def test_hwsd_class_ranges_decode():
    s = codelist.summarise_class_ranges("hwsd_soil_quality", "1-4", "5-7")
    assert s["n_included"] == 4
    inc = dict(s["included"])
    assert inc[1].startswith("No or slight")
    assert inc[4].startswith("Very severe")
    exc = dict(s["excluded"])
    assert exc[5] == "Mainly non-soil"
    assert exc[6] == "Permafrost area"
    assert exc[7] == "Water bodies"
