from nbs_ruralscan.recipe.evidence_assessment import assessments


def unit(eid, **kw):
    return dict(
        evidence_id=eid,
        source_id=kw.get("source", "paper"),
        variable="slope",
        suitability_family_id="regional",
        claim_scope=kw.get("scope", "practice_technology"),
        relationship={"direction": kw.get("direction", "decreasing")},
        reviewer_ok=kw.get("approved", False),
        review_state=kw.get("state", ""),
        lineage_of=kw.get("lineage", ""),
        context={
            "model_use": {"verified": True},
            "t4_assessment": {
                "source_checked": True,
                "context_id": kw.get("context", "region_A"),
                "calibration_status": "uncalibrated",
            },
        },
    )


def test_duplicate_and_companion_are_one_vote():
    rows = assessments(
        [unit("a"), unit("b"), unit("c", source="companion", lineage="a")], {}
    )
    assert len(rows) == 1
    assert rows[0]["pending_only_paper_vote"]
    assert rows[0]["pending_directions"] == ["decreasing"]


def test_context_scope_and_review_state_stay_distinct():
    rows = assessments(
        [
            unit("a", approved=True),
            unit("b", context="region_B"),
            unit("c", scope="species_specific"),
            unit("d", state="dropped"),
        ],
        {},
    )
    assert len(rows) == 3
    assert sum(r["approved_paper_vote"] for r in rows) == 1
    assert all("d" not in r["evidence_ids"] for r in rows)


def test_opposite_pending_direction_does_not_overwrite_approved():
    row = assessments(
        [unit("a", approved=True), unit("b", direction="increasing")], {}
    )[0]
    assert row["direction_conflict"]
    assert row["approved_directions"] == ["decreasing"]
    assert row["pending_directions"] == ["increasing"]
    assert row["calibration_status"] == ["uncalibrated"]
