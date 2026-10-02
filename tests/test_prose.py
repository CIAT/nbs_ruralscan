"""Prose sidecar: apply only on an exact evidence_ids match; gate numbers/ids/levels."""

from __future__ import annotations

import json

from nbs_ruralscan.recipe import prose as P

EV = {
    "ev_a": {
        "evidence_id": "ev_a",
        "quote": "yield rose by 23% in alley cropping",
        "relationship": json.dumps({"magnitude": 23, "direction": "positive"}),
        "review_state": "",
    },
    "ev_b": {
        "evidence_id": "ev_b",
        "quote": "no change in income was observed",
        "relationship": "{}",
        "review_state": "",
    },
    "ev_dropped": {
        "evidence_id": "ev_dropped",
        "quote": "x",
        "relationship": "{}",
        "review_state": "dropped",
    },
}


def _row(ids=("ev_a", "ev_b")):
    return {
        "record_id": "nbs__target",
        "evidence_ids": list(ids),
        "n_sources": 2,
        "applicability": {"n_sources_in_scope": 2, "weight_share_in_context": 1.0},
        "effect_mechanism": "[prose pending] nbs increases target ...",
        "conditionality": "",
        "justification": {
            "statement": "nbs increases target ...",
            "agreement": 1.0,
            "prose_pending": True,
        },
    }


def test_apply_only_on_exact_evidence_match():
    sidecar = {
        "nbs__target": {
            "evidence_ids": ["ev_a", "ev_b"],
            "mechanism": "Trees shade the crop [ev_a].",
            "conditionality": "",
        }
    }
    r = _row()
    assert P.apply_prose([r], "T6", sidecar) == (1, 0)
    assert r["effect_mechanism"].startswith("Trees shade")
    assert r["justification"]["prose_pending"] is False
    # evidence set changed → stale, row untouched
    r2 = _row(ids=("ev_a",))
    assert P.apply_prose([r2], "T6", sidecar) == (0, 1)
    assert r2["effect_mechanism"].startswith("[prose pending]")


def test_check_flags_numbers_ids_and_level_language():
    rows = [_row()]
    good = {
        "nbs__target": {"mechanism": "Yield rose by 23% under alley cropping [ev_a]."}
    }
    assert P.check_prose(rows, "T6", good, EV) == []
    bad_num = {"nbs__target": {"mechanism": "Yield rose by 40% [ev_a]."}}
    sig = {f["signal"] for f in P.check_prose(rows, "T6", bad_num, EV)}
    assert "number_not_in_evidence" in sig
    bad_id = {"nbs__target": {"mechanism": "As shown [ev_zzz]."}}
    sig = {f["signal"] for f in P.check_prose(rows, "T6", bad_id, EV)}
    assert "cited_id_not_used" in sig
    lvl = {"nbs__target": {"mechanism": "There is high confidence that trees help."}}
    sig = {f["signal"] for f in P.check_prose(rows, "T6", lvl, EV)}
    assert "level_language" in sig
    unknown = {"other": {"mechanism": "x"}}
    sig = {f["signal"] for f in P.check_prose(rows, "T6", unknown, EV)}
    assert sig == {"unknown_record"}


def test_merge_writes_sidecar_keyed_to_current_ids(tmp_path):
    rows = [_row()]
    prose = {
        "nbs__target": {
            "mechanism": "Shade lowers crop heat stress [ev_a].",
            "conditionality": "Only with pruning.",
        }
    }
    n, flags = P.merge_prose(tmp_path, rows, "T6", prose, writer="test", ev=EV)
    assert (n, flags) == (1, [])
    side = P.load_sidecar(tmp_path)
    assert side["nbs__target"]["evidence_ids"] == ["ev_a", "ev_b"]
    assert side["nbs__target"]["writer"] == "test"
    assert rows[0]["conditionality"] == "Only with pruning."
    # a flagged payload writes nothing
    bad = {"nbs__target": {"mechanism": "Yield rose by 99% [ev_a]."}}
    n, flags = P.merge_prose(tmp_path, [_row()], "T6", bad, writer="test", ev=EV)
    assert n == 0 and flags
    assert P.load_sidecar(tmp_path)["nbs__target"]["mechanism"].startswith("Shade")
