"""Dashboard snapshot identity and stale detection on isolated fixture repositories."""

import csv
import json
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from nbs_ruralscan.schema_tools import generate


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    import subprocess

    monkeypatch.setattr(
        subprocess, "run", lambda *args, **kwargs: SimpleNamespace(stdout="commit-one")
    )
    schema = tmp_path / "schema"
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "dashboard.html").write_text("<title>Progress</title>")
    write_csv(
        docs / "dashboard-releases.csv",
        [{"version": "1.0.0", "count_definition_version": "1"}],
    )
    write_csv(
        schema / "registers" / "SRC_source_register.csv",
        [{"source_id": "paper", "nbs_ids": "trees", "source_kind": "paper"}],
    )
    write_csv(
        schema / "registers" / "EV_evidence_register.csv",
        [
            {
                "evidence_id": "a",
                "source_id": "paper",
                "nbs_id": "trees",
                "use_role": "nbs_effect",
                "reviewer_ok": "false",
            }
        ],
    )
    write_csv(
        tmp_path / "pipeline" / "acquisition_queue.csv",
        [
            {
                "source_id": "queued",
                "nbs_id": "trees",
                "tables": "T3|T6",
                "status": "pending",
            }
        ],
    )
    # No T0/T4 file: effect-only recipes must still be included in the dashboard.
    write_csv(
        schema / "recipes" / "trees" / "T3_nbs_hazard_farming.csv",
        [{"record_id": "hazard", "nbs_id": "trees", "evidence_ids": '["a"]'}],
    )
    return schema


def read_build(schema):
    return json.loads((schema.parent / "docs" / "dashboard_data.json").read_text())


def test_presentation_labels_are_generated_without_rewriting_registry(repo):
    family = {
        "nbs_id": "trees",
        "suitability_family_id": "trees__planted",
        "subpractice_id": "alley",
        "name": "Alley cropping",
    }
    write_csv(repo / "registers" / "FAM_family_registry.csv", [family])
    labels = repo.parent / "docs" / "dashboard-family-presentation.csv"
    write_csv(
        labels,
        [
            {
                "suitability_family_id": "trees__planted",
                "display_name": "Planted tree–crop systems",
                "navigation_group": "practice",
            }
        ],
    )
    generate.generate_dashboard_data(repo)
    data = read_build(repo)
    assert data["registers"]["FAM_family_registry"] == [family]
    assert data["family_presentation"]["trees__planted"]["display_name"] == (
        "Planted tree–crop systems"
    )
    group = next(
        f
        for p in data["progress_overview"]["practices"]
        for f in p["families"]
        if f["family_id"] == "trees__planted"
    )
    assert group["name"] == "Planted tree–crop systems"
    assert group["subpractices"][0]["name"] == "Alley cropping"
    assert generate.generate_dashboard_data(repo, check=True) == []


def test_repeat_build_is_byte_stable_and_retains_history(repo, monkeypatch):
    path = repo.parent / "docs" / "dashboard_data.json"
    assert generate.generate_dashboard_data(repo) == [path]
    first_bytes = path.read_bytes()
    first = read_build(repo)
    assert first["recipes"]["trees"]["T3_nbs_hazard_farming"]
    assert first["progress_overview"]["totals"]["known_sources"] == 2
    assert len(first["build"]["history"]) == 1

    class Later(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2099, 1, 1, tzinfo=timezone.utc)

    monkeypatch.setattr(generate, "datetime", Later)
    assert generate.generate_dashboard_data(repo) == []
    assert generate.generate_dashboard_data(repo, check=True) == []
    assert path.read_bytes() == first_bytes


def test_ui_change_updates_ui_identity_and_appends_one_history_entry(repo):
    generate.generate_dashboard_data(repo)
    first = read_build(repo)
    (repo.parent / "docs" / "dashboard.html").write_text(
        "<title>New progress UI</title>"
    )
    path = repo.parent / "docs" / "dashboard_data.json"
    before = path.read_bytes()
    assert generate.generate_dashboard_data(repo, check=True) == [path]
    assert path.read_bytes() == before  # Check must not mutate history or payload.
    generate.generate_dashboard_data(repo)
    second = read_build(repo)
    assert first["build"]["ui_id"] != second["build"]["ui_id"]
    assert first["build"]["data_id"] == second["build"]["data_id"]
    assert len(second["build"]["history"]) == 2
    assert generate.generate_dashboard_data(repo) == []


