"""Generator boundaries: isolated inputs, no-write checks and explicit mutation."""

import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from nbs_ruralscan.schema_tools import generate, quarantine
from nbs_ruralscan.schema_tools.build_paths import SchemaBuildPaths, source_revision

ROOT = Path(__file__).resolve().parents[1]


def snapshot(root):
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        if path.is_file()
        else "directory"
        for path in root.rglob("*")
    }


@pytest.fixture(scope="module")
def input_template(tmp_path_factory):
    root = tmp_path_factory.mktemp("generator-template")
    names = (
        subprocess.check_output(
            [
                "git",
                "ls-files",
                "-z",
                "schema",
                "docs",
                "pipeline",
                "methodology",
                "reference",
            ],
            cwd=ROOT,
        )
        .decode()
        .split("\0")
    )
    for name in filter(None, names):
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    return root


@pytest.fixture
def inputs(input_template, tmp_path):
    root = tmp_path / "input snapshot"
    shutil.copytree(input_template, root)
    return root


def write_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def forbid(*args, **kwargs):
    raise AssertionError("Unexpected call across generator boundary")


def test_relocated_build_is_read_only_and_uses_csv_not_stale_json(
    inputs, tmp_path, monkeypatch
):
    from nbs_ruralscan.runtime import effect_rows, codelist
    from nbs_ruralscan.schema_tools import (
        ledger,
        learnings,
        verify_metadata,
        review_exports,
        check_scope,
        check_species,
        check_direction,
    )

    # Poison legacy defaults: a selected snapshot must supply every data path.
    for module, names in (
        (ledger, ["LEDGER"]),
        (learnings, ["REVIEW_LOG", "LEARNINGS_LOG"]),
        (verify_metadata, ["QUEUE", "SRC"]),
        (review_exports, ["EXPORTS", "BATCH_DIR", "DEST"]),
        (check_scope, ["M2B_POLICY"]),
        (check_species, ["SRC"]),
        (check_direction, ["_EXCEPTIONS"]),
        (codelist, ["CODELISTS"]),
    ):
        for name in names:
            monkeypatch.setattr(module, name, tmp_path / "must-not-read-installed-data")
    source_json = inputs / "schema/recipes/agroforestry/T3_nbs_hazard_farming.json"
    source_json.write_text("[]\n")
    before = snapshot(inputs)
    monkeypatch.chdir(ROOT)  # unrelated checkout must not supply provenance
    output = tmp_path / "output"
    paths = SchemaBuildPaths(inputs / "schema", output)
    assert generate.build(paths)
    assert snapshot(inputs) == before
    assert (output / "docs/effect_rows_flat.csv").read_text() == effect_rows.build_flat(
        inputs / "schema", from_csv=True
    )
    assert json.loads(
        (output / "schema/recipes/agroforestry/T3_nbs_hazard_farming.json").read_text()
    )
    assert (
        json.loads((output / "docs/progress.json").read_text())["git_commit"]
        == "unknown"
    )
    original_history = json.loads((inputs / "docs/dashboard_data.json").read_text())[
        "build"
    ]["history"]
    assert (
        json.loads((output / "docs/dashboard_data.json").read_text())["build"][
            "history"
        ]
        == original_history
    )
    before_output = snapshot(output)
    assert generate.build(paths, check=True) == []
    assert generate.build(paths) == []
    assert snapshot(output) == before_output
    assert snapshot(inputs) == before


def test_check_on_missing_destination_creates_nothing(inputs, tmp_path):
    before = snapshot(inputs)
    output = tmp_path / "never-created"
    assert generate.build(SchemaBuildPaths(inputs / "schema", output), check=True)
    assert not output.exists()
    assert snapshot(inputs) == before


def test_validate_only_never_quarantines_or_publishes(inputs, monkeypatch):
    before = snapshot(inputs)
    monkeypatch.setattr(generate, "quarantine_inputs", forbid)
    monkeypatch.setattr(generate, "publish_outputs", forbid)
    assert generate.main([str(inputs / "schema"), "--validate-only"]) == 0
    assert snapshot(inputs) == before


