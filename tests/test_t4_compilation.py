"""Regression cases from the October 2026 agroforestry compilation audit."""

import importlib.util
from pathlib import Path
from typing import Any

import pytest

from nbs_ruralscan.recipe.evidence import EvidenceUnit
from nbs_ruralscan.recipe.family import synthesise_family
from nbs_ruralscan.recipe.synthesis import synthesise_t4_row
from nbs_ruralscan.recipe.t4_relationships import decode


def unit(eid, source="source", **kw):
    args: dict[str, Any] = dict(
        evidence_id=eid,
        source_id=source,
        nbs_id="agroforestry",
        suitability_family_id="agroforestry__shaded_perennial",
        variable="slope",
        use_role="structural_suitability",
        evidence_type="literature_relationship",
        claim_basis="primary_measured",
        claim_scope="practice_technology",
        extraction_confidence="high",
        quote="Test provenance: slope limit is 20 degrees.",
        page=1,
        relationship={"abs_max": 20, "unit": "degrees"},
        reviewer_ok=True,
    )
    args.update(kw)
    return EvidenceUnit(**args)


def row(units):
    return synthesise_t4_row(
        units, {}, variable="slope", family="F1", canonical_unit="degrees"
    )


def family(units, **kw):
    return synthesise_family(units, {}, family="F1", corpus_n=10, group_map={}, **kw)


def test_narrative_does_not_displace_numeric_claim():
    result, report = row(
        [
            unit("narrative", relationship={"direction": "negative"}),
            unit("table", claim_basis="table"),
        ]
    )
    assert result["relationship_params"] == {"abs_max": 20}
    assert report.used == ["table"]
    assert report.parameter_evidence == {"abs_max": ["table"]}
    assert ("narrative", "qualitative_relationship") in report.unresolved


def test_nonnumeric_sources_do_not_supply_confidence_or_provenance():
    result, report = row(
        [
            unit("numeric"),
            unit("n1", "other", relationship=None),
            unit("n2", "third", relationship=None),
        ]
    )
    assert result["evidence_ids"] == ["numeric"]
    assert result["uncertainty_pct"] == 20
    assert len(report.unresolved) == 2


def test_distinct_bounds_survive_and_repeated_source_cannot_outvote_others():
    items = [
        unit("low", relationship={"abs_min": 0, "unit": "degrees"}),
        unit("high", relationship={"abs_max": 20, "unit": "degrees"}),
        unit("independent1", "b", relationship={"abs_max": 50, "unit": "degrees"}),
        unit("independent2", "c", relationship={"abs_max": 50, "unit": "degrees"}),
    ]
    items += [unit(f"repeat{i}", context={"aez": str(i)}) for i in range(10)]
    result, report = row(items)
    assert result["relationship_params"] == {"abs_min": 0, "abs_max": 50}
    assert "low" in report.used and "high" in report.used


def test_exact_echo_collapses_but_context_remains():
    result, report = row(
        [
            unit("a"),
            unit("echo", "secondary", lineage_of="source"),
            unit("context", context={"aez": "dry"}),
        ]
    )
    assert len(report.used) == 2
    assert len(report.collapsed) == 1
    assert result["uncertainty_pct"] == 20


def test_hard_threshold_keeps_type_and_converts_units():
    result, report = row(
        [
            unit(
                "cut",
                relationship={
                    "threshold": 100,
                    "direction": "exclude_above",
                    "unit": "%",
                },
            )
        ]
    )
    assert result["relationship_type"] == "threshold"
    assert result["relationship_params"] == {
        "threshold": 45,
        "above_is_suitable": False,
    }
    assert report.parameter_evidence["threshold"] == ["cut"]


def test_mixed_shapes_require_decision_not_silent_blending():
    result, report = row(
        [
            unit("plateau"),
            unit("cut", relationship={"threshold": 20, "above_is_suitable": False}),
        ]
    )
    assert not result["relationship_params"]
    assert len(report.unresolved) == 2
    assert not report.used


def test_class_scores_preserved_no_guessed_scores():
    result, _ = row(
        [unit("classes", relationship={"class_map": {"crop": 1, "water": 0}})]
    )
    assert result["relationship_type"] == "ranked_classes"
    assert result["relationship_params"]["class_map"]["water"] == 0
    assert (
        decode({"very_good_max_deg": 5, "good_min_deg": 5})[2]
        == "unsupported_numeric_encoding"
    )
    assert decode({"classes_suitable": ["crop"]})[2] == "class_or_gate_requires_mapping"


