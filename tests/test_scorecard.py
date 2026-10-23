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


def test_live_build_uses_benefit_rows_and_never_scores_flags():
    b = S.build(ROOT / "schema")
    rows = S.load_rows(ROOT / "schema")
    assert {r["group"] for r in rows} >= {
        "climate_resilience",
        "land_water",
        "nature_carbon",
        "livelihoods",
    }
    # food security and rural income are separate rows (Pete 2026-10-23)
    keys = {r["source_key"] for r in rows}
    assert {"food_insecurity", "rural_poverty"} <= keys
    # T6 hazard priorities duplicate T3 and agricultural_dependency can never be evidenced
    assert not keys & {
        "drought_hazard",
        "flood_hazard",
        "heat_stress_hazard",
        "agricultural_dependency",
    }
    for v in b["nbs"].values():
        assert "score" not in v  # D3: no NbS-level number
        assert "context_flags" not in v["groups"]
        assert sum(v["counts"].values()) == sum(1 for r in v["rows"] if r["scored"])


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


def test_row_label_is_the_benefit_name_not_the_chip_label():
    b = S.build(ROOT / "schema")
    v = next(iter(b["nbs"].values()))
    labels = {r["row_id"]: r["label"] for r in v["rows"]}
    assert labels["gender_flag"] == "Gender inequity"
    assert labels["food_security"] == "Food security"
