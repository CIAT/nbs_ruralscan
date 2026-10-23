"""Prevent contextual/source-error evidence from becoming executable T4 rules."""

import csv
import json
from pathlib import Path

from nbs_ruralscan.recipe.variable_usage import summarize_usage, variable_usage

ROOT = Path(__file__).resolve().parents[1]


def evidence():
    with (ROOT / "schema/registers/EV_evidence_register.csv").open() as stream:
        return {r["evidence_id"]: r for r in csv.DictReader(stream)}


def test_land_unit_bands_are_not_absolute_suitability_bounds():
    row = evidence()["ev_T4_slope_seja2022_1"]
    relationship = json.loads(row["relationship"])
    assert row["review_state"] == "dropped"
    assert relationship["type"] == "observed_presence"
    assert len(relationship["land_unit_ranges"]) == 5
    assert not {"abs_min", "abs_max", "opt_min", "opt_max"} & relationship.keys()


def test_source_typo_cannot_be_silently_reversed_into_tenure_direction():
    row = evidence()["ev_tenure_security_lasco14_1"]
    assert "secure land tenure" in row["quote"]
    assert json.loads(row["relationship"])["direction"] == "not_established"
    assert json.loads(row["context"])["runtime_status"].startswith("held_")


def test_species_rainfall_model_use_survives_without_general_vote():
    row = evidence()["ev_T4_annualprecip_haris2021_1"]
    summary = summarize_usage(variable_usage([row], {}))[0]
    assert summary["verified_crop_species_model_papers"] == 1
    assert summary["verified_general_model_papers"] == 0
    assert json.loads(row["relationship"])["direction"] == "not_reported"


def test_material_supply_and_gender_comparison_have_distinct_variables():
    ev = evidence()
    material = ev["ev_market_value_chain_faosen24_19"]
    gender = ev["ev_adoption_rate_wvfmnr19_13"]
    assert material["variable"] == "planting_material_availability"
    assert gender["variable"] == "gender_participation_gap"
    assert material["use_role"] == gender["use_role"] == "operational_risk"
    assert json.loads(gender["relationship"])["effect_scale"] == "unresolved"


def test_secondary_citations_survive_clipped_quote_repair():
    ev = evidence()
    for eid, citation in (
        ("EV_lohbeck_2020_016", "Chomba et al., 2016"),
        ("EV_lohbeck_2020_017", "Binam et al., 2017"),
        ("ev_labour_availability_faosen24_18", "Yossi et al., 2006"),
    ):
        row = ev[eid]
        assert citation in row["quote"]
        assert row["claim_basis"] == "cited_secondary"
