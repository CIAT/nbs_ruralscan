from nbs_ruralscan.recipe.family_coverage import family_coverage


def unit(eid="a", **changes):
    return dict(
        evidence_id=eid,
        nbs_id="af",
        source_id="s",
        suitability_family_id="af__cross_family",
        variable="rain",
        use_role="structural_suitability",
        claim_scope="practice_technology",
        context={"model_use": {"verified": True}},
        relationship={"direction": "increasing"},
        reviewer_ok="true",
        **changes,
    )


def test_family_counts_no_inheritance_duplicates_or_drops():
    a = unit()
    duplicate = unit("b")
    dropped = unit("c", review_state="dropped")
    dropped["source_id"] = "rejected"
    r = family_coverage([a, duplicate, dropped], [], {}, "af")
    assert len(r) == 1
    assert r[0]["family"] == "af__cross_family"
    assert r[0]["evidence_papers"] == 1
    assert r[0]["verified_model_use_papers"] == 1
    assert r[0]["direction_counts"] == {"increasing": 1}
    assert r[0]["evidence_ids"] == ["a", "b"]


def test_presence_is_not_direction_and_scoped_claims_stay_out():
    a = unit()
    a["relationship"] = {
        "type": "observed_presence",
        "direction": "practice_present_in_range",
    }
    b = unit("b")
    b["claim_scope"] = "species_specific"
    c = unit("c")
    c["use_role"] = "operational_risk"
    r = family_coverage([a, b, c], [], {}, "af")[0]
    assert r["observed_presence_papers"] == 1
    assert r["direction_counts"] == {}
    assert r["evidence_ids"] == ["a"]


def test_conflicts_and_model_scope_and_configured_rule_independent():
    a = unit()
    b = unit("b")
    b["relationship"] = {"direction": "decreasing"}
    for x in [a, b]:
        x["context"]["model_use"]["scope"] = "species_selection"
    mapping = dict(
        nbs_id="af",
        suitability_family_id="af__planted",
        variable="rain",
        mapping_id="rule",
        relationship_type="piecewise",
        weight_default="1",
        evidence_ids='["a"]',
    )
    rows = family_coverage([a, b], [mapping], {}, "af")
    shared = next(r for r in rows if r["family"] == "af__cross_family")
    planted = next(r for r in rows if r["family"] == "af__planted")
    assert shared["direction_counts"] == {"conflicting_within_source": 1}
    assert shared["verified_model_use_papers"] == 0
    assert planted["evidence_papers"] == 0
    assert planted["mapping_ids"] == ["rule"]


def test_required_boundary_geometry_is_separate_from_land_cover():
    mapping = dict(
        nbs_id="af",
        suitability_family_id="af__linear",
        variable="land_cover",
        mapping_id="host_gate",
        relationship_type="ranked_classes",
        weight_default="0",
        evidence_ids=["source_claim"],
        relationship_params={
            "class_requirements": {
                "30": ["field_boundary_zone"],
                "40": ["field_boundary_zone"],
            },
            "host_bindings": {
                "field_boundary_zone": {
                    "variables": ["field_boundary_zone"],
                    "operation": "supplied_mask",
                    "note": "Observed geometry; locally justified width.",
                }
            },
        },
    )
    rows = family_coverage([], [mapping], {}, "af")
    boundary = next(r for r in rows if r["variable"] == "field_boundary_zone")
    land = next(r for r in rows if r["variable"] == "land_cover")
    assert boundary["mapping_ids"] == []
    assert boundary["evidence_papers"] == 0
    assert len(boundary["required_input_for"]) == 1
    assert boundary["required_input_for"][0]["evidence_ids"] == ["source_claim"]
    assert land["mapping_ids"] == ["host_gate"]
    assert land["required_input_for"] == []
