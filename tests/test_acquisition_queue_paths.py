"""Queue, cache and library publish as one bounded acquisition operation.

Only synthetic PDFs and mocked HTTP are used. All selected records, immutable
copies, competing-writer fixtures and recovery workspaces are test-owned.
"""

import csv
from dataclasses import replace
import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace

import fitz
import pytest
from requests.structures import CaseInsensitiveDict

from nbs_ruralscan.ingest import acquisition_queue as queue
from nbs_ruralscan.schema_tools import publication


ROOT = Path(__file__).resolve().parents[1]
acquire = importlib.import_module("nbs_ruralscan.ingest.acquire")
DATE = "2026-11-06"
NBS = "forest_restoration"
SUBDIR = "forest"
TITLE = "Synthetic riparian restoration infiltration and sediment retention"
CITATION = f"Fixture (2026). {TITLE}. Synthetic publication."
URL = "https://example.invalid/paper.pdf"
COLS = [
    "source_id",
    "nbs_id",
    "date_added",
    "status",
    "citation",
    "doi",
    "doi_verified",
    "url",
    "blocker",
    "note",
    "target_library_path",
    "tables",
    "family",
]


def row(sid="paper", **values):
    result = dict.fromkeys(COLS, "")
    result.update(
        source_id=sid,
        nbs_id=NBS,
        date_added=DATE,
        status="pending",
        citation=CITATION,
        url=URL if sid == "paper" else f"https://example.invalid/{sid}.pdf",
        note="Original note",
        tables="T3|T6",
        family="forest_restoration__passive_regeneration",
    )
    result.update(values)
    return result


def write_csv(path, rows, cols=COLS):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=cols, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def pdf_bytes(title=TITLE, *, long=True):
    detail = (
        (
            "Synthetic fixture text for testing acquisition and preserved provenance. "
            * 6
        )
        if long
        else ""
    )
    with fitz.open() as doc:
        page = doc.new_page()
        page.insert_textbox((40, 40, 550, 700), title + "\n" + detail, fontsize=10)
        return doc.tobytes()


def response(
    body=b"", *, url=URL, content_type="application/pdf", text=None, payload=None
):
    return SimpleNamespace(
        status_code=200,
        content=body,
        url=url,
        headers=CaseInsensitiveDict({"Content-Type": content_type}),
        text=text if text is not None else body.decode("utf-8", errors="replace"),
        json=lambda: payload,
    )


def make_inputs(root, *, rows=None, layout="flat", prefix="archive/library"):
    root = root.resolve()
    if layout == "canonical":
        paths = queue.AcquisitionPaths.from_root(
            root / "data",
            library=root / "team-library",
            library_prefix=prefix,
            corpus=root / "external-cache",
        )
    elif layout == "split":
        paths = queue.AcquisitionPaths(
            root / "records/acquisition_queue.csv",
            root / "cache-volume/corpus",
            root / "library-volume/library",
            prefix,
        )
    else:
        paths = queue.AcquisitionPaths(
            root / "queue.csv", root / "corpus", root / "library", prefix
        )
    write_csv(paths.queue, [row()] if rows is None else rows)
    (paths.library / SUBDIR).mkdir(parents=True)
    return paths


def selected_tree(paths):
    result = {"queue": paths.queue.read_bytes()}
    for label, root in (("corpus", paths.corpus), ("library", paths.library)):
        result.update(
            {
                f"{label}/{p.relative_to(root)}": p.read_bytes()
                for p in root.rglob("*")
                if p.is_file()
            }
        )
    return result


def file_state(path):
    stat = path.stat()
    return path.read_bytes(), stat.st_mode, stat.st_mtime_ns


def seed_pair(paths, sid, body, *, url=None):
    artifact = paths.corpus / f"{sid}.pdf"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_bytes(body)
    metadata = {
        "source_id": sid,
        "url": url or f"https://example.invalid/{sid}.pdf",
        "kind": "pdf",
        "sha1": hashlib.sha1(body).hexdigest(),
        "bytes": len(body),
        "commit_sha": None,
        "fetched_at": "2026-11-06T00:00:00+00:00",
        "http_status": 200,
        "content_type": "application/pdf",
    }
    sidecar = artifact.with_suffix(".meta.json")
    sidecar.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return artifact, sidecar


def run(paths, **kwargs):
    return queue.run_acquisition(
        paths, date=DATE, nbs=NBS, library_subdir=SUBDIR, **kwargs
    )


