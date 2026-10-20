"""Reviewed numeric bands reach executable T4 without inventing missing tails."""

import csv
import json
import runpy
from pathlib import Path
import numpy as np
import pytest
from nbs_ruralscan.recipe.numeric_bands import bounds, parse_profiles
from nbs_ruralscan.runtime.numeric import evaluate_numeric

ROOT = Path(__file__).resolve().parents[1]


def live(variable, family):
    rows = csv.DictReader(
        (ROOT / "schema/recipes/agroforestry/T4_suitability_mappings.csv").open()
    )
    return next(
        r
        for r in rows
        if r["variable"] == variable and r["suitability_family_id"].endswith(family)
    )


def test_reviewed_ph_reaches_t4_and_unstated_ranges_stay_unknown():
    row = live("soil_ph", "planted_silvoarable")
    assert json.loads(row["evidence_ids"]) == ["ev_soil_ph_singh26"]
    np.testing.assert_allclose(
        evaluate_numeric(
            row, [5, 6, 6.5, 7, 8, 9, np.nan], profile_id="ev_soil_ph_singh26"
        ),
        [np.nan, 0.75, np.nan, 0.9, 0.5, np.nan, np.nan],
        equal_nan=True,
    )
    assert np.isnan(evaluate_numeric(row, [7])).all()
    with pytest.raises(ValueError, match="Unknown"):
        evaluate_numeric(row, [7], profile_id="wrong")


def test_rainfall_favourable_tail_does_not_invent_exclusion():
    row = live("annual_precipitation", "shaded_perennial")
    np.testing.assert_allclose(
        evaluate_numeric(
            row, [500, 1200, 1500], profile_id="ev_t4_precip_mushtaq2023_2"
        ),
        [np.nan, np.nan, np.nan],
        equal_nan=True,
    )


def test_organic_carbon_percent_is_converted_to_grams_per_kg():
    row = live("soil_organic_carbon", "cross_family")
    values = evaluate_numeric(row, [4, 6, 8], profile_id="ev_T4_soc_ahmad2018_1")
    np.testing.assert_allclose(values, [0.25, 0.5, 0.75])
    assert np.isnan(
        evaluate_numeric(row, [8], profile_id="ev_T4_soc_haile2024_1")
    ).all()


def test_context_profiles_do_not_get_averaged_or_auto_selected():
    row = live("mean_annual_temperature", "cross_family")
    np.testing.assert_allclose(
        evaluate_numeric(
            row, [19, 21], profile_id="ev_t4_mat_yadav24_1__group1_temperate_warm"
        ),
        [0.9, 0.75],
    )
    np.testing.assert_allclose(
        evaluate_numeric(
            row, [19, 21], profile_id="ev_t4_mat_yadav24_1__group2_temperate_hot"
        ),
        [0.75, 0.9],
    )
    assert np.isnan(evaluate_numeric(row, [19])).all()
    assert np.isnan(
        evaluate_numeric(row, [26], profile_id="ev_t4_meanann_nath21_01")
    ).all()


def test_ranges_require_explicit_permission_to_reverse():
    with pytest.raises(ValueError):
        bounds("0.75-0.50")
    assert bounds("0.75-0.50", reverse=True)[:2] == (0.5, 0.75)
    with pytest.raises(ValueError):
        bounds("<5 OR >8")
    policy = {
        "encoding": "labelled_ranges",
        "field": "classes",
        "ordinal_scale": '{"low":1,"high":2}',
    }
    with pytest.raises(ValueError, match="overlapping"):
        parse_profiles(
            {
                "classes": [
                    {"range": "5-8", "label": "low"},
                    {"range": "7-9", "label": "high"},
                ]
            },
            policy,
        )


def test_source_policy_never_bypasses_review_or_species_routing():
    from nbs_ruralscan.recipe.evidence import EvidenceUnit
    from nbs_ruralscan.recipe.family import synthesise_family

    eid = "test"
    policy = {
        eid: {
            "encoding": "named_bounds",
            "action": "compile",
            "input_unit": "pH_units",
            "ordinal_scale": '{"high":1}',
            "applicability_note": "test",
            "threshold_direction": "",
        }
    }

    def result(**kwargs):
        args = dict(
            evidence_id=eid,
            source_id="s",
            nbs_id="agroforestry",
            suitability_family_id="f",
            variable="soil_ph",
            use_role="structural_suitability",
            evidence_type="literature_relationship",
            claim_basis="table",
            claim_scope="practice_technology",
            extraction_confidence="high",
            quote="pH 6-7",
            page=1,
            relationship={"high_low": 6, "high_high": 7},
            reviewer_ok=True,
        )
        args.update(kwargs)
        return synthesise_family(
            [EvidenceUnit(**args)],
            {},
            family="f",
            corpus_n=None,
            group_map={},
            approved_only=True,
            numeric_policies=policy,
            canonical_units={"soil_ph": "pH_units"},
        )

    assert result().rows
    assert not result(reviewer_ok=False).rows
    assert not result(review_state="dropped").rows
    assert not result(claim_scope="species_specific").rows


def test_all_numeric_policy_rows_accounted_for_without_unhandled_encoding():
    build = runpy.run_path(str(ROOT / "scripts/synthesise-recipe.py"))
    results = build["synthesise"]("agroforestry")
    dispositions = {
        eid: d for f in results.values() for eid, d in f.dispositions.items()
    }
    policies = list(
        csv.DictReader(
            (ROOT / "schema/lookups/t4_numeric_compilation_policy.csv").open()
        )
    )
    for p in policies:
        assert dispositions[p["evidence_id"]]["status"] == (
            "parameter_contributor" if p["action"] == "compile" else p["reason"]
        )
    assert sum(len(f.rows) for f in results.values()) == 8


def test_nath_recovered_ph_and_carbon_preserve_source_classes():
    ph = live("soil_ph", "cross_family")
    np.testing.assert_allclose(
        evaluate_numeric(
            ph, [4, 5, 6, 7.3, 7.5, 8], profile_id="ev_t4_soilph_nath21_01"
        ),
        [np.nan, 0.75, 0.9, 0.75, 0.5, np.nan],
        equal_nan=True,
    )
    carbon = live("soil_organic_carbon", "cross_family")
    np.testing.assert_allclose(
        evaluate_numeric(carbon, [3, 8, 15, 25], profile_id="ev_t4_soilorg_nath21_01"),
        [0.25, 0.5, 0.75, 0.9],
    )
