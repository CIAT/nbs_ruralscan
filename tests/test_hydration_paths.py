"""Hydration uses selected read-only inputs and one guarded corpus publication."""

import csv
from dataclasses import replace
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from nbs_ruralscan.ingest import hydration as h, wocat, wocat_approach
from nbs_ruralscan.schema_tools import publication


ROOT = Path(__file__).resolve().parents[1]
SOURCE_COLUMNS = [
    "source_id",
    "library_path",
    "url",
    "source_kind",
    "source_category",
    "artifact_sha1",
]
QUEUE_COLUMNS = [
    "source_id",
    "nbs_id",
    "status",
    "target_library_path",
    "url",
    "blocker",
]


def source(sid, **fields):
    return dict(dict.fromkeys(SOURCE_COLUMNS, ""), source_id=sid, **fields)


def queued(sid, **fields):
    row = dict.fromkeys(QUEUE_COLUMNS, "")
    row.update(source_id=sid, status="acquired", nbs_id="forest")
    row.update(fields)
    return row


def write_csv(path, rows, columns):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def inputs(root, *, sources=None, queue=None, layout="split"):
    root = root.resolve()
    if layout == "canonical":
        paths = h.HydrationPaths.from_root(root / "data", library=root / "library")
    else:
        paths = h.HydrationPaths(
            root / "records/sources.csv",
            root / "queue/acquisition.csv",
            root / "storage/corpus",
            root / "archives",
            root / "library",
        )
    write_csv(paths.sources, [] if sources is None else sources, SOURCE_COLUMNS)
    write_csv(paths.queue, [] if queue is None else queue, QUEUE_COLUMNS)
    paths.archives.mkdir(parents=True)
    assert paths.library is not None
    paths.library.mkdir(parents=True)
    return paths


def inventory(root):
    return {
        str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()
    }


def no_network(*args, **kwargs):
    raise AssertionError("Unexpected source adapter/network call")


@pytest.fixture(autouse=True)
def isolate_network(monkeypatch):
    monkeypatch.setattr(h, "_fetch", no_network)
    monkeypatch.setattr(wocat, "acquire", no_network)
    monkeypatch.setattr(wocat_approach, "acquire", no_network)


def add_library(paths, name="fixture.pdf", body=b"%PDF-1.4 synthetic fixture"):
    assert paths.library is not None
    target = paths.library / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(body)
    return target


def seed_cache(paths, name, body):
    paths.corpus.mkdir(parents=True, exist_ok=True)
    target = paths.corpus / name
    target.write_bytes(body)
    return target


def adapter_bodies(sid, version=1):
    raw = json.dumps({"id": sid, "selected_version": {"id": version}}).encode()
    md = f"# {sid}\nVersion {version}\n".encode()
    meta = json.dumps(
        {
            "source_id": sid,
            "source_sha1": hashlib.sha1(raw).hexdigest(),
            "render_sha1": hashlib.sha1(md).hexdigest(),
            "selected_version_id": version,
        }
    ).encode()
    return {sid + ".source.json": raw, sid + ".md": md, sid + ".meta.json": meta}


def adapter_stub(calls, *, fail=False, incomplete=False):
    def acquire(sid, corpus, **kwargs):
        calls.append((sid, kwargs))
        for i, (name, body) in enumerate(adapter_bodies(sid).items()):
            (corpus / name).write_bytes(body)
            if i == 0 and fail:
                raise ValueError("synthetic adapter failure")
            if i == 0 and incomplete:
                return corpus / name
        return corpus / (sid + ".md")

    return acquire


@pytest.mark.parametrize("layout", ["canonical", "split"])
def test_library_bytes_and_records_preserved_in_selected_layout(tmp_path, layout):
    paths = inputs(
        tmp_path, sources=[source("fixture", library_path="fixture.pdf")], layout=layout
    )
    pdf = add_library(paths)
    before = inventory(tmp_path)
    result = h.run_hydration(paths)
    assert result.changed == (paths.corpus / "fixture.pdf",)
    assert result.changed[0].read_bytes() == pdf.read_bytes()
    assert "PDF copied         : 1" in result.report
    after = inventory(tmp_path)
    for name, body in before.items():
        assert after[name] == body