def mock_pdf(monkeypatch, body):
    calls = []

    def get(url, **kwargs):
        calls.append((url, kwargs))
        return response(body, url=url)

    monkeypatch.setattr(acquire.requests, "get", get)
    return calls


@pytest.fixture(autouse=True)
def isolated_io(tmp_path, monkeypatch):
    def no_network(*args, **kwargs):
        pytest.fail("Unexpected HTTP request in isolated acquisition test")

    monkeypatch.setattr(acquire.requests, "get", no_network)
    monkeypatch.setattr(queue.time, "sleep", lambda *args: None)
    scratch = tmp_path / "workspaces"
    scratch.mkdir()
    original_mkdtemp = tempfile.mkdtemp
    original_rmtree = shutil.rmtree

    def mkdtemp(*args, **kwargs):
        if str(kwargs.get("prefix", "")).startswith("ruralscan-"):
            kwargs["dir"] = scratch
        return original_mkdtemp(*args, **kwargs)

    monkeypatch.setattr(tempfile, "mkdtemp", mkdtemp)
    yield
    original_rmtree(scratch, ignore_errors=True)


@pytest.mark.parametrize("layout", ["flat", "split", "canonical"])
def test_selected_layout_publishes_only_selected_records_from_foreign_cwd(
    tmp_path, monkeypatch, layout
):
    original = row(blocker="Historical route note")
    paths = make_inputs(
        tmp_path / "selected",
        rows=[original],
        layout=layout,
        prefix="logical/team-library",
    )
    decoy = make_inputs(tmp_path / "decoy", rows=[row("decoy")])
    untouched = selected_tree(decoy)
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    monkeypatch.chdir(foreign)
    body = pdf_bytes()
    calls = mock_pdf(monkeypatch, body)
    result = run(paths)
    assert result.log
    (saved,) = read_csv(paths.queue)
    assert saved["status"] == "acquired"
    assert saved["target_library_path"] == "logical/team-library/forest/paper.pdf"
    assert saved["blocker"] == original["blocker"]
    assert (
        saved["note"]
        == f"Original note; acquired {DATE} by acquire-queue.py (1 pp) → cache + SharePoint mirror"
    )
    for field in ("source_id", "citation", "nbs_id", "tables", "family", "date_added"):
        assert saved[field] == original[field]
    assert saved["url"] == URL
    assert (paths.corpus / "paper.pdf").read_bytes() == body
    assert (paths.library / SUBDIR / "paper.pdf").read_bytes() == body
    meta = json.loads((paths.corpus / "paper.meta.json").read_text(encoding="utf-8"))
    assert meta["sha1"] == hashlib.sha1(body).hexdigest() and meta["url"] == URL
    assert [url for url, _ in calls] == [URL]
    assert selected_tree(decoy) == untouched


@pytest.mark.parametrize("all_dates", [False, True])
def test_selectors_skip_unrelated_reviewed_and_human_rows_without_rewriting_them(
    tmp_path, monkeypatch, all_dates
):
    rows = [
        row("selected", nbs_id="wetland_management| forest_restoration"),
        row("older", date_added="2026-01-01"),
        row("substring", nbs_id="forest_restoration_extended"),
        row("acquired", status="acquired"),
        row("human", blocker="HUMAN CHECK — repository copy"),
        row("paywall", blocker="paywalled (verified-no-OA-copy-found)"),
        row("../unsafe"),
        row("historical#ref44_cited", status="extracted"),
    ]
    paths = make_inputs(tmp_path / "selected", rows=rows)
    before = {r["source_id"]: r for r in read_csv(paths.queue)}
    calls = mock_pdf(monkeypatch, pdf_bytes())
    run(paths, all_dates=all_dates)
    after = {r["source_id"]: r for r in read_csv(paths.queue)}
    selected = {"selected", "older"} if all_dates else {"selected"}
    assert {
        r["source_id"] for r in after.values() if r["status"] == "acquired"
    } == selected | {"acquired"}
    assert len(calls) == len(selected)
    for sid in before.keys() - selected:
        assert after[sid] == before[sid]


@pytest.mark.parametrize("short_text", [False, True])
def test_ocr_marker_and_notes_keep_original_rule(tmp_path, monkeypatch, short_text):
    paths = make_inputs(
        tmp_path / "selected", rows=[row(note="", blocker="old blocker")]
    )
    mock_pdf(monkeypatch, pdf_bytes(long=not short_text))
    run(paths)
    (saved,) = read_csv(paths.queue)
    assert saved["blocker"] == (
        "needs_ocr (scanned PDF, no text layer)" if short_text else "old blocker"
    )
    assert ("NO TEXT LAYER" in saved["note"]) is short_text
    assert not saved["note"].startswith(";")


