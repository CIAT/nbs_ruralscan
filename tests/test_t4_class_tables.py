"""Audit tables preserve categorical evidence without inventing memberships."""

import runpy
from pathlib import Path

entries = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "scripts/tabulate-t4-classes.py")
)["class_entries"]


def test_source_ranks_do_not_become_membership_scores():
    rows = entries({"classes": [{"range": "6.6-7.3", "rank": 4, "label": "Very high"}]})
    assert rows == [("6.6-7.3", "Very high; rank 4", "", "classes")]


def test_land_categories_each_remain_visible_without_scores():
    rows = entries(
        {
            "highly_suitable_classes": ["Agriculture", "Scrubland"],
            "not_suitable_classes": ["Water", "Built up area"],
        }
    )
    assert [r[0] for r in rows] == [
        "Agriculture",
        "Scrubland",
        "Water",
        "Built up area",
    ]
    assert all(r[2] == "" for r in rows)


def test_drainage_codes_remain_source_codes():
    rows = entries({"very_good_code": 4, "good_codes": "3,6"})
    assert [(r[0], r[1]) for r in rows] == [
        ("4", "very_good"),
        ("3", "good"),
        ("6", "good"),
    ]


def test_missing_class_encoding_is_explicit():
    rows = entries({"threshold": 46.42, "unit": "percent allocated area"})
    assert rows == [("", "No explicit category mapping encoded", "", "unresolved")]
