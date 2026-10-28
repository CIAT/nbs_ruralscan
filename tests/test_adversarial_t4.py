"""Adversarial boundary tests: invalid evidence cannot become executable T4."""

from copy import deepcopy
import json
import math

import pytest

from nbs_ruralscan.recipe.evidence import EvidenceUnit
from nbs_ruralscan.recipe.family import synthesise_family
from nbs_ruralscan.recipe.harmonization import (
    combine_profiles,
    median_bounds,
    standardize,
)
from nbs_ruralscan.recipe.numeric_bands import parse_profiles
from nbs_ruralscan.recipe.synthesis import (
    SynthesisReport,
    _harmonise,
    synthesise_t4_row,
)


def unit(eid="e1", **changes):
    values = dict(
        evidence_id=eid,
        source_id=eid,
        nbs_id="forest_restoration",
        suitability_family_id="forest_restoration__planting",
        variable="slope",
        use_role="structural_suitability",
        evidence_type="literature_relationship",
        claim_basis="table",
        claim_scope="practice_technology",
        extraction_confidence="high",
        quote="Source table gives slope suitability classes.",
        page=1,
        reviewer_ok=True,
        relationship={"abs_max": 20, "unit": "degrees"},
    )
    values.update(changes)
    return EvidenceUnit(**values)


def synthesize(units, canonical_unit="degrees"):
    return synthesise_t4_row(
        units,
        {},
        variable="slope",
        family="forest_restoration__planting",
        canonical_unit=canonical_unit,
    )


def profile():
    return dict(
        profile_id="one",
        origin_id="paper",
        source_weight=1,
        pool_id="test",
        system_id="planting",
        context_id="test_region",
        variable="slope",
        unit="degrees",
        score_policy="test",
        compatibility_approved=True,
        intervals=[
            dict(
                lower=0,
                upper=10,
                lower_inclusive=True,
                upper_inclusive=False,
                score=0.75,
                label="high",
            )
        ],
    )


def test_direct_row_synthesis_cannot_resurrect_quarantined_evidence():
    row, report = synthesize([unit(review_state="dropped")])
    assert row["relationship_params"] == {}
    assert not row["evidence_ids"]
    assert report.dropped == [("e1", "qa_dropped")]


def test_direct_row_synthesis_cannot_relabel_other_variable():
    row, report = synthesize([unit(variable="soil_ph")])
    assert not row["relationship_params"]
    assert report.dropped == [("e1", "variable_mismatch")]


@pytest.mark.parametrize("value", [True, False, math.nan, math.inf, -math.inf, "20"])
def test_invalid_bound_cannot_hide_beside_valid_bound(value):
    row, report = synthesize([unit(relationship={"abs_min": value, "abs_max": 20})])
    assert not row["relationship_params"]
    assert report.unresolved == [("e1", "invalid_numeric_bound")]
    rep = SynthesisReport()
    assert not _harmonise(unit(relationship={"abs_max": value}), "degrees", rep=rep)
    assert rep.dropped == [("e1", "invalid_numeric_bound")]


def test_null_bound_remains_unspecified_not_invalid():
    row, _ = synthesize([unit(relationship={"abs_min": None, "abs_max": 20})])
    assert row["relationship_params"] == {"abs_max": 20}


def test_piecewise_conversion_preserves_close_knots():
    row, _ = synthesize(
        [unit(relationship={"unit": "%", "points": [[0.01, 0], [0.02, 1]]})]
    )
    points = row["relationship_params"]["points"]
    assert 0 < points[0][0] < points[1][0]
    assert points[1][0] == pytest.approx(math.degrees(math.atan(0.02 / 100)))


@pytest.mark.parametrize("canonical", ["native", "mixed", "boolean_or_distance"])
def test_alternative_units_do_not_authorize_cross_scale_pooling(canonical):
    units = [
        unit("metres", relationship={"abs_max": 500, "unit": "m"}),
        unit("kilometres", relationship={"abs_max": 1, "unit": "km"}),
    ]
    row, report = synthesize(units, canonical)
    assert not row["relationship_params"]
    assert {reason for _, reason in report.unresolved} == {
        "mixed_source_units_require_canonical_unit"
    }


def test_conversion_overflow_is_refused():
    rep = SynthesisReport()
    result = _harmonise(
        unit(relationship={"abs_max": 1e308, "unit": "m"}),
        "km",
        {"m->km": "*1000"},
        rep,
    )
    assert not result
    assert rep.dropped