def test_all_sources_and_exact_queue_filter_keep_distinct_routes(tmp_path, monkeypatch):
    paths = inputs(
        tmp_path,
        sources=[
            source("src_pdf", library_path="fixture.pdf"),
            source(
                "src_web", url="https://example.invalid/page", source_kind="website"
            ),
            source(
                "src_code",
                url="https://github.com/org/repo/blob/pin/file.R",
                source_category="tool",
            ),
            source("no_route"),
        ],
        queue=[
            queued("queue_pdf", target_library_path="fixture.pdf"),
            queued("queue_web", url="https://example.invalid/queued"),
            queued(
                "pipe_scope",
                nbs_id="forest|wetland",
                url="https://example.invalid/skip",
            ),
            queued("other_scope", nbs_id="wetland", url="https://example.invalid/skip"),
            queued("pending", status="pending", blocker="needs browser"),
            queued("duplicate", status="duplicate"),
        ],
    )
    add_library(paths)
    calls = []
    result = h.run_hydration(
        paths,
        include_queue=True,
        nbs="forest",
        fetch=lambda url: calls.append(url) or b"raw snapshot",
    )
    assert calls == [
        "https://example.invalid/page",
        "https://raw.githubusercontent.com/org/repo/pin/file.R",
        "https://example.invalid/queued",
    ]
    assert {p.name for p in result.changed} == {
        "src_pdf.pdf",
        "src_web.html",
        "src_code.txt",
        "queue_pdf.pdf",
        "queue_web.html",
    }
    assert "SKIP pending - not acquired (needs browser)" in result.report
    assert "duplicate" not in result.report


def test_existing_cache_routes_use_markers_without_copying_existing_body(
    tmp_path, monkeypatch
):
    paths = inputs(
        tmp_path,
        sources=[
            source("pdf_route", library_path="fixture.pdf"),
            source(
                "web_route", url="https://example.invalid/page", source_kind="website"
            ),
        ],
        queue=[queued("queue_route", target_library_path="fixture.pdf")],
    )
    for sid, ext in [
        ("pdf_route", ".pdf"),
        ("web_route", ".md"),
        ("queue_route", ".html"),
    ]:
        seed_cache(paths, sid + ext, b"preserved large body" * 1000)
    seed_cache(paths, "web_route.meta.json", b"malformed held metadata")
    before = inventory(tmp_path)
    monkeypatch.setattr(h, "copy_immutable", no_network)
    result = h.run_hydration(paths, include_queue=True)
    assert not result.changed and inventory(tmp_path) == before
    assert "PDF already cached  : 1" in result.report
    assert "code/web cached     : 1" in result.report
    assert "queue already cached: 1" in result.report


def test_pdf_branch_does_not_treat_existing_text_as_pdf(tmp_path):
    paths = inputs(tmp_path, sources=[source("fixture", library_path="fixture.pdf")])
    add_library(paths)
    old = seed_cache(paths, "fixture.txt", b"keep this too")
    result = h.run_hydration(paths)
    assert result.changed == (paths.corpus / "fixture.pdf",)
    assert old.read_bytes() == b"keep this too"


def test_approach_archive_precedes_network_and_generic_page(tmp_path):
    sid = "wocat_demo_approach_12"
    md = b"# Exact archived narrative\n"
    paths = inputs(
        tmp_path,
        sources=[
            source(
                sid,
                source_kind="website",
                url="https://example.invalid/page",
                artifact_sha1=hashlib.sha1(md).hexdigest(),
            )
        ],
    )
    archive = paths.archives / "round" / (sid + ".md")
    archive.parent.mkdir()
    archive.write_bytes(md)
    result = h.run_hydration(paths)
    assert result.changed == (paths.corpus / (sid + ".md"),)
    assert result.changed[0].read_bytes() == md