@pytest.mark.parametrize("section", ["queue", "recipe", "evidence"])
def test_data_inputs_invalidate_snapshot_without_ui_change(repo, section):
    generate.generate_dashboard_data(repo)
    first = read_build(repo)
    if section == "queue":
        write_csv(
            repo.parent / "pipeline" / "acquisition_queue.csv",
            [
                {
                    "source_id": "queued",
                    "nbs_id": "trees",
                    "tables": "T3|T6",
                    "status": "acquired",
                }
            ],
        )
    elif section == "recipe":
        write_csv(
            repo / "recipes" / "trees" / "T6_nbs_scorecard.csv",
            [{"record_id": "benefit", "nbs_id": "trees", "evidence_ids": '["a"]'}],
        )
    else:
        write_csv(
            repo / "registers" / "EV_evidence_register.csv",
            [
                {
                    "evidence_id": "a",
                    "source_id": "paper",
                    "nbs_id": "trees",
                    "use_role": "nbs_effect",
                    "reviewer_ok": "true",
                }
            ],
        )
    assert generate.generate_dashboard_data(repo, check=True)
    generate.generate_dashboard_data(repo)
    second = read_build(repo)
    assert first["build"]["ui_id"] == second["build"]["ui_id"]
    assert first["build"]["data_id"] != second["build"]["data_id"]
    assert len(second["build"]["history"]) == 2


def test_tampered_payload_fails_even_with_unchanged_stored_hashes(repo):
    generate.generate_dashboard_data(repo)
    path = repo.parent / "docs" / "dashboard_data.json"
    original = read_build(repo)
    tampered = read_build(repo)
    tampered["progress_overview"]["totals"]["known_sources"] = 999999
    path.write_text(json.dumps(tampered))
    assert generate.generate_dashboard_data(repo, check=True) == [path]
    assert read_build(repo)["build"] == original["build"]
    generate.generate_dashboard_data(repo)
    repaired = read_build(repo)
    assert repaired["progress_overview"]["totals"]["known_sources"] == 2
    assert repaired["build"] == original["build"]  # Repair is not a new content build.


def test_new_release_and_count_definition_are_logged(repo):
    generate.generate_dashboard_data(repo)
    first = read_build(repo)
    write_csv(
        repo.parent / "docs" / "dashboard-releases.csv",
        [
            {"version": "1.0.0", "count_definition_version": "1"},
            {"version": "1.1.0", "count_definition_version": "2"},
        ],
    )
    generate.generate_dashboard_data(repo)
    second = read_build(repo)
    assert second["build"]["release"] == "1.1.0"
    assert second["build"]["count_definition_version"] == "2"
    assert second["build"]["history"][0] == first["build"]["history"][0]
    assert second["build"]["data_id"] != first["build"]["data_id"]


def test_build_history_is_bounded(repo):
    generate.generate_dashboard_data(repo)
    path = repo.parent / "docs" / "dashboard_data.json"
    data = read_build(repo)
    data["build"]["history"] = [{"release": f"old-{i}"} for i in range(60)]
    path.write_text(json.dumps(data))
    (repo.parent / "docs" / "dashboard.html").write_text("changed")
    generate.generate_dashboard_data(repo)
    history = read_build(repo)["build"]["history"]
    assert len(history) == 50
    assert history[0]["release"] == "old-11"
    assert history[-1]["release"] == "1.0.0"


def test_decoded_class_tuples_compare_as_serialised_json(repo, monkeypatch):
    from nbs_ruralscan.runtime import codelist

    write_csv(
        repo / "registers" / "EV_evidence_register.csv",
        [{"evidence_id": "mask", "source_id": "paper", "quote": "band.lte(10)"}],
    )
    monkeypatch.setattr(
        codelist,
        "summarise_cdl_mask",
        lambda quote: {"n_included": 1, "included": [(1, "Class one")]},
    )
    generate.generate_dashboard_data(repo)
    assert generate.generate_dashboard_data(repo, check=True) == []
    assert generate.generate_dashboard_data(repo) == []