def test_explicit_crop_selection_does_not_pool_other_taxa():
    result = synthesise_family(
        [
            unit("coffee", claim_scope="crop_specific", taxon="coffee"),
            unit(
                "cocoa",
                claim_scope="crop_specific",
                taxon="cocoa",
                relationship={"abs_max": 80},
            ),
        ],
        {},
        family="forest_restoration__planting",
        corpus_n=2,
        group_map={},
        canonical_units={"slope": "degrees"},
        allow_crop_scope=True,
        crop="coffee",
        approved_only=True,
    )
    assert result.rows[0]["evidence_ids"] == ["coffee"]
    assert result.rows[0]["relationship_params"] == {"abs_max": 20}
    assert result.dispositions["cocoa"]["status"] == "other_crop_taxon"
    assert result.rows[0]["n_sources"] == 1


@pytest.mark.parametrize("bad", [True, math.nan, math.inf, "1"])
def test_ordinal_rank_requires_finite_number(bad):
    policy = dict(
        encoding="labelled_ranges",
        field="classes",
        ordinal_scale=json.dumps({"high": bad}),
    )
    with pytest.raises(ValueError, match="invalid_ordinal_scale"):
        parse_profiles({"classes": [{"label": "high", "range": "0-10"}]}, policy)


@pytest.mark.parametrize("bad", [True, math.nan, math.inf, "1"])
def test_named_bounds_require_finite_number(bad):
    policy = dict(encoding="named_bounds", ordinal_scale='{"high": 1}')
    with pytest.raises(ValueError, match="invalid_numeric_bound"):
        parse_profiles({"high_low": bad, "high_high": 10}, policy)


@pytest.mark.parametrize(
    "key,bad,error",
    [
        ("lower", math.nan, "invalid_numeric_bound"),
        ("upper", math.inf, "invalid_numeric_bound"),
        ("upper", -1, "reversed_source_interval"),
        ("score", math.nan, "invalid_suitability_score"),
        ("score", 2, "invalid_suitability_score"),
        ("score", True, "invalid_suitability_score"),
        ("upper_inclusive", "false", "invalid_interval_inclusivity"),
    ],
)
def test_pool_rejects_invalid_source_interval(key, bad, error):
    source = profile()
    source["intervals"][0][key] = bad
    with pytest.raises(ValueError, match=error):
        combine_profiles([source])


def test_string_false_is_not_compatibility_approval():
    source = profile()
    source["compatibility_approved"] = "false"
    with pytest.raises(ValueError, match="compatibility_not_approved"):
        combine_profiles([source])


@pytest.mark.parametrize("bad", [True, math.nan, math.inf, -1, 1.01])
def test_weighted_median_refuses_invalid_score(bad):
    with pytest.raises(ValueError, match="invalid_suitability_score"):
        median_bounds([(bad, 1)])


def test_boolean_weight_is_not_source_authority():
    source = profile()
    source["source_weight"] = True
    with pytest.raises(ValueError, match="invalid_source_weight"):
        combine_profiles([source])


@pytest.mark.parametrize(
    "field,value,error",
    [
        ("source_min", False, "cardinal_scale_definition_required"),
        ("meaning_verified", "false", "cardinal_scale_definition_required"),
        ("source_scores", {"high": True}, "source_score_outside_declared_scale"),
    ],
)
def test_cardinal_mapping_cannot_use_boolean_numbers_or_string_approval(
    field, value, error
):
    policy = dict(
        score_kind="comparable_cardinal",
        source_min=0,
        source_max=100,
        meaning_verified=True,
        source_scores={"high": 75},
    )
    policy[field] = value
    with pytest.raises(ValueError, match=error):
        standardize(deepcopy(profile()["intervals"]), policy)


@pytest.mark.parametrize("pointer_kind", ["source", "evidence"])
def test_lineage_cycles_never_count_as_independent_origins(pointer_kind):
    first = unit(
        "e1", source_id="s1", lineage_of="s2" if pointer_kind == "source" else "e2"
    )
    second = unit(
        "e2", source_id="s2", lineage_of="s1" if pointer_kind == "source" else "e1"
    )
    with pytest.raises(ValueError, match="lineage_cycle"):
        synthesize([first, second])


def test_source_lineage_ambiguity_cannot_depend_on_input_order():
    units = [
        unit("e1", source_id="s1", lineage_of="origin_a"),
        unit("e2", source_id="s1", lineage_of="origin_b"),
        unit("echo", source_id="echo", lineage_of="s1"),
    ]
    for ordered in (units, list(reversed(units))):
        with pytest.raises(ValueError, match="ambiguous_source_lineage"):
            synthesize(ordered)


