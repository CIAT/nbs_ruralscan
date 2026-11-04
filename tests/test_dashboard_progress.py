"""Count contracts: overlap, incomplete search history and evidence review are distinct."""

from nbs_ruralscan.schema_tools.dashboard_progress import build_progress


def test_family_presentation_preserves_variants_evidence_and_counts():
    import copy

    data = fixture_data()
    original_registers = copy.deepcopy(data["registers"])
    before = build_progress(data, [])
    data["family_presentation"] = {
        "trees__planted": {
            "display_name": "Planted tree systems",
            "navigation_group": "practice",
            "umbrella_subpractice_id": "alley",
        }
    }
    after = build_progress(data, [])
    assert data["registers"] == original_registers
    assert before["totals"] == after["totals"]
    assert before["sources"] == after["sources"]
    for old, new in zip(before["practices"], after["practices"], strict=True):
        assert old["metrics"] == new["metrics"]
        for old_family, new_family in zip(
            old["families"], new["families"], strict=True
        ):
            assert old_family["family_id"] == new_family["family_id"]
            assert old_family["metrics"] == new_family["metrics"]
            assert [s["subpractice_id"] for s in old_family["subpractices"]] == [
                s["subpractice_id"] for s in new_family["subpractices"]
            ]
    planted = next(
        f
        for p in after["practices"]
        for f in p["families"]
        if f["family_id"] == "trees__planted"
    )
    assert planted["name"] == "Planted tree systems"
    assert [s["presentation_role"] for s in planted["subpractices"]] == [
        "umbrella",
        "variant",
    ]


def test_routing_tags_remain_counted_as_evidence_groups():
    data = fixture_data()
    data["registers"]["FAM_family_registry"].append(
        {
            "nbs_id": "trees",
            "suitability_family_id": "trees__cross_family",
            "subpractice_id": "cross_cutting",
            "name": "Cross-family evidence",
        }
    )
    data["registers"]["EV_evidence_register"][0]["suitability_family_id"] = (
        "trees__cross_family"
    )
    result = build_progress(data, [])
    families = next(p for p in result["practices"] if p["nbs_id"] == "trees")[
        "families"
    ]
    cross = next(f for f in families if f["family_id"] == "trees__cross_family")
    assert cross["navigation_group"] == "evidence"
    assert cross["subpractices"][0]["presentation_role"] == "evidence"
    assert cross["metrics"]["active_excerpts"] == 1
    assert (
        next(f for f in families if f["family_id"] == "__unassigned")[
            "navigation_group"
        ]
        == "evidence"
    )


def fixture_data():
    return {
        "registers": {
            "SRC_source_register": [
                {
                    "source_id": "paper",
                    "nbs_ids": "trees|water",
                    "source_category": "stock",
                    "source_kind": "grey_lit",
                    "venue_type": "peer_reviewed_journal",
                },
                {"source_id": "empty", "nbs_ids": "trees", "source_kind": "pdf"},
            ],
            "FAM_family_registry": [
                {
                    "nbs_id": "trees",
                    "suitability_family_id": "trees__planted",
                    "subpractice_id": "alley",
                    "name": "Alley",
                },
                {
                    "nbs_id": "trees",
                    "suitability_family_id": "trees__planted",
                    "subpractice_id": "boundary",
                    "name": "Boundary",
                },
                {
                    "nbs_id": "trees",
                    "suitability_family_id": "trees__natural",
                    "subpractice_id": "regen",
                    "name": "Regeneration",
                },
            ],
            "EV_evidence_register": [
                {
                    "evidence_id": "a",
                    "source_id": "alias",
                    "nbs_id": "trees",
                    "suitability_family_id": "trees__planted",
                    "reviewer_ok": True,
                    "use_role": "structural_suitability",
                },
                {
                    "evidence_id": "b",
                    "source_id": "paper",
                    "nbs_id": "trees",
                    "suitability_family_id": "",
                    "reviewer_ok": False,
                    "use_role": "operational_risk",
                },
                {
                    "evidence_id": "c",
                    "source_id": "paper",
                    "nbs_id": "water",
                    "reviewer_ok": "true",
                    "use_role": "nbs_effect",
                },
                {
                    "evidence_id": "d",
                    "source_id": "paper",
                    "nbs_id": "trees",
                    "reviewer_ok": True,
                    "review_state": "dropped",
                },
            ],
        },
        "recipes": {
            "trees": {
                "T4_suitability_mappings": [
                    {
                        "mapping_id": "m",
                        "nbs_id": "trees",
                        "suitability_family_id": "trees__planted",
                        "evidence_ids": '["a","a","d","missing"]',
                    },
                    {"mapping_id": "empty", "nbs_id": "trees", "evidence_ids": []},
                ],
                "T3_nbs_hazard_farming": [{"evidence_ids": ["a"]}],
                "T6_nbs_scorecard": [{"evidence_ids": ["c"]}],
                "T6E_economic_profile": [{"evidence_ids": ["b"]}],
            }
        },
    }


