"""Tests for evidence module — dedup and load/save round-trip."""

import json
import textwrap

from nbs_ruralscan.recipe.evidence import (
    EvidenceUnit,
    already_extracted,
    load_units,
    save_units,
    package_for_extraction_multi,
)
from nbs_ruralscan.ingest.models import DocIndex


from typing import Any


def _sample_unit(**overrides: Any) -> EvidenceUnit:
    defaults: dict[str, Any] = dict(
        evidence_id="ev_test_01",
        source_id="smith_2020",
        nbs_id="agroforestry",
        suitability_family_id="agroforestry__planted_silvoarable",
        variable="slope",
        use_role="structural_suitability",
        evidence_type="literature_relationship",
        claim_basis="primary_measured",
        claim_scope="practice_technology",
        extraction_confidence="high",
        quote="Slopes above 30 degrees are unsuitable.",
        page=7,
    )
    defaults.update(overrides)
    return EvidenceUnit(**defaults)


def test_save_load_round_trip(tmp_path):
    units = [_sample_unit(), _sample_unit(evidence_id="ev_test_02", page=12)]
    out = save_units(units, tmp_path / "ev.json")
    loaded = load_units(out)
    assert len(loaded) == 2
    assert loaded[0].evidence_id == "ev_test_01"
    assert loaded[1].page == 12


def test_load_units_missing_file(tmp_path):
    loaded = load_units(tmp_path / "missing.json")
    assert loaded == []


def test_load_units_forward_compat(tmp_path):
    """Extra keys in the JSON (from a future schema) are silently dropped."""
    data = [
        {
            "evidence_id": "ev_future",
            "source_id": "x",
            "nbs_id": "y",
            "suitability_family_id": "z",
            "variable": "rain",
            "use_role": "structural_suitability",
            "evidence_type": "literature_relationship",
            "claim_basis": "primary_measured",
            "claim_scope": "practice_technology",
            "extraction_confidence": "high",
            "quote": "q",
            "page": 1,
            "new_future_field": "should be ignored",
        }
    ]
    p = tmp_path / "ev.json"
    p.write_text(json.dumps(data))
    loaded = load_units(p)
    assert len(loaded) == 1
    assert loaded[0].evidence_id == "ev_future"
    assert not hasattr(loaded[0], "new_future_field")


def test_already_extracted_finds_existing(tmp_path):
    csv_content = textwrap.dedent("""\
        evidence_id,source_id,variable,nbs_id,other
        ev_slope_nath21,nath_2021,slope,agroforestry,x
        ev_slope_zomer14,zomer_2014,slope,agroforestry,x
        ev_rain_nath21,nath_2021,annual_precipitation,agroforestry,x
    """)
    ev = tmp_path / "EV.csv"
    ev.write_text(csv_content)

    result = already_extracted("nath_2021", "slope", ev_register=ev)
    assert result == ["ev_slope_nath21"]


def test_already_extracted_returns_empty_when_not_found(tmp_path):
    csv_content = textwrap.dedent("""\
        evidence_id,source_id,variable,nbs_id
        ev_slope_nath21,nath_2021,slope,agroforestry
    """)
    ev = tmp_path / "EV.csv"
    ev.write_text(csv_content)

    result = already_extracted("nath_2021", "soil_depth", ev_register=ev)
    assert result == []


def test_already_extracted_missing_file(tmp_path):
    result = already_extracted("x", "y", ev_register=tmp_path / "nope.csv")
    assert result == []


def test_package_for_extraction_multi(tmp_path):
    # Setup dummy document with multiple term mentions
    index = DocIndex(
        source_id="nath_2021",
        path="nath.pdf",
        sha1="sha123",
        n_pages=1,
        pages=[
            "Alley cropping is highly suitable on slope of 0-5 degrees. "
            "However, if annual precipitation is less than 600mm, it fails."
        ],
    )

    # We want to search for two variables
    variables = [
        {"variable": "slope", "aliases": ["gradient"]},
        {"variable": "annual_precipitation", "aliases": ["rainfall", "precipitation"]},
    ]

    # Run packaging without any ev register (so no skipping)
    res = package_for_extraction_multi(
        index, variables, ev_register=tmp_path / "EV.csv"
    )

    assert res["source_id"] == "nath_2021"
    assert "slope" in res["variables"]
    assert "annual_precipitation" in res["variables"]
    assert len(res["skipped"]) == 0

    # The text contains both slope and precipitation in the same passage window.
    # Therefore, the deduplicated passages list should have exactly one passage,
    # and it should be flagged as relevant to BOTH variables.
    assert len(res["passages"]) == 1
    passage = res["passages"][0]
    assert "relevant_to" in passage
    assert sorted(passage["relevant_to"]) == ["annual_precipitation", "slope"]


def test_package_for_extraction_multi_skips_and_force(tmp_path):
    index = DocIndex(
        source_id="nath_2021",
        path="nath.pdf",
        sha1="sha123",
        n_pages=1,
        pages=["Slope is 5% and rainfall is 800mm."],
    )

    # Write EV register containing nath_2021 and slope already extracted
    csv_content = textwrap.dedent("""\
        evidence_id,source_id,variable,nbs_id
        ev_slope_nath21,nath_2021,slope,agroforestry
    """)
    ev = tmp_path / "EV.csv"
    ev.write_text(csv_content)

    variables = [
        {"variable": "slope", "aliases": ["gradient"]},
        {"variable": "annual_precipitation", "aliases": ["rainfall"]},
    ]

    # Run packaging: should skip 'slope' but keep 'annual_precipitation'
    res = package_for_extraction_multi(index, variables, ev_register=ev)
    assert "annual_precipitation" in res["variables"]
    assert "slope" not in res["variables"]
    assert res["skipped"] == ["slope"]
    assert len(res["passages"]) == 1
    assert res["passages"][0]["relevant_to"] == ["annual_precipitation"]

    # Run packaging with force=True: should NOT skip 'slope'
    res_force = package_for_extraction_multi(
        index, variables, ev_register=ev, force=True
    )
    assert sorted(res_force["variables"]) == ["annual_precipitation", "slope"]
    assert len(res_force["skipped"]) == 0
    assert sorted(res_force["passages"][0]["relevant_to"]) == [
        "annual_precipitation",
        "slope",
    ]
