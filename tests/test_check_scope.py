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
    "relationship",
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


# --- site_context (catalogue #16): study-site / figure / region context, not a rule ---

# Cases the pure-quote `study_site` signal MISSES → the site_context block must catch them.
# (A quote naming "study area"/"located in" is already caught upstream as study_site.)
_SITE_CASES = [
    (
        "ev_site_rain",  # site point-value via the AI's `site_envelope` direction tell
        "The annual rainfall is about 900 mm/yr and average annual temperature is 28 C.",
        '{"direction": "site_envelope_where_FMNR_occurs"}',
    ),
    (
        "ev_fig",  # figure caption describing the study's data
        "Extended Figure 1: Country level counts trees for croplands experiencing more than 300mm.",
        '{"direction": "lower_bound"}',
    ),
    (
        "ev_region",  # geographic region-extent context
        "Au Mali, le sahel couvre 320 000 km2, environ 26% du territoire national.",
        "",
    ),
]

_RULE_CASES = [
    # (id, quote, relationship_json) — a generalising RULE, must NOT be flagged
    (
        "ev_envelope",
        "FMNR in Africa is confined to a wide range of mean annual rainfall of between 100 and 950 mm.",
        '{"direction": "envelope"}',
    ),
    (
        "ev_gradient",
        "These zones reflect the banding of rainfall isohyets along a north-south gradient.",
        "",
    ),
    (
        "ev_suitable",
        "Suitable climate: annual rainfall 250 to 600 mm; suitable on degraded land.",
        '{"direction": "suitable_range"}',
    ),
    (
        "ev_requires",
        "Natural regeneration requires existing stumps or rootstock in the soil.",
        '{"direction": "required_regeneration_source"}',
    ),
]


def test_site_context_flags_study_context(tmp_path):
    p = _write(
        tmp_path,
        [
            _row(eid, "annual_precipitation", q, relationship=rel)
            for eid, q, rel in _SITE_CASES
        ],
    )
    flagged = {f["evidence_id"] for f in check(p) if f["signal"] == "site_context"}
    assert flagged == {eid for eid, _, _ in _SITE_CASES}


def test_site_context_keeps_generalising_rules(tmp_path):
    p = _write(
        tmp_path,
        [
            _row(eid, "annual_precipitation", q, relationship=rel)
            for eid, q, rel in _RULE_CASES
        ],
    )
    assert [f for f in check(p) if f["signal"] == "site_context"] == []
