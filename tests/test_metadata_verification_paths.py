"""Metadata verification uses selected artifacts and publishes complete updates.

Queue entries and documents are synthetic test fixtures. Only the Crossref
response adapter is replaced; title matching uses real PDF/text content.
"""

import csv
from dataclasses import replace
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

import fitz
import pytest

from nbs_ruralscan.schema_tools import publication
from nbs_ruralscan.schema_tools import verify_metadata as verification


ROOT = Path(__file__).resolve().parents[1]
TITLE = "Riparian corridor infiltration thresholds and sediment retention"
WRONG_TITLE = "Urban transit electrification finance and municipal governance"
CITATION = f"Synthetic incorrect author (2026). {TITLE}. Test publication."


def write_csv(path, rows, columns):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows({name: row.get(name, "") for name in columns} for row in rows)


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def tree(root):
    return {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def row(source_id="synthetic", **changes):
    return {
        "source_id": source_id,
        "citation": CITATION,
        "doi": "10.0000/synthetic",
        "status": "pending",
        "doi_verified": "",
        "title_verified": "",
        "target_library_path": f"synthetic-library/{source_id}.pdf",
        "note": "Synthetic fixture, not discovered project evidence.",
        **changes,
    }


def record(title=TITLE):
    return {
        "title": [title],
        "author": [{"family": "Verified"}, {"family": "Coauthor"}],
        "issued": {"date-parts": [[2024]]},
        "container-title": ["Synthetic journal"],
    }


def pdf(path, page_texts):
    path.parent.mkdir(parents=True, exist_ok=True)
    with fitz.open() as doc:
        for text in page_texts:
            doc.new_page().insert_textbox((40, 40, 550, 700), text)
        doc.save(path)


def make_inputs(root, *, layout="flat", rows=None, corpus=None, source_exists=True):
    root = root.resolve()
    if layout == "canonical":
        paths = verification.MetadataVerificationPaths.from_root(root, corpus=corpus)
    else:
        paths = verification.MetadataVerificationPaths(
            root / "queue.csv",
            root / "sources.csv",
            corpus or root / "corpus",
            root / "reports/audit.json",
        )
        if layout == "split":
            paths = replace(
                paths,
                queue=root / "acquisition/queue.csv",
                sources=root / "bibliography/sources.csv",
                report=root / "audit/reports/doi.json",
            )
    with (ROOT / "pipeline/acquisition_queue.csv").open(newline="") as stream:
        columns = next(csv.reader(stream))
    write_csv(paths.queue, [row()] if rows is None else rows, columns)
    if source_exists:
        write_csv(paths.sources, [], ["source_id", "citation"])
    return paths


@pytest.fixture(autouse=True)
def no_real_crossref(monkeypatch):
    def unconfigured(doi):
        pytest.fail(f"Unexpected Crossref request in isolated test: {doi}")

    monkeypatch.setattr(verification, "_crossref", unconfigured)


def successful_crossref(monkeypatch):
    monkeypatch.setattr(verification, "_crossref", lambda doi: (record(), "ok"))


@pytest.mark.parametrize("layout", ["flat", "split"])
@pytest.mark.parametrize("operation", ["verify", "verify_titles"])
def test_explicit_paths_ignore_compiler_defaults_from_foreign_cwd(
    tmp_path, monkeypatch, layout, operation
):
    rows = [row(doi="", status="acquired")] if operation == "verify_titles" else [row()]
    paths = make_inputs(
        tmp_path / "selected",
        layout=layout,
        rows=rows,
        corpus=tmp_path / "external-corpus",
    )
    pdf(paths.corpus / "synthetic.pdf", [TITLE])
    decoy = make_inputs(tmp_path / "compiler-defaults", rows=[row("compiler_decoy")])
    for attr, selected in (
        ("QUEUE", decoy.queue),
        ("SRC", decoy.sources),
        ("CORPUS", decoy.corpus),
        ("REPORT", decoy.report),
    ):
        monkeypatch.setattr(verification, attr, selected)
    foreign = tmp_path / "foreign-cwd"
    foreign.mkdir()
    monkeypatch.chdir(foreign)
    successful_crossref(monkeypatch)
    before = tree(tmp_path)
    assert getattr(verification, operation)(paths=paths) == 0
    after = tree(tmp_path)
    expected = {paths.queue.relative_to(tmp_path)}
    if operation == "verify":
        expected.add(paths.report.relative_to(tmp_path))
    assert {
        p for p in set(before) | set(after) if before.get(p) != after.get(p)
    } == expected
    (verified,) = read_csv(paths.queue)
    assert (
        verified["title_verified" if operation == "verify_titles" else "doi_verified"]
        == "true"
    )


def test_doi_outcomes_preserve_identity_and_unreachable_fields(tmp_path, monkeypatch):
    rows = [
        row("good", doi="10.0000/good"),
        row("default_pending", doi="10.0000/default", status=""),
        row("not_found", doi="10.0000/not_found"),
        row("mismatch", doi="10.0000/mismatch"),
        row(
            "unreachable",
            doi="10.0000/unreachable",
            doi_verified="true",
            title_verified="true",
        ),
        row("already_acquired", doi="10.0000/acquired", status="acquired"),
        row("already_extracted", doi="10.0000/extracted", status="extracted"),
        row("no_doi", doi=""),
    ]
    paths = make_inputs(tmp_path, rows=rows)
    before = {r["source_id"]: r for r in read_csv(paths.queue)}
    calls = []

    def crossref(doi):
        calls.append(doi)
        if doi.endswith("not_found"):
            return None, "not_found"
        if doi.endswith("unreachable"):
            return None, "unreachable"
        return record(WRONG_TITLE if doi.endswith("mismatch") else TITLE), "ok"

    monkeypatch.setattr(verification, "_crossref", crossref)
    assert verification.verify(paths=paths) == 0
    after = {r["source_id"]: r for r in read_csv(paths.queue)}
    assert set(calls) == {
        "10.0000/good",
        "10.0000/default",
        "10.0000/not_found",
        "10.0000/mismatch",
        "10.0000/unreachable",
    }
    for sid in ("good", "default_pending"):
        assert (
            after[sid]["citation"]
            == f"Verified et al. (2024). {TITLE}. Synthetic journal."
        )
        assert (
            after[sid]["doi"] == before[sid]["doi"]
            and after[sid]["doi_verified"] == "true"
        )
    for sid in ("not_found", "mismatch"):
        assert after[sid]["doi"] == "" and after[sid]["doi_verified"] == "false"
        assert after[sid]["citation"] == before[sid]["citation"]
        assert "acquire by TITLE" in after[sid]["note"]
    for sid in ("unreachable", "already_acquired", "already_extracted", "no_doi"):
        assert after[sid] == before[sid]
    audit = json.loads(paths.report.read_text())
    assert {k: audit[k] for k in ("checked", "verified", "failed", "unreachable")} == {
        "checked": 5,
        "verified": 2,
        "failed": 2,
        "unreachable": 1,
    }
    assert {r["source_id"]: r["reason"] for r in audit["results"]} == {
        "good": "ok",
        "default_pending": "ok",
        "not_found": "doi_unresolved",
        "mismatch": "title_mismatch",
        "unreachable": "unreachable",
    }


def test_crossref_uses_two_workers_without_mocking_executor(tmp_path, monkeypatch):
    paths = make_inputs(
        tmp_path, rows=[row(f"fixture_{i}", doi=f"10.0000/{i}") for i in range(4)]
    )
    barrier, lock = threading.Barrier(2), threading.Lock()
    active = maximum = 0

    def crossref(doi):
        nonlocal active, maximum
        with lock:
            active += 1
            maximum = max(maximum, active)
        try:
            barrier.wait(timeout=3)
            time.sleep(0.02)
            return record(), "ok"
        finally:
            with lock:
                active -= 1

    monkeypatch.setattr(verification, "_crossref", crossref)
    verification.verify(paths=paths)
    assert maximum == 2
    assert json.loads(paths.report.read_text())["verified"] == 4


def test_interleaved_paths_and_helpers_never_reuse_other_corpus(tmp_path, monkeypatch):
    first = make_inputs(tmp_path / "first", rows=[row(doi="", status="acquired")])
    second = make_inputs(
        tmp_path / "second",
        rows=[row(doi="", status="acquired")],
        corpus=tmp_path / "separate-corpus",
    )
    pdf(first.corpus / "synthetic.pdf", [TITLE])
    pdf(second.corpus / "synthetic.pdf", [WRONG_TITLE] * 3 + [TITLE])
    monkeypatch.setattr(verification, "CORPUS", tmp_path / "absent-compiler-corpus")
    first_head = verification._head_text("synthetic", corpus=first.corpus)
    second_head = verification._head_text("synthetic", pages=3, corpus=second.corpus)
    assert first_head is not None and TITLE in first_head
    assert second_head is not None and TITLE not in second_head
    assert (
        verification._title_page_in_body("synthetic", TITLE, corpus=second.corpus) == 4
    )
    verification.verify_titles(paths=first)
    first_after = tree(tmp_path / "first")
    verification.verify_titles(paths=second)
    second_after = tree(tmp_path / "second")
    verification.verify_titles(paths=first)
    assert (
        tree(tmp_path / "first") == first_after
        and tree(tmp_path / "second") == second_after
    )
    assert read_csv(first.queue)[0]["title_verified"] == "true"
    assert read_csv(second.queue)[0]["title_verified"] == "false"
    assert "Body-only match at PDF page 4" in read_csv(second.queue)[0]["note"]


def test_title_cover_body_reference_and_untouched_rows(tmp_path):
    ids = (
        "cover",
        "body",
        "reference",
        "hand",
        "uncached",
        "web",
        "has_doi",
        "pending",
    )
    rows = [row(sid, doi="", status="acquired") for sid in ids]
    rows[3].update(title_verified="true", note=verification.HAND_CONFIRMED)
    rows[5].update(url="https://example.invalid/synthetic", target_library_path="")
    rows[6]["doi"] = "10.0000/kept"
    rows[7]["status"] = "pending"
    paths = make_inputs(tmp_path, rows=rows)
    pdf(paths.corpus / "cover.pdf", [TITLE])
    pdf(paths.corpus / "body.pdf", [WRONG_TITLE] * 3 + ["Chapter 4\n" + TITLE])
    pdf(
        paths.corpus / "reference.pdf",
        [WRONG_TITLE] * 3 + ["References\nSynthetic Author (2024). " + TITLE],
    )
    for sid in ("hand", "web", "has_doi", "pending"):
        pdf(paths.corpus / f"{sid}.pdf", [WRONG_TITLE])
    paths.report.parent.mkdir(parents=True)
    paths.report.write_text('{"historical_audit": true}\n')
    before = {r["source_id"]: r for r in read_csv(paths.queue)}
    old_report = paths.report.read_bytes()
    assert (
        verification._title_page_in_body("reference", TITLE, corpus=paths.corpus)
        is None
    )
    assert verification.verify_titles(paths=paths) == 0
    after = {r["source_id"]: r for r in read_csv(paths.queue)}
    assert after["cover"]["title_verified"] == "true"
    assert (
        after["body"]["title_verified"] == "false"
        and "verify chapter identity manually" in after["body"]["note"]
    )
    assert (
        after["reference"]["title_verified"] == "false"
        and "TITLE CHECK FAILED" in after["reference"]["note"]
    )
    assert "Body-only match" not in after["reference"]["note"]
    for sid in ("hand", "uncached", "web", "has_doi", "pending"):
        assert after[sid] == before[sid]
    assert paths.report.read_bytes() == old_report


@pytest.mark.parametrize("extension", [".txt", ".html", ".md"])
def test_selected_text_snapshot_formats_and_extracted_status(tmp_path, extension):
    paths = make_inputs(tmp_path, rows=[row(doi="", status="extracted")])
    paths.corpus.mkdir()
    (paths.corpus / f"synthetic{extension}").write_text(
        f"<h1>{TITLE}</h1>\nSynthetic fixture."
    )
    verification.verify_titles(paths=paths)
    assert read_csv(paths.queue)[0]["title_verified"] == "true"
    assert not paths.report.exists()


def test_missing_optional_src_and_corpus_keep_uncached_rows_unchanged(tmp_path, capsys):
    paths = make_inputs(
        tmp_path, rows=[row(doi="", status="acquired")], source_exists=False
    )
    before = tree(tmp_path)
    assert verification.verify_titles(paths=paths) == 0
    assert "not_cached=1" in capsys.readouterr().out
    assert verification.check(queue_path=paths.queue, sources_path=paths.sources) == 0
    assert tree(tmp_path) == before


def test_legacy_no_argument_entrypoints_keep_selected_constants(tmp_path, monkeypatch):
    paths = make_inputs(
        tmp_path, rows=[row(), row("title_source", doi="", status="acquired")]
    )
    pdf(paths.corpus / "title_source.pdf", [TITLE])
    for attr, selected in (
        ("QUEUE", paths.queue),
        ("SRC", paths.sources),
        ("CORPUS", paths.corpus),
        ("REPORT", paths.report),
    ):
        monkeypatch.setattr(verification, attr, selected)
    successful_crossref(monkeypatch)
    assert verification.verify() == verification.verify_titles() == 0
    doi_row, title_row = read_csv(paths.queue)
    assert doi_row["doi_verified"] == title_row["title_verified"] == "true"
    head = verification._head_text("title_source")
    assert head is not None and TITLE in head


def test_citation_chasing_fragment_ids_keep_identity_and_selected_artifact(
    tmp_path, monkeypatch
):
    doi_id, title_id = "synthetic_parent#ref44_cited", "synthetic_parent#ref45_cited"
    paths = make_inputs(
        tmp_path,
        rows=[row(doi_id), row(title_id, doi="", status="acquired")],
        corpus=tmp_path / "selected-citation-artifacts",
    )
    pdf(paths.corpus / f"{title_id}.pdf", [TITLE])
    successful_crossref(monkeypatch)
    assert verification.verify(paths=paths) == 0
    assert verification.verify_titles(paths=paths) == 0
    doi_row, title_row = read_csv(paths.queue)
    assert doi_row["source_id"] == doi_id and doi_row["doi_verified"] == "true"
    assert title_row["source_id"] == title_id and title_row["title_verified"] == "true"
    head = verification._head_text(title_id, corpus=paths.corpus)
    assert head is not None and TITLE in head
    assert json.loads(paths.report.read_text())["results"][0]["source_id"] == doi_id


@pytest.mark.parametrize("operation", ["verify", "verify_titles"])
@pytest.mark.parametrize("bad_id", ["", "   ", "../escape", "duplicate"])
def test_invalid_or_duplicate_source_ids_fail_before_any_work(
    tmp_path, monkeypatch, operation, bad_id
):
    rows = [row("duplicate"), row(bad_id)] if bad_id == "duplicate" else [row(bad_id)]
    paths = make_inputs(tmp_path, rows=rows)
    before = tree(tmp_path)
    with pytest.raises(ValueError):
        getattr(verification, operation)(paths=paths)
    assert tree(tmp_path) == before


@pytest.mark.parametrize("operation", ["verify", "verify_titles"])
@pytest.mark.parametrize("malformed", [False, True])
def test_dry_run_checks_full_batch_and_serialization_without_outputs(
    tmp_path, monkeypatch, operation, malformed
):
    rows = [row(doi="", status="acquired")] if operation == "verify_titles" else [row()]
    paths = make_inputs(tmp_path, rows=rows)
    pdf(paths.corpus / "synthetic.pdf", [TITLE])
    successful_crossref(monkeypatch)
    if malformed:
        paths.queue.write_bytes(
            paths.queue.read_bytes().rstrip(b"\n") + b",extra_unheaded_field\n"
        )
    before = tree(tmp_path)
    if malformed:
        with pytest.raises(ValueError):
            getattr(verification, operation)(paths=paths, dry_run=True)
    else:
        assert getattr(verification, operation)(paths=paths, dry_run=True) == 0
    assert tree(tmp_path) == before
    assert not paths.report.parent.exists()


@pytest.mark.parametrize(
    "alias",
    [
        "queue_report",
        "case_queue_report",
        "queue_src",
        "report_src",
        "case_report_src",
        "queue_corpus",
        "report_corpus",
        "case_report_corpus",
        "symlink_queue",
        "symlink_report",
        "hardlink_queue",
        "hardlink_report",
    ],
)
def test_output_aliases_rejected_before_crossref_and_writes(tmp_path, alias):
    paths = make_inputs(tmp_path)
    if alias == "queue_report":
        paths = replace(paths, report=paths.queue)
    elif alias == "case_queue_report":
        paths = replace(paths, report=paths.queue.with_name(paths.queue.name.upper()))
    elif alias == "queue_src":
        paths = replace(paths, sources=paths.queue)
    elif alias == "report_src":
        paths = replace(paths, report=paths.sources)
    elif alias == "case_report_src":
        paths = replace(
            paths, report=paths.sources.with_name(paths.sources.name.upper())
        )
    elif alias == "queue_corpus":
        paths = replace(paths, corpus=paths.queue.parent)
    elif alias == "report_corpus":
        paths = replace(paths, report=paths.corpus / "audit.json")
    elif alias == "case_report_corpus":
        paths = replace(
            paths,
            report=paths.corpus.with_name(paths.corpus.name.upper()) / "audit.json",
        )
    elif alias == "symlink_queue":
        selected = tmp_path / "queue-link.csv"
        selected.symlink_to(paths.queue)
        paths = replace(paths, queue=selected)
    elif alias == "symlink_report":
        paths.report.parent.mkdir(parents=True)
        paths.report.symlink_to(paths.sources)
    elif alias == "hardlink_queue":
        os.link(paths.queue, tmp_path / "queue-link.csv")
    else:
        paths.report.parent.mkdir(parents=True)
        os.link(paths.sources, paths.report)
    before = tree(tmp_path)
    with pytest.raises(ValueError):
        verification.verify(paths=paths)
    assert tree(tmp_path) == before


@pytest.mark.parametrize("existing_report", [False, True])
@pytest.mark.parametrize("after_replace", [False, True])
def test_second_output_failure_restores_both_files_without_success_message(
    tmp_path, monkeypatch, capsys, existing_report, after_replace
):
    paths = make_inputs(tmp_path)
    if existing_report:
        paths.report.parent.mkdir(parents=True)
        paths.report.write_text('{"previous_audit": true}\n')
    successful_crossref(monkeypatch)
    original = publication.os.replace
    attempted = []
    failed = False

    def fail_report(source, destination):
        nonlocal failed
        if Path(destination) in (paths.queue, paths.report):
            attempted.append(Path(destination))
        if Path(destination) == paths.report and not failed:
            failed = True
            if after_replace:
                original(source, destination)
            raise OSError("injected audit installation failure")
        return original(source, destination)

    monkeypatch.setattr(publication.os, "replace", fail_report)
    before = tree(tmp_path)
    with pytest.raises(OSError, match="injected audit installation failure"):
        verification.verify(paths=paths)
    assert attempted[:2] == [paths.queue, paths.report]
    assert tree(tmp_path) == before
    assert "verify:" not in capsys.readouterr().out
    assert paths.report.parent.exists() is existing_report
    assert not list(tmp_path.rglob(".nbs-publish-*"))


def test_title_queue_failure_restores_original_before_success_output(
    tmp_path, monkeypatch, capsys
):
    paths = make_inputs(tmp_path, rows=[row(doi="", status="acquired")])
    pdf(paths.corpus / "synthetic.pdf", [TITLE])
    original = publication.os.replace
    failed = False

    def fail_queue(source, destination):
        nonlocal failed
        if Path(destination) == paths.queue and not failed:
            failed = True
            original(source, destination)
            raise OSError("injected title queue failure")
        return original(source, destination)

    monkeypatch.setattr(publication.os, "replace", fail_queue)
    before = tree(tmp_path)
    with pytest.raises(OSError, match="injected title queue failure"):
        verification.verify_titles(paths=paths)
    assert tree(tmp_path) == before
    assert "verify-titles:" not in capsys.readouterr().out


def test_cli_selected_root_corpus_and_optional_src_check(tmp_path):
    root = tmp_path / "data-only"
    paths = make_inputs(
        root,
        layout="canonical",
        corpus=tmp_path / "external-pdfs",
        rows=[row(doi="", status="acquired")],
    )
    pdf(paths.corpus / "synthetic.pdf", [TITLE])
    foreign = tmp_path / "foreign-cwd"
    foreign.mkdir()
    env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    command = [
        sys.executable,
        "-I",
        str(ROOT / "src/nbs_ruralscan/schema_tools/verify_metadata.py"),
    ]
    options = ["--root", str(root), "--corpus-dir", str(paths.corpus)]

    def execute(*args):
        return subprocess.run(
            command + list(args), cwd=foreign, env=env, capture_output=True, text=True
        )

    before = tree(tmp_path)
    dry = execute("verify-titles", *options, "--dry-run")
    assert dry.returncode == 0 and "nothing published" in dry.stdout, (
        dry.stdout + dry.stderr
    )
    assert tree(tmp_path) == before
    applied = execute("verify-titles", *options)
    assert applied.returncode == 0, applied.stdout + applied.stderr
    assert read_csv(paths.queue)[0]["title_verified"] == "true"
    assert execute(*options).returncode == 0
    assert execute("check", *options, "--dry-run").returncode == 2
    queued = read_csv(paths.queue)
    queued[0]["title_verified"] = "false"
    write_csv(paths.queue, queued, list(queued[0]))
    write_csv(
        paths.sources,
        [{"source_id": "synthetic", "citation": CITATION}],
        ["source_id", "citation"],
    )
    before_check = tree(tmp_path)
    assert execute("check", *options).returncode == 1
    assert tree(tmp_path) == before_check
    paths.sources.unlink()
    assert execute("check", *options).returncode == 0
    assert not list(foreign.iterdir()) and not paths.report.exists()
