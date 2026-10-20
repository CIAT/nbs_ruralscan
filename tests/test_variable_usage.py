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
