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
