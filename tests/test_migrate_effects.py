"""Deterministic migration of archived T3/T6 units into the v1.6.0 effect-claim shape (PR4),
plus the ledger's XW-derived table attribution."""

from __future__ import annotations

import csv
import json

from nbs_ruralscan.schema_tools import ledger, migrate_effects as m

BANDS = [
    {
        "metric": "smd_hedges_g",
        "strength_class": "slight",
        "abs_min": "0",
        "abs_max": "0.2",
    },
    {
        "metric": "smd_hedges_g",
        "strength_class": "moderate",
        "abs_min": "0.2",
        "abs_max": "0.5",
    },
    {
        "metric": "smd_hedges_g",
        "strength_class": "strong",
        "abs_min": "0.5",
        "abs_max": "",
    },
    {
        "metric": "pct_change",
        "strength_class": "moderate",
        "abs_min": "10",
        "abs_max": "30",
    },
    {
        "metric": "pct_change",
        "strength_class": "strong",
        "abs_min": "30",
        "abs_max": "",
    },
]
ISO_INC = {"KEN": "lower_middle", "USA": "high", "ETH": "low", "MDG": "low"}
NAME_ISO = {
    "kenya": "KEN",
    "united states": "USA",
    "ethiopia": "ETH",
    "madagascar": "MDG",
}
AEZ = {"semi_arid", "temperate_europe"}
FS = {"mixed_crop_livestock", "agro_pastoral"}


def _unit(**kw):
    base = {
        "evidence_id": "ev_x",
        "source_id": "s",
        "nbs_id": "agroforestry",
        "suitability_family_id": "agroforestry__planted_silvoarable",
        "variable": "drought_hazard",
        "use_role": "climate_risk",
        "evidence_type": "scoping_candidate",
        "claim_basis": "primary_measured",
        "claim_scope": "practice_technology",
        "extraction_confidence": "high",
        "quote": "q",
        "page": 2,
        "locator_type": "page",
        "relationship": None,
        "context": {},
        "review_state": "",
        "ruleset_version": "v1.2",
    }
    base.update(kw)
    return base


def _mig(u, src=None):
    return m.migrate_unit(u, src or {}, BANDS, ISO_INC, NAME_ISO, AEZ, FS)


def test_authored_mitigation_class_becomes_direction_only_and_is_kept_in_note():
    u = _unit(
        context={
            "hazard_type": "drought",
            "farming_system": "mixed_crop_livestock",
            "risk_role": "livelihood_mitigation",
            "mitigation_potential": "moderate",
            "study_region": "Isiolo County, Kenya",
        }
    )
    out = _mig(u, {"study_country": "Kenya", "aez": "semi_arid"})
    assert out["use_role"] == "nbs_effect"
    assert out["ruleset_version"] == "v1.6.0"
    rel = out["relationship"]
    assert (
        rel["direction"] == "negative"
    )  # hazard impact reduced, on the outcome as measured
    assert (
        rel["strength_class"] == "unspecified"
    )  # the authored 'moderate' is not trusted
    assert rel["metric"] == "narrative"
    ctx = out["context"]
    assert ctx["country"] == ["KEN"] and ctx["income_group"] == "lower_middle"
    assert ctx["aez"] == "semi_arid" and ctx["farming_system"] == "mixed_crop_livestock"
    assert ctx["hazard_type"] == "drought"
    assert (
        "mitigation_potential=moderate" in ctx["note"]
        and "risk_role=livelihood_mitigation" in ctx["note"]
    )
    assert set(ctx) <= {
        "country",
        "income_group",
        "aez",
        "farming_system",
        "hazard_type",
        "note",
    }


def test_asset_threat_rows_become_asset_vulnerability():
    u = _unit(
        context={
            "hazard_type": "fire",
            "risk_role": "asset_threat",
            "mitigation_potential": "none",
        }
    )
    assert _mig(u)["use_role"] == "asset_vulnerability"


def test_erosion_is_not_a_t3_hazard_and_goes_to_note():
    u = _unit(
        variable="erosion_hazard",
        context={
            "hazard_type": "erosion",
            "mitigation_potential": "moderate",
            "landscape_scale": True,
        },
    )
    out = _mig(u)
    assert "hazard_type" not in out["context"]
    assert "hazard_type=erosion" in out["context"]["note"]
    assert out["context"]["landscape_scale_only"] is True
    assert out["relationship"]["direction"] == "negative"