@pytest.mark.parametrize("library_matches", [False, True])
def test_existing_library_is_immutable_while_valid_cache_and_queue_hold_are_coordinated(
    tmp_path, monkeypatch, library_matches
):
    paths = make_inputs(tmp_path / "selected")
    body = pdf_bytes()
    library_pdf = paths.library / SUBDIR / "paper.pdf"
    library_pdf.write_bytes(
        body if library_matches else b"immutable previous library object"
    )
    library_pdf.chmod(0o640)
    before = file_state(library_pdf)
    mock_pdf(monkeypatch, body)
    run(paths)
    (saved,) = read_csv(paths.queue)
    assert (paths.corpus / "paper.pdf").read_bytes() == body
    assert (paths.corpus / "paper.meta.json").exists()
    assert file_state(library_pdf) == before
    if library_matches:
        assert saved["status"] == "acquired"
    else:
        assert saved["status"] == "pending" and saved["target_library_path"] == ""
        assert (
            saved["blocker"]
            == f"library copy held — Existing artifact differs: {library_pdf}; reconcile before replacement"
        )


def test_cached_rerun_is_no_network_no_rewrite(tmp_path, monkeypatch):
    paths = make_inputs(tmp_path / "selected")
    mock_pdf(monkeypatch, pdf_bytes())
    run(paths)
    before = selected_tree(paths)
    cache = paths.corpus / "paper.pdf"
    prior = file_state(cache)

    def no_network(*args, **kwargs):
        pytest.fail("Acquired rows must not be fetched again")

    monkeypatch.setattr(acquire.requests, "get", no_network)
    run(paths)
    assert selected_tree(paths) == before and file_state(cache) == prior


@pytest.mark.parametrize("malformed_sidecar", [False, True])
def test_held_original_cache_is_preserved_and_does_not_block_other_source(
    tmp_path, monkeypatch, malformed_sidecar
):
    paths = make_inputs(tmp_path / "selected", rows=[row("held"), row("fresh")])
    held, sidecar = seed_pair(paths, "held", pdf_bytes())
    if malformed_sidecar:
        sidecar.write_bytes(b"not valid JSON")
    else:
        held.write_bytes(pdf_bytes("Unrelated urban transit financing handbook"))
    before = {p.name: p.read_bytes() for p in (held, sidecar)}
    calls = mock_pdf(monkeypatch, pdf_bytes())
    run(paths)
    after = {r["source_id"]: r for r in read_csv(paths.queue)}
    assert (
        after["held"]["status"] == "pending" and after["fresh"]["status"] == "acquired"
    )
    assert {p.name: p.read_bytes() for p in (held, sidecar)} == before
    assert len(calls) == 1 and calls[0][0].endswith("/fresh.pdf")


def test_wrong_direct_pdf_can_fall_back_via_wayback_without_exposing_private_download(
    tmp_path, monkeypatch
):
    wrong_url, good_url = (
        "https://example.invalid/wrong.pdf",
        "https://example.invalid/good.pdf",
    )
    paths = make_inputs(tmp_path / "selected", rows=[row(url=wrong_url)])
    wayback = tmp_path / "wayback.json"
    wayback.write_text(json.dumps({"paper": good_url}), encoding="utf-8")
    good = pdf_bytes()
    calls = []

    def get(url, **kwargs):
        calls.append(url)
        assert not (paths.corpus / "paper.pdf").exists()
        assert read_csv(paths.queue)[0]["status"] == "pending"
        return response(
            good if url == good_url else pdf_bytes("Unrelated railway financing"),
            url=url,
        )

    monkeypatch.setattr(acquire.requests, "get", get)
    run(paths, wayback_path=wayback)
    assert calls == [wrong_url, good_url]
    assert read_csv(paths.queue)[0]["url"] == good_url
    assert (paths.corpus / "paper.pdf").read_bytes() == good


