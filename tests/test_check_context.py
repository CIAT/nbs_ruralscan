"""check_context — hazard-severity rules (ruleset v1.6.3)."""

from __future__ import annotations

import json

from nbs_ruralscan.schema_tools import check_context as cc


def _row(ctx: dict, quote: str = "yields fell in the severe drought of 1992") -> dict:
    return {
        "evidence_id": "ev_x",
        "use_role": "nbs_effect",
        "review_state": "",
        "quote": quote,
        "relationship": json.dumps({"direction": "none", "outcome_raw": "no gain"}),
        "context": json.dumps(ctx),
    }


def _codes(ctx, **kw):
    return {f["signal"] for f in cc.check_unit(_row(ctx, **kw), set(), set())}


def test_unspecified_needs_no_cue():
    assert not _codes({"hazard_type": "drought", "hazard_severity": "unspecified"})


def test_cue_must_be_verbatim():
    ok = {
        "hazard_type": "drought",
        "hazard_severity": "severe",
        "severity_cue": "severe drought",
    }
    assert not _codes(ok)
    bad = dict(ok, severity_cue="very severe drought")
    assert "severity_cue_not_in_quote" in _codes(bad)
    assert "missing_severity_cue" in _codes(
        {"hazard_type": "drought", "hazard_severity": "extreme"}
    )


def test_vocab_and_hazard_required():
    assert "bad_vocab" in _codes({"hazard_type": "drought", "hazard_severity": "harsh"})
    assert "severity_without_hazard" in _codes({"hazard_severity": "unspecified"})


# ── practice_as_described (ruleset v1.6.9, review theme 2) ───────────────────────────


def test_practice_description_required_from_v1_6_9_only():
    old = dict(
        _row({"country": ["KEN"], "income_group": "low"}), ruleset_version="v1.6.2"
    )
    assert "missing_practice_description" not in {
        f["signal"] for f in cc.check_unit(old, set(), set())
    }
    new = dict(old, ruleset_version="v1.6.9")
    assert "missing_practice_description" in {
        f["signal"] for f in cc.check_unit(new, set(), set())
    }
    filled = dict(
        new,
        context=json.dumps(
            {
                "country": ["KEN"],
                "income_group": "low",
                "practice_as_described": "planting basins dug in the dry season",
            }
        ),
    )
    assert "missing_practice_description" not in {
        f["signal"] for f in cc.check_unit(filled, set(), set())
    }


def test_practice_description_is_a_known_key():
    row = dict(
        _row({"practice_as_described": "contour stone bunds"}), ruleset_version="v1.6.9"
    )
    assert "unknown_context_key" not in {
        f["signal"] for f in cc.check_unit(row, set(), set())
    }


def test_version_parse_is_lenient():
    assert cc._ver("v1.6.10") > cc._ver("v1.6.9")
    assert cc._ver("") == (0,)
    assert cc._ver(None) == (0,)


def test_t4_model_metadata_is_not_an_effect_context_alias():
    from nbs_ruralscan.schema_tools.check_context import check_unit

    row = {
        "evidence_id": "t4",
        "use_role": "structural_suitability",
        "context": {
            "model_use": {"used": True},
            "reported_values": {"classes": ["high"]},
            "vertical_reference": "mean sea level",
            "calibration_hold": "No score",
        },
    }
    assert check_unit(row, set(), set()) == []
    effect = {**row, "use_role": "nbs_effect"}
    assert any(
        f["signal"] == "unknown_context_key" for f in check_unit(effect, set(), set())
    )
    row["context"]["country"] = "Bangladesh"
    assert any(f["signal"] == "bad_vocab" for f in check_unit(row, set(), set()))
