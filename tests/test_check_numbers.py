"""check_numbers tests."""

from __future__ import annotations

import copy
import csv
import json

import pytest

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


@pytest.mark.parametrize("space", [" ", "\u00a0", "\u2009", "\u202f"])
def test_observed_summary_catches_split_thousands_without_changing_classes(space):
    rel = {
        "type": "observed_presence",
        "observed_classes": [f"751 – 1{space}000 mm", f"1{space}001 – 1{space}500 mm"],
        "observed_min": 751,
        "observed_max": 1,
        "unit": "mm",
    }
    before = copy.deepcopy(rel)
    assert cn.observed_range_mismatches(rel) == [
        {"field": "observed_max", "stored": 1, "class_envelope": 1500.0}
    ]
    assert rel == before
    rel["observed_max"] = 1500
    assert cn.observed_range_mismatches(rel) == []


def test_observed_summary_preserves_disjoint_classes_and_decimal_units():
    rel = {
        "type": "observed_presence",
        "observed_classes": ["0.5–1.5 m", "3.5–4.5 m"],
        "observed_min": 0.5,
        "observed_max": 1.5,
        "unit": "m",
    }
    assert cn.observed_range_mismatches(rel) == [
        {"field": "observed_max", "stored": 1.5, "class_envelope": 4.5}
    ]
    assert rel["observed_classes"] == ["0.5–1.5 m", "3.5–4.5 m"]
    rel.update(observed_min=0.8, observed_max=4.0)
    assert cn.observed_range_mismatches(rel) == []  # measured extrema within bins


def test_overlapping_bins_allow_measured_extrema_but_not_reversed_bounds():
    rel = {
        "type": "observed_presence",
        "observed_classes": ["0–1000 mm", "200–300 mm"],
        "observed_min": 250,
        "observed_max": 500,
        "unit": "mm",
    }
    assert cn.observed_range_mismatches(rel) == []
    rel.update(observed_min=280, observed_max=250)
    assert "below observed minimum" in cn.observed_range_mismatches(rel)[0]["problem"]


@pytest.mark.parametrize(
    "classes,unit",
    [
        (["<500 mm", "501–750 mm"], "mm"),
        (["501–750 mm", ">1000 mm"], "mm"),
        (["0–1.000 mm"], "mm"),  # ambiguous decimal/thousands dot
        (["0–1,000 mm"], "mm"),
        (["751–1000 mm", "1–2 m"], "mm"),
        (["751–1000 mm"], "m"),  # no implicit unit conversion
        (["moderate (5–8%)"], "percent"),
        (["751–1000 mm", "unknown"], "mm"),
        (["1000–751 mm"], "mm"),
        ([], "mm"),
    ],
)
def test_observed_summary_does_not_guess_unparsed_classes(classes, unit):
    assert (
        cn.observed_range_mismatches(
            {
                "type": "observed_presence",
                "observed_classes": classes,
                "observed_max": 1,
                "unit": unit,
            }
        )
        == []
    )


def test_observed_summary_is_not_a_suitability_or_missing_field_rule():
    rel = {"observed_classes": ["751–1000 mm"], "unit": "mm", "abs_max": 1}
    assert cn.observed_range_mismatches(rel) == []
    rel["type"] = "observed_presence"
    assert cn.observed_range_mismatches(rel) == []


@pytest.mark.parametrize("value", ["1", True, [], {}, None, float("nan"), float("inf")])
def test_present_observed_summary_requires_a_finite_number(value):
    # Even unparsed/open classes cannot smuggle malformed numeric summary fields.
    rel = {"type": "observed_presence", "observed_classes": [">500 mm"]}
    rel["observed_max"] = value
    result = cn.observed_range_mismatches(rel)
    assert len(result) == 1
    assert result[0]["field"] == "observed_max"
    assert "finite number" in result[0]["problem"]


def test_register_check_flags_summary_even_when_number_occurs_in_quote(tmp_path):
    directory = tmp_path / "registers"
    directory.mkdir()
    rel = {
        "type": "observed_presence",
        "observed_classes": ["751 – 1 000 mm"],
        "observed_max": 1,
        "unit": "mm",
    }
    quote = "Observed rainfall class: 751 – 1 000 mm."
    assert "1" in cn._nums(quote)  # legacy containment is intentionally permissive
    with (directory / "EV_evidence_register.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, ["evidence_id", "source_id", "variable", "quote", "relationship"]
        )
        writer.writeheader()
        writer.writerow(
            {
                "evidence_id": "observed",
                "source_id": "source",
                "variable": "annual_precipitation",
                "quote": quote,
                "relationship": json.dumps(rel),
            }
        )
    findings = cn.check(tmp_path)
    assert len(findings) == 1
    assert findings[0]["missing_numbers"] == []
    assert findings[0]["observed_range_mismatches"] == [
        {"field": "observed_max", "stored": 1, "class_envelope": 1000.0}
    ]