@pytest.mark.parametrize("route", ["unpaywall", "html_meta", "html_link"])
def test_actual_fallback_resolvers_preserve_source_route(tmp_path, monkeypatch, route):
    landing = (
        "https://doi.org/10.9999/fixture"
        if route == "unpaywall"
        else "https://example.invalid/landing"
    )
    pdf_url = "https://example.invalid/archive/paper.pdf"
    paths = make_inputs(
        tmp_path / "selected",
        rows=[
            row(
                url=landing,
                doi="10.9999/fixture",
                doi_verified="true" if route == "unpaywall" else "false",
            )
        ],
    )
    calls = []
    body = pdf_bytes()

    def get(url, **kwargs):
        calls.append((url, kwargs))
        if "api.unpaywall.org" in url:
            assert route == "unpaywall"
            return response(
                url=url,
                content_type="application/json",
                payload={
                    "best_oa_location": {"url_for_pdf": pdf_url},
                    "oa_locations": [{"url_for_pdf": pdf_url}],
                },
            )
        if url == pdf_url:
            return response(body, url=url)
        assert url == landing
        text = (
            "<html>No direct document</html>"
            if route == "unpaywall"
            else (
                '<meta name="citation_pdf_url" content="paper.pdf">'
                if route == "html_meta"
                else '<a href="paper.pdf">PDF</a>'
            )
        )
        return response(
            text.encode(),
            url="https://example.invalid/archive/landing",
            content_type="text/html",
            text=text,
        )

    monkeypatch.setattr(acquire.requests, "get", get)
    run(paths)
    assert read_csv(paths.queue)[0]["url"] == pdf_url
    assert (paths.library / SUBDIR / "paper.pdf").read_bytes() == body
    assert sum("api.unpaywall.org" in url for url, _ in calls) == (
        1 if route == "unpaywall" else 0
    )


@pytest.mark.parametrize("dry_run", [False, True])
def test_header_only_queue_has_no_side_effects(tmp_path, dry_run):
    paths = make_inputs(tmp_path / "selected", rows=[])
    before = selected_tree(paths)
    result = run(paths, dry_run=dry_run)
    assert not result.log and selected_tree(paths) == before
    assert not paths.corpus.exists()


def test_dry_run_performs_real_private_checks_without_selected_writes(
    tmp_path, monkeypatch
):
    paths = make_inputs(tmp_path / "selected")
    before = selected_tree(paths)
    calls = mock_pdf(monkeypatch, pdf_bytes())
    result = run(paths, dry_run=True)
    assert calls and result.log
    assert selected_tree(paths) == before and not paths.corpus.exists()


@pytest.mark.parametrize(
    "malformed",
    [
        "duplicate",
        "blank",
        "whitespace",
        "duplicate_header",
        "missing_header",
        "extra_cell",
        "missing_cell",
    ],
)
def test_whole_queue_validation_precedes_network_and_outputs(tmp_path, malformed):
    rows = (
        [row(), row()]
        if malformed == "duplicate"
        else [
            row(
                source_id=""
                if malformed == "blank"
                else "   "
                if malformed == "whitespace"
                else "paper"
            )
        ]
    )
    paths = make_inputs(tmp_path / "selected", rows=rows)
    raw = paths.queue.read_text(encoding="utf-8")
    if malformed == "duplicate_header":
        raw = raw.replace("source_id,nbs_id", "source_id,source_id", 1)
    elif malformed == "missing_header":
        raw = raw.replace("source_id,", "wrong_header,", 1)
    elif malformed == "extra_cell":
        raw = raw.rstrip("\n") + ",unheaded\n"
    elif malformed == "missing_cell":
        raw = raw.rsplit(",", 1)[0] + "\n"
    paths.queue.write_text(raw, encoding="utf-8")
    before = selected_tree(paths)
    with pytest.raises(ValueError):
        run(paths)
    assert selected_tree(paths) == before and not paths.corpus.exists()