@pytest.mark.parametrize("exists", [False, True])
def test_explicit_missing_or_empty_corpus_fails_without_writes(
    inputs, tmp_path, exists
):
    corpus = tmp_path / "corpus"
    if exists:
        corpus.mkdir()
    output = tmp_path / "output"
    before = snapshot(inputs)
    with pytest.raises(ValueError, match="no cached artifact|Explicit source corpus"):
        generate.build(SchemaBuildPaths(inputs / "schema", output, corpus))
    assert not output.exists()
    assert snapshot(inputs) == before


def test_selected_ledger_failure_precedes_mutation_and_publication(inputs, monkeypatch):
    write_rows(
        inputs / "pipeline/progress_ledger.csv",
        [
            {
                "nbs_id": "missing_practice",
                "table": "T4",
                "category": "grey",
                "family": "",
                "searched": "done",
            }
        ],
    )
    before = snapshot(inputs)
    monkeypatch.setattr(generate, "quarantine_inputs", forbid)
    monkeypatch.setattr(generate, "publish_outputs", forbid)
    with pytest.raises(ValueError, match="PROGRESS LEDGER FAILED"):
        generate.generate(inputs / "schema")
    assert snapshot(inputs) == before


def test_separate_build_refuses_quarantine_and_legacy_flow_preserves_it(
    inputs, tmp_path
):
    path = inputs / "schema/registers/EV_evidence_register.csv"
    rows = list(csv.DictReader(path.open()))
    sources = csv.DictReader(
        (inputs / "schema/registers/SRC_source_register.csv").open()
    )
    source_id = next(
        row["source_id"] for row in sources if row["source_category"] == "updated_lit"
    )
    row = dict(
        rows[0],
        evidence_id="fixture_pending_quarantine",
        source_id=source_id,
        nbs_id="agroforestry",
        use_role="structural_suitability",
        variable="slope",
        quote="The study area was located in Kenya.",
        reviewer_ok="false",
        review_state="pending",
        relationship="{}",
    )
    write_rows(path, [*rows, row])
    assert any(
        r["evidence_id"] == row["evidence_id"]
        for r in quarantine.candidates(inputs / "schema")
    )
    before = snapshot(inputs)
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="pending automatic quarantine"):
        generate.build(SchemaBuildPaths(inputs / "schema", output))
    assert not output.exists()
    assert snapshot(inputs) == before
    generate.generate(inputs / "schema")
    after = next(
        r for r in csv.DictReader(path.open()) if r["evidence_id"] == row["evidence_id"]
    )
    assert after["review_state"] == "dropped"
    assert after["quote"] == row["quote"]


@pytest.mark.parametrize(
    "destination",
    ["docs/progress.json", "schema/registers/EV_evidence_register.json", "docs"],
)
def test_symlink_output_escape_refused_before_validation(
    inputs, tmp_path, monkeypatch, destination
):
    output = tmp_path / "output"
    link = output / destination
    link.parent.mkdir(parents=True)
    target = (
        inputs / "schema/registers/EV_evidence_register.csv"
        if destination != "docs"
        else inputs / "docs"
    )
    link.symlink_to(target, target_is_directory=target.is_dir())
    before = snapshot(inputs)
    monkeypatch.setattr(generate, "validate_inputs", forbid)
    with pytest.raises(ValueError, match="symlink"):
        generate.build(SchemaBuildPaths(inputs / "schema", output))
    assert snapshot(inputs) == before


def test_output_root_cannot_overlap_external_corpus(inputs, tmp_path, monkeypatch):
    corpus = tmp_path / "external-corpus"
    corpus.mkdir()
    monkeypatch.setattr(generate, "validate_inputs", forbid)
    with pytest.raises(ValueError, match="overlaps protected"):
        generate.build(SchemaBuildPaths(inputs / "schema", corpus / "output", corpus))
    assert not list(corpus.iterdir())


def test_hardlinked_output_refused_before_validation(inputs, tmp_path, monkeypatch):
    output = tmp_path / "output"
    linked = output / "docs/progress.json"
    linked.parent.mkdir(parents=True)
    source = inputs / "schema/registers/EV_evidence_register.csv"
    linked.hardlink_to(source)
    before = source.read_bytes()
    monkeypatch.setattr(generate, "validate_inputs", forbid)
    with pytest.raises(ValueError, match="independent file"):
        generate.build(SchemaBuildPaths(inputs / "schema", output))
    assert source.read_bytes() == before