def test_hedges_g_meta_analysis_shape_and_ns():
    u = _unit(
        variable="crop_yield",
        use_role="nbs_effect",
        evidence_type="literature_relationship",
        relationship={
            "effect_size_type": "standardized_mean_difference_hedges_g",
            "central": 1.16,
            "ci_low": -0.35,
            "ci_high": 2.67,
            "p_value": 0.13,
            "model": "random_effects",
        },
        context={
            "effect_direction": "moderate_positive",
            "claim_basis_note": "meta_analysis — pools 5 studies",
            "timescale_of_effect": "short_to_medium_term",
        },
    )
    rel = _mig(u, {"study_country": "Global", "region": "LMICs"})["relationship"]
    assert rel["metric"] == "smd_hedges_g" and rel["magnitude"] == 1.16
    assert (rel["magnitude_low"], rel["magnitude_high"]) == (-0.35, 2.67)
    assert rel["significance"] == "ns" and rel["design"] == "meta_analysis"
    assert rel["strength_class"] == "strong"  # from BANDS; the engine halves ns weight
    assert rel["direction"] == "positive"
    assert rel["legacy"]["central"] == 1.16
    ctx = _mig(u, {"study_country": "Global", "region": "LMICs"})["context"]
    assert ctx["income_group"] == "lic_lmic" and "country" not in ctx
    assert "timescale=short_to_medium_term" in ctx["note"]  # not an enum value → note


def test_effect_direction_on_high_is_bad_variable_is_inverted_to_outcome_frame():
    u = _unit(
        variable="erosion_hazard",
        use_role="nbs_effect",
        context={"effect_direction": "strong_positive"},
    )
    # authored 'positive' = benefit (less erosion) → outcome-as-measured direction negative
    assert _mig(u)["relationship"]["direction"] == "negative"
    u2 = _unit(
        variable="household_income",
        use_role="nbs_effect",
        context={"effect_direction": "slight_positive"},
    )
    assert _mig(u2)["relationship"]["direction"] == "positive"


def test_economics_keep_magnitude_and_unit_without_inventing_direction():
    cost = _unit(
        variable="project_cost",
        use_role="nbs_effect",
        relationship={"total_project_cost_usd_million": 279.7, "unit": "usd_million"},
    )
    rel = _mig(cost, {"study_country": "Kenya"})["relationship"]
    assert (
        rel["metric"] == "absolute"
        and rel["magnitude"] == 279.7
        and rel["unit"] == "usd_million"
    )
    assert "direction" not in rel  # magnitude-only unit
    ret = _unit(
        variable="economic_return",
        use_role="nbs_effect",
        relationship={
            "npv_incremental_usd_per_acre": 794,
            "bc_ratio": 1.8,
            "unit": "usd_per_acre",
        },
    )
    rel = _mig(ret)["relationship"]
    assert (
        rel["direction"] == "positive"
        and rel["unit"] == "usd_per_acre"
        and rel["magnitude"] == 794.0
    )
    eirr = _unit(
        variable="economic_return",
        use_role="nbs_effect",
        relationship={"opt_low": 27.9, "opt_high": 72.9, "unit": "percent_eirr"},
    )
    rel = _mig(eirr)["relationship"]
    assert (rel["magnitude_low"], rel["magnitude_high"]) == (27.9, 72.9) and rel[
        "unit"
    ] == "percent_eirr"


def test_pct_increase_maps_to_pct_change_with_band():
    u = _unit(
        variable="food_security",
        use_role="nbs_effect",
        relationship={"pct_increase": 35, "p_value": "<0.01", "unit": "MWK_per_acre"},
        context={"effect_direction": "strong_positive"},
    )
    rel = _mig(u)["relationship"]
    assert (
        rel["metric"] == "pct_change"
        and rel["magnitude"] == 35.0
        and rel["significance"] == "sig"
    )
    assert rel["strength_class"] == "strong"