def test_wocat_routes_publish_complete_bundles_and_repair_partial_sidecars(
    tmp_path, monkeypatch
):
    tech, approach = "wocat_1234_2020", "wocat_demo_approach_12"
    paths = inputs(
        tmp_path,
        sources=[
            source(tech, library_path="fixture.pdf"),
            source(approach, artifact_sha1="expected"),
        ],
    )
    seed_cache(paths, tech + ".pdf", b"old PDF stays")
    for sid in (tech, approach):
        seed_cache(paths, sid + ".source.json", b'{"old":true}')
        seed_cache(paths, sid + ".meta.json", b'{"old":true}')
    calls = []
    monkeypatch.setattr(wocat, "acquire", adapter_stub(calls))
    monkeypatch.setattr(wocat_approach, "acquire", adapter_stub(calls))
    result = h.run_hydration(paths)
    assert calls == [(approach, {"expected_sha1": "expected"}), (tech, {})]
    assert len(result.changed) == 6
    for sid in (tech, approach):
        for name, body in adapter_bodies(sid).items():
            assert (paths.corpus / name).read_bytes() == body
    assert (paths.corpus / (tech + ".pdf")).read_bytes() == b"old PDF stays"


@pytest.mark.parametrize("incomplete", [False, True])
def test_failed_or_incomplete_adapter_cannot_publish_partial_bundle(
    tmp_path, monkeypatch, incomplete
):
    sid = "wocat_demo_approach_12"
    paths = inputs(tmp_path, sources=[source(sid)])
    old = seed_cache(paths, sid + ".source.json", b'{"old":true}')
    before = inventory(tmp_path)
    monkeypatch.setattr(
        wocat_approach,
        "acquire",
        adapter_stub([], fail=not incomplete, incomplete=incomplete),
    )
    result = h.run_hydration(paths)
    assert not result.changed and inventory(tmp_path) == before
    assert old.read_bytes() == b'{"old":true}'
    assert "code/web fetch FAILED: 1" in result.report


def test_dry_run_fetches_but_publishes_nothing(tmp_path):
    paths = inputs(
        tmp_path,
        sources=[
            source("web", url="https://example.invalid/page", source_kind="website")
        ],
    )
    before = inventory(tmp_path)
    calls = []
    result = h.run_hydration(
        paths, dry_run=True, fetch=lambda url: calls.append(url) or b"snapshot"
    )
    assert calls == ["https://example.invalid/page"]
    assert result.changed == (paths.corpus / "web.html",)
    assert inventory(tmp_path) == before and not paths.corpus.exists()
    assert "DRY RUN" in result.report


@pytest.mark.parametrize("input_kind", ["sources", "queue"])
def test_record_read_snapshot_race_stops_before_fetch(
    tmp_path, monkeypatch, input_kind
):
    paths = inputs(
        tmp_path,
        sources=[
            source("web", source_kind="website", url="https://example.invalid/page")
        ],
        queue=[],
    )
    target = getattr(paths, input_kind)
    read = Path.read_bytes
    changed = False

    def racing_read(path):
        nonlocal changed
        body = read(path)
        if path == target and not changed:
            changed = True
            path.write_bytes(body + b"\n")
        return body

    monkeypatch.setattr(Path, "read_bytes", racing_read)
    with pytest.raises(ValueError, match="records changed while reading"):
        h.run_hydration(paths, include_queue=True)
    assert not paths.corpus.exists()


