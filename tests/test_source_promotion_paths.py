"""Selected source promotion validates synthetic PDFs and publishes SRC as one batch.

All titles, documents and assessments here are synthetic test fixtures. The real
body, title-identity and metadata gates run without scientific-check mocks.
"""

import csv
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from types import SimpleNamespace

import fitz
import pytest

from nbs_ruralscan.schema_tools import publication
from nbs_ruralscan.schema_tools import source_promotion as promotion


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-11-06"


def columns(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return next(csv.reader(stream))


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows, names):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=names, lineterminator="\n")
        writer.writeheader()
        writer.writerows({name: row.get(name, "") for name in names} for row in rows)


def tree(root):
    return {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def make_pdf(path, title, detail="Synthetic document, not project evidence."):
    path.parent.mkdir(parents=True, exist_ok=True)
    with fitz.open() as doc:
        page = doc.new_page()
        page.insert_text((50, 50), title + "\n" + detail)
        doc.save(path)


def make_inputs(root, *, layout="flat", source_ids=("synthetic_alpha",), corpus=None):
    root = root.resolve()
    if layout == "canonical":
        paths = promotion.SourcePromotionPaths.from_root(root, corpus=corpus)
    else:
        paths = promotion.SourcePromotionPaths(
            root / "queue.csv", root / "sources.csv", corpus or root / "pdfs"
        )
        if layout == "split":
            paths = replace(
                paths,
                queue=root / "acquisition/queue.csv",
                sources=root / "bibliography/sources.csv",
            )
    queue = []
    metadata = {}
    for sid in source_ids:
        title = f"Synthetic promotion fixture for {sid}"
        make_pdf(paths.corpus / f"{sid}.pdf", title)
        queue.append(
            {
                "source_id": sid,
                "citation": f"Synthetic fixtures (2026). {title}. Test publication.",
                "doi": "",
                "doi_verified": "",
                "title_verified": "true",
                "nbs_id": "agroforestry | forest_restoration| agroforestry",
                "status": "acquired",
                "access_status": "paywalled",
                "target_library_path": f"synthetic-test-library/{sid}.pdf",
                "url": f"https://example.invalid/synthetic/{sid}",
                "note": 'process=grey; method_subtype=review; study_scope=["HTI"]; income_groups_covered=["LIC"]',
            }
        )
        metadata[sid] = {
            "benchmark_tier": "medium",
            "venue_type": "institutional_report",
        }
    write_csv(paths.queue, queue, columns(ROOT / "pipeline/acquisition_queue.csv"))
    write_csv(
        paths.sources, [], columns(ROOT / "schema/registers/SRC_source_register.csv")
    )
    return paths, metadata


def run(paths, metadata, source_ids=("synthetic_alpha",), **options):
    return promotion.promote(
        list(source_ids),
        metadata,
        paths=paths,
        nbs="agroforestry",
        retrieved_at=DATE,
        **options,
    )


def rewrite_queue(paths, **changes):
    rows = read_csv(paths.queue)
    rows[-1].update(changes)
    write_csv(paths.queue, rows, columns(paths.queue))


def existing_source(
    paths, *, source_id="historical_fixture", scopes="agroforestry|forest_restoration"
):
    row = {
        "source_id": source_id,
        "citation": "Synthetic historical fixture (2025). Existing reviewed source. Test publication.",
        "nbs_ids": scopes,
        "extraction_status": "swept",
        "vars_extracted": "synthetic_variable",
        "extractor": "synthetic_historical_reviewer",
        "extraction_date": "2025-01-01",
        "extraction_run_id": "synthetic_historical_run",
    }
    write_csv(paths.sources, [row], columns(paths.sources))


@pytest.mark.parametrize("layout", ["flat", "split", "canonical"])
def test_selected_paths_from_foreign_cwd_preserve_scope_access_and_provenance(
    tmp_path, monkeypatch, layout
):
    paths, metadata = make_inputs(
        tmp_path / "data", layout=layout, corpus=tmp_path / "external-pdfs"
    )
    existing_source(paths)
    foreign = tmp_path / "foreign-cwd"
    foreign.mkdir()
    monkeypatch.chdir(foreign)
    before = tree(tmp_path)
    old_src = paths.sources.read_bytes()
    result = run(paths, metadata)
    assert result.appended == 1 and result.skipped == ()
    after = tree(tmp_path)
    assert {p for p in set(before) | set(after) if before.get(p) != after.get(p)} == {
        paths.sources.relative_to(tmp_path)
    }
    assert paths.sources.read_bytes().startswith(old_src)
    historical, source = read_csv(paths.sources)
    assert historical["extraction_status"] == "swept"
    assert source["nbs_ids"] == "agroforestry|forest_restoration"
    assert source["extraction_status"] == "pending"
    assert all(
        source[key] == ""
        for key in (
            "vars_extracted",
            "extraction_date",
            "extraction_run_id",
            "extractor",
        )
    )
    assert (
        source["artifact_sha1"]
        == hashlib.sha1((paths.corpus / "synthetic_alpha.pdf").read_bytes()).hexdigest()
    )
    assert source["access_status"] == "paywalled"
    assert source["source_category"] == "grey" and source["source_kind"] == "grey_lit"
    assert source["library_path"] == "synthetic-test-library/synthetic_alpha.pdf"
    assert source["method_type"] == "review"
    assert source["study_country"] == "HTI" and source["study_income_group"] == "LIC"
    assert source["retrieved_at"] == DATE
    assert source["url"] == "https://example.invalid/synthetic/synthetic_alpha"
    stats = (paths.sources.stat().st_mtime_ns, paths.sources.stat().st_ino)
    repeated = run(paths, {}, source_ids=("synthetic_alpha", "synthetic_alpha"))
    assert repeated.appended == 0 and repeated.skipped == ("synthetic_alpha",)
    assert tree(tmp_path) == after
    assert stats == (paths.sources.stat().st_mtime_ns, paths.sources.stat().st_ino)


def test_interleaved_contexts_and_row_builder_use_selected_corpus(tmp_path):
    first, meta_first = make_inputs(tmp_path / "first")
    second, meta_second = make_inputs(
        tmp_path / "second", corpus=tmp_path / "other-artifacts"
    )
    second_pdf = second.corpus / "synthetic_alpha.pdf"
    second_pdf.unlink()
    make_pdf(
        second_pdf,
        "Synthetic promotion fixture for synthetic_alpha",
        "A different synthetic corpus copy.",
    )
    rewrite_queue(
        second,
        access_status="oa",
        note="process=updated_lit; method_subtype=meta_analysis",
    )
    meta_second["synthetic_alpha"]["benchmark_tier"] = "high"
    first_result = run(first, meta_first)
    first_before = tree(tmp_path / "first")
    second_result = run(second, meta_second)
    second_before = tree(tmp_path / "second")
    run(first, {})
    assert first_result.appended == second_result.appended == 1
    assert (
        tree(tmp_path / "first") == first_before
        and tree(tmp_path / "second") == second_before
    )
    (first_row,) = read_csv(first.sources)
    (second_row,) = read_csv(second.sources)
    assert first_row["artifact_sha1"] != second_row["artifact_sha1"]
    assert (
        first_row["access_status"] == "paywalled"
        and second_row["access_status"] == "open_access"
    )
    assert (
        second_row["benchmark_tier"] == "high"
        and second_row["method_type"] == "meta_analysis"
    )
    direct = promotion.build_row(
        read_csv(second.queue)[0],
        meta_second["synthetic_alpha"],
        columns(second.sources),
        SimpleNamespace(nbs="agroforestry", date=DATE),
        corpus=second.corpus,
    )
    assert direct == second_row


@pytest.mark.parametrize(
    "scope_issue",
    [None, "requested_not_in_queue", "existing_missing_queue_scope", "absent_queue"],
)
def test_existing_src_skip_checks_scope_before_artifact_acquisition_or_metadata(
    tmp_path, scope_issue
):
    paths, _ = make_inputs(tmp_path)
    existing_source(
        paths,
        source_id="synthetic_alpha",
        scopes="agroforestry"
        if scope_issue == "existing_missing_queue_scope"
        else "agroforestry|forest_restoration",
    )
    (paths.corpus / "synthetic_alpha.pdf").unlink()
    paths.corpus.rmdir()  # A preserved existing source does not require any cache.
    rewrite_queue(paths, status="pending", title_verified="false")
    if scope_issue == "requested_not_in_queue":
        rewrite_queue(paths, nbs_id="forest_restoration")
    elif scope_issue == "absent_queue":
        write_csv(paths.queue, [], columns(paths.queue))
    before = tree(tmp_path)
    if scope_issue:
        with pytest.raises(promotion.PromotionGateError) as failure:
            run(paths, {})
        message = str(failure.value)
        assert "scope" in message and "synthetic_alpha" in message
        assert "not acquired" not in message and "No such file" not in message
    else:
        result = run(paths, {})
        assert result.appended == 0 and result.skipped == ("synthetic_alpha",)
    assert tree(tmp_path) == before


@pytest.mark.parametrize(
    "defect",
    [
        "wrong_document",
        "unverified",
        "missing_pdf",
        "missing_assessment",
        "unacquired",
        "missing_library_path",
    ],
)
def test_mixed_valid_invalid_batch_publishes_nothing(tmp_path, defect):
    paths, metadata = make_inputs(tmp_path, source_ids=("a_valid", "z_invalid"))
    invalid_pdf = paths.corpus / "z_invalid.pdf"
    if defect == "wrong_document":
        invalid_pdf.unlink()
        make_pdf(
            invalid_pdf,
            "Unrelated report on urban transport and infrastructure finance",
        )
    elif defect == "unverified":
        rewrite_queue(paths, title_verified="false")
    elif defect == "missing_pdf":
        invalid_pdf.unlink()
    elif defect == "missing_assessment":
        metadata.pop("z_invalid")
    elif defect == "unacquired":
        rewrite_queue(paths, status="pending")
    else:
        rewrite_queue(paths, target_library_path="")
    before = tree(tmp_path)
    with pytest.raises(promotion.PromotionGateError) as failure:
        run(paths, metadata, source_ids=("a_valid", "z_invalid"))
    assert "z_invalid" in str(failure.value)
    assert all("a_valid" not in problem for problem in failure.value.problems)
    assert tree(tmp_path) == before


@pytest.mark.parametrize("register", ["queue", "sources"])
@pytest.mark.parametrize("defect", ["duplicate", "blank", "whitespace"])
def test_ambiguous_register_ids_fail_closed(tmp_path, register, defect):
    paths, metadata = make_inputs(tmp_path)
    selected = getattr(paths, register)
    if register == "sources":
        existing_source(paths)
    rows = read_csv(selected)
    if defect == "duplicate":
        rows.append(dict(rows[0]))
    else:
        rows[0]["source_id"] = "" if defect == "blank" else "  "
    write_csv(selected, rows, columns(selected))
    before = tree(tmp_path)
    with pytest.raises(ValueError, match="blank/duplicate source_id"):
        run(paths, metadata)
    assert tree(tmp_path) == before


@pytest.mark.parametrize("invalid_header", [False, True])
def test_dry_run_serializes_complete_rows_and_rejects_incompatible_header(
    tmp_path, invalid_header
):
    paths, metadata = make_inputs(tmp_path)
    if invalid_header:
        write_csv(
            paths.sources,
            [],
            [name for name in columns(paths.sources) if name != "artifact_sha1"],
        )
    before = tree(tmp_path)
    if invalid_header:
        with pytest.raises(ValueError, match="fields not in fieldnames"):
            run(paths, metadata, dry_run=True)
    else:
        result = run(paths, metadata, dry_run=True)
        assert result.appended == 1 and result.skipped == ()
    assert tree(tmp_path) == before


def test_missing_final_newline_appends_without_changing_existing_record_bytes(tmp_path):
    paths, metadata = make_inputs(tmp_path)
    existing_source(paths)
    old = paths.sources.read_bytes().replace(b"\n", b"\r\n").rstrip(b"\r\n")
    paths.sources.write_bytes(old)
    assert run(paths, metadata).appended == 1
    assert paths.sources.read_bytes().startswith(old + b"\n")
    assert [row["source_id"] for row in read_csv(paths.sources)] == [
        "historical_fixture",
        "synthetic_alpha",
    ]


@pytest.mark.parametrize(
    "alias",
    [
        "queue",
        "queue_case",
        "protected",
        "protected_case",
        "corpus",
        "corpus_case",
        "symlink",
        "parent_symlink",
        "hardlink",
    ],
)
def test_destination_aliases_to_readonly_inputs_are_refused(tmp_path, alias):
    paths, metadata = make_inputs(tmp_path)
    protected = ()
    if alias == "queue":
        paths = replace(paths, sources=paths.queue)
    elif alias == "queue_case":
        selected = paths.queue.with_name(paths.queue.name.upper())
        if not selected.exists():
            shutil.copyfile(paths.queue, selected)
        paths = replace(paths, sources=selected)
    elif alias in {"protected", "protected_case"}:
        selected = (
            paths.sources
            if alias == "protected"
            else paths.sources.with_name(paths.sources.name.upper())
        )
        if not selected.exists():
            shutil.copyfile(paths.sources, selected)
        protected = (selected,)
    elif alias in {"corpus", "corpus_case"}:
        selected = paths.corpus / "sources.csv"
        shutil.copyfile(paths.sources, selected)
        paths = replace(
            paths,
            sources=selected,
            corpus=paths.corpus
            if alias == "corpus"
            else paths.corpus.with_name(paths.corpus.name.upper()),
        )
    elif alias == "symlink":
        selected = tmp_path / "source-alias.csv"
        selected.symlink_to(paths.sources)
        paths = replace(paths, sources=selected)
    elif alias == "parent_symlink":
        selected = tmp_path / "parent-alias"
        selected.symlink_to(paths.sources.parent, target_is_directory=True)
        paths = replace(paths, sources=selected / paths.sources.name)
    else:
        selected = tmp_path / "source-hardlink.csv"
        os.link(paths.sources, selected)
        protected = (selected,)
    before = tree(tmp_path)
    with pytest.raises(ValueError):
        run(paths, metadata, protected_inputs=protected)
    assert tree(tmp_path) == before


@pytest.mark.parametrize("after_replace", [False, True])
def test_publication_failure_before_or_after_replace_restores_entire_src(
    tmp_path, monkeypatch, after_replace
):
    paths, metadata = make_inputs(tmp_path, source_ids=("a_valid", "z_valid"))
    existing_source(paths)
    original = publication.os.replace
    failed = False

    def fail_once(source, destination):
        nonlocal failed
        if Path(destination) == paths.sources and not failed:
            failed = True
            if after_replace:
                original(source, destination)
            raise OSError("injected source publication failure")
        return original(source, destination)

    monkeypatch.setattr(publication.os, "replace", fail_once)
    before = tree(tmp_path)
    with pytest.raises(OSError, match="injected source publication failure"):
        run(paths, metadata, source_ids=("a_valid", "z_valid"))
    assert failed
    assert tree(tmp_path) == before
    assert not list(tmp_path.rglob(".nbs-publish-*"))


def test_staged_csv_write_failure_never_changes_selected_src(tmp_path, monkeypatch):
    paths, metadata = make_inputs(tmp_path)
    original = Path.write_bytes
    failed = False

    def fail_staged(path, data):
        nonlocal failed
        result = original(path, data)
        if path.name == paths.sources.name and path != paths.sources:
            failed = True
            raise OSError("injected private CSV write failure")
        return result

    monkeypatch.setattr(Path, "write_bytes", fail_staged)
    before = tree(tmp_path)
    with pytest.raises(OSError, match="injected private CSV write failure"):
        run(paths, metadata)
    assert failed and tree(tmp_path) == before


def test_relocated_cli_selects_data_root_and_separate_corpus(tmp_path):
    paths, metadata = make_inputs(
        tmp_path / "data-only", layout="canonical", corpus=tmp_path / "selected-pdfs"
    )
    compiler = tmp_path / "compiler"
    wrapper = compiler / "scripts/promote-queue-to-src.py"
    wrapper.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / "scripts/promote-queue-to-src.py", wrapper)
    inputs = tmp_path / "input-requests"
    inputs.mkdir()
    ids, meta = inputs / "sources.json", inputs / "metadata.json"
    ids.write_text(json.dumps([{"source_id": "synthetic_alpha"}]))
    meta.write_text(json.dumps(metadata))
    foreign = tmp_path / "foreign-cwd"
    foreign.mkdir()
    command = [
        sys.executable,
        str(wrapper),
        "--root",
        str(tmp_path / "data-only"),
        "--corpus-dir",
        str(paths.corpus),
        "--nbs",
        "agroforestry",
        "--run-id",
        "synthetic-test",
        "--sources",
        str(ids),
        "--meta",
        str(meta),
        "--date",
        DATE,
    ]
    env = {
        **os.environ,
        "PYTHONPATH": str(ROOT / "src"),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    before = tree(tmp_path)
    dry = subprocess.run(
        command + ["--dry-run"], cwd=foreign, env=env, capture_output=True, text=True
    )
    assert dry.returncode == 0, dry.stdout + dry.stderr
    assert "nothing published" in dry.stdout and tree(tmp_path) == before
    result = subprocess.run(
        command, cwd=foreign, env=env, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "appended 1 row(s)" in result.stdout
    assert read_csv(paths.sources)[0]["extraction_status"] == "pending"
    after = tree(tmp_path)
    assert {p for p in set(before) | set(after) if before.get(p) != after.get(p)} == {
        paths.sources.relative_to(tmp_path)
    }
    assert not (compiler / "schema").exists() and not (compiler / ".cache").exists()
    assert not list(foreign.iterdir())
