"""Categorical gates must never turn missing evidence/context into eligibility."""

from pathlib import Path

import numpy as np
import pytest

from nbs_ruralscan.runtime.categorical import (
    apply_eligibility,
    evaluate_categorical,
    evaluate_family,
)

SCHEMA = Path(__file__).resolve().parents[1] / "schema"


def config():
    return dict(
        mapping_id="gate",
        dataset_id="codes_v1",
        relationship_type="ranked_classes",
        evidence_ids=["ev"],
        relationship_params=dict(
            mapping_role="eligibility_gate",
            class_map={"40": 1, "30": 1, "80": 0},
            class_requirements={"30": ["host"]},
        ),
    )


def evaluate(data, **kw):
    return evaluate_categorical(
        config(),
        data,
        dataset_id="codes_v1",
        evidence={"ev": {"reviewer_ok": True}},
        **kw,
    )


def test_unknown_codes_and_missing_host_are_not_excluded_or_eligible():
    result = evaluate([40, 30, 80, 10, 40.1, np.nan])
    np.testing.assert_equal(result.values, [1, np.nan, 0, np.nan, np.nan, np.nan])
    assert result.status.tolist() == [
        "mapped",
        "missing_host_context",
        "excluded",
        "unmapped_class",
        "unmapped_class",
        "unmapped_class",
    ]


def test_masks_and_hard_gate_application():
    result = evaluate([30, 30, 30], masks={"host": np.array([1, 0, np.nan])})
    np.testing.assert_equal(result.values, [1, 0, np.nan])
    np.testing.assert_equal(
        apply_eligibility([0.9, np.nan, 1], result.values), [0.9, 0, np.nan]
    )


@pytest.mark.parametrize(
    "evidence,status",
    [
        (None, "missing_evidence"),
        ({}, "unavailable_evidence"),
        (
            {"ev": {"reviewer_ok": True, "review_state": "dropped"}},
            "unavailable_evidence",
        ),
        ({"ev": {"reviewer_ok": False}}, "pending_evidence_review"),
    ],
)
def test_review_gate(evidence, status):
    result = evaluate_categorical(
        config(), [40], dataset_id="codes_v1", evidence=evidence
    )
    assert np.isnan(result.values[0]) and result.status[0] == status


def test_different_codebooks_cannot_be_substituted():
    with pytest.raises(ValueError, match="Dataset mismatch"):
        evaluate_categorical(config(), [40], dataset_id="other")


@pytest.mark.parametrize("mask", [[0.5], [np.inf], [1, 0]])
def test_invalid_host_masks_rejected(mask):
    with pytest.raises(ValueError, match="Mask"):
        evaluate([30], masks={"host": mask})


def test_numeric_code_aliases_rejected():
    row = config()
    row["relationship_params"]["class_map"]["40.0"] = 0
    with pytest.raises(ValueError, match="Duplicate"):
        evaluate_categorical(row, [40], dataset_id="codes_v1")


def test_false_host_dominates_unknown_host():
    row = config()
    row["relationship_params"]["class_requirements"]["30"] = ["missing", "absent"]
    result = evaluate_categorical(
        row,
        [30],
        dataset_id="codes_v1",
        masks={"absent": [0]},
        evidence={"ev": {"reviewer_ok": True}},
    )
    assert result.values[0] == 0


def family(name, **kw):
    return evaluate_family(
        SCHEMA,
        "agroforestry",
        "agroforestry__" + name,
        {
            "esa_worldcover_2021": np.array([40, 30, 10, 80]),
            "gpw_grassland_class_v1": np.array([0, 1, 2, 0]),
        },
        **kw,
    )


def test_live_schema_family_rules_and_missing_families():
    np.testing.assert_equal(
        family("planted_silvoarable").values, [1, np.nan, np.nan, 0]
    )
    np.testing.assert_equal(
        family(
            "planted_silvoarable",
            masks={"managed_forage_without_grazing": [0, 1, 0, 0]},
        ).values,
        [1, 1, np.nan, 0],
    )
    np.testing.assert_equal(
        family("regeneration_farmland").values, [1, np.nan, np.nan, 0]
    )
    np.testing.assert_equal(
        family(
            "regeneration_farmland",
            masks={
                "farmland_context": [0, 1, 0, 0],
            },
        ).values,
        [1, 1, np.nan, 0],
    )
    assert family("silvopastoral").status[1] == "missing_host_context"
    np.testing.assert_equal(
        family(
            "silvopastoral",
            approved_only=False,
            masks={"grazing_system_present": [0, 1, 0, 0]},
        ).values,
        [0, 1, 0, 0],
    )
    for name in ["linear_boundary", "shaded_perennial"]:
        result = family(name)
        assert np.isnan(result.values[:3]).all()
        assert result.values[-1] == 0
    assert set(family("homegardens_proximity").status) == {"qualitative_only"}


def host_meta(crop, basis="observed"):
    return {
        "dataset_id": "survey_2026_" + crop,
        "source_reference": "test survey",
        "data_basis": basis,
        "host_crop": crop,
        "unit": "fraction_of_pixel",
    }


