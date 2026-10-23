"""Direction sense lookup, display wording and the direction checker (ruleset v1.6.17)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from nbs_ruralscan.recipe.direction_sense import load_sense, reads, verdict
from nbs_ruralscan.schema_tools import check_direction as cd

ROOT = Path(__file__).resolve().parents[1]


def _row(var, d, quote, cue="", role="nbs_effect", framing="", rs="v1.6.17", sid="x"):
    rel = {"direction": d}
    if cue:
        rel["direction_cue"] = cue
    if framing:
        rel["framing"] = framing
    return {
        "evidence_id": "ev_t",
        "variable": var,
        "use_role": role,
        "quote": quote,
        "source_id": sid,
        "ruleset_version": rs,
        "relationship": json.dumps(rel),
    }


def test_sense_rows_are_complete_and_well_formed():
    rows = list(
        csv.DictReader(
            (ROOT / "schema/lookups/variable_direction_sense.csv").open(
                encoding="utf-8"
            )
        )
    )
    assert len({r["variable"] for r in rows}) == len(rows)
    assert {r["high_is"] for r in rows} <= {"good", "bad", "context"}
    assert all(r["positive_means"] and r["negative_means"] for r in rows)


def test_live_register_and_crosswalk_pass_structure():
    assert cd.check_structure() == []


def test_erosion_down_reads_as_benefit():
    r = reads("erosion_hazard", "negative")
    assert r["verdict"] == "benefit" and r["text"].startswith("↓ less erosion")
    assert verdict("erosion_hazard", "positive") == "harm"
    assert verdict("runoff_reduction", "positive") == "benefit"
    assert verdict("crop_yield", "negative") == "harm"


def test_loss_framing_and_asset_role_flip_the_verdict():
    assert verdict("flood_hazard", "positive", framing="loss") == "benefit"
    assert verdict("climate_shock", "positive", "asset_vulnerability") == "harm"
    assert (
        "damage to the NbS"
        in reads("climate_shock", "positive", "asset_vulnerability")["text"]
    )


def test_cue_must_be_verbatim():
    f = cd.check_unit(
        _row(
            "erosion_hazard", "negative", "it reduced erosion a lot", "lowered erosion"
        )
    )
    assert [x["signal"] for x in f] == ["cue_not_verbatim"]


def test_missing_cue_only_from_v1_6_17():
    assert [
        x["signal"]
        for x in cd.check_unit(_row("crop_yield", "positive", "yields rose"))
    ] == ["missing_cue"]
    assert (
        cd.check_unit(_row("crop_yield", "positive", "yields rose", rs="v1.6.14")) == []
    )


def test_cue_word_conflict_catches_good_bad_flip():
    q = "Improved infiltration and reduced erosion commonly documented"
    bad = cd.check_unit(_row("erosion_hazard", "positive", q, "reduced erosion"))
    assert [x["signal"] for x in bad] == ["cue_word_conflict"]
    assert cd.check_unit(_row("erosion_hazard", "negative", q, "reduced erosion")) == []
    # benefit-named variable: "reduced runoff" is the variable going UP
    assert (
        cd.check_unit(
            _row("runoff_reduction", "positive", "runoff reduced 40%", "runoff reduced")
        )
        == []
    )
    # loss framing is coded as measured, so no conflict check
    assert (
        cd.check_unit(
            _row(
                "flood_hazard",
                "positive",
                "if lost, more people flooded",
                "more people flooded",
                framing="loss",
            )
        )
        == []
    )


def test_polarity_mismatch_fails(tmp_path):
    xw = tmp_path / "xw.csv"
    xw.write_text(
        "xw_id,ev_variable,target_table,target_key,polarity\n"
        "a,erosion_hazard,T6,soil_erosion_risk,same\n"
        "b,project_cost,T6,cost_per_beneficiary,same\n",
        encoding="utf-8",
    )
    ev = tmp_path / "ev.csv"
    ev.write_text("evidence_id,variable,use_role,review_state\n", encoding="utf-8")
    sig = [f["signal"] for f in cd.check_structure(ev, xw)]
    assert sig == ["polarity_mismatch"]


def test_sense_covers_every_variable_named_in_sense_loader():
    assert "erosion_hazard" in load_sense()
