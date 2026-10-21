from nbs_ruralscan.recipe.variable_usage import variable_usage, summarize_usage


def test_usage_deduplicates_papers_preserves_scope_and_nested_weights():
    unit = {
        "variable": "soil_organic_carbon",
        "claim_scope": "practice_technology",
        "source_id": "a",
        "evidence_id": "one",
        "suitability_family_id": "cross_family",
        "context": {
            "model_use": {
                "verified": True,
                "method": "expert_weight",
                "page": "11",
                "weight_path_pct": [25, 20, 20],
            }
        },
    }
    duplicate = dict(unit, evidence_id="two", review_state="dropped")
    unverified = dict(unit, evidence_id="three", source_id="b", context={})
    records = variable_usage([unit, duplicate, unverified], {})
    assert len(records) == 1
    assert records[0]["effective_model_weight_pct"] == 1
    assert records[0]["evidence_ids"] == ["one", "two"]
    assert summarize_usage(records)[0]["verified_general_model_papers"] == 1
    scoped = dict(unit, claim_scope="species_specific", source_id="c")
    summary = summarize_usage(variable_usage([unit, scoped], {}))[0]
    assert summary["verified_general_model_papers"] == 1
    assert summary["verified_crop_species_model_papers"] == 1


def test_model_scope_does_not_inherit_generic_scope_of_secondary_quote():
    row = {
        "variable": "annual_precipitation",
        "claim_scope": "practice_technology",
        "source_id": "mulberry",
        "evidence_id": "secondary_assertion",
        "suitability_family_id": "shaded",
        "context": {
            "model_use": {
                "verified": True,
                "method": "AHP",
                "page": "13",
                "scope": "species_specific",
                "weight_path_pct": [14.98],
            }
        },
    }
    result = summarize_usage(variable_usage([row], {}))[0]
    assert result["verified_general_model_papers"] == 0
    assert result["verified_crop_species_model_papers"] == 1


def test_species_selection_method_does_not_inflate_practice_agreement():
    records = [
        {
            "variable": "soil_ph",
            "claim_scope": "species_selection",
            "paper_key": "ellis",
            "source_id": "ellis_2000",
        }
    ]
    summary = summarize_usage(records)[0]
    assert summary["verified_general_model_papers"] == 0
    assert summary["verified_crop_species_model_papers"] == 0
    assert summary["verified_species_selection_model_papers"] == 1


def test_conflicting_source_tables_do_not_emit_settled_weight():
    row = dict(
        variable="slope",
        claim_scope="practice_technology",
        source_id="haile",
        evidence_id="slope",
        suitability_family_id="regional",
        context={
            "model_use": {
                "verified": True,
                "method": "AHP",
                "page": "4,9",
                "weight_path_pct": [30],
                "weight_alternatives_pct": [[30], [29.5]],
                "weight_conflict": True,
            }
        },
    )
    result = variable_usage([row], {})[0]
    assert result["weight_conflict"]
    assert result["effective_model_weight_pct"] is None
    assert result["reported_weight_paths_pct"] == [[29.5], [30]]


def test_identical_weights_in_distinct_branches_are_not_a_total():
    def row(eid, branch):
        return dict(
            variable="soil_ph",
            claim_scope="practice_technology",
            source_id="nath",
            evidence_id=eid,
            suitability_family_id="regional",
            context={
                "branch": branch,
                "model_use": {
                    "verified": True,
                    "method": "expert",
                    "page": "11",
                    "weight_path_pct": [25, 20, 20],
                },
            },
        )

    result = variable_usage([row("a", "nutrients"), row("b", "rooting")], {})[0]
    assert result["branch_aggregation_unresolved"]
    assert result["effective_model_weight_pct"] is None
    assert result["weight_branches"] == ["nutrients", "rooting"]


def test_chuma_road_weight_does_not_become_travel_time_or_structural_response():
    """Table 2 criterion weights must not inherit the old false proxy label."""
    import csv
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    with (root / "schema/registers/EV_evidence_register.csv").open() as handle:
        units = [r for r in csv.DictReader(handle) if r["source_id"] == "chuma_2021"]
    record = next(
        r
        for r in units
        if r["evidence_id"] == "ev_T4_accessibility_travel_time_chuma21_1"
    )
    assert record["variable"] == "distance_to_road"
    assert record["use_role"] == "operational_risk"
    assert record["evidence_type"] == "scoping_candidate"
    assert json.loads(record["relationship"])["type"] == "model_use_only"
    original = json.loads(record["context"])["source_corrections"][-1][
        "original_record"
    ]
    assert original["variable"] == "accessibility_travel_time"
    assert "84%" in original["quote"]
    usage = variable_usage(units, {})
    assert not any(r["variable"] == "accessibility_travel_time" for r in usage)
    roads = [r for r in usage if r["variable"] == "distance_to_road"]
    assert len(roads) == 1
    assert roads[0]["effective_model_weight_pct"] == 10.8
    with (
        root / "schema/recipes/agroforestry/T4_suitability_mappings.csv"
    ).open() as handle:
        structural = [
            r
            for r in csv.DictReader(handle)
            if r["suitability_dimension"] != "operational_constraint"
        ]
    assert all(
        record["evidence_id"] not in json.loads(r["evidence_ids"] or "[]")
        for r in structural
    )
