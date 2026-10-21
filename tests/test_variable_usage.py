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


def test_source_proxy_labels_do_not_assert_tenure_or_canopy_equivalence():
    """Preserve distinct source constructs and existing quarantine decisions."""
    import csv
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    with (root / "schema/registers/EV_evidence_register.csv").open() as handle:
        rows = {r["evidence_id"]: r for r in csv.DictReader(handle)}
    ownership = rows["ev_operational_risk_tenure_security_baldwin_2022_full"]
    assert ownership["variable"] == "ownership_consolidation"
    assert ownership["raw_name"] == "Single Entity Ownership"
    assert ownership["use_role"] == "operational_risk"
    assert not any(
        r["source_id"] == "baldwin_2022" and r["variable"] == "tenure_security"
        for r in rows.values()
    )
    with (root / "schema/registers/VONT_variable_ontology.csv").open() as handle:
        ontology = {r["canonical_variable_id"]: r for r in csv.DictReader(handle)}
    assert ontology["ownership_consolidation"]["review_status"] == "pending_review"
    assert (
        json.loads(ontology["ownership_consolidation"]["candidate_dataset_ids"]) == []
    )
    trees = rows["ev_structural_suitability_tree_canopy_cover_pinto_2019_full"]
    assert trees["raw_name"] == "land occupied by trees"
    assert trees["review_state"] == "dropped"
    assert json.loads(trees["context"])["canonical_mapping_hold"]


def test_paper_review_counts_partition_duplicates_and_quarantine():
    def unit(eid, source, approved=False, dropped=False, scope="practice_technology"):
        return dict(
            evidence_id=eid,
            source_id=source,
            variable="slope",
            claim_scope=scope,
            suitability_family_id="regional",
            reviewer_ok=approved,
            review_state="dropped" if dropped else "",
            context={
                "model_use": {
                    "verified": True,
                    "method": "AHP",
                    "page": "5",
                    "weight_path_pct": [10],
                }
            },
        )

    units = [
        unit("a1", "a", True),
        unit("a2", "a"),
        unit("a3", "a", True, True),
        unit("b1", "b"),
        unit("b2", "b"),
        unit("c1", "c", True, True),
        unit("crop1", "a", False, False, "crop_specific"),
    ]
    usage = variable_usage(units, {})
    summary = summarize_usage(usage)[0]
    assert summary["verified_general_model_papers"] == 3
    assert summary["reviewed_general_model_papers"] == 1
    assert summary["pending_general_model_papers"] == 1
    assert summary["quarantined_only_general_model_papers"] == 1
    assert summary["pending_crop_species_model_papers"] == 1
    a = next(
        r
        for r in usage
        if r["source_id"] == "a" and r["claim_scope"] == "practice_technology"
    )
    assert a["reviewed_evidence_ids"] == ["a1"]
    assert a["pending_evidence_ids"] == ["a2"]
    assert a["quarantined_evidence_ids"] == ["a3"]
    assert "not all reported weights are human-approved" in a["note"]
    # Source aliases sharing a DOI still supply one paper vote.
    alias = unit("alias", "alias")
    summary = summarize_usage(
        variable_usage(
            [unit("orig", "a", True), alias],
            {"a": {"doi": "same"}, "alias": {"doi": "same"}},
        )
    )[0]
    assert summary["reviewed_general_model_papers"] == 1
    assert summary["pending_general_model_papers"] == 0


def test_model_lineage_keeps_threshold_citations_separate_and_holds_bad_links():
    def unit(eid, sid, origin=None, setting="north"):
        use = {"verified": True, "method": "AHP", "page": "1", "weight_path_pct": [10]}
        if origin:
            use["lineage_of"] = origin
        return dict(
            evidence_id=eid,
            source_id=sid,
            variable="slope",
            claim_scope="practice_technology",
            suitability_family_id="regional",
            context={"study_area": setting, "model_use": use},
        )

    primary = unit("primary", "a")
    secondary = unit("secondary", "b", "primary")
    own_model = unit("own", "c")
    own_model["lineage_of"] = (
        "primary"  # Threshold borrowed; own model use is distinct.
    )
    broken = unit("broken", "d", "missing")
    cycle1, cycle2 = unit("cycle1", "e", "cycle2"), unit("cycle2", "f", "cycle1")
    rows = variable_usage([primary, secondary, own_model, broken, cycle1, cycle2], {})
    by_source = {r["source_id"]: r for r in rows}
    assert (
        by_source["a"]["model_origin_ids"]
        == by_source["b"]["model_origin_ids"]
        == ["a"]
    )
    assert by_source["c"]["model_origin_ids"] == ["c"]
    assert by_source["c"]["response_lineage"] == ["primary"]
    assert by_source["d"]["origin_status"] == "held"
    assert (
        by_source["e"]["model_origin_ids"] == by_source["f"]["model_origin_ids"] == []
    )
    summary = summarize_usage(rows)[0]
    assert summary["verified_general_model_papers"] == 6
    assert summary["recorded_general_model_origins"] == 2
    assert summary["general_papers_with_origin_holds"] == 3
    # Same paper, different settings: separate weight records, one paper count.
    south = unit("south", "a", setting="south")
    south["context"]["model_use"]["weight_path_pct"] = [20]
    rows = variable_usage([primary, south], {})
    assert len(rows) == 2
    assert not any(r["weight_conflict"] for r in rows)
    assert summarize_usage(rows)[0]["verified_general_model_papers"] == 1
    # DOI aliases normalize case and resolver prefixes, preserving all source IDs.
    rows = variable_usage(
        [primary, unit("alias", "alias")],
        {"a": {"doi": "https://doi.org/10.1/ABC"}, "alias": {"doi": "10.1/abc"}},
    )
    assert len(rows) == 1
    assert rows[0]["source_ids"] == ["a", "alias"]
    # Source references resolve directly; an unverified evidence target is held.
    rows = variable_usage([unit("ref", "b", "a")], {"a": {"doi": "DOI:10.1/ABC"}})
    assert rows[0]["model_origin_ids"] == ["10.1/abc"]
    unverified = unit("unverified", "a")
    unverified["context"]["model_use"]["verified"] = False
    rows = variable_usage([unverified, unit("ref", "b", "unverified")], {})
    assert rows[0]["model_origin_ids"] == []
    assert "lacks verified" in rows[0]["model_origin_holds"][0]