@pytest.mark.parametrize(
    "kind", ["sources", "queue", "library", "archive", "archive_listing", "destination"]
)
def test_drift_during_preparation_aborts_without_clobber(tmp_path, kind):
    sid = "wocat_demo_approach_12"
    md = b"# fixture archive"
    paths = inputs(
        tmp_path,
        sources=[
            source("pdf", library_path="fixture.pdf"),
            source(sid, artifact_sha1=hashlib.sha1(md).hexdigest()),
            source("web", source_kind="website", url="https://example.invalid/page"),
        ],
    )
    pdf = add_library(paths)
    archive = paths.archives / "round" / (sid + ".md")
    archive.parent.mkdir()
    archive.write_bytes(md)
    targets = {
        "sources": paths.sources,
        "queue": paths.queue,
        "library": pdf,
        "archive": archive,
        "archive_listing": paths.archives / "later" / (sid + ".md"),
        "destination": paths.corpus / "web.html",
    }
    target = targets[kind]

    def fetch(url):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"competing edit")
        return b"new fetched snapshot"

    with pytest.raises(ValueError, match="changed"):
        h.run_hydration(paths, include_queue=True, fetch=fetch)
    assert target.read_bytes() == b"competing edit"
    assert not (paths.corpus / "pdf.pdf").exists()
    assert not (paths.corpus / (sid + ".md")).exists()


def test_input_change_after_render_is_rejected_before_install(tmp_path, monkeypatch):
    paths = inputs(tmp_path, sources=[source("fixture", library_path="fixture.pdf")])
    pdf = add_library(paths)
    original_publish = h.staged_publish

    def publish(context, destinations, render, **kwargs):
        def racing_render(staged):
            result = render(staged)
            pdf.write_bytes(b"competing library revision")
            return result

        return original_publish(context, destinations, racing_render, **kwargs)

    monkeypatch.setattr(h, "staged_publish", publish)
    with pytest.raises(ValueError, match="changed"):
        h.run_hydration(paths)
    assert not paths.corpus.exists()
    assert pdf.read_bytes() == b"competing library revision"


@pytest.mark.parametrize(
    "kind",
    [
        "unsafe_id",
        "traversal",
        "absolute",
        "library_overlap",
        "archive_overlap",
        "input_overlap",
        "target_symlink",
        "target_hardlink",
    ],
)
def test_paths_refuse_unsafe_or_aliased_publication(tmp_path, kind):
    paths = inputs(tmp_path, sources=[source("fixture", library_path="fixture.pdf")])
    pdf = add_library(paths)
    if kind == "unsafe_id":
        write_csv(
            paths.sources,
            [source("../outside", library_path="fixture.pdf")],
            SOURCE_COLUMNS,
        )
    elif kind in {"traversal", "absolute"}:
        write_csv(
            paths.sources,
            [
                source(
                    "fixture",
                    library_path="../outside.pdf" if kind == "traversal" else str(pdf),
                )
            ],
            SOURCE_COLUMNS,
        )
    elif kind == "library_overlap":
        paths = replace(paths, corpus=paths.library / "cache")
    elif kind == "archive_overlap":
        paths = replace(paths, corpus=paths.archives / "cache")
    elif kind == "input_overlap":
        paths = replace(paths, corpus=paths.sources.parent)
    else:
        paths.corpus.mkdir(parents=True)
        target = paths.corpus / "fixture.pdf"
        if kind == "target_symlink":
            target.symlink_to(pdf)
        else:
            os.link(pdf, target)
    before = inventory(tmp_path)
    with pytest.raises(ValueError):
        h.run_hydration(paths)
    assert inventory(tmp_path) == before


def test_later_output_failure_rolls_back_earlier_files_and_suppresses_report(
    tmp_path, monkeypatch, capsys
):
    paths = inputs(
        tmp_path,
        sources=[
            source("one", library_path="fixture.pdf"),
            source("two", library_path="fixture.pdf"),
        ],
    )
    add_library(paths)
    original_link = publication.os.link
    calls = []

    def fail_after_link(src, dest):
        original_link(src, dest)
        calls.append(Path(dest))
        if Path(dest).parent == paths.corpus and Path(dest).name == "two.pdf":
            raise OSError("synthetic late install failure")

    monkeypatch.setattr(publication.os, "link", fail_after_link)
    with pytest.raises(OSError, match="synthetic late"):
        h.run_hydration(paths)
    assert [p for p in calls if p.parent == paths.corpus] == [
        paths.corpus / "one.pdf",
        paths.corpus / "two.pdf",
    ]
    assert not paths.corpus.exists()
    assert capsys.readouterr().out == ""


