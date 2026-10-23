"""Keep source concepts and evidence strength distinct in T4 review answers."""

import csv
import json
from pathlib import Path
from nbs_ruralscan.recipe.variable_usage import summarize_usage, variable_usage

ROOT = Path(__file__).resolve().parents[1]


def evidence():
    with (ROOT / "schema/registers/EV_evidence_register.csv").open() as f:
        return {r["evidence_id"]: r for r in csv.DictReader(f)}


def test_chuma_model_use_survives_without_class_scores():
    row = evidence()["ev_T4_land_cover_chuma21_1"]
    summary = summarize_usage(variable_usage([row], {}))[0]
    assert summary["verified_general_model_papers"] == 1
    assert row["evidence_type"] == "scoping_candidate"
    assert json.loads(row["relationship"])["class_scores"] == "not_extracted"


def test_grazing_water_access_does_not_become_road_or_agroforestry_rule():
    row = evidence()["ev_t4_road_jawarneh2025_1"]
    assert row["variable"] == "distance_to_waterbody"
    assert row["evidence_type"] == "scoping_candidate"
    rel = json.loads(row["relationship"])
    assert rel["unit_interpretation"] == "unresolved"
    assert rel["agroforestry_numeric_rule"] is False
    assert json.loads(row["context"])["model_use"]["verified"] is False


def test_composite_index_stays_quarantined_without_generic_threshold():
    row = evidence()["ev_t4_lc_mucida23_1"]
    assert row["variable"] == "potential_conservation_use_index"
    assert row["review_state"] == "dropped"
    rel = json.loads(row["relationship"])
    assert "threshold_min" not in rel
    assert rel["independent_variable_response"] is False


def test_financial_returns_and_land_access_keep_actual_source_concepts():
    ev = evidence()
    for eid in ["ev_t4_market_palma2007_01", "ev_finance_credit_access_diasf08_5"]:
        assert ev[eid]["variable"] == "economic_return"
        assert ev[eid]["use_role"] == "operational_risk"
    land = ev["ev_tenure_security_ribeiro22_4"]
    assert land["variable"] == "land_access"
    assert (
        json.loads(land["relationship"])["design"]
        == "systematic_review_qualitative_component"
    )
    assert json.loads(land["relationship"])["effect_size"] == "not_reported"


def test_missing_soil_class_definitions_cannot_generate_exclusions():
    ev = evidence()
    for eid in ["ev_soil_drainage_singh26", "ev_soil_texture_singh26"]:
        rel = json.loads(ev[eid]["relationship"])
        assert rel["missing_class_interpretation"] == "unknown_not_unsuitable"
        assert rel["runtime_numeric_rule"] is False
        assert (
            json.loads(ev[eid]["context"])["runtime_status"]
            == "held_dataset_legend_and_class_crosswalk"
        )