def test_countries_from_text_and_multi_country_income_band():
    assert m.countries_from_text("Isiolo County, Kenya", NAME_ISO) == ["KEN"]
    assert m.countries_from_text("Global", NAME_ISO) == []
    assert m.countries_from_text("KEN", NAME_ISO) == ["KEN"]
    u = _unit(
        context={
            "country_context": "Ethiopia, Madagascar",
            "hazard_type": "flood",
            "mitigation_potential": "low",
        }
    )
    ctx = _mig(u)["context"]
    assert ctx["country"] == ["ETH", "MDG"] and ctx["income_group"] == "low"


def test_dropped_state_and_ids_are_preserved():
    u = _unit(
        evidence_id="ev_d",
        review_state="dropped",
        context={"hazard_type": "fire", "mitigation_potential": "low"},
    )
    out = _mig(u)
    assert out["evidence_id"] == "ev_d" and out["review_state"] == "dropped"


def test_append_and_resync_are_idempotent(tmp_path):
    ev = tmp_path / "EV.csv"
    cols = [
        "evidence_id",
        "source_id",
        "nbs_id",
        "suitability_family_id",
        "variable",
        "relationship",
        "context",
        "use_role",
        "review_state",
        "ruleset_version",
    ]
    with open(ev, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerow(
            {c: "" for c in cols}
            | {
                "evidence_id": "ev_old",
                "source_id": "s",
                "variable": "slope",
                "use_role": "structural_suitability",
            }
        )
    rows = [
        _mig(
            _unit(
                evidence_id="ev_new",
                context={"hazard_type": "fire", "mitigation_potential": "low"},
            )
        )
    ]
    assert m.append_to_register(rows, ev) == 1
    assert m.append_to_register(rows, ev) == 0  # already there
    with open(ev, encoding="utf-8", newline="") as f:
        got = list(csv.DictReader(f))
    assert [r["evidence_id"] for r in got] == ["ev_old", "ev_new"]
    assert json.loads(got[1]["relationship"])["direction"] == "negative"
    assert got[1]["ruleset_version"] == "v1.6.0"
    src = tmp_path / "SRC.csv"
    with open(src, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["source_id", "vars_extracted"])
        w.writeheader()
        w.writerow({"source_id": "s", "vars_extracted": "slope"})
    assert m.resync_vars_extracted({"s"}, src, ev) == {"s": "drought_hazard|slope"}
    assert m.resync_vars_extracted({"s"}, src, ev) == {}


def test_ledger_tables_derive_from_role_and_xw():
    routes = {"drought_hazard": {"T3", "T6"}, "erosion_hazard": {"T6"}}
    assert ledger.tables_for("structural_suitability", "slope", routes) == {"T4"}
    assert ledger.tables_for("asset_vulnerability", "seedling_mortality", routes) == {
        "T3"
    }
    assert ledger.tables_for("nbs_effect", "drought_hazard", routes) == {"T3", "T6"}
    assert ledger.tables_for("nbs_effect", "erosion_hazard", routes) == {"T6"}
    assert ledger.tables_for("nbs_effect", "unmapped_var", routes) == set()
    assert ledger.tables_for("operational_risk", "tenure_security", routes) == set()
    assert ledger.TABLES == ["T4", "T3", "T6"]


def test_protective_outcomes_and_hazard_impacts_get_opposite_directions():
    prot = _unit(
        variable="microclimate_buffering",
        context={"hazard_type": "heat_stress", "mitigation_potential": "moderate"},
    )
    assert _mig(prot)["relationship"]["direction"] == "positive"  # service goes up
    haz = _unit(
        variable="drought_hazard",
        context={"hazard_type": "drought", "mitigation_potential": "moderate"},
    )
    assert _mig(haz)["relationship"]["direction"] == "negative"  # impact goes down
    worse = _unit(
        variable="fire_hazard",
        context={"hazard_type": "fire", "mitigation_potential": "negative"},
    )
    assert _mig(worse)["relationship"]["direction"] == "positive"  # NbS worsens fire


def test_wildfire_mitigation_resolves_to_fire_hazard_alias():
    u = _unit(
        variable="wildfire_mitigation",
        relationship={"direction": "negative", "unit": "qualitative"},
        context={"hazard_type": "fire"},
    )
    out = _mig(u)
    assert out["variable"] == "fire_hazard" and out["raw_name"] == "wildfire_mitigation"
    assert out["relationship"]["direction"] == "negative"
