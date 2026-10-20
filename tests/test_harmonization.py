"""Approved hypothetical scenarios: semantics, missingness, independence and pooling."""

from copy import deepcopy
import math
import numpy as np
import pytest
from nbs_ruralscan.recipe.harmonization import (
    standardize,
    combine_profiles,
    harmonize,
    median_bounds,
)
from nbs_ruralscan.runtime.numeric import evaluate_numeric


def band(lo, hi, score, label="low", il=True, ih=False):
    return dict(
        lower=lo,
        upper=hi,
        lower_inclusive=il,
        upper_inclusive=ih,
        score=score,
        label=label,
    )


def profile(sid, bands, weight=1):
    return dict(
        profile_id=sid,
        origin_id=sid,
        source_weight=weight,
        intervals=bands,
        pool_id="approved_test_pool",
        system_id="alley",
        context_id="test_region",
        variable="slope",
        unit="degrees",
        score_policy="v1",
        compatibility_approved=True,
    )


def pair():
    return [
        profile("a", [band(0, 5, 0.75), band(5, 15, 0.5), band(15, None, 0.25)]),
        profile(
            "b",
            [band(0, 8, 0.75), band(8, 20, 0.5, ih=True), band(20, None, 0, il=False)],
        ),
    ]


def at(pool, x):
    return next(
        c
        for c in pool["cells"]
        if (
            c["lower"] is None
            or x > c["lower"]
            or (x == c["lower"] and c["lower_inclusive"])
        )
        and (
            c["upper"] is None
            or x < c["upper"]
            or (x == c["upper"] and c["upper_inclusive"])
        )
    )


@pytest.mark.parametrize(
    "x,bounds,flag",
    [
        (3, (0.75, 0.75), None),
        (7, (0.5, 0.75), "median_tie"),
        (17, (0.25, 0.5), "median_tie"),
        (25, (0, 0.25), "exclusion_conflict"),
    ],
)
def test_equal_papers_keep_disagreement(x, bounds, flag):
    c = at(combine_profiles(pair()), x)
    assert (c["median_lower"], c["median_upper"]) == bounds
    assert c["n_sources"] == 2 and c["weight_coverage"] == 1
    if flag:
        assert flag in c["flags"] and c["score"] is None


def test_three_five_and_missing_scores_use_same_semantic_anchors():
    policy = dict(
        score_kind="ordinal",
        class_scores=dict(
            very_low=0.1, low=0.25, moderate=0.5, high=0.75, very_high=0.9
        ),
    )
    a = [band(0, 1, 0.2), band(1, 2, 0.6, "moderate"), band(2, 3, 0.9, "high")]
    b = [
        band(i, i + 1, s, label)
        for i, (label, s) in enumerate(
            [
                ("very_low", 0.2),
                ("low", 0.3),
                ("moderate", 0.5),
                ("high", 1),
                ("very_high", 1),
            ]
        )
    ]
    standardize(a, policy)
    standardize(b, policy)
    assert [x["score"] for x in a] == [0.25, 0.5, 0.75]
    assert [x["score"] for x in b] == [0.1, 0.25, 0.5, 0.75, 0.9]
    assert a[0]["legacy_score"] == 0.2 and b[1]["legacy_score"] == 0.3


@pytest.mark.parametrize("kind", ["probability", "relative_yield", "undefined"])
def test_incompatible_score_meaning_rejected(kind):
    with pytest.raises(ValueError, match="score_meaning"):
        standardize([band(0, 10, 0.8)], dict(score_kind=kind))


def test_undefined_rank_and_favourable_are_unknown_not_optimal():
    bands = [band(0, 1, 1, "class_3"), band(1, 2, 1, "favourable")]
    standardize(bands, dict(score_kind="ordinal", class_scores={"high": 0.75}))
    assert all(b["score"] is None for b in bands)


def test_low_does_not_extrapolate_zero_and_missing_is_not_a_vote():
    ps = [profile("a", [band(0, 10, 0.75)]), profile("b", [band(15, None, 0.25)])]
    pool = combine_profiles(ps)
    c = at(pool, 20)
    assert c["score"] == 0.25 and c["weight_coverage"] == 0.5 and c["n_sources"] == 1
    assert "partial_coverage" in c["flags"]
    assert at(pool, 12)["score"] is None
    assert at(pool, 1000)["score"] == 0.25


def test_ambiguous_boundary_not_assigned_and_runtime_matches():
    p = profile("a", [band(0, 5, 0.75, ih=True), band(5, 10, 0.5)])
    pool = combine_profiles([p])
    assert at(pool, 5)["score"] is None
    row = dict(
        relationship_type="piecewise",
        relationship_params=dict(harmonization={"pools": [pool]}),
    )
    np.testing.assert_allclose(
        evaluate_numeric(row, [4, 5, 6, 11], pool_id=pool["pool_id"]),
        [0.75, np.nan, 0.5, np.nan],
        equal_nan=True,
    )
    with pytest.raises(ValueError, match="not both"):
        evaluate_numeric(row, [4], pool_id=pool["pool_id"], profile_id="a")


