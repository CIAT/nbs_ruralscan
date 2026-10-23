"""Regression checks for the bounded source-purpose and lineage review."""

import csv
import json
from pathlib import Path

from nbs_ruralscan.recipe.direction_usage import direction_usage
from nbs_ruralscan.recipe.variable_usage import summarize_usage, variable_usage

ROOT = Path(__file__).resolve().parents[1]


def evidence():
    return {
        r["evidence_id"]: r
        for r in csv.DictReader(
            (ROOT / "schema/registers/EV_evidence_register.csv").open()
        )
    }


def test_model_use_survives_missing_curve_without_inflating_paper_votes():
    ev = evidence()
    units = [r for r in ev.values() if r["source_id"] == "kiziridis_2026"]
    summaries = {r["variable"]: r for r in summarize_usage(variable_usage(units, {}))}
    assert summaries["mean_annual_temperature"]["verified_general_model_papers"] == 1
    assert summaries["land_cover"]["verified_general_model_papers"] == 1
    temp = json.loads(ev["ev_t4_temp_kizir_1"]["relationship"])
    assert temp["type"] == "model_input"
    assert temp["direction"] == "not_reported"
    assert not {"abs_min", "abs_max", "opt_min", "opt_max"} & temp.keys()


def test_species_model_input_does_not_become_general_agroforestry_vote():
    row = evidence()["ev_t4_soildrain_yadav24_9"]
    summary = summarize_usage(variable_usage([row], {}))[0]
    assert row["variable"] == "soil_bulk_density"
    assert summary["verified_general_model_papers"] == 0
    assert summary["verified_crop_species_model_papers"] == 1


def test_observations_and_practice_comparisons_do_not_vote_for_direction():
    ev = evidence()
    for eid in (
        "EV_binam_2017_007",
        "ev_aridity_index_zomer14_1",
        "ev_aridity_index_zomer14_2",
    ):
        assert json.loads(ev[eid]["relationship"])["type"] == "observed_presence"
    comparison = json.loads(ev["ev_labour_availability_snapp10_2"]["relationship"])
    assert comparison["type"] == "practice_comparison"
    assert comparison["direction"] not in ("positive", "negative")
    rows = direction_usage([ev["ev_aridity_index_zomer14_1"]], {})
    assert rows[0]["papers"][0]["directions"]["reviewed"] == "not_classified"


def test_assets_and_training_keep_distinct_meanings_and_sources():
    ev = evidence()
    assets = ev["ev_finance_credit_access_coulibaly16_1"]
    assert assets["variable"] == "farm_asset_index"
    assert assets["use_role"] == "operational_risk"
    training = json.loads(ev["ev_extension_governance_coulibaly16_1"]["context"])
    assert training["claim_origin"] == "own_model_result"
    assert "Franzel" in training["corroborating_citation"]
    for eid in ("ev_labour_availability_snapp10_1", "ev_labour_availability_snapp10_2"):
        assert ev[eid]["claim_basis"] == "cited_secondary"
        assert ev[eid]["lineage_of"].startswith("external:")


def test_regional_mask_is_labelled_and_kept_separate_from_importance():
    ev = evidence()
    classes = json.loads(ev["ev_t4_lc_kizir_2"]["relationship"])
    assert len(classes["eligible_classes"]) == 16
    assert set(classes["eligible_classes"]) == set(classes["source_class_labels"])
    assert classes["transfer_to_other_classifications"] == "unknown"
    importance = json.loads(ev["ev_t4_lc_kizir_1"]["relationship"])
    assert "direction" not in importance
    assert importance["permutation_importance_pct"] == 61.3


def test_code_weights_have_full_denominator_and_remain_outside_t4():
    ev = evidence()
    for eid in (
        "ev_soil_erosion_risk_saraheb3_p1_water",
        "ev_soil_erosion_wind_saraheb3_p1_wind",
        "ev_carbon_sequestration_potential_saraheb3_p1_soil",
    ):
        row = ev[eid]
        context = json.loads(row["context"])["importance_comparison"]
        assert sum(context["effective_weights"]) == context["total"] == 17
        assert context["relative_to_mean_input"] == 25 / 17
        assert context["runtime_t4_weight"] is False
        assert row["review_state"] == "dropped"


def test_code_mask_audit_does_not_hide_background_or_perennials():
    audit = json.loads(
        (
            ROOT / "pipeline/t4_audit/agroforestry/"
            "cdl_code_predicate_audit_2026-10-23.json"
        ).read_text()
    )
    selected = audit["selected_named_codes"]
    assert selected["0"] == "Background"
    assert selected["36"] == "Alfalfa"
    assert selected["61"] == "Fallow/Idle Cropland"
    assert selected["242"] == "Blueberries"
    assert "215" not in selected
    assert audit["pasture"] == {"176": "Grass/Pasture"}
    assert "not a separately archived 2022" in audit["dictionary_scope"]