def test_source_union_aliases_scopes_and_no_fuzzy_merge():
    data = fixture_data()
    queue = [
        {
            "source_id": "alias",
            "duplicate_of": "paper",
            "status": "duplicate",
            "nbs_id": "trees",
            "family": "planted",
        },
        {"source_id": "paper", "status": "extracted", "nbs_id": "trees"},
        {"source_id": "third", "status": "pending", "nbs_id": "water", "doi": "same"},
        {"source_id": "fourth", "status": "pending", "nbs_id": "water", "doi": "same"},
    ]
    result = build_progress(data, queue)
    assert result["totals"]["known_sources"] == 4
    paper = next(s for s in result["sources"] if s["source_id"] == "paper")
    assert paper["aliases"] == ["alias"]
    assert paper["type"] == "literature"
    assert paper["origins"] == ["stock"]
    assert paper["queue_statuses"] == ["duplicate", "extracted"]
    assert paper["nbs_ids"] == ["trees", "water"]
    assert paper["screening"] == "not_recorded"
    assert paper["search_ids"] == []


def test_review_evidence_compiled_counts_and_family_no_inheritance():
    result = build_progress(
        fixture_data(), [{"source_id": "alias", "duplicate_of": "paper"}]
    )
    totals = result["totals"]
    assert totals["active_excerpts"] == 3
    assert totals["approved_excerpts"] == 2
    assert totals["dropped_excerpts"] == 1
    assert totals["extracted_sources"] == totals["reviewed_sources"] == 1
    assert totals["fully_reviewed_sources"] == 0
    assert totals["t4_relationships"] == 2
    assert totals["t4_evidence_backed_relationships"] == 1
    assert totals["t4_contributing_sources"] == 1
    paper = next(s for s in result["sources"] if s["source_id"] == "paper")
    assert paper["contributions"] == {
        "T4": ["a"],
        "T3": ["a"],
        "T6": ["c"],
        "M2b": ["b"],
    }
    assert result["diagnostics"]["compiled_missing_evidence_ids"] == ["missing"]
    assert result["diagnostics"]["compiled_dropped_evidence_ids"] == ["d"]
    trees = next(p for p in result["practices"] if p["nbs_id"] == "trees")
    planted = next(f for f in trees["families"] if f["family_id"] == "trees__planted")
    natural = next(f for f in trees["families"] if f["family_id"] == "trees__natural")
    assert len(planted["subpractices"]) == 2
    assert planted["metrics"]["active_excerpts"] == 1
    assert planted["metrics"]["fully_reviewed_sources"] == 1
    assert natural["metrics"]["known_sources"] == 0
    assert natural["metrics"]["fully_reviewed_sources"] == 0


