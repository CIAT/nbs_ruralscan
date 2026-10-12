"""build-review-batch — what the reviewer is shown (review themes 2 · 4 · 5)."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "build_review_batch", ROOT / "scripts" / "build-review-batch.py"
)
assert _spec and _spec.loader
brb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(brb)


def _unit(ctx: dict | None = None, rel: dict | None = None) -> dict:
    return {
        "evidence_id": "ev_x",
        "nbs_id": "water_harvesting_conservation",
        "use_role": "nbs_effect",
        "variable": "crop_yield",
        "suitability_family_id": "",
        "quote": "yields rose behind the bunds",
        "relationship": json.dumps(rel or {"direction": "positive"}),
        "context": json.dumps(ctx or {}),
    }


# ── theme 2: the source's own words for the practice ────────────────────────────────


def test_described_line_quotes_the_source():
    line = brb.described_line(
        {"practice_as_described": "contour stone bunds built by hand"}, "nbs_effect"
    )
    assert "contour stone bunds built by hand" in line


def test_missing_description_tells_the_reviewer_to_judge_from_the_quote():
    line = brb.described_line({}, "nbs_effect")
    assert "not captured" in line and "quote" in line
    assert brb.described_line({}, "operational_risk") == ""


def test_picos_intervention_carries_the_sources_words():
    u = _unit({"practice_as_described": "planting basins dug in the dry season"})
    p = brb.picos(
        u, json.loads(u["relationship"]), json.loads(u["context"]), {}, {}, {}
    )
    assert "planting basins dug in the dry season" in p["I"]
    p2 = brb.picos(_unit(), {"direction": "positive"}, {}, {}, {}, {})
    assert "not captured" in p2["I_note"].lower() or p2["I_note"] == ""


# ── theme 5: several units from one paper are not several findings ──────────────────


def test_pool_sentence_warns_only_when_units_outnumber_sources():
    many = brb._pool_sentence(41, 32)
    assert "41 units from 32 sources" in many
    assert "counts sources, not units" in many
    one = brb._pool_sentence(1, 1)
    assert "1 unit from 1 source" in one
    assert "counts sources" not in one


def test_placement_line_carries_the_pool_sentence():
    places = [
        {
            "table": "T3 — hazard table",
            "record_id": "wh__drought__all",
            "family": "",
            "scope": "",
            "role": "livelihood_mitigation",
            "pool": brb._pool_sentence(5, 2),
        }
    ]
    lines, none_reason = brb.placement_lines(_unit(), {}, places, {})
    assert none_reason == ""
    assert "5 units from 2 sources" in lines[0]


def test_placements_count_units_and_sources_from_the_real_recipes():
    places = brb._placements({"ev_a": "src_1", "ev_b": "src_1"})
    assert places, "the generated recipes should place at least one unit"
    some = next(iter(places.values()))[0]
    assert "draws on" in some["pool"]
