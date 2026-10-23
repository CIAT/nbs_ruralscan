"""Dashboard scorecard layer (decisions D3–D7, runtime/scorecard.py)."""

from __future__ import annotations

from pathlib import Path

from nbs_ruralscan.runtime import scorecard as S

ROOT = Path(__file__).resolve().parents[1]
SC = S.load_scale(ROOT / "schema")


def _row(cls, conf="high", **j):
    return {
        "record_id": "r",
        "effect_direction": cls,
        "effect_confidence": conf,
        "justification": j,
    }


def _c(cls, conf="high", **j):
    return S.chip(_row(cls, conf, **j), "effect_direction", "effect_confidence", SC)


def test_chip_scale_d6():
    assert _c("strong_positive")["glyph"] == "++"
    assert _c("slight_positive")["glyph"] == "+"
    assert _c("no_relationship")["glyph"] == "0"
    assert _c("moderate_negative")["glyph"] == "−−"
    assert _c("conflicting_evidence")["glyph"] == "±"
    assert _c("", data_deficient=True)["glyph"] == "?"
    assert S.chip(None, "effect_direction", "effect_confidence", SC)["glyph"] == "n/a"
    assert _c("slight_positive", "very_high")["badge"] == "HIGH"
    assert _c("slight_positive", "medium")["badge"] == "MED"
    assert _c("slight_positive", "very_low")["badge"] == "LOW"


def test_caution_is_measured_harm():
    assert _c("moderate_positive", maladaptation={"n_units": 2})["caution"] is True
    assert _c("moderate_positive")["caution"] is False


def test_theme_median_ignores_low_confidence_rows():
    chips = [
        _c("strong_positive"),
        _c("slight_positive", "medium"),
        _c("strong_negative", "low"),
    ]
    t = S.theme_chip(chips, [2, 2, 2], SC)
    assert (
        t["glyph"] in ("+", "++") and t["confidence"] == "medium"
    )  # weakest setting row
    assert len(t["setting_rows"]) == 2


def test_theme_dissent_states_disagreement():
    chips = [_c("strong_positive"), _c("moderate_negative")]
    assert S.theme_chip(chips, [2, 2], SC)["glyph"] == "±"


def test_ttl_weights_move_the_median():
    chips = [_c("strong_positive"), _c("slight_positive"), _c("slight_positive")]
    assert S.theme_chip(chips, [2, 2, 2], SC)["glyph"] == "+"
    assert S.theme_chip(chips, [3, 1, 1], SC)["glyph"] == "++"


def test_theme_without_setting_rows():
    assert S.theme_chip([_c("strong_positive", "low")], [2], SC)["glyph"] == "?"
    na = S.chip(None, "effect_direction", "effect_confidence", SC)
    assert S.theme_chip([na], [2], SC)["glyph"] == "n/a"


def test_rows_are_the_mockup_rows():
    rows = S.load_rows(ROOT / "schema")
    labels = [r["label"] for r in rows]
    assert labels[:4] == ["Erosion risk", "Drought", "Flood hazard", "Heat stress"]
    assert {
        "Biodiversity loss",
        "Rural poverty",
        "Gender inequality",
        "Food insecurity",
    } <= set(labels)
    srcs = "|".join(r["sources"] for r in rows)
    # fire is a project risk; production gap is an intermediate step (Pete 2026-10-23)
    assert "fire" not in srcs and "production_gap" not in srcs


def test_live_build_has_no_groups_and_pools_the_water_row():
    b = S.build(ROOT / "schema")
    for v in b["nbs"].values():
        assert "groups" not in v and "score" not in v
        water = next(r for r in v["rows"] if r["row_id"] == "water_table")
        assert len(water["sources"]) == 3
        assert sum(v["counts"].values()) == len(v["rows"])


def test_food_security_routes_to_food_insecurity():
    import csv

    xw = list(
        csv.DictReader(
            (ROOT / "schema/registers/XW_target_crosswalk.csv").open(encoding="utf-8")
        )
    )
    t6 = [
        x
        for x in xw
        if x["ev_variable"] == "food_security" and x["target_table"] == "T6"
    ]
    assert t6 and all(x["target_key"] == "food_insecurity" for x in t6)


def test_row_label_is_the_problem_name_not_the_chip_label():
    b = S.build(ROOT / "schema")
    v = next(iter(b["nbs"].values()))
    labels = {r["row_id"]: r["label"] for r in v["rows"]}
    assert labels["gender"] == "Gender inequality"
    assert labels["food_insecurity"] == "Food insecurity"