@pytest.mark.parametrize(
    "alias",
    [
        "same_roots",
        "nested_corpus",
        "nested_library",
        "queue_in_corpus",
        "queue_in_library",
        "case_roots",
        "queue_symlink",
        "queue_hardlink",
        "corpus_symlink",
        "library_symlink",
        "artifact_symlink",
        "library_hardlink",
    ],
)
def test_selected_destinations_reject_aliases_and_redirected_writes_before_fetch(
    tmp_path, alias
):
    paths = make_inputs(tmp_path / "selected")
    if alias == "same_roots":
        paths = replace(paths, corpus=paths.library)
    elif alias == "nested_corpus":
        paths = replace(paths, corpus=paths.library / "cache")
    elif alias == "nested_library":
        paths = replace(paths, corpus=paths.library.parent)
    elif alias in ("queue_in_corpus", "queue_in_library"):
        root = paths.corpus if alias == "queue_in_corpus" else paths.library
        target = root / "queue.csv"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(paths.queue, target)
        paths = replace(paths, queue=target)
    elif alias == "case_roots":
        paths = replace(
            paths, corpus=paths.library.with_name(paths.library.name.upper())
        )
    elif alias in ("queue_symlink", "queue_hardlink"):
        target = paths.queue.with_name("queue-alias.csv")
        if alias == "queue_symlink":
            target.symlink_to(paths.queue)
        else:
            os.link(paths.queue, target)
        paths = replace(paths, queue=target)
    elif alias in ("corpus_symlink", "library_symlink"):
        target = tmp_path / "redirected"
        if alias == "corpus_symlink":
            actual = tmp_path / "real-corpus"
            actual.mkdir()
            target.symlink_to(actual, target_is_directory=True)
            paths = replace(paths, corpus=target)
        else:
            target.symlink_to(paths.library, target_is_directory=True)
            paths = replace(paths, library=target)
    elif alias == "artifact_symlink":
        paths.corpus.mkdir()
        target = tmp_path / "external.pdf"
        target.write_bytes(pdf_bytes())
        (paths.corpus / "paper.pdf").symlink_to(target)
    else:
        target = tmp_path / "external.pdf"
        target.write_bytes(pdf_bytes())
        os.link(target, paths.library / SUBDIR / "paper.pdf")
    before = selected_tree(paths)
    with pytest.raises((ValueError, OSError)):
        run(paths)
    assert selected_tree(paths) == before


@pytest.mark.parametrize("kind", ["queue", "cache", "library", "wayback"])
def test_snapshot_before_network_refuses_competing_writer_without_clobber(
    tmp_path, monkeypatch, kind
):
    paths = make_inputs(tmp_path / "selected")
    wayback = tmp_path / "wayback.json"
    wayback.write_text("{}", encoding="utf-8")
    body = pdf_bytes()
    competing = {}

    def get(url, **kwargs):
        if kind == "queue":
            write_csv(paths.queue, [row(note="Other writer's queue edit")])
        elif kind == "cache":
            seed_pair(paths, "paper", pdf_bytes(TITLE + "\nOther writer"), url=URL)
        elif kind == "library":
            (paths.library / SUBDIR / "paper.pdf").write_bytes(
                b"Other writer immutable copy"
            )
        else:
            wayback.write_text(
                '{"paper":"https://example.invalid/new.pdf"}', encoding="utf-8"
            )
        competing.update(selected_tree(paths))
        return response(body, url=url)

    monkeypatch.setattr(acquire.requests, "get", get)
    with pytest.raises((ValueError, publication.PublicationRecoveryError)):
        run(paths, wayback_path=wayback)
    assert selected_tree(paths) == competing


def test_wayback_change_between_read_and_snapshot_blocks_before_fetch(
    tmp_path, monkeypatch
):
    paths = make_inputs(tmp_path)
    wayback = tmp_path / "wayback.json"
    wayback.write_bytes(b"{}")
    before = selected_tree(paths)
    replacement = b'{"paper":"https://example.invalid/new.pdf"}'
    read_bytes = Path.read_bytes

    def racing_read(path):
        value = read_bytes(path)
        if path == wayback:
            path.write_bytes(replacement)
        return value

    calls = mock_pdf(monkeypatch, pdf_bytes())
    monkeypatch.setattr(Path, "read_bytes", racing_read)
    with pytest.raises(ValueError, match="Wayback input changed while reading"):
        run(paths, wayback_path=wayback)
    assert not calls
    assert selected_tree(paths) == before
    assert read_bytes(wayback) == replacement


def test_drift_in_unchanged_cached_input_still_blocks_whole_batch(
    tmp_path, monkeypatch
):
    paths = make_inputs(tmp_path / "selected", rows=[row("cached"), row("fresh")])
    cached, sidecar = seed_pair(paths, "cached", pdf_bytes())
    before = selected_tree(paths)
    competing_body = pdf_bytes("Competing writer replacement")

    def get(url, **kwargs):
        assert url.endswith("/fresh.pdf")
        cached.write_bytes(competing_body)
        return response(pdf_bytes(), url=url)

    monkeypatch.setattr(acquire.requests, "get", get)
    with pytest.raises((ValueError, publication.PublicationRecoveryError)):
        run(paths)
    before["corpus/cached.pdf"] = competing_body
    assert selected_tree(paths) == before
    assert sidecar.exists()