def test_adapter_recovery_error_is_not_converted_to_missing(tmp_path, monkeypatch):
    paths = inputs(tmp_path, sources=[source("wocat_1234_2020")])
    error = publication.PublicationRecoveryError(tmp_path / "retained", ["fixture"])

    def fail(*args, **kwargs):
        raise error

    monkeypatch.setattr(wocat, "acquire", fail)
    with pytest.raises(publication.PublicationRecoveryError) as caught:
        h.run_hydration(paths)
    assert caught.value is error
    assert not paths.corpus.exists()


def test_wrapper_queue_only_keeps_legacy_globals_injectable(
    tmp_path, monkeypatch, capsys
):
    paths = inputs(
        tmp_path, queue=[queued("queued", target_library_path="fixture.pdf")]
    )
    add_library(paths)
    spec = importlib.util.spec_from_file_location(
        "hydration_wrapper_test", ROOT / "scripts/hydrate-corpus.py"
    )
    assert spec and spec.loader
    wrapper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wrapper)
    monkeypatch.setattr(wrapper, "ROOT", tmp_path)
    monkeypatch.setattr(wrapper, "SRC_CSV", tmp_path / "missing-src.csv")
    monkeypatch.setattr(wrapper, "QUEUE_CSV", paths.queue)
    monkeypatch.setattr(wrapper, "CACHE", paths.corpus)
    wrapper.hydrate_queue(paths.library, "forest")
    assert (paths.corpus / "queued.pdf").exists()
    assert "queue copied/fetched: 1" in capsys.readouterr().out


def test_direct_cli_works_from_unrelated_directory_with_selected_inputs(tmp_path):
    paths = inputs(
        tmp_path,
        sources=[source("fixture", library_path="fixture.pdf")],
        layout="canonical",
    )
    add_library(paths)
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    compiler = tmp_path / "compiler"
    shutil.copytree(
        ROOT / "src", compiler / "src", ignore=shutil.ignore_patterns("__pycache__")
    )
    (compiler / "scripts").mkdir()
    shutil.copy2(
        ROOT / "scripts/hydrate-corpus.py", compiler / "scripts/hydrate-corpus.py"
    )
    result = subprocess.run(
        [
            sys.executable,
            str(compiler / "scripts/hydrate-corpus.py"),
            "--root",
            str(paths.sources.parents[2]),
            "--corpus-dir",
            str(paths.corpus),
            "--library-root",
            str(paths.library),
            "--archive-dir",
            str(paths.archives),
        ],
        cwd=foreign,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (paths.corpus / "fixture.pdf").exists()
    assert "PDF copied         : 1" in result.stdout


def test_missing_source_register_preserves_default_early_return(tmp_path):
    paths = inputs(
        tmp_path, queue=[queued("queued", target_library_path="fixture.pdf")]
    )
    add_library(paths)
    paths.sources.unlink()
    result = h.run_hydration(paths, include_queue=True)
    assert "SRC register not found" in result.report
    assert not result.changed and not paths.corpus.exists()
    result = h.run_hydration(paths, queue_only=True)
    assert result.changed == (paths.corpus / "queued.pdf",)


def test_source_pass_populates_cache_before_same_queue_id_is_considered(tmp_path):
    paths = inputs(
        tmp_path,
        sources=[
            source("shared", source_kind="website", url="https://example.invalid/page")
        ],
        queue=[queued("shared", target_library_path="fixture.pdf")],
    )
    add_library(paths)
    result = h.run_hydration(
        paths, include_queue=True, fetch=lambda url: b"source web snapshot"
    )
    assert result.changed == (paths.corpus / "shared.html",)
    assert "queue already cached: 1" in result.report