def test_snapshot_provenance_does_not_inherit_cwd_or_ancestor_repo(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(ROOT)
    assert source_revision(tmp_path) == "unknown"
    assert source_revision(ROOT / "schema") == "unknown"
    assert (
        source_revision(ROOT)
        == subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    )


def test_snapshot_build_refuses_unsupported_input_layout(tmp_path, monkeypatch):
    monkeypatch.setattr(generate, "validate_inputs", forbid)
    with pytest.raises(ValueError, match="CIAT-layout schema/"):
        generate.build(SchemaBuildPaths(tmp_path / "renamed-schema", tmp_path / "out"))
    assert not (tmp_path / "out").exists()


def test_interleaved_snapshots_use_own_legends_and_review_exports(tmp_path):
    from nbs_ruralscan.schema_tools import table_progress, review_exports

    for name in ("first", "second", "first"):
        root = tmp_path / name
        write_rows(
            root / "schema/registers/SRC_source_register.csv",
            [{"source_id": "paper", "nbs_ids": "trees"}],
        )
        write_rows(
            root / "schema/registers/EV_evidence_register.csv",
            [{"evidence_id": "mask", "source_id": "paper", "quote": "band.lte(1)"}],
        )
        write_rows(root / "schema/codelists/cdl.csv", [{"code": "1", "label": name}])
        write_rows(
            root / "docs/review/exports/batch.csv",
            [
                {
                    "batch": "b",
                    "evidence_id": "mask",
                    "reviewer": name,
                    "decision": "approve",
                }
            ],
        )
        (root / "docs/review/b.json").write_text(
            json.dumps(
                {
                    "batch": {"id": "b"},
                    "units": [{"evidence_id": "mask", "nbs_id": "trees"}],
                }
            )
        )
        generate.generate_dashboard_data(root / "schema")
        data = json.loads((root / "docs/dashboard_data.json").read_text())
        assert data["decoded_classes"]["mask"]["included"] == [[1, name]]
        assert table_progress.build(root / "schema")["review"]["batches"]["b"][
            "reviewers"
        ] == [name]
        review_exports.write_decisions(
            dest=root / "docs/out.json",
            exports_dir=root / "docs/review/exports",
            batch_dir=root / "docs/review",
        )
        assert set(
            json.loads((root / "docs/out.json").read_text())["decisions"]["b"]["mask"]
        ) == {name}


def test_individual_check_writers_do_not_create_docs(tmp_path):
    schema = tmp_path / "schema"
    write_rows(
        schema / "registers/SRC_source_register.csv",
        [{"source_id": "p", "nbs_ids": "trees"}],
    )
    before = snapshot(tmp_path)
    assert generate.generate_progress_report(schema, check=True)
    assert generate.generate_dashboard_data(schema, check=True)
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("isolated", [False, True])
def test_late_generator_failure_cannot_publish_partial_output(
    inputs, tmp_path, monkeypatch, isolated
):
    from nbs_ruralscan.runtime import effect_rows

    paths = SchemaBuildPaths(inputs / "schema", tmp_path / "out" if isolated else None)
    # A stale artifact would have been overwritten before the last producer failed.
    stale = inputs / "schema/registers/SRC_source_register.json"
    stale.write_text("[]\n")
    before = snapshot(inputs)

    def fail_last(*args, **kwargs):
        raise RuntimeError("flat effect rows failed")

    monkeypatch.setattr(effect_rows, "write_flat", fail_last)
    with pytest.raises(RuntimeError, match="flat effect rows failed"):
        generate.build(paths)
    assert snapshot(inputs) == before
    if isolated:
        assert paths.output_root is not None
        assert not paths.output_root.exists()


def test_check_does_not_stage_artifacts(inputs, monkeypatch):
    from nbs_ruralscan.schema_tools import publication

    before = snapshot(inputs)
    monkeypatch.setattr(publication, "staged_publish", forbid)
    generate.build(SchemaBuildPaths(inputs / "schema"), check=True)
    assert snapshot(inputs) == before
