"""Relocated intake uses its selected artifacts and preserves a whole register batch.

PDFs and claims here are explicitly synthetic test fixtures, never project evidence.
The real intake gates inspect each fixture; no quote or scientific gate is mocked.
"""

import csv
from dataclasses import fields, replace
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import fitz
import pytest

from nbs_ruralscan.recipe.evidence import EvidenceUnit
from nbs_ruralscan.schema_tools import evidence_intake as intake, publication


ROOT = Path(__file__).resolve().parents[1]


def write_csv(path, rows, columns=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=columns or list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def tree(root):
    return {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def make_inputs(root, *, flat=True, corpus=None):
    if flat:
        paths = intake.EvidenceIntakePaths(
            **{
                field.name: root / (field.name + ".csv")
                for field in fields(intake.EvidenceIntakePaths)
                if field.name != "corpus"
            },
            corpus=corpus or root / "source artifacts",
        )
    else:
        paths = intake.EvidenceIntakePaths.from_root(root, corpus=corpus)
    paths.corpus.mkdir(parents=True)
    pdf = paths.corpus / "synthetic_paper.pdf"
    title = "Synthetic intake test fixture"
    with fitz.open() as doc:
        doc.new_page().insert_text(
            (50, 50),
            title + "\nAgroforestry increased yield by 20 percent in the test region.",
        )
        doc.save(pdf)
    # The claim is sliced from the actual PDF text, not retyped into the staged unit.
    with fitz.open(pdf) as doc:
        text = doc[0].get_text()
    quote = text[text.index("Agroforestry") :].strip()
    source = {
        "source_id": "synthetic_paper",
        "citation": f"Synthetic fixture (2026). {title}.",
        "doi": "",
        "artifact_sha1": hashlib.sha1(pdf.read_bytes()).hexdigest(),
        "extraction_status": "pending",
        "extraction_date": "",
        "extraction_run_id": "",
        "extractor": "",
        "vars_extracted": "",
        "study_income_group": "",
        "venue_type": "",
    }
    write_csv(paths.sources, [source])
    write_csv(paths.queue, [{**source, "doi_verified": "", "title_verified": "true"}])
    write_csv(paths.evidence, [], [f.name for f in fields(EvidenceUnit)])
    write_csv(
        paths.families,
        [
            {
                "nbs_id": "agroforestry",
                "suitability_family_id": "agroforestry__test_family",
            }
        ],
    )
    write_csv(paths.variables, [{"canonical_variable_id": "test_measurement"}])
    write_csv(
        paths.bands,
        [
            {
                "metric": "pct_change",
                "abs_min": 0,
                "abs_max": "",
                "strength_class": "moderate",
            }
        ],
    )
    write_csv(
        paths.contexts,
        [
            {"context_type": "aez", "context_id": "test_aez"},
            {"context_type": "farming_system", "context_id": "test_farming"},
        ],
    )
    write_csv(
        paths.direction_sense,
        [{"variable": "test_measurement", "quantity": "yield", "high_is": "good"}],
    )
    write_csv(
        paths.operational_policy,
        [
            {
                "variable": "test_measurement",
                "decision": "allow",
                "reason": "Synthetic fixture policy",
            }
        ],
    )
    unit = {
        "evidence_id": "ev_synthetic",
        "source_id": "synthetic_paper",
        "nbs_id": "agroforestry",
        "suitability_family_id": "agroforestry__test_family",
        "variable": "test_measurement",
        "use_role": "nbs_effect",
        "evidence_type": "literature_relationship",
        "claim_basis": "primary_measured",
        "claim_scope": "practice_technology",
        "extraction_confidence": "high",
        "quote": quote,
        "locator_type": "page",
        "page": 1,
        "relationship": {
            "direction": "positive",
            "direction_cue": quote[quote.index("increased") : quote.index(" in the")],
            "metric": "pct_change",
            "magnitude": 20,
            "unit": "percent",
            "strength_class": "moderate",
        },
        "context": {
            "practice_as_described": "Agroforestry",
            "aez": "test_aez",
            "farming_system": "test_farming",
        },
        "ruleset_version": "v1.9.6",
    }
    return paths, unit


def ingest(paths, units, **kwargs):
    return intake.ingest(
        units,
        paths=paths,
        run_id="test_run",
        extractor="test fixture",
        day="2026-11-06",
        **kwargs,
    )


def test_flat_context_from_foreign_cwd_is_interleaved_and_read_only_on_preview(
    tmp_path, monkeypatch
):
    first, a = make_inputs(tmp_path / "first")
    second, b = make_inputs(tmp_path / "second")
    foreign = tmp_path / "unrelated cwd"
    foreign.mkdir()
    monkeypatch.chdir(foreign)
    before = tree(tmp_path)
    assert intake.gate([a], paths=first) == []
    assert intake.gate([b], paths=second) == []
    assert ingest(first, [a], dry_run=True).appended == 1
    assert ingest(second, [b], dry_run=True).appended == 1
    assert tree(tmp_path) == before
    ingest(first, [a])
    assert tree(tmp_path / "second") == {
        p.relative_to("second"): data
        for p, data in before.items()
        if p.parts[0] == "second"
    }
    ingest(second, [b])
    first_saved = tree(tmp_path / "first")
    assert ingest(first, [a]).appended == 0
    assert tree(tmp_path / "first") == first_saved


def test_evidence_and_sources_can_live_in_separate_directories(tmp_path):
    paths, unit = make_inputs(tmp_path / "evidence workspace")
    sources = tmp_path / "separate source catalog" / "sources.csv"
    sources.parent.mkdir()
    paths.sources.rename(sources)
    selected = replace(paths, sources=sources)
    before = tree(tmp_path)
    result = ingest(selected, [unit])
    assert result.appended == 1
    after = tree(tmp_path)
    assert {p for p in after if after[p] != before.get(p)} == {
        selected.evidence.relative_to(tmp_path),
        selected.sources.relative_to(tmp_path),
    }
    assert read_csv(selected.evidence)[0]["evidence_id"] == unit["evidence_id"]
    assert read_csv(selected.sources)[0]["vars_extracted"] == unit["variable"]


@pytest.mark.parametrize(
    "policy,signal",
    [
        ("bands", "band_mismatch"),
        ("contexts", "not in T7"),
        ("variables", "no VONT id"),
        ("families", "not in FAM"),
        ("corpus", "no cached PDF"),
    ],
)
def test_selected_inputs_control_gate_not_installed_defaults(tmp_path, policy, signal):
    good, unit = make_inputs(tmp_path / "good")
    other, _ = make_inputs(tmp_path / "other")
    if policy == "bands":
        rows = read_csv(other.bands)
        rows[0]["strength_class"] = "strong"
        write_csv(other.bands, rows)
    elif policy == "contexts":
        rows = read_csv(other.contexts)
        for row in rows:
            row["context_id"] = "other_" + row["context_id"]
        write_csv(other.contexts, rows)
    elif policy == "variables":
        write_csv(other.variables, [{"canonical_variable_id": "unrelated"}])
    elif policy == "families":
        write_csv(
            other.families,
            [
                {
                    "nbs_id": "agroforestry",
                    "suitability_family_id": "agroforestry__unrelated",
                }
            ],
        )
    else:
        (other.corpus / "synthetic_paper.pdf").unlink()
    before = tree(tmp_path)
    selected = replace(good, **{policy: getattr(other, policy)})
    assert any(signal in error for error in intake.gate([unit], paths=selected))
    assert intake.gate([unit], paths=good) == []
    assert tree(tmp_path) == before


def test_direction_policy_reload_same_path_and_interleave(tmp_path):
    first, unit = make_inputs(tmp_path / "first")
    second, _ = make_inputs(tmp_path / "second")
    unit["relationship"]["direction"] = "negative"
    assert any("cue_word_conflict" in e for e in intake.gate([unit], paths=first))
    rows = read_csv(first.direction_sense)
    rows[0]["quantity"] = "unrelated"
    write_csv(first.direction_sense, rows)
    assert intake.gate([unit], paths=first) == []
    assert any("cue_word_conflict" in e for e in intake.gate([unit], paths=second))
    assert intake.gate([unit], paths=first) == []


def test_operational_policy_is_selected_and_reloaded(tmp_path):
    paths, unit = make_inputs(tmp_path)
    unit["use_role"] = "operational_risk"
    assert intake.gate([unit], {"operational_risk"}, paths=paths) == []
    rows = read_csv(paths.operational_policy)
    rows[0]["decision"] = "exclude"
    write_csv(paths.operational_policy, rows)
    before = tree(tmp_path)
    with pytest.raises(intake.IntakeGateError, match="may not be an operational_risk"):
        ingest(paths, [unit], allowed_roles={"operational_risk"})
    assert tree(tmp_path) == before


@pytest.mark.parametrize(
    "name",
    [
        "queue",
        "families",
        "variables",
        "bands",
        "contexts",
        "direction_sense",
        "operational_policy",
        "corpus",
    ],
)
def test_missing_required_input_fails_before_writes(tmp_path, name):
    paths, unit = make_inputs(tmp_path)
    selected = replace(paths, **{name: tmp_path / "missing"})
    before = tree(tmp_path)
    with pytest.raises(FileNotFoundError, match="Missing intake"):
        ingest(selected, [unit])
    assert tree(tmp_path) == before


@pytest.mark.parametrize("status", ["pending", "signed_off"])
def test_accept_only_updates_ev_src_preserves_reviews_and_repeat(tmp_path, status):
    paths, unit = make_inputs(tmp_path)
    prior = []
    for eid, reviewed, dropped in [
        ("reviewed", "true", ""),
        ("dropped", "false", "dropped"),
    ]:
        row = {
            **unit,
            "evidence_id": eid,
            "reviewer_ok": reviewed,
            "review_state": dropped,
        }
        row["relationship"] = json.dumps(row["relationship"])
        row["context"] = json.dumps(row["context"])
        prior.append(row)
    write_csv(paths.evidence, prior, [f.name for f in fields(EvidenceUnit)])
    source = read_csv(paths.sources)[0]
    source.update(
        extraction_status=status,
        extraction_date="2020-01-01",
        extraction_run_id="original_run",
        extractor="original_extractor",
    )
    write_csv(paths.sources, [source])
    batch = [
        unit,
        {**unit, "evidence_id": "reviewed"},
        {**unit, "evidence_id": "dropped"},
    ]
    before = tree(tmp_path)
    result = ingest(paths, batch)
    assert result.appended == 1
    after = tree(tmp_path)
    assert {p for p in after if after[p] != before.get(p)} == {
        paths.evidence.relative_to(tmp_path),
        paths.sources.relative_to(tmp_path),
    }
    rows = {r["evidence_id"]: r for r in read_csv(paths.evidence)}
    assert rows["reviewed"]["reviewer_ok"] == "true"
    assert rows["dropped"]["review_state"] == "dropped"
    saved_source = read_csv(paths.sources)[0]
    assert saved_source["vars_extracted"] == "test_measurement"
    assert saved_source["extraction_status"] == (
        "swept" if status == "pending" else "signed_off"
    )
    assert saved_source["extraction_run_id"] == (
        "test_run" if status == "pending" else "original_run"
    )
    assert ingest(paths, batch).appended == 0
    assert tree(tmp_path) == after


def test_existing_id_conflict_refuses_entire_batch(tmp_path):
    paths, unit = make_inputs(tmp_path)
    ingest(paths, [unit])
    conflict = {**unit, "quote": unit["quote"][:-1]}
    new = {**unit, "evidence_id": "ev_other"}
    before = tree(tmp_path)
    with pytest.raises(ValueError, match="existing evidence differs"):
        ingest(paths, [new, conflict])
    assert tree(tmp_path) == before


@pytest.mark.parametrize(
    "operation", ["append_to_register", "resync_vars_extracted", "stamp_extracted"]
)
def test_staged_mutation_failure_preserves_registers(tmp_path, monkeypatch, operation):
    paths, unit = make_inputs(tmp_path)
    before = tree(tmp_path)
    original = getattr(intake, operation)

    def fail(*args, **kwargs):
        original(*args, **kwargs)
        raise OSError("injected staged mutation failure")

    monkeypatch.setattr(intake, operation, fail)
    with pytest.raises(OSError, match="injected staged mutation"):
        ingest(paths, [unit])
    assert tree(tmp_path) == before


@pytest.mark.parametrize("after_replace", [False, True])
def test_second_register_install_failure_rolls_back(
    tmp_path, monkeypatch, after_replace
):
    paths, unit = make_inputs(tmp_path)
    before = tree(tmp_path)
    real_replace = publication.os.replace
    failed = False

    def fail(source, destination):
        nonlocal failed
        if Path(destination) == paths.sources and not failed:
            failed = True
            if after_replace:
                real_replace(source, destination)
                raise KeyboardInterrupt("after source replacement")
            raise OSError("source replacement failed")
        return real_replace(source, destination)

    monkeypatch.setattr(publication.os, "replace", fail)
    with pytest.raises(KeyboardInterrupt if after_replace else OSError):
        ingest(paths, [unit])
    assert failed
    assert tree(tmp_path) == before


@pytest.mark.parametrize("name", ["evidence", "sources"])
@pytest.mark.parametrize("link", ["symlink", "hardlink"])
def test_redirected_destinations_refused(tmp_path, name, link):
    paths, unit = make_inputs(tmp_path)
    target = getattr(paths, name)
    external = tmp_path / "external.csv"
    external.write_bytes(target.read_bytes())
    target.unlink()
    if link == "symlink":
        target.symlink_to(external)
    else:
        os.link(external, target)
    before = tree(tmp_path)
    with pytest.raises(ValueError, match="symlink|independent file"):
        ingest(paths, [unit])
    assert tree(tmp_path) == before


@pytest.mark.parametrize("target", ["sources", "queue", "bands"])
def test_aliased_destinations_refused(tmp_path, target):
    paths, unit = make_inputs(tmp_path)
    aliased = replace(paths, evidence=getattr(paths, target))
    before = tree(tmp_path)
    with pytest.raises(ValueError, match="distinct|overlaps read-only"):
        ingest(aliased, [unit])
    assert tree(tmp_path) == before


def test_relocated_cli_selects_external_corpus_and_keeps_inputs_on_dry_run(tmp_path):
    data = tmp_path / "data"
    paths, unit = make_inputs(data, flat=False, corpus=tmp_path / "external corpus")
    staging = tmp_path / "staging.json"
    staging.write_text(json.dumps([unit]))
    cwd = tmp_path / "foreign cwd"
    cwd.mkdir()
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    command = [
        sys.executable,
        str(ROOT / "scripts/ingest-effects-staging.py"),
        str(staging),
        "--root",
        str(data),
        "--corpus-dir",
        str(paths.corpus),
    ]
    before = tree(tmp_path)
    preview = subprocess.run(
        [*command, "--dry-run"], cwd=cwd, env=env, text=True, capture_output=True
    )
    assert preview.returncode == 0, preview.stdout + preview.stderr
    assert tree(tmp_path) == before
    applied = subprocess.run(
        [*command, "--run-id", "relocated_test"],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
    )
    assert applied.returncode == 0, applied.stdout + applied.stderr
    assert len(read_csv(paths.evidence)) == 1
    assert read_csv(paths.sources)[0]["extraction_run_id"] == "relocated_test"
    after = tree(tmp_path)
    assert {p for p in after if after[p] != before.get(p)} == {
        paths.evidence.relative_to(tmp_path),
        paths.sources.relative_to(tmp_path),
    }