def test_conflicting_class_scores_not_arbitrarily_selected():
    result, report = row(
        [
            unit("a", relationship={"class_map": {"crop": 1}}),
            unit("b", "b", relationship={"class_map": {"crop": 0.5}}),
        ]
    )
    assert not result["relationship_params"]
    assert {reason for _, reason in report.unresolved} == {
        "conflicting_typed_relationships"
    }


def test_crop_lanes_never_mix_taxa_or_leak_into_generic_rows():
    result = family(
        [
            unit("coffee", claim_scope="crop_specific", taxon="coffee"),
            unit(
                "cocoa",
                claim_scope="crop_specific",
                taxon="cocoa",
                relationship={"abs_max": 50},
            ),
            unit("species", claim_scope="species_specific", taxon="tree"),
        ],
        allow_crop_scope=True,
    )
    assert not result.rows
    assert set(result.crop_results) == {"coffee", "cocoa"}
    assert result.crop_results["coffee"].rows[0]["relationship_params"] == {
        "abs_max": 20
    }
    assert result.crop_results["cocoa"].rows[0]["relationship_params"] == {
        "abs_max": 50
    }
    assert result.dispositions["species"]["status"] == "species_scope"


def test_every_record_has_disposition_and_approval_mode_is_explicit():
    items = [
        unit("ok"),
        unit("flag", reviewer_ok=False),
        unit("dropped", review_state="dropped"),
        unit("site", relationship={"type": "observed_presence"}),
        unit("effect", use_role="nbs_effect"),
        unit("missing", relationship=None),
    ]
    result = family(items, approved_only=True)
    assert set(result.dispositions) == {u.evidence_id for u in items}
    assert all(d["status"] != "pending" for d in result.dispositions.values())
    assert result.dispositions["flag"]["status"] == "unresolved_review"
    assert result.rows[0]["evidence_ids"] == ["ok"]


@pytest.fixture
def runner():
    spec = importlib.util.spec_from_file_location(
        "t4_runner", Path("scripts/synthesise-recipe.py")
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_runner_uses_t4_counts_and_actual_f5_policy(runner):
    result = runner.synthesise("agroforestry")
    assert result["agroforestry__regeneration_farmland"].corpus_n == 14
    assert result["agroforestry__cross_family"].corpus_n == 7
    assert result["agroforestry__shaded_perennial"].crop_results
    assert "not_unique" in result["agroforestry__cross_family"].support_basis


def test_isolated_writer_preserves_design_rows_and_live_recipe(runner, tmp_path):
    import csv
    import json

    live = Path("schema/recipes/agroforestry/T4_suitability_mappings.csv")
    original = live.read_bytes()
    before = list(csv.DictReader(original.decode().splitlines()))
    result = runner.synthesise("agroforestry")
    runner.write_recipe(
        "agroforestry",
        result,
        runner._rd(runner.REG / "VONT_variable_ontology.csv"),
        output_dir=tmp_path,
    )
    after = list(csv.DictReader((tmp_path / "T4_suitability_mappings.csv").open()))
    assert live.read_bytes() == original
    design = [r for r in before if not runner._is_synthesised(r)]
    for r in design:
        assert r in after
    assert len(design) == 10
    for r in after:
        old = next((x for x in before if x["mapping_id"] == r["mapping_id"]), None)
        if old:
            assert {k: old[k] for k in runner.DESIGN_FIELDS} == {
                k: r[k] for k in runner.DESIGN_FIELDS
            }
    assert json.loads((tmp_path / "T4_agroforestry__shaded_perennial.json").read_text())


def test_custom_curve_units_and_order_are_checked():
    result, _ = row(
        [unit("curve", relationship={"points": [[0, 1], [100, 0]], "unit": "%"})]
    )
    assert result["relationship_type"] == "piecewise"
    assert result["relationship_params"]["points"] == [[0, 1], [45, 0]]
    assert decode({"points": [[2, 1], [1, 0]]})[2] == "invalid_piecewise_points"
    assert decode({"class_map": {"crop": True}})[2] == "invalid_class_scores"


def test_opposite_bounds_are_held_for_review():
    result, report = row(
        [
            unit("optimum", relationship={"opt_high": 27}),
            unit("limit", "other", relationship={"abs_max": 10}),
        ]
    )
    assert not result["relationship_params"]
    assert not report.used
    assert {reason for _, reason in report.unresolved} == {"inconsistent_bound_order"}
