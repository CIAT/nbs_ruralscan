from nbs_ruralscan.recipe.relationship_catalogue import (
    build_catalogue,
    render_catalogue,
)


def unit(eid, **kwargs):
    return dict(
        evidence_id=eid,
        use_role="structural_suitability",
        review_state="",
        claim_scope="practice_technology",
        variable="slope",
        source_id="source",
        **kwargs,
    )


def test_scoping_direction_and_classes_survive_without_authorizing_function():
    rows = [
        unit(
            "direction",
            evidence_type="scoping_candidate",
            relationship='{"direction":"decreasing"}',
        ),
        unit("classes", relationship='{"classes":[{"label":"high","range":"<5"}]}'),
    ]
    result = build_catalogue(
        rows,
        [
            dict(evidence_id=r["evidence_id"], disposition="selection_only")
            for r in rows
        ],
        [],
    )
    assert result["summary"]["selection_only_with_relationship_content"] == 2
    assert result["records"][0]["source_direction"] == "decreasing"
    assert all(
        r["runtime_authorization"] == "None granted by this catalogue"
        for r in result["records"]
    )
    assert all(not r["linked_mapping_ids"] for r in result["records"])


def test_scope_drop_linkage_and_unknowns_are_not_conflated():
    rows = [
        unit("species", relationship="{}"),
        unit("dropped"),
        unit("effect"),
        unit("linked"),
    ]
    rows[0]["claim_scope"] = "species_specific"
    rows[1]["review_state"] = "dropped"
    rows[2]["use_role"] = "nbs_effect"
    result = build_catalogue(
        rows, [], [{"mapping_id": "gate", "evidence_ids": '["linked"]'}]
    )
    assert result["summary"]["structural_claims"] == 2
    assert result["summary"]["explicitly_linked_claims"] == 1
    assert result["records"][0]["claim_scope"] == "species_specific"
    assert not result["records"][0]["has_stated_direction"]


def test_source_text_cannot_inject_html():
    result = build_catalogue(
        [
            unit(
                "x",
                quote="<script>alert(1)</script>",
                relationship='{"direction":"<img src=x onerror=alert(1)>"}',
            )
        ],
        [],
        [],
    )
    rendered = render_catalogue(result)
    assert "<script>alert(1)</script>" not in rendered
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in rendered
    assert "<img src=x" not in rendered


def test_contextual_numbers_do_not_become_direction_or_classes():
    result = build_catalogue(
        [unit("site", relationship='{"site_mean":950,"unit":"mm"}')],
        [{"evidence_id": "site", "disposition": "selection_only"}],
        [],
    )
    assert result["summary"]["selection_only_with_relationship_content"] == 0
    assert result["records"][0]["source_direction"] == ""