def search(sid, **kwargs):
    return {
        "search_id": sid,
        "run_id": "run",
        "nbs_id": "trees",
        "category": "updated_lit",
        "search_terms": "trees",
        "search_date": "2026-11-04",
        "n_retrieved": "20",
        "n_screened": "10",
        "n_included": "4",
        "table": "T4",
        **kwargs,
    }


def test_search_shared_tables_and_strict_complete_record_ratio():
    data = fixture_data()
    data["registers"]["SRCH_search_register"] = [
        search("t3", table="T3"),
        search("t6", table="T6"),
        search("approx", run_id="approx", n_retrieved="~100", n_screened="64 shared"),
        search("missing", run_id="missing", n_retrieved="1000", n_screened=""),
        search("invalid", run_id="invalid", n_retrieved="1", n_screened="8"),
    ]
    result = build_progress(data, [])
    assert len(result["searches"]) == 4
    shared = result["searches"][0]
    assert shared["tables"] == ["T3", "T6"]
    assert shared["search_ids"] == ["t3", "t6"]
    counts = result["totals"]["search_metrics"]
    assert counts["retrieved"] == 1020
    assert counts["screened"] == 10
    assert counts["screened_pct"] == 50.0
    assert counts["complete_counts"] == 1
    assert counts["coverage"]["retrieved"] == {"recorded": 2, "total": 4}
    assert result["searches"][1]["raw_counts"][0]["n_screened"] == "64 shared"


def test_search_conflicts_excluded_blank_runs_not_merged():
    data = {
        "registers": {
            "SRCH_search_register": [
                search("a"),
                search("b", n_retrieved="21"),
                search("blank1", run_id=""),
                search("blank2", run_id=""),
            ]
        }
    }
    result = build_progress(data, [])
    assert len(result["searches"]) == 3
    assert result["searches"][0]["counts_conflict"] is True
    assert result["totals"]["search_metrics"]["retrieved"] == 40


def test_alias_cycles_dangling_targets_and_explicit_tool_join():
    data = {
        "registers": {
            "SRC_source_register": [{"source_id": "a"}, {"source_id": "b"}],
            "TOOL_tool_registry": [
                {"tool_id": "tool", "source_id": "a"},
                {"tool_id": "legacy"},
            ],
        }
    }
    result = build_progress(
        data,
        [
            {"source_id": "a", "duplicate_of": "b"},
            {"source_id": "b", "duplicate_of": "a"},
            {"source_id": "old", "duplicate_of": "target"},
        ],
    )
    assert result["totals"]["known_sources"] == 2
    assert [s["source_id"] for s in result["sources"]] == ["a", "target"]
    assert result["sources"][0]["type"] == "tools"
    assert len(result["sources"][0]["tools"]) == 1


def test_missing_counts_empty_sources_and_repeat_dropped_payload():
    result = build_progress({}, [])
    assert result["totals"]["fully_reviewed_sources"] == 0
    assert result["totals"]["search_metrics"]["screened_pct"] is None
    assert result["totals"]["search_metrics"]["retrieved"] is None
    data = fixture_data()
    data["_evDropped"] = [data["registers"]["EV_evidence_register"][-1]]
    assert build_progress(data, [])["totals"]["dropped_excerpts"] == 1


def test_unassigned_bucket_historical_total_and_operational_t4():
    data = fixture_data()
    data["recipes"]["trees"]["T4_suitability_mappings"][1]["suitability_dimension"] = (
        "operational_constraint"
    )
    data["recipes"]["trees"]["T4_suitability_mappings"][1]["is_scenario_candidate"] = (
        True
    )
    result = build_progress(data, [{"source_id": "alias", "duplicate_of": "paper"}])
    trees = next(p for p in result["practices"] if p["nbs_id"] == "trees")
    unassigned = next(f for f in trees["families"] if f["family_id"] == "__unassigned")
    assert unassigned["metrics"]["known_sources"] == 2
    assert unassigned["metrics"]["active_excerpts"] == 1
    assert unassigned["metrics"]["all_excerpts"] == 2
    assert result["totals"]["all_excerpts"] == 4
    assert result["totals"]["t4_structural_relationships"] == 1
    assert result["totals"]["t4_operational_relationships"] == 1