@pytest.mark.parametrize("target", ["cache_pdf", "cache_meta", "library_pdf", "queue"])
@pytest.mark.parametrize("phase", ["before", "after"])
def test_batch_install_failure_restores_queue_and_removes_only_owned_new_objects(
    tmp_path, monkeypatch, target, phase
):
    paths = make_inputs(
        tmp_path / "selected", rows=[row("cached"), row("alpha"), row("beta")]
    )
    body = pdf_bytes()
    existing = list(seed_pair(paths, "cached", body))
    library_cached = paths.library / SUBDIR / "cached.pdf"
    library_cached.write_bytes(body)
    existing.append(library_cached)
    before = selected_tree(paths)
    states = {p: file_state(p) for p in existing}
    targets = {
        "cache_pdf": paths.corpus / "alpha.pdf",
        "cache_meta": paths.corpus / "alpha.meta.json",
        "library_pdf": paths.library / SUBDIR / "alpha.pdf",
        "queue": paths.queue,
    }
    fail_path = targets[target]
    original_link, original_replace = publication.os.link, publication.os.replace
    failed = False

    def perform(original, source, destination, *args, **kwargs):
        nonlocal failed
        should_fail = Path(destination) == fail_path and not failed
        if should_fail and phase == "before":
            failed = True
            raise OSError("injected coordinated install failure")
        result = original(source, destination, *args, **kwargs)
        if should_fail:
            failed = True
            raise OSError("injected coordinated install failure")
        return result

    monkeypatch.setattr(
        publication.os,
        "link",
        lambda *args, **kwargs: perform(original_link, *args, **kwargs),
    )
    monkeypatch.setattr(
        publication.os,
        "replace",
        lambda *args, **kwargs: perform(original_replace, *args, **kwargs),
    )
    mock_pdf(monkeypatch, body)
    with pytest.raises(OSError, match="coordinated install failure"):
        run(paths)
    assert failed and selected_tree(paths) == before
    assert {p: file_state(p) for p in existing} == states


def test_private_queue_write_failure_publishes_nothing(tmp_path, monkeypatch, capsys):
    paths = make_inputs(tmp_path / "selected")
    before = selected_tree(paths)
    mock_pdf(monkeypatch, pdf_bytes())

    def fail_queue(path, data):
        assert Path(path) != paths.queue
        raise OSError("injected private queue serialization failure")

    with pytest.raises(OSError, match="private queue"):
        run(paths, write_queue=fail_queue)
    assert selected_tree(paths) == before and not paths.corpus.exists()
    assert not capsys.readouterr().out


def test_incomplete_batch_rollback_is_explicit_and_retains_recovery(
    tmp_path, monkeypatch
):
    paths = make_inputs(tmp_path / "selected")
    original_queue = paths.queue.read_bytes()
    original_replace, original_unlink = publication.os.replace, Path.unlink
    armed = False

    def fail_after_queue(source, destination):
        nonlocal armed
        original_replace(source, destination)
        if Path(destination) == paths.queue and not armed:
            armed = True
            raise OSError("injected queue failure")

    def refuse_owned_removal(path, *args, **kwargs):
        if armed and path == paths.corpus / "paper.pdf":
            raise OSError("injected rollback hold")
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(publication.os, "replace", fail_after_queue)
    monkeypatch.setattr(Path, "unlink", refuse_owned_removal)
    mock_pdf(monkeypatch, pdf_bytes())
    with pytest.raises(publication.PublicationRecoveryError) as caught:
        run(paths)
    assert caught.value.recovery_dir.is_dir()
    assert (caught.value.recovery_dir / "manifest.json").is_file()
    assert "rollback hold" in str(caught.value)
    assert paths.queue.read_bytes() == original_queue


def test_direct_cli_header_only_external_root_needs_no_caller_cwd_data(tmp_path):
    paths = make_inputs(tmp_path / "selected", rows=[], layout="canonical")
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    before = selected_tree(paths)
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            str(ROOT / "scripts/acquire-queue.py"),
            "--date",
            DATE,
            "--nbs",
            NBS,
            "--library-subdir",
            SUBDIR,
            "--root",
            str(paths.queue.parent.parent),
            "--corpus-dir",
            str(paths.corpus),
            "--library-dir",
            str(paths.library),
            "--library-prefix",
            "logical/library",
            "--dry-run",
        ],
        cwd=foreign,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert selected_tree(paths) == before and not paths.corpus.exists()
