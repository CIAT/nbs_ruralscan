from nbs_ruralscan.recipe.inclusion import inclusion_estimates

ONTOLOGY = {
    "slope": {"group_id": "terrain"},
    "elevation": {"group_id": "terrain"},
    "rain": {"group_id": "climate"},
}


def unit(eid, paper, variable, reviewed=True, **kwargs):
    return dict(
        evidence_id=eid,
        source_id=paper,
        variable=variable,
        nbs_id="agroforestry",
        use_role="structural_suitability",
        review_state="",
        reviewer_ok=reviewed,
        claim_scope="practice_technology",
        suitability_family_id="f1",
        context={"model_use": {"verified": True}},
        **kwargs,
    )


def find(
    rows,
    variable="",
    group="terrain",
    lane="reviewed",
    scope="practice_technology",
    system="all_systems",
):
    return next(
        r
        for r in rows
        if r["variable"] == variable
        and r["group"] == group
        and r["review_lane"] == lane
        and r["claim_scope"] == scope
        and r["system"] == system
    )


def test_group_union_and_doi_deduplication_have_same_denominator():
    rows = [
        unit("a1", "a", "slope"),
        unit("a2", "a", "elevation"),
        unit("alias", "alias", "slope"),
        unit("b", "b", "rain"),
    ]
    sources = {
        "a": {"doi": "DOI:10.1/ABC"},
        "alias": {"doi": "https://doi.org/10.1/abc"},
    }
    result = inclusion_estimates(rows, sources, ONTOLOGY)
    group, variable = find(result), find(result, "slope")
    assert (group["n"], group["N"], group["percent"]) == (1, 2, 50)
    assert (variable["n"], variable["N"]) == (1, 2)
    assert variable["within_group_percent"] == 100
    assert len(group["evidence_ids"]) == 3


def test_reviewed_other_variable_cannot_approve_pending_inclusion():
    rows = [
        unit("a1", "a", "rain"),
        unit("a2", "a", "slope", False),
        unit("b", "b", "slope", False),
    ]
    result = inclusion_estimates(rows, {}, ONTOLOGY)
    reviewed, all_records = (
        find(result, "slope"),
        find(result, "slope", lane="all_recorded"),
    )
    assert (reviewed["n"], reviewed["N"], reviewed["percent"]) == (0, 1, 0)
    assert (all_records["n"], all_records["N"], all_records["percent"]) == (2, 2, 100)


def test_dropped_unverified_effects_other_nbs_do_not_enter_denominator():
    rows = [unit("keep", "keep", "slope")]
    for field, value in [
        ("review_state", "dropped"),
        ("use_role", "nbs_effect"),
        ("nbs_id", "other"),
        ("context", {}),
    ]:
        row = unit(field, field, "rain")
        row[field] = value
        rows.append(row)
    assert find(inclusion_estimates(rows, {}, ONTOLOGY))["N"] == 1


def test_scope_and_system_denominators_are_separate():
    a, b, c = unit("a", "a", "slope"), unit("b", "b", "rain"), unit("c", "c", "rain")
    b["suitability_family_id"] = "f2"
    c["context"]["model_use"]["scope"] = "species_specific"
    result = inclusion_estimates([a, b, c], {}, ONTOLOGY)
    assert find(result)["N"] == 2
    assert find(result, system="f1")["N"] == 1
    assert find(result, "rain", "climate", scope="species_specific")["N"] == 1


def test_empty_review_cohort_is_unknown_not_zero_percent():
    result = inclusion_estimates([unit("a", "a", "slope", False)], {}, ONTOLOGY)
    assert find(result)["N"] == 0
    assert find(result)["percent"] is None


def test_modules_share_cohort_but_not_group_numerators():
    a, b = unit("a", "a", "slope"), unit("b", "b", "elevation", False)
    b["use_role"] = "operational_risk"
    rows = inclusion_estimates([a, b], {}, ONTOLOGY)
    groups = [
        r
        for r in rows
        if r["level"] == "group"
        and r["review_lane"] == "all_recorded"
        and r["system"] == "all_systems"
    ]
    assert {r["module"] for r in groups} == {"M1", "M2b"}
    assert all((r["n"], r["N"], r["percent"]) == (1, 2, 50) for r in groups)
    reviewed_op = next(
        r
        for r in rows
        if r["module"] == "M2b"
        and r["level"] == "group"
        and r["review_lane"] == "reviewed"
        and r["system"] == "all_systems"
    )
    assert (reviewed_op["n"], reviewed_op["N"]) == (0, 1)