def test_uncited_excerpts_have_extraction_counts_separate_from_compilation():
    data = fixture_data()
    data["registers"]["EV_evidence_register"] += [
        {
            "evidence_id": "uncited_t4",
            "source_id": "paper",
            "nbs_id": "trees",
            "use_role": "structural_suitability",
        },
        {
            "evidence_id": "uncited_effect",
            "source_id": "paper",
            "nbs_id": "trees",
            "use_role": "nbs_effect",
        },
        {
            "evidence_id": "asset",
            "source_id": "paper",
            "nbs_id": "trees",
            "use_role": "asset_vulnerability",
        },
        {
            "evidence_id": "dataset",
            "source_id": "paper",
            "nbs_id": "trees",
            "use_role": "dataset",
        },
    ]
    result = build_progress(data, [{"source_id": "alias", "duplicate_of": "paper"}])
    paper = next(s for s in result["sources"] if s["source_id"] == "paper")
    assert paper["extraction_counts"] == {"T4": 2, "effects": 2, "M2b": 2, "other": 1}
    assert sum(paper["extraction_counts"].values()) == len(paper["evidence_ids"])
    assert paper["contributions"]["T4"] == ["a"]
    assert paper["contributions"]["T6"] == ["c"]
    empty = next(s for s in result["sources"] if s["source_id"] == "empty")
    assert sum(empty["extraction_counts"].values()) == 0


def test_shared_retrieval_keeps_screening_variants_without_adding_them():
    rows = [search("base"), search("shared_table", table="T6")]
    for field in ("screening_steps", "inclusion_criteria"):
        rows.append(search(field, **{field: "different screening"}))
    result = build_progress({"registers": {"SRCH_search_register": rows}}, [])
    assert len(result["searches"]) == 1
    event = result["searches"][0]
    assert event["screening_variants"] == 3
    assert len(event["raw_records"]) == 4
    assert event["counts"] == {"retrieved": 20, "screened": None, "included": None}
    assert event["complete_counts"] is False
    metrics = result["totals"]["search_metrics"]
    assert metrics["retrieved"] == 20
    assert metrics["screened_pct"] is None
    assert metrics["screening_variant_events"] == 1


def test_hard_operational_mask_stays_in_core_suitability():
    data = {
        "recipes": {
            "trees": {
                "T4_suitability_mappings": [
                    {
                        "mapping_id": "legal_mask",
                        "suitability_dimension": "operational_constraint",
                        "is_scenario_candidate": "false",
                    },
                    {
                        "mapping_id": "access",
                        "suitability_dimension": "operational_constraint",
                        "is_scenario_candidate": "true",
                    },
                    {
                        "mapping_id": "legal_mask_bool",
                        "suitability_dimension": "operational_constraint",
                        "is_scenario_candidate": False,
                    },
                ]
            }
        }
    }
    totals = build_progress(data, [])["totals"]
    assert totals["t4_relationships"] == 3
    assert totals["t4_structural_relationships"] == 2
    assert totals["t4_operational_relationships"] == 1


def test_relverify_stocktake_retrieval_not_tripled_by_table_screening():
    rows = [
        search(
            "stock_" + table,
            run_id="relverify_2026-06",
            category="stock",
            table=table,
            search_terms="300-paper benchmarked stocktake",
            limits="stocktake corpus",
            n_retrieved="300",
            n_screened="300",
            n_included=included,
            inclusion_criteria=criteria,
        )
        for table, included, criteria in [
            ("T4", "23", "Suitability relationships"),
            ("T3", "12", "Hazard relationships"),
            ("T6", "15", "Benefit relationships"),
        ]
    ]
    result = build_progress({"registers": {"SRCH_search_register": rows}}, [])
    metrics = result["totals"]["search_metrics"]
    assert metrics["events"] == 1
    assert metrics["retrieved"] == 300
    assert metrics["screened"] is None
    assert metrics["included"] is None
    assert metrics["screened_pct"] is None
    assert result["searches"][0]["count_conflict_fields"] == ["included"]


