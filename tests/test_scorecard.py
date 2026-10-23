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


def test_live_build_has_no_nbs_number_and_covers_all_priorities():
    b = S.build(ROOT / "schema")
    assert b["nbs"]
    for v in b["nbs"].values():
        assert "score" not in v  # D3: no NbS-level number
        assert v["themes"] and v["hazards"]
        assert sum(v["counts"].values()) == len(v["priorities"])
        assert all(
            p in [q["priority"] for q in v["priorities"]]
            for p in v["evidenced_priorities"]
        )