def test_duplicate_citation_does_not_increase_votes_or_weight():
    ps = pair()
    base = combine_profiles(ps)
    echo = deepcopy(ps[0])
    echo["profile_id"] = "echo"
    assert combine_profiles([*ps, echo])["cells"] == base["cells"]
    assert combine_profiles(list(reversed(ps)))["cells"] == base["cells"]


def test_conflicting_profiles_from_one_origin_do_not_get_extra_votes():
    ps = pair()
    extra = deepcopy(ps[0])
    extra["profile_id"] = "regional_variant"
    extra["intervals"] = [band(0, None, 0.9)]
    c = at(combine_profiles([*ps, extra]), 3)
    assert c["n_sources"] == 1 and "within_origin_conflict" in c["flags"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("context_id", "elsewhere"),
        ("system_id", "different"),
        ("unit", "%"),
        ("variable", "soil_ph"),
        ("score_policy", "unreviewed"),
    ],
)
def test_incompatible_pools_fail(field, value):
    ps = pair()
    ps[1][field] = value
    with pytest.raises(ValueError, match="incompatible"):
        combine_profiles(ps)


def test_no_implicit_compatibility_and_unknown_crosswalk_are_reported():
    p = pair()[0]
    p["pool_id"] = ""
    p["intervals"][0]["score"] = None
    result = harmonize([p])
    assert result["pools"] == []
    assert {r["reason"] for r in result["review"]} == {
        "compatibility_review_required",
        "unresolved_class_meaning",
    }


def test_quality_weights_affect_median_not_disagreement_range():
    ps = [
        profile("a", [band(0, None, 0.25)], 0.9),
        profile("b", [band(0, None, 0.5)], 0.6),
    ]
    c = at(combine_profiles(ps), 17)
    assert c["score"] == 0.25 and c["source_max"] == 0.5
    assert "source_disagreement" in c["flags"]
    assert median_bounds([(0.25, 0.1), (0.5, 0.1)]) == (0.25, 0.5)


def test_unit_conversion_preserves_cutoff_and_exposes_real_difference():
    from nbs_ruralscan.recipe.numeric_bands import compile_bands
    from nbs_ruralscan.recipe.evidence import EvidenceUnit

    u = EvidenceUnit(
        "e",
        "s",
        "agroforestry",
        "alley",
        "slope",
        "structural_suitability",
        "literature_relationship",
        "table",
        "practice_technology",
        "high",
        "test",
        relationship={"classes": [{"label": "high", "range": "<10"}]},
    )
    policy = {
        "e": dict(
            action="compile",
            encoding="labelled_ranges",
            field="classes",
            input_unit="%",
            ordinal_scale='{"high":1}',
            applicability_note="test",
            harmonization={
                "version": "v1",
                "score_kind": "ordinal",
                "class_scores": {"high": 0.75},
                "pool_id": "test",
                "system_id": "alley",
                "context_id": "test_region",
                "compatibility_approved": True,
            },
        )
    }
    params, used, unresolved = compile_bands([u], policy, "degrees", {})
    assert used == ["e"] and not unresolved
    assert params["profiles"][0]["intervals"][0]["upper"] == pytest.approx(
        math.degrees(math.atan(0.1))
    )
    assert len(params["harmonization"]["pools"]) == 1
    row = {"relationship_type": "piecewise", "relationship_params": params}
    np.testing.assert_allclose(
        evaluate_numeric(row, [5, 6], pool_id="test"), [0.75, np.nan], equal_nan=True
    )


def test_exclusion_conflict_stays_unknown_even_when_zero_wins_weight():
    ps = [
        profile("a", [band(0, None, 0)], 0.9),
        profile("b", [band(0, None, 0.25)], 0.1),
    ]
    c = at(combine_profiles(ps), 2)
    assert c["median_lower"] == 0 and c["median_upper"] == 0
    assert c["score"] is None and "exclusion_conflict" in c["flags"]


def test_opposite_shapes_remain_visible_and_not_forced_monotone():
    a = profile("a", [band(0, 5, 0.9), band(5, 10, 0.5), band(10, 15, 0.1)])
    b = profile("b", [band(0, 5, 0.1), band(5, 10, 0.9), band(10, 15, 0.1)])
    pool = combine_profiles([a, b])
    assert at(pool, 2)["source_min"] == 0.1 and at(pool, 2)["source_max"] == 0.9
    assert at(pool, 7)["median_upper"] == 0.9
    assert at(pool, 12)["score"] == 0.1


def test_cardinal_rescale_requires_verified_meaning_and_declared_endpoints():
    bands = [band(0, 10, 1, "high")]
    policy = dict(
        score_kind="comparable_cardinal",
        meaning_verified=True,
        source_min=0,
        source_max=100,
        source_scores={"high": 75},
    )
    standardize(bands, policy)
    assert bands[0]["score"] == 0.75 and bands[0]["source_score"] == 75
    policy["meaning_verified"] = False
    with pytest.raises(ValueError, match="definition_required"):
        standardize([band(0, 10, 1, "high")], policy)