def test_count_conflicts_only_exclude_affected_field():
    rows = [search("one"), search("two", n_included="5")]
    result = build_progress({"registers": {"SRCH_search_register": rows}}, [])
    assert result["searches"][0]["counts"] == {
        "retrieved": 20,
        "screened": 10,
        "included": None,
    }
    assert result["totals"]["search_metrics"]["retrieved"] == 20
    assert result["totals"]["search_metrics"]["screened"] == 10
    assert result["totals"]["search_metrics"]["screened_pct"] is None


def test_truly_different_queries_or_retrieval_limits_stay_separate():
    rows = [
        search("base"),
        search("other_query", search_terms="different query"),
        search("other_limit", limits="screen <= 50"),
    ]
    result = build_progress({"registers": {"SRCH_search_register": rows}}, [])
    assert len(result["searches"]) == 3
    assert result["totals"]["search_metrics"]["retrieved"] == 60
    assert result["totals"]["search_metrics"]["screened_pct"] == 50


def test_complete_discovery_columns_share_one_cohort():
    data = fixture_data()
    data["registers"]["SRCH_search_register"] = [
        {
            "search_id": "partial_found",
            "nbs_id": "trees",
            "n_retrieved": "41",
            "n_screened": "",
            "n_included": "",
        },
        {
            "search_id": "partial_screened",
            "nbs_id": "trees",
            "n_retrieved": "",
            "n_screened": "93",
            "n_included": "26",
        },
        {
            "search_id": "complete",
            "nbs_id": "trees",
            "n_retrieved": "100",
            "n_screened": "20",
            "n_included": "10",
        },
    ]
    counts = build_progress(data, [])["totals"]["search_metrics"]
    assert [counts["paired_" + k] for k in ("retrieved", "screened", "included")] == [
        100,
        20,
        10,
    ]
    assert counts["complete_counts"] == 1
    assert counts["retrieved"] == 141
    assert counts["screened"] == 113
    assert counts["included"] == 36


def test_review_work_is_distinct_from_current_approval_and_detector_flags():
    data = fixture_data()
    rows = data["registers"]["EV_evidence_register"]
    for eid in ("queried", "flagged", "reopened", "unknown_drop", "retagged"):
        rows.append(
            {
                "evidence_id": eid,
                "source_id": "empty",
                "nbs_id": "trees",
                "reviewer_ok": False,
                "review_state": "dropped" if eid == "unknown_drop" else "",
            }
        )
    data["review_log"] = [
        {"evidence_id": "b", "decision": "keep"},
        {"evidence_id": "b", "decision": "keep"},  # repeated event is one claim
        {"evidence_id": "queried", "decision": "query"},
        {"evidence_id": "flagged", "decision": "flag"},
        {"evidence_id": "reopened", "decision": "ok"},
        {"evidence_id": "reopened", "decision": "reopen"},
        {"evidence_id": "retagged", "decision": "retag"},
        {"evidence_id": "not_in_register", "decision": "ok"},
    ]
    result = build_progress(data, [{"source_id": "alias", "duplicate_of": "paper"}])
    m = result["totals"]
    assert m["all_excerpts"] == 9
    assert m["reviewed_excerpts"] == 7
    assert m["reviewed_pct"] == 77.8
    assert m["unreviewed_excerpts"] == 2  # detector flag + unexplained quarantine
    assert m["approved_excerpts"] == 2
    assert m["approved_pct"] == 28.6
    assert m["reviewed_active_excerpts"] == 6
    assert m["reviewed_dropped_excerpts"] == 1
    assert m["dropped_excerpts"] == 2
    assert m["reviewed_unresolved_excerpts"] == 4
    assert m["sources_with_reviewed_excerpts"] == 2
    assert m["sources_with_approved_excerpts"] == 1
    empty = next(s for s in result["sources"] if s["source_id"] == "empty")
    assert empty["reviewed_evidence_ids"] == ["queried", "reopened", "retagged"]
    assert empty["approved_evidence_ids"] == []