def test_crop_alternatives_use_max_and_retain_drivers():
    masks = {
        "coffee_host_fraction": [1, 0, 1, 0],
        "cocoa_host_fraction": [0, 1, 1, 0],
        "tea_host_fraction": [0, 0, 0, 0],
    }
    meta = {
        crop + "_host_fraction": host_meta(crop) for crop in ("coffee", "cocoa", "tea")
    }
    result = family(
        "shaded_perennial", approved_only=False, masks=masks, mask_metadata=meta
    )
    np.testing.assert_equal(result.values, [1, 1, 1, 0])
    assert result.driver_crops.tolist() == ["coffee", "cocoa", "cocoa|coffee", ""]
    np.testing.assert_equal(
        family(
            "shaded_perennial",
            crop="coffee",
            approved_only=False,
            masks=masks,
            mask_metadata=meta,
        ).values,
        [1, 0, 1, 0],
    )
    with pytest.raises(ValueError, match="Crop"):
        family("shaded_perennial", crop="unconfigured_crop")


def test_crop_unknown_alternative_does_not_erase_known_pass():
    result = family(
        "shaded_perennial",
        approved_only=False,
        masks={"coffee_host_fraction": [1, 0, 0, 0]},
        mask_metadata={"coffee_host_fraction": host_meta("coffee")},
    )
    np.testing.assert_equal(result.values, [1, np.nan, np.nan, 0])
    assert result.driver_crops[0] == "coffee"


@pytest.mark.parametrize("basis", ["niche_model"])
def test_modelled_host_is_not_observed_presence(basis):
    result = family(
        "shaded_perennial",
        crop="coffee",
        approved_only=False,
        masks={"coffee_host_fraction": [1, 1, 1, 0]},
        mask_metadata={"coffee_host_fraction": host_meta("coffee", basis)},
    )
    np.testing.assert_equal(result.values, [np.nan, np.nan, np.nan, 0])
    assert result.status[0] == "incompatible_host_data"


def test_boundary_geometry_suffices_for_cropland_and_grassland():
    result = family(
        "linear_boundary",
        approved_only=False,
        masks={
            "field_boundary_zone": [1, 1, 1, 0],
        },
        mask_metadata={
            "field_boundary_zone": {
                "dataset_id": "fields",
                "source_reference": "test boundary survey",
                "data_basis": "observed_geometry",
                "placement": "field_boundary",
            }
        },
    )
    np.testing.assert_equal(result.values, [1, 1, np.nan, 0])
    assert result.spatial_product_type == "applicability_zone"
    assert result.applicable_subpractices == ("windbreaks_shelterbelts",)
    assert np.isnan(family("linear_boundary", approved_only=False).values[0])


def test_mapping_approval_is_separate_from_evidence_approval():
    row = config()
    row["relationship_params"]["mapping_review_status"] = "pending"
    result = evaluate_categorical(
        row, [40], dataset_id="codes_v1", evidence={"ev": {"reviewer_ok": True}}
    )
    assert result.status[0] == "pending_mapping_review"
    assert np.isnan(result.values[0])


def test_scoping_fraction_or_retains_crop_extent_and_tea_driver():
    result = family(
        "shaded_perennial",
        masks={
            "coffee_host_fraction": [0.2, 0, 0.1, 1],
            "cocoa_host_fraction": [0, 0, 0.3, 0],
            "tea_host_fraction": [0, 0.15, 0, 0],
        },
        mask_metadata={
            crop + "_host_fraction": host_meta(crop, "modelled_allocation")
            for crop in ("coffee", "cocoa", "tea")
        },
    )
    np.testing.assert_equal(result.values, [1, 1, 1, 0])
    assert result.driver_crops.tolist() == ["coffee", "tea", "cocoa|coffee", ""]
    np.testing.assert_equal(result.crop_fractions["coffee"], [0.2, 0, 0.1, 0])
    np.testing.assert_equal(result.crop_fractions["cocoa"], [0, 0, 0.3, 0])
    np.testing.assert_equal(result.crop_fractions["tea"], [0, 0.15, 0, 0])


@pytest.mark.parametrize("value", [-0.1, 20, float("inf")])
def test_fraction_masks_reject_invalid_units_and_values(value):
    with pytest.raises(ValueError, match="fractions"):
        family(
            "shaded_perennial",
            crop="coffee",
            masks={"coffee_host_fraction": [value, 0, 0, 0]},
            mask_metadata={"coffee_host_fraction": host_meta("coffee")},
        )


def test_fraction_mask_requires_fraction_unit_provenance():
    meta = host_meta("coffee", "modelled_allocation")
    meta["unit"] = "hectares"
    result = family(
        "shaded_perennial",
        crop="coffee",
        masks={"coffee_host_fraction": [0.2, 0, 0, 0]},
        mask_metadata={"coffee_host_fraction": meta},
    )
    assert result.status[0] == "incompatible_host_data"
    assert np.isnan(result.crop_fractions["coffee"][0])


def test_gpw_both_grassland_classes_require_local_confirmation():
    for mask, expected in [([0, 1, 1, 0], [0, 1, 1, 0]), ([0, 0, 0, 0], [0, 0, 0, 0])]:
        np.testing.assert_equal(
            family("silvopastoral", masks={"grazing_system_present": mask}).values,
            expected,
        )
    np.testing.assert_equal(family("silvopastoral").values, [0, np.nan, np.nan, 0])


def test_gpw_unknown_codes_and_missing_dataset_stay_unknown():
    result = evaluate_family(
        SCHEMA,
        "agroforestry",
        "agroforestry__silvopastoral",
        {"gpw_grassland_class_v1": np.array([np.nan, 99])},
        masks={"grazing_system_present": [1, 1]},
    )
    assert np.isnan(result.values).all()
    result = evaluate_family(
        SCHEMA,
        "agroforestry",
        "agroforestry__silvopastoral",
        {"esa_worldcover_2021": np.array([30])},
        masks={"grazing_system_present": [1]},
    )
    assert np.isnan(result.values).all()
    assert result.status[0] == "missing_dataset"