@pytest.mark.parametrize("denominator", [True, -1, 1.5, math.nan, math.inf, "2", 0, 1])
def test_source_count_denominator_cannot_be_invalid_or_smaller_than_membership(
    denominator,
):
    from nbs_ruralscan.recipe.support import variable_support, group_support

    units = [unit("s1"), unit("s2")]
    with pytest.raises(ValueError, match="[Ss]creened corpus"):
        variable_support(units, denominator)
    with pytest.raises(ValueError, match="[Ss]creened corpus"):
        group_support(units, {"slope": "terrain"}, denominator)


@pytest.mark.parametrize("source_family", ["forest_restoration__other", "", "F1"])
@pytest.mark.parametrize("review_state", ["", "dropped"])
def test_public_synthesis_rejects_cross_family_relabelling(source_family, review_state):
    records = [unit(suitability_family_id=source_family, review_state=review_state)]
    with pytest.raises(ValueError, match="Evidence family does not match target"):
        synthesize(records)
    with pytest.raises(ValueError, match="Evidence family does not match target"):
        synthesise_family(
            records,
            {},
            family="forest_restoration__planting",
            corpus_n=None,
            group_map={},
        )


def test_synthetic_family_alias_is_valid_when_source_and_target_match():
    result, _ = synthesise_t4_row(
        [unit(suitability_family_id="F1")], {}, variable="slope", family="F1"
    )
    assert result["evidence_ids"] == ["e1"]


@pytest.mark.parametrize("target", [None, "", " "])
def test_missing_target_family_cannot_create_unassigned_configuration(target):
    with pytest.raises(ValueError, match="nonempty target suitability family"):
        synthesise_t4_row([], {}, variable="slope", family=target)
    with pytest.raises(ValueError, match="nonempty target suitability family"):
        synthesise_family([], {}, family=target, corpus_n=None, group_map={})


def test_approved_support_convention_keeps_quality_separate_from_selection():
    from nbs_ruralscan.recipe.support import variable_support, selection_table

    records = [
        unit("high", source_id="high"),
        unit("low", source_id="low", variable="rainfall"),
    ]
    support = variable_support(records, {"high", "low"}, {"high": "high", "low": "low"})
    assert support["slope"].pct == support["rainfall"].pct == 50
    assert support["slope"].quality_weighted_pct == 74.1
    assert support["rainfall"].quality_weighted_pct == 25.9
    assert all(
        row.decision == "review_low_support"
        for row in selection_table(support, floor_pct=60)
    )


@pytest.mark.parametrize("cohort", [None, 3])
def test_unknown_membership_never_invents_quality_tiers(cohort):
    from nbs_ruralscan.recipe.support import variable_support

    support = variable_support([unit()], cohort, {"e1": "high"})["slope"]
    assert support.quality_weighted_pct is None
    assert support.pct == (33.3 if cohort == 3 else None)
    assert support.n_sources == 1


@pytest.mark.parametrize(
    "tiers",
    [
        None,
        {},
        {"e1": "high"},
        {"e1": "high", "unseen": "unknown"},
        {"e1": "high", "unseen": None},
    ],
)
def test_incomplete_or_unknown_cohort_tiers_hold_only_quality_diagnostic(tiers):
    from nbs_ruralscan.recipe.support import variable_support

    support = variable_support([unit()], {"e1", "unseen"}, tiers)["slope"]
    assert support.pct == 50
    assert support.quality_weighted_pct is None


def test_group_support_uses_union_and_includes_screened_noncontributors_in_denominator():
    from nbs_ruralscan.recipe.support import variable_support, group_support

    records = [
        unit("slope", source_id="one"),
        unit("elevation", source_id="one", variable="elevation"),
        unit("slope2", source_id="two"),
        unit("repeat", source_id="one"),
    ]
    cohort = {"one", "two", "screened_only"}
    tiers = {"one": "High", "two": "low", "screened_only": "medium"}
    variables = variable_support(records, cohort, tiers)
    grouped = group_support(
        records, {"slope": "terrain", "elevation": "terrain"}, cohort, tiers
    )
    terrain = grouped["terrain"]
    assert terrain.n_sources == 2 and terrain.corpus_n == 3
    assert terrain.pct == variables["slope"].pct == 66.7
    assert (
        terrain.quality_weighted_pct == variables["slope"].quality_weighted_pct == 69.2
    )
    assert variables["elevation"].pct == 33.3
    assert terrain.members == ["elevation", "slope"]
