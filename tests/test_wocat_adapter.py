"""WOCAT adapter: deterministic render + rule-based units (ingest/wocat.py)."""

from __future__ import annotations

from nbs_ruralscan.ingest import wocat
from nbs_ruralscan.recipe.cell_synthesis import _default_bands

PAYLOAD = {
    "id": 999,
    "selected_version": {
        "name": {"en": "Test pits"},
        "country": "BF",
        "compiler": "x",
        "date_documentation": "2020-01-01",
        "slm_group": ["WATERHARVESTING"],
        "impacts_socio_economic_production": {
            "crop_production": {"value": 3, "comment": {"en": "doubled"}},
            "risk_of_production_failure": {"value": 2},
        },
        "impacts_ecological_soil": {
            "soil_loss": {"value": 2},
            "soil_moisture": {"value": 0},
        },
        "impacts_ecological_water": {"surface_runoff": {"value": 1}},
        "climatological_disaster_coping": {"drought": "NOT_WELL"},
        "hydrological_disaster_coping": {
            "flash_flood": "VERY_WELL",
            "general_river_flood": "UNKNOWN",
        },
    },
}
IMAP = wocat._load_csv(wocat.LOOKUPS / "wocat_impact_map.csv")
HMAP = wocat._load_csv(wocat.LOOKUPS / "wocat_hazard_map.csv")


def _units():
    md = wocat.render(PAYLOAD, "wocat_999_2020")
    return md, wocat.emit_units(
        "wocat_999_2020",
        PAYLOAD,
        md,
        "water_harvesting_conservation",
        "water_harvesting__in_situ",
        IMAP,
        HMAP,
        _default_bands(),
    )


def test_render_is_deterministic_and_quotes_are_lines():
    md1 = wocat.render(PAYLOAD, "wocat_999_2020")
    md2 = wocat.render(PAYLOAD, "wocat_999_2020")
    assert md1 == md2
    _, units = _units()
    lines = set(md1.splitlines())
    assert all(u["quote"] in lines for u in units)
    assert all(u["locator_type"] == "section" and u["locator"] for u in units)


def test_value_sign_maps_to_quantity_direction_and_class():
    _, units = _units()
    by = {u["locator"]: u for u in units}
    crop = by["impacts_socio_economic_production/crop_production"]
    assert crop["relationship"]["direction"] == "positive"
    assert crop["relationship"]["strength_class"] == "strong"
    loss = by["impacts_ecological_soil/soil_loss"]  # right label 'decreased', +2
    assert loss["relationship"]["direction"] == "negative"
    assert loss["relationship"]["strength_class"] == "moderate"
    runoff = by["impacts_ecological_water/surface_runoff"]  # inverted on emit
    assert runoff["variable"] == "runoff_reduction"
    assert runoff["relationship"]["direction"] == "positive"
    risk = by["impacts_socio_economic_production/risk_of_production_failure"]
    assert risk["variable"] == "food_security"
    assert risk["relationship"]["direction"] == "positive"
    zero = by["impacts_ecological_soil/soil_moisture"]
    assert zero["relationship"]["direction"] == "none"


def test_coping_scale_becomes_asset_vulnerability():
    _, units = _units()
    assets = {
        u["context"]["hazard_type"]: u
        for u in units
        if u["use_role"] == "asset_vulnerability"
    }
    assert assets["drought"]["relationship"]["direction"] == "positive"
    assert assets["drought"]["relationship"]["strength_class"] == "strong"
    assert assets["flood"]["relationship"]["direction"] == "none"


def test_unknown_coping_is_not_a_rating():
    _, units = _units()
    assert not any(u["locator"].endswith("general_river_flood") for u in units)
