"""Tests for CSV -> JSON schema generation."""

from __future__ import annotations

import json
from pathlib import Path

from nbs_ruralscan.generate import _coerce, _csv_to_rows, generate

SCHEMA = Path(__file__).resolve().parents[1] / "schema"


def test_coerce_types():
    assert _coerce("1000") == 1000
    assert _coerce("true") is True
    assert _coerce('["a","b"]') == ["a", "b"]
    assert _coerce('{"min":2}') == {"min": 2}
    assert _coerce("v2.1") == "v2.1"  # not valid JSON -> raw string
    assert _coerce("10.1038/sdata") == "10.1038/sdata"
    assert _coerce("") is None  # empty -> dropped


def test_empty_cells_dropped(tmp_path):
    csv = tmp_path / "t.csv"
    csv.write_text("a,b,c\n1,,x\n")
    assert _csv_to_rows(csv) == [{"a": 1, "c": "x"}]


def test_committed_json_is_in_sync():
    """The repo's JSON must match what the generator produces from the CSVs."""
    assert generate(SCHEMA, check=True) == []


def test_roundtrip_is_valid_json():
    for jp in SCHEMA.rglob("*.json"):
        json.loads(jp.read_text())  # raises if malformed
