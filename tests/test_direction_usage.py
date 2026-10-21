import copy
import json

from nbs_ruralscan.recipe.direction_usage import direction_usage, write_direction_report


def unit(eid="one", source="a", direction="negative", **changes):
    return dict(
        nbs_id="agroforestry",
        evidence_id=eid,
        source_id=source,
        variable="slope",
        suitability_family_id="cross_family",
        claim_scope="practice_technology",
        unit="degrees",
        taxon="",
        use_role="structural_suitability",
        relationship={"direction": direction},
        context={},
        reviewer_ok="true",
        **changes,
    )


def test_doi_aliases_and_duplicate_rows_count_once():
    sources = {"a": {"doi": "DOI:10.1/ABC"}, "b": {"doi": "https://doi.org/10.1/abc"}}
    result = direction_usage([unit(), unit("two", "b", "decreasing")], sources)
    assert result[0]["reviewed_counts"] == {"decreasing": 1}
    assert len(result[0]["papers"]) == 1


def test_pending_conflict_cannot_change_reviewed_direction():
    pending = unit("pending", direction="increasing")
    pending["reviewer_ok"] = "false"
    result = direction_usage([unit(), pending], {})[0]
    assert result["reviewed_counts"] == {"decreasing": 1}
    assert result["pending_only_counts"] == {}
    assert result["papers"][0]["directions"]["pending"] == "increasing"


def test_reviewed_model_use_does_not_approve_pending_direction():
    reviewed = unit(direction="")
    pending = unit("pending")
    pending["reviewer_ok"] = "false"
    result = direction_usage([reviewed, pending], {})[0]
    assert result["reviewed_counts"] == {}
    assert result["pending_only_counts"] == {"decreasing": 1}


def test_quarantine_observed_presence_effects_and_other_nbs_cannot_vote():
    dropped = unit("dropped", review_state="dropped")
    observed = unit("observed")
    observed["relationship"]["type"] = "observed_presence"
    effect = unit("effect")
    effect["use_role"] = "nbs_effect"
    other = unit("other")
    other["nbs_id"] = "wetland"
    result = direction_usage([dropped, observed, effect, other], {})[0]
    assert result["reviewed_counts"] == result["pending_only_counts"] == {}
    assert len(result["papers"][0]["records"]["reviewed"]) == 1


def test_scopes_families_units_taxa_stay_separate():
    rows = [unit()]
    for key, value in [
        ("claim_scope", "species_specific"),
        ("unit", "%"),
        ("taxon", "coffee"),
        ("suitability_family_id", "shaded"),
    ]:
        row = unit(key)
        row[key] = value
        rows.append(row)
    assert len(direction_usage(rows, {})) == 5


def test_conflicting_directions_one_vote_context_and_lineage_preserved():
    first, second = unit(), unit("two", direction="increasing")
    first["context"] = {"study_country": "India"}
    second["context"] = {
        "study_country": "Nepal",
        "model_use": {"lineage_of": "original"},
    }
    second["lineage_of"] = "response citation"
    rows = [first, second]
    before = copy.deepcopy(rows)
    result = direction_usage(rows, {})[0]
    assert result["reviewed_counts"] == {"conflicting_directions": 1}
    records = result["papers"][0]["records"]["reviewed"]
    assert records[1]["study_context"]["study_country"] == "Nepal"
    assert records[1]["model_use_lineage"] == "original"
    assert records[1]["response_lineage"] == "response citation"
    assert rows == before


def test_unrecognised_and_missing_labels_not_zero_relationship_votes():
    result = direction_usage(
        [unit(direction="positive_within_range"), unit("two", direction="")], {}
    )[0]
    assert result["reviewed_counts"] == {}
    assert (
        result["papers"][0]["records"]["reviewed"][0]["reported_direction"]
        == "positive_within_range"
    )


def test_csv_json_inputs_match_native_objects():
    row = unit()
    encoded = dict(row, relationship=json.dumps(row["relationship"]), context="{}")
    assert direction_usage([row], {}) == direction_usage([encoded], {})


def test_matrix_has_paper_columns_review_lanes_and_escaped_context(tmp_path):
    (tmp_path / "pipeline/t4_audit/agroforestry/final_audit").mkdir(parents=True)
    (tmp_path / "docs/review").mkdir(parents=True)
    row = unit()
    row["context"] = {"study_area": "<script>unsafe</script>"}
    write_direction_report(tmp_path, [row, unit("two", "b", "increasing")], {})
    page = (tmp_path / "docs/review/t4-direction-agreement.html").read_text()
    assert "<th>a</th><th>b</th>" in page
    assert "Reviewed: Lower favoured" in page
    assert "<script>unsafe</script>" not in page
    assert "&lt;script&gt;unsafe&lt;/script&gt;" in page
    assert "data-search=" in page


def test_csv_units_come_from_relationship_or_reported_values():
    first, second = unit(), unit("two")
    first.pop("unit")
    second.pop("unit")
    first["relationship"]["unit"] = "degrees"
    second["context"] = {"reported_values": {"unit": "%"}}
    assert {r["unit"] for r in direction_usage([first, second], {})} == {"degrees", "%"}
