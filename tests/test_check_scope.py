"""Tests for the 2026-07 sweep-retro additions to check_scope: `land_capability`
(AOI-constraining land-capability schemes → constrained_aoi) and `land_cover_no_classes`
(a land_cover quote naming no in/out classes)."""

from __future__ import annotations

import csv

from nbs_ruralscan.schema_tools.check_scope import check

_FIELDS = [
    "evidence_id",
    "variable",
    "use_role",
    "quote",
    "review_state",
    "reviewer_ok",
]


def _write(tmp_path, rows):
    p = tmp_path / "EV.csv"
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in _FIELDS})
    return p


def _row(eid, variable, quote, **kw):
    return {
        "evidence_id": eid,
        "variable": variable,
        "use_role": "structural_suitability",
        "quote": quote,
        **kw,
    }


def _sig(flags, eid):
    return next((f["signal"] for f in flags if f["evidence_id"] == eid), None)


def test_land_capability_flags_residual_classification(tmp_path):
    p = _write(
        tmp_path,
        [
            _row(
                "ev_inab",
                "slope",
                "The INAB land-capability classification assigns agroforestry to "
                "marginal land after prime agriculture and protection forest.",
            )
        ],
    )
    assert _sig(check(p), "ev_inab") == "land_capability"


def test_land_cover_without_classes_flagged(tmp_path):
    p = _write(
        tmp_path,
        [
            _row(
                "ev_lc",
                "land_cover",
                "Land cover is an important suitability variable.",
            )
        ],
    )
    assert _sig(check(p), "ev_lc") == "land_cover_no_classes"


def test_land_cover_with_classes_not_flagged(tmp_path):
    p = _write(
        tmp_path,
        [
            _row(
                "ev_lc_ok",
                "land_cover",
                "Suitable classes are cropland and grassland; forest and water are excluded.",
            )
        ],
    )
    assert _sig(check(p), "ev_lc_ok") is None


def test_resolved_and_dropped_rows_skipped(tmp_path):
    p = _write(
        tmp_path,
        [
            _row("ev_ok", "land_cover", "land cover variable", reviewer_ok="true"),
            _row(
                "ev_drop", "land_cover", "land cover variable", review_state="dropped"
            ),
        ],
    )
    assert check(p) == []


def test_plain_suitability_quote_not_flagged(tmp_path):
    p = _write(
        tmp_path,
        [
            _row(
                "ev_slope",
                "slope",
                "Slopes below 15% are highly suitable for alley cropping.",
            )
        ],
    )
    assert check(p) == []