def test_review_counts_include_logged_drops_but_reopen_alone_is_not_assessment():
    data = fixture_data()
    for row in data["registers"]["EV_evidence_register"]:
        row["reviewer_ok"] = False
    data["review_log"] = [
        {"evidence_id": "d", "decision": "drop"},
        {"evidence_id": "b", "decision": "reopen"},
    ]
    totals = build_progress(data, [])["totals"]
    assert totals["reviewed_excerpts"] == 1
    assert totals["reviewed_pct"] == 25.0
    assert totals["approved_excerpts"] == 0
    assert totals["approved_pct"] == 0.0
    assert totals["reviewed_dropped_excerpts"] == 1
    assert totals["reviewed_unresolved_excerpts"] == 0
    empty = build_progress({}, [])["totals"]
    assert empty["reviewed_pct"] is None
    assert empty["approved_pct"] is None


def test_all_family_tag_is_explicit_scope_not_unassigned_or_inherited():
    data = fixture_data()
    data["registers"]["FAM_family_registry"].append(
        {
            "nbs_id": "trees",
            "suitability_family_id": "trees__cross_family",
            "subpractice_id": "cross_cutting_envelope",
            "name": "Cross-cutting envelope",
            "definition": "Applies across all families; not a subpractice.",
        }
    )
    data["registers"]["EV_evidence_register"][1]["suitability_family_id"] = (
        "trees__cross_family"
    )
    result = build_progress(data, [{"source_id": "alias", "duplicate_of": "paper"}])
    tree = next(p for p in result["practices"] if p["nbs_id"] == "trees")
    fams = {f["family_id"]: f for f in tree["families"]}
    assert fams["trees__cross_family"]["scope_kind"] == "all_families"
    assert fams["trees__cross_family"]["metrics"]["active_excerpts"] == 1
    assert fams["trees__natural"]["metrics"]["active_excerpts"] == 0
    assert fams["__unassigned"]["scope_kind"] == "unassigned"
    assert fams["__unassigned"]["metrics"]["active_excerpts"] == 0


def test_scope_source_keys_match_counts_for_mixed_named_and_unassigned_claims():
    data = fixture_data()
    result = build_progress(data, [{"source_id": "alias", "duplicate_of": "paper"}])
    trees = next(p for p in result["practices"] if p["nbs_id"] == "trees")
    families = {f["family_id"]: f for f in trees["families"]}
    # One paper has both a planted-family claim and claims with no family tag.
    # Source-level unioned family tags cannot recover this unassigned drilldown.
    assert families["trees__planted"]["metrics"]["source_keys"] == ["paper"]
    assert families["__unassigned"]["metrics"]["source_keys"] == ["empty", "paper"]
    for metrics in [
        result["totals"],
        trees["metrics"],
        *[f["metrics"] for f in trees["families"]],
    ]:
        assert metrics["known_sources"] == len(metrics["source_keys"])
        assert "alias" not in metrics["source_keys"]


