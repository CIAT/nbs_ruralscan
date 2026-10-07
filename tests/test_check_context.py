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
