from pathlib import Path

import numpy as np
import pytest

from nbs_ruralscan.runtime.host_inputs import crop_area_fraction, plan_family_inputs

SCHEMA = Path(__file__).resolve().parents[1] / "schema"


def test_crop_plan_resolves_species_bands_and_sle_fallback():
    p = plan_family_inputs(
        SCHEMA, "agroforestry", "agroforestry__shaded_perennial", {"SLE"}
    )
    coffee = p["coffee_host_fraction"]
    assert coffee["status"] == "ready_to_fetch"
    assert {v["band"] for v in coffee["inputs"].values()} == {"32", "33"}
    cocoa = p["cocoa_host_fraction"]["inputs"]["cocoa_distribution"]
    assert cocoa["needs_upload"] and cocoa["band"] == "34"
    assert cocoa["dataset_id"] == "mapspam_physical_area_2020"
    assert "physical_area-all.tif" in cocoa["dataset"]["download_url"]
    assert p["tea_host_fraction"]["inputs"]["tea_distribution"]["band"] == "35"


def test_boundary_and_grazing_do_not_get_fabricated_fallback():
    p = plan_family_inputs(
        SCHEMA, "agroforestry", "agroforestry__linear_boundary", set()
    )
    assert p["field_boundary_zone"]["status"] == "requires_upload"
    assert (
        p["field_boundary_zone"]["inputs"]["field_boundary_zone"]["dataset_id"] is None
    )
    p = plan_family_inputs(SCHEMA, "agroforestry", "agroforestry__silvopastoral", set())
    grazing = p["grazing_system_present"]
    assert grazing["status"] == "requires_upload"
    assert grazing["inputs"]["grassland_class"]["band"] == "dominant_class"
    assert "ruminant_density" not in grazing["inputs"]


def test_physical_area_conversion_preserves_unknown_and_rejects_overallocation():
    np.testing.assert_equal(
        crop_area_fraction([[20, np.nan], [30, 10]], [100, 100]), [0.5, np.nan]
    )
    for components, area in [
        ([[60], [60]], [100]),
        ([[-1]], [100]),
        ([[1]], [0]),
        ([[1, 2]], [100]),
    ]:
        with pytest.raises(ValueError):
            crop_area_fraction(components, area)


def test_stale_numeric_t4_rows_removed():
    import json

    rows = json.loads(
        (SCHEMA / "recipes/agroforestry/T4_suitability_mappings.json").read_text(
            encoding="utf-8"
        )
    )
    numeric = [
        r for r in rows if r["suitability_dimension"] == "biophysical_constraint"
    ]
    assert len(numeric) == 8
    slope = next(
        r
        for r in numeric
        if r["mapping_id"] == "agroforestry__planted_silvoarable__slope"
    )
    assert slope["relationship_params"]["threshold"] == 19.3
    assert slope["relationship_params"]["above_is_suitable"] is False
    assert len(slope["relationship_params"]["profiles"]) == 2
    assert len(slope["relationship_params"]["harmonization"]["pools"]) == 1
    assert (
        len(
            [
                r
                for r in rows
                if r.get("relationship_params", {}).get("mapping_role")
                == "eligibility_gate"
            ]
        )
        == 7
    )
    assert (
        len([r for r in rows if r["suitability_dimension"] == "operational_constraint"])
        == 9
    )
