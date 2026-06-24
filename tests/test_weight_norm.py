"""Tests for cross-source weight normalisation (uninterpretable_weight synthesis half)."""

import csv
import json

from nbs_ruralscan.schema_tools import weight_norm

_FIELDS = ["evidence_id", "source_id", "variable", "relationship", "review_state"]


def _write(tmp_path, rows):
    reg = tmp_path / "registers"
    reg.mkdir(parents=True)
    with (reg / "EV_evidence_register.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        w = csv.DictWriter(f, fieldnames=_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in _FIELDS})
    return tmp_path


def test_normalise_each_basis(tmp_path):
    schema = _write(
        tmp_path,
        [
            # AHP share — already 0–1, unchanged, is_share
            {
                "evidence_id": "a",
                "source_id": "paperA",
                "variable": "slope",
                "relationship": json.dumps({"ahp_weight": 0.24}),
            },
            # tool slider 5 on a /10 criterion → intensity 0.5, NOT a share
            {
                "evidence_id": "b",
                "source_id": "toolB",
                "variable": "soil_erosion_risk",
                "relationship": json.dumps({"weight": 5, "criterion": "water_erosion"}),
            },
            # raw RF importance → normalised within source (3 / (3+1) = 0.75), becomes share
            {
                "evidence_id": "c1",
                "source_id": "rfC",
                "variable": "slope",
                "relationship": json.dumps({"variable_importance": 3.0}),
            },
            {
                "evidence_id": "c2",
                "source_id": "rfC",
                "variable": "precip",
                "relationship": json.dumps({"variable_importance": 1.0}),
            },
            # dropped row excluded
            {
                "evidence_id": "d",
                "source_id": "paperA",
                "variable": "ph",
                "relationship": json.dumps({"ahp_weight": 0.9}),
                "review_state": "dropped",
            },
        ],
    )
    items = {(i["source_id"], i["variable"]): i for i in weight_norm.normalise(schema)}

    assert items[("paperA", "slope")]["normalised"] == 0.24
    assert items[("paperA", "slope")]["is_share"] is True

    tool = items[("toolB", "soil_erosion_risk")]
    assert tool["normalised"] == 0.5  # 5/10
    assert tool["is_share"] is False  # intensity, not a share

    assert items[("rfC", "slope")]["normalised"] == 0.75  # 3/(3+1)
    assert items[("rfC", "slope")]["is_share"] is True  # share after ÷sum

    # dropped row never appears
    assert ("paperA", "ph") not in items


def test_compare_groups_by_variable(tmp_path):
    schema = _write(
        tmp_path,
        [
            {
                "evidence_id": "a",
                "source_id": "s1",
                "variable": "slope",
                "relationship": json.dumps({"ahp_weight": 0.2}),
            },
            {
                "evidence_id": "b",
                "source_id": "s2",
                "variable": "slope",
                "relationship": json.dumps({"weight": 4, "criterion": "x"}),
            },
        ],
    )
    cmp = weight_norm.compare(schema)
    assert set(cmp) == {"slope"}
    assert len(cmp["slope"]) == 2  # both sources, distinct bases preserved
    bases = {i["is_share"] for i in cmp["slope"]}
    assert bases == {True, False}  # share + intensity kept distinct, not merged