def test_table_views_route_inputs_but_count_only_retained_output_citations():
    data = fixture_data()
    data["registers"]["XW_target_crosswalk"] = [
        {"ev_variable": "shared", "target_table": "T3", "target_key": "drought"},
        {"ev_variable": "shared", "target_table": "T6", "target_key": "yield"},
        {"ev_variable": "yield", "target_table": "T6", "target_key": "yield"},
        {"ev_variable": "cost", "target_table": "T6", "target_key": "cost_per_hectare"},
    ]
    data["global_tables"] = {
        "T5_opportunity_space": [{"variable_id": "yield", "mcda_role": "priority"}]
    }
    rows = data["registers"]["EV_evidence_register"]
    rows[2]["variable"] = "shared"
    rows += [
        {
            "evidence_id": "uncited",
            "source_id": "empty",
            "nbs_id": "trees",
            "use_role": "nbs_effect",
            "variable": "yield",
        },
        {
            "evidence_id": "asset",
            "source_id": "empty",
            "nbs_id": "trees",
            "use_role": "asset_vulnerability",
        },
        {
            "evidence_id": "economic",
            "source_id": "empty",
            "nbs_id": "trees",
            "use_role": "nbs_effect",
            "variable": "cost",
        },
        {
            "evidence_id": "unmapped",
            "source_id": "empty",
            "nbs_id": "trees",
            "use_role": "nbs_effect",
            "variable": "unknown",
        },
    ]
    data["recipes"]["trees"]["T3_nbs_hazard_farming"] = [
        {"record_id": "cell", "evidence_ids": ["a", "c", "d", "missing"]},
        {"record_id": "cell", "evidence_ids": ["a", "c"]},
        {"record_id": "empty", "evidence_ids": []},
    ]
    result = build_progress(data, [{"source_id": "alias", "duplicate_of": "paper"}])
    t3, t6 = (result["table_views"][t] for t in ("T3", "T6"))
    assert t3["totals"]["evidence_ids"] == ["a", "asset", "c", "d"]
    assert t6["totals"]["evidence_ids"] == ["c", "uncited"]
    assert t3["totals"]["contributing_excerpts"] == 2
    assert t6["totals"]["contributing_excerpts"] == 1
    output = t3["outputs"][0]
    assert output["output_count"] == 2
    assert output["evidence_backed_outputs"] == 1
    assert output["evidence_ids"] == ["a", "c"]
    assert output["source_keys"] == ["paper"]
    assert len(output["rows"]) == 2
    assert result["totals"]["contributing_excerpts"] == 2  # cross-table union
    assert result["totals"]["all_excerpts"] == 8
    assert "Relevance does not establish suitability for use" in t3["scope_note"]
    assert "unmapped" in result["totals"]["evidence_ids"]
    for view in result["table_views"].values():
        for metrics in [view["totals"], *[p["metrics"] for p in view["practices"]]]:
            assert metrics["all_excerpts"] == sum(
                metrics[k]
                for k in (
                    "approved_excerpts",
                    "reviewed_unresolved_excerpts",
                    "reviewed_dropped_excerpts",
                    "unreviewed_excerpts",
                )
            )
            assert metrics["known_sources"] == len(metrics["source_keys"])
            assert metrics["contributing_excerpts"] <= metrics["active_excerpts"]


def test_table_scope_fallback_keeps_uncited_effects_and_uses_table_search_cohort():
    data = fixture_data()
    data["registers"]["EV_evidence_register"].append(
        {
            "evidence_id": "uncited",
            "source_id": "empty",
            "nbs_id": "trees",
            "use_role": "nbs_effect",
        }
    )
    data["registers"]["SRCH_search_register"] = [
        search("t3", table="T3", n_included="2"),
        search("t6", table="T6", n_included="4"),
    ]
    result = build_progress(data, [])
    assert result["totals"]["search_metrics"]["included"] is None
    for table, included in (("T3", 2), ("T6", 4)):
        view = result["table_views"][table]
        assert view["evidence_tracking"] == "shared_effect_pool"
        assert "uncited" in view["totals"]["evidence_ids"]
        assert view["totals"]["search_metrics"]["included"] == included
        assert "Shared T3/T6" in view["scope_note"]


def test_shared_t2_configuration_has_project_scope_and_separate_citation_coverage():
    data = fixture_data()
    data["global_tables"] = {
        "T2_climate_risk": [
            {"variable_id": "drought", "evidence_ids": []},
            {"variable_id": "flood", "evidence_ids": ["a", "d", "missing_t2"]},
            {"variable_id": "flood", "evidence_ids": ["a"]},
        ]
    }
    data["registers"]["EV_evidence_register"].append(
        {"evidence_id": "climate", "source_id": "empty", "use_role": "climate_risk"}
    )
    result = build_progress(data, [{"source_id": "alias", "duplicate_of": "paper"}])
    view = result["table_views"]["T2a"]
    assert view["project_level"] is True
    assert view["practices"] == []
    assert view["totals"]["evidence_ids"] == ["a", "climate", "d"]
    assert view["totals"]["contributing_excerpts"] == 1
    assert view["outputs"][0]["output_count"] == 2
    assert view["outputs"][0]["evidence_backed_outputs"] == 1
    assert view["outputs"][0]["source_keys"] == ["paper"]
    assert "missing_t2" in result["diagnostics"]["compiled_missing_evidence_ids"]
    empty = build_progress(
        {"global_tables": {"T2_climate_risk": [{"variable_id": "drought"}]}}, []
    )["table_views"]["T2a"]
    assert empty["totals"]["all_excerpts"] == 0
    assert empty["totals"]["reviewed_pct"] is None
    assert empty["outputs"][0]["output_count"] == 1
    assert empty["outputs"][0]["evidence_backed_outputs"] == 0


def test_t4_table_scope_excludes_soft_operational_outputs_preserves_legacy_counts():
    data = fixture_data()
    data["recipes"]["trees"]["T4_suitability_mappings"] += [
        {
            "mapping_id": "soft",
            "suitability_dimension": "operational_constraint",
            "is_scenario_candidate": True,
            "evidence_ids": ["b"],
        },
        {
            "mapping_id": "mask",
            "suitability_dimension": "operational_constraint",
            "is_scenario_candidate": False,
            "evidence_ids": [],
        },
    ]
    result = build_progress(data, [{"source_id": "alias", "duplicate_of": "paper"}])
    assert result["totals"]["t4_relationships"] == 4
    t4 = result["table_views"]["T4"]
    assert t4["outputs"][0]["output_count"] == 3
    assert t4["totals"]["t4_relationships"] == 3
    assert t4["totals"]["evidence_ids"] == ["a", "d"]
    assert t4["totals"]["source_keys"] == ["paper"]
    trees = next(p for p in t4["practices"] if p["nbs_id"] == "trees")
    families = {f["family_id"]: f["metrics"] for f in trees["families"]}
    assert families["trees__planted"]["evidence_ids"] == ["a"]
    assert families["trees__planted"]["contributing_excerpts"] == 1
    assert families["__unassigned"]["evidence_ids"] == ["d"]
    assert families["trees__natural"]["evidence_ids"] == []


def test_output_details_distinguish_family_rollups_and_context_variants():
    data = {
        "recipes": {
            "trees": {
                "T3_nbs_hazard_farming": [
                    {
                        "record_id": "rollup",
                        "hazard_type": "drought",
                        "farming_system": "all",
                    },
                    {
                        "record_id": "family",
                        "hazard_type": "drought",
                        "suitability_family_id": "trees__planted",
                        "farming_system": "all",
                    },
                    {
                        "record_id": "context",
                        "hazard_type": "drought",
                        "scope_type": "income_group",
                        "scope_id": "low",
                        "risk_role": "asset_threat",
                    },
                ]
            }
        }
    }
    output = build_progress(data, [])["table_views"]["T3"]["outputs"][0]
    rows = output["rows"]
    assert len({r["label"] for r in rows}) == 3
    assert "practice roll-up" in rows[0]["label"]
    assert "planted" in rows[1]["label"]
    assert rows[1]["family_ids"] == ["trees__planted"]
    assert "income group: low" in rows[2]["label"]
    assert rows[2]["risk_role"] == "asset_threat"
    assert "context variants" in output["count_definition"]
