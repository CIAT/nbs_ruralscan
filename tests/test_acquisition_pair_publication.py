"""Acquisition publishes artifact/provenance pairs with bounded recovery.

HTTP responses and PDFs are synthetic. Real body, metadata and wrapper title
checks run; injected filesystem failures exercise only temporary destinations.
"""

import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
from types import SimpleNamespace

import fitz
import pytest

from nbs_ruralscan.ingest.artifact_publication import PairSnapshot, publish_pair
from nbs_ruralscan.schema_tools import publication
from nbs_ruralscan.schema_tools.build_paths import SchemaBuildPaths


ROOT = Path(__file__).resolve().parents[1]
acquisition = importlib.import_module("nbs_ruralscan.ingest.acquire")
URL = "https://example.invalid/synthetic-source"
TITLE = "Synthetic riparian corridor infiltration and sediment retention"
CITATION = f"Synthetic fixture (2026). {TITLE}. Test publication."
KINDS = {
    "pdf": (".pdf", "application/pdf", b"%PDF-1.4 synthetic signature-only fixture\n"),
    "website": (".html", "text/html", b"<html>synthetic raw \xff body</html>\r\n"),
    "markdown": (".md", "text/markdown", b"# Synthetic raw \xfe Markdown\r\n"),
}


def tree(root):
    return {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def provenance(body, *, source_id="paper", url=URL, kind="pdf", commit_sha=None):
    return {
        "source_id": source_id,
        "url": url,
        "kind": kind,
        "sha1": hashlib.sha1(body).hexdigest(),
        "bytes": len(body),
        "commit_sha": commit_sha,
        "fetched_at": "2026-11-06T12:00:00+00:00",
        "http_status": 200,
        "content_type": KINDS[kind][1],
    }


def seed_pair(root, *, body=b"%PDF-1.4 synthetic old body\n", kind="pdf"):
    root.mkdir(parents=True, exist_ok=True)
    artifact, sidecar = root / ("paper" + KINDS[kind][0]), root / "paper.meta.json"
    artifact.write_bytes(body)
    sidecar.write_bytes(json.dumps(provenance(body, kind=kind), indent=2).encode())
    return artifact, sidecar


def response(body, kind="pdf", status=200):
    return SimpleNamespace(
        status_code=status, headers={"Content-Type": KINDS[kind][1]}, content=body
    )


def mock_http(monkeypatch, body, kind="pdf"):
    calls = []

    def get(url, **kwargs):
        calls.append((url, kwargs))
        return response(body, kind)

    monkeypatch.setattr(acquisition.requests, "get", get)
    return calls


def queue_script():
    spec = importlib.util.spec_from_file_location(
        "acquisition_pair_test_queue", ROOT / "scripts/acquire-queue.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def track_acquisition_workspaces(module, tmp_path, monkeypatch):
    """Select owned download workspaces without redirecting publication recovery."""
    original = module.tempfile.mkdtemp
    workspaces = []

    def mkdtemp(*args, **kwargs):
        owned = kwargs.get("prefix") == "ruralscan-acquisition-"
        if owned:
            kwargs["dir"] = tmp_path
        directory = original(*args, **kwargs)
        if owned:
            workspaces.append(Path(directory).resolve())
        return directory

    monkeypatch.setattr(module.tempfile, "mkdtemp", mkdtemp)
    return workspaces


def pdf_bytes(title=TITLE):
    with fitz.open() as doc:
        doc.new_page().insert_textbox(
            (40, 40, 550, 700), title + "\nSynthetic fixture, not project evidence."
        )
        return doc.tobytes()


@pytest.fixture(autouse=True)
def no_unconfigured_network(monkeypatch):
    def fail(*args, **kwargs):
        pytest.fail("Unconfigured HTTP request in isolated acquisition test")

    monkeypatch.setattr(acquisition.requests, "get", fail)


@pytest.mark.parametrize("kind", list(KINDS))
def test_exact_raw_bytes_relative_results_and_cached_noop(tmp_path, monkeypatch, kind):
    monkeypatch.chdir(tmp_path)
    suffix, _, body = KINDS[kind]
    calls = mock_http(monkeypatch, body, kind)
    relative = Path("selected-cache")
    result = acquisition.acquire(
        "paper", URL, kind=kind, corpus_dir=relative, commit_sha="synthetic-pin"
    )
    assert result.artifact_path == relative / ("paper" + suffix)
    assert result.meta_path == relative / "paper.meta.json"
    assert result.artifact_path is not None and result.meta_path is not None
    assert result.artifact_path.read_bytes() == body
    meta = json.loads(result.meta_path.read_text())
    assert meta["sha1"] == hashlib.sha1(body).hexdigest()
    assert meta["bytes"] == len(body) and meta["commit_sha"] == "synthetic-pin"
    before = tree(tmp_path)
    stats = {
        p: (p.stat().st_ino, p.stat().st_mtime_ns)
        for p in (result.artifact_path, result.meta_path)
    }
    repeated = acquisition.acquire(
        "paper", URL, kind=kind, corpus_dir=relative, commit_sha="synthetic-pin"
    )
    assert repeated.reason == "already_cached" and len(calls) == 1
    assert tree(tmp_path) == before
    assert stats == {p: (p.stat().st_ino, p.stat().st_mtime_ns) for p in stats}


def test_user_agent_fallback_and_explicit_overwrite_remain_supported(
    tmp_path, monkeypatch
):
    artifact, sidecar = seed_pair(tmp_path)
    body = b"%PDF-1.4 synthetic new body\n"
    calls = []

    def get(url, **kwargs):
        calls.append(kwargs)
        return response(body, status=403 if len(calls) == 1 else 200)

    monkeypatch.setattr(acquisition.requests, "get", get)
    result = acquisition.acquire(
        "paper", URL, kind="pdf", corpus_dir=tmp_path, overwrite=True
    )
    assert result.reason is None
    assert [call["headers"]["User-Agent"] for call in calls] == [
        acquisition._USER_AGENT,
        acquisition._FALLBACK_USER_AGENT,
    ]
    assert all(call["timeout"] == (10, 60) and call["stream"] is True for call in calls)
    assert artifact.read_bytes() == body
    assert json.loads(sidecar.read_text())["sha1"] == hashlib.sha1(body).hexdigest()


def test_other_kind_sidecar_hold_precedes_http_even_with_overwrite(tmp_path):
    sidecar = tmp_path / "paper.meta.json"
    sidecar.write_text('{"kind": "github_code", "commit": "historical"}')
    before = tree(tmp_path)
    with pytest.raises(acquisition.AcquireError, match="conflicting source kind"):
        acquisition.acquire(
            "paper", URL, kind="pdf", corpus_dir=tmp_path, overwrite=True
        )
    assert tree(tmp_path) == before


@pytest.mark.parametrize("existing", [False, True])
@pytest.mark.parametrize("failed_index", [0, 1])
@pytest.mark.parametrize("after_replace", [False, True])
def test_each_final_replacement_failure_restores_previous_pair_or_absence(
    tmp_path, monkeypatch, existing, failed_index, after_replace
):
    corpus = tmp_path / "corpus"
    if existing:
        seed_pair(corpus)
    destinations = (corpus / "paper.pdf", corpus / "paper.meta.json")
    mock_http(monkeypatch, b"%PDF-1.4 synthetic replacement body\n")
    original = publication.os.replace
    failed = False
    attempted = []

    def fail_once(source, destination):
        nonlocal failed
        selected = Path(destination)
        if selected in destinations:
            attempted.append(selected)
        if selected == destinations[failed_index] and not failed:
            failed = True
            if after_replace:
                original(source, destination)
            raise OSError("injected final pair replacement failure")
        return original(source, destination)

    monkeypatch.setattr(publication.os, "replace", fail_once)
    before = tree(tmp_path)
    with pytest.raises(OSError, match="injected final pair replacement failure"):
        acquisition.acquire(
            "paper", URL, kind="pdf", corpus_dir=corpus, overwrite=existing
        )
    assert attempted[: failed_index + 1] == list(destinations[: failed_index + 1])
    assert tree(tmp_path) == before
    assert not list(tmp_path.rglob(".nbs-publish-*"))


@pytest.mark.parametrize("existing", [False, True])
def test_drift_during_http_preserves_competing_pair(tmp_path, monkeypatch, existing):
    corpus = tmp_path / "corpus"
    if existing:
        seed_pair(corpus)
    observed = {}

    def get(url, **kwargs):
        seed_pair(corpus, body=b"%PDF-1.4 other writer's synthetic body\n")
        observed.update(tree(tmp_path))
        return response(b"%PDF-1.4 this download must not overwrite the other writer\n")

    monkeypatch.setattr(acquisition.requests, "get", get)
    with pytest.raises(ValueError, match="changed"):
        acquisition.acquire(
            "paper", URL, kind="pdf", corpus_dir=corpus, overwrite=existing
        )
    assert tree(tmp_path) == observed


@pytest.mark.parametrize(
    "alias",
    [
        "artifact_symlink",
        "sidecar_symlink",
        "parent_symlink",
        "artifact_hardlink",
        "sidecar_hardlink",
    ],
)
def test_destination_preflight_refuses_redirection_before_http(tmp_path, alias):
    corpus = tmp_path / "corpus"
    artifact, sidecar = seed_pair(corpus)
    if alias == "parent_symlink":
        redirect = tmp_path / "redirect"
        redirect.symlink_to(corpus, target_is_directory=True)
        corpus = redirect
    else:
        selected = artifact if alias.startswith("artifact") else sidecar
        peer = tmp_path / "independent-owner"
        if alias.endswith("symlink"):
            selected.rename(peer)
            selected.symlink_to(peer)
        else:
            os.link(selected, peer)
    before = tree(tmp_path)
    with pytest.raises(ValueError):
        acquisition.acquire("paper", URL, kind="pdf", corpus_dir=corpus, overwrite=True)
    assert tree(tmp_path) == before


@pytest.mark.parametrize("case_only", [False, True])
def test_snapshot_refuses_same_or_case_alias_destinations(tmp_path, case_only):
    artifact = tmp_path / "paper.pdf"
    sidecar = artifact.with_name(artifact.name.upper()) if case_only else artifact
    with pytest.raises(ValueError, match="alias"):
        PairSnapshot.capture(artifact, sidecar)
    assert tree(tmp_path) == {}


@pytest.mark.parametrize(
    "field", ["source_id", "url", "kind", "sha1", "bytes", "commit_sha"]
)
def test_pair_validator_checks_complete_provenance_before_publication(tmp_path, field):
    artifact, sidecar = seed_pair(tmp_path)
    snapshot = PairSnapshot.capture(artifact, sidecar)
    body = b"%PDF-1.4 proposed synthetic body\n"
    meta = provenance(body)
    meta[field] = len(body) + 1 if field == "bytes" else "incorrect-value"
    before = tree(tmp_path)
    with pytest.raises(ValueError, match="provenance mismatch"):
        publish_pair(
            snapshot,
            body,
            json.dumps(meta).encode(),
            source_id="paper",
            url=URL,
            kind="pdf",
        )
    assert tree(tmp_path) == before


@pytest.mark.parametrize(
    "defect",
    ["invalid_json", "wrong_artifact_name", "wrong_sidecar_name", "invalid_body"],
)
def test_pair_rejects_bad_serialization_identity_or_body(tmp_path, defect):
    artifact = tmp_path / (
        "different.pdf" if defect == "wrong_artifact_name" else "paper.pdf"
    )
    sidecar = tmp_path / (
        "different.meta.json" if defect == "wrong_sidecar_name" else "paper.meta.json"
    )
    body = b"HTML error response" if defect == "invalid_body" else KINDS["pdf"][2]
    metadata = (
        b"{" if defect == "invalid_json" else json.dumps(provenance(body)).encode()
    )
    with pytest.raises(ValueError):
        publish_pair(
            PairSnapshot.capture(artifact, sidecar),
            body,
            metadata,
            source_id="paper",
            url=URL,
            kind="pdf",
        )
    assert tree(tmp_path) == {}


def test_stage_corruption_is_caught_by_complete_pair_validator(tmp_path, monkeypatch):
    artifact, sidecar = seed_pair(tmp_path)
    snapshot = PairSnapshot.capture(artifact, sidecar)
    body = b"%PDF-1.4 synthetic proposed body\n"
    original = Path.write_bytes
    corrupted = False

    def corrupt_staged(path, data):
        nonlocal corrupted
        if path.name == sidecar.name and path != sidecar:
            corrupted = True
            data = b'{"source_id":"wrong staged identity"}'
        return original(path, data)

    monkeypatch.setattr(Path, "write_bytes", corrupt_staged)
    before = tree(tmp_path)
    with pytest.raises(ValueError, match="provenance mismatch"):
        publish_pair(
            snapshot,
            body,
            json.dumps(provenance(body)).encode(),
            source_id="paper",
            url=URL,
            kind="pdf",
        )
    assert corrupted and tree(tmp_path) == before


def test_pair_preserves_original_metadata_bytes_and_ignores_unrelated_files(tmp_path):
    artifact, sidecar = seed_pair(tmp_path)
    unrelated = tmp_path / "unrelated.txt"
    unrelated.write_bytes(b"another owner's data")
    body = KINDS["pdf"][2]
    meta = (
        json.dumps(
            {**provenance(body), "extra_provenance": "retained"}, indent=3
        ).encode()
        + b"\n\n"
    )
    publish_pair(
        PairSnapshot.capture(artifact, sidecar),
        body,
        meta,
        source_id="paper",
        url=URL,
        kind="pdf",
    )
    assert artifact.read_bytes() == body and sidecar.read_bytes() == meta
    assert unrelated.read_bytes() == b"another owner's data"


def test_incomplete_rollback_retains_recovery_and_original_pair(tmp_path, monkeypatch):
    artifact, sidecar = seed_pair(tmp_path / "corpus")
    before = {p.name: p.read_bytes() for p in (artifact, sidecar)}
    mock_http(monkeypatch, b"%PDF-1.4 replacement synthetic body\n")
    original = publication.os.replace
    attempts = 0

    def fail_after_first(source, destination):
        nonlocal attempts
        if Path(destination) in (artifact, sidecar):
            attempts += 1
            if attempts > 1:
                raise OSError("injected publication and rollback failure")
        return original(source, destination)

    monkeypatch.setattr(publication.os, "replace", fail_after_first)
    with pytest.raises(publication.PublicationRecoveryError) as failure:
        acquisition.acquire(
            "paper", URL, kind="pdf", corpus_dir=artifact.parent, overwrite=True
        )
    recovery = failure.value.recovery_dir
    try:
        assert recovery.is_dir() and (recovery / "manifest.json").is_file()
        assert str(artifact) in str(failure.value)
        for name, data in before.items():
            assert (recovery / "before" / name).read_bytes() == data
        assert artifact.read_bytes() != before[artifact.name]
        assert sidecar.read_bytes() == before[sidecar.name]
    finally:
        shutil.rmtree(recovery)


@pytest.mark.parametrize("valid_title", [False, True])
def test_queue_temporary_promotion_keeps_real_title_gate(
    tmp_path, monkeypatch, valid_title
):
    module = queue_script()
    body = pdf_bytes(
        TITLE if valid_title else "Unrelated urban transport investment mechanisms"
    )
    mock_http(monkeypatch, body)
    dest = tmp_path / "corpus/paper.pdf"
    holds = []
    assert module._acquire("paper", URL, dest, CITATION, holds) is valid_title
    if valid_title:
        assert dest.read_bytes() == body
        assert (
            json.loads(dest.with_suffix(".meta.json").read_text())["sha1"]
            == hashlib.sha1(body).hexdigest()
        )
        assert holds == []
    else:
        assert holds and "document identity" in holds[0]
        assert not dest.exists() and not dest.with_suffix(".meta.json").exists()


def test_queue_final_pair_failure_returns_false_with_no_partial_cache(
    tmp_path, monkeypatch
):
    module = queue_script()
    mock_http(monkeypatch, pdf_bytes())
    dest = tmp_path / "corpus/paper.pdf"
    sidecar = dest.with_suffix(".meta.json")
    original = publication.os.replace
    failed = False

    def fail_after_sidecar(source, destination):
        nonlocal failed
        original(source, destination)
        if Path(destination) == sidecar and not failed:
            failed = True
            raise OSError("injected queue promotion failure")

    monkeypatch.setattr(publication.os, "replace", fail_after_sidecar)
    assert module._acquire("paper", URL, dest, CITATION, []) is False
    assert failed and tree(tmp_path) == {}


def test_queue_orphan_sidecar_stays_held_before_network(tmp_path):
    module = queue_script()
    dest = tmp_path / "paper.pdf"
    sidecar = dest.with_suffix(".meta.json")
    sidecar.write_text('{"kind":"github_code","commit":"historical"}')
    before = tree(tmp_path)
    assert module._acquire("paper", URL, dest, CITATION, []) is False
    assert tree(tmp_path) == before


def test_queue_snapshot_predates_temporary_download(tmp_path, monkeypatch):
    module = queue_script()
    dest = tmp_path / "corpus/paper.pdf"
    competing = {}

    def get(url, **kwargs):
        seed_pair(dest.parent, body=pdf_bytes(TITLE + "\nOther writer copy"))
        competing[dest.name] = dest.read_bytes()
        competing["paper.meta.json"] = dest.with_suffix(".meta.json").read_bytes()
        return response(pdf_bytes())

    monkeypatch.setattr(acquisition.requests, "get", get)
    assert module._acquire("paper", URL, dest, CITATION, []) is False
    assert dest.read_bytes() == competing[dest.name]
    assert dest.with_suffix(".meta.json").read_bytes() == competing["paper.meta.json"]


def test_queue_cached_success_rechecks_outer_snapshot_after_title_check(
    tmp_path, monkeypatch
):
    module = queue_script()
    dest, sidecar = seed_pair(tmp_path / "corpus", body=pdf_bytes())
    real_title_check = module.pdf_title_error
    competing = {}

    def checked_then_replaced(path, citation):
        problem = real_title_check(path, citation)
        assert problem is None
        seed_pair(
            dest.parent,
            body=pdf_bytes("Unrelated urban transport investment mechanisms"),
        )
        competing.update({p.name: p.read_bytes() for p in (dest, sidecar)})
        return problem

    monkeypatch.setattr(module, "pdf_title_error", checked_then_replaced)
    assert module._acquire("paper", URL, dest, CITATION, []) is False
    assert {p.name: p.read_bytes() for p in (dest, sidecar)} == competing
    assert real_title_check(dest, CITATION) is not None


def test_queue_propagates_incomplete_recovery_instead_of_download_miss(
    tmp_path, monkeypatch
):
    module = queue_script()
    workspaces = track_acquisition_workspaces(module, tmp_path, monkeypatch)
    body = pdf_bytes()
    mock_http(monkeypatch, body)
    dest = tmp_path / "corpus/paper.pdf"
    sidecar = dest.with_suffix(".meta.json")
    original_replace, original_unlink = publication.os.replace, Path.unlink

    def refuse_sidecar(source, destination):
        if Path(destination) == sidecar:
            raise OSError("injected final sidecar failure")
        return original_replace(source, destination)

    def refuse_rollback(path, *args, **kwargs):
        if path == dest:
            raise OSError("injected rollback deletion failure")
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(publication.os, "replace", refuse_sidecar)
    monkeypatch.setattr(Path, "unlink", refuse_rollback)
    with pytest.raises(publication.PublicationRecoveryError) as failure:
        module._acquire("paper", URL, dest, CITATION, [])
    recovery = failure.value.recovery_dir
    try:
        assert recovery.is_dir() and (recovery / "manifest.json").is_file()
        assert dest.read_bytes() == body and not sidecar.exists()
        assert str(dest) in str(failure.value)
    finally:
        shutil.rmtree(recovery)
        for workspace in workspaces:
            shutil.rmtree(workspace)


def test_inner_recovery_error_survives_cleanup_failure_without_cleanup_attempt(
    tmp_path, monkeypatch
):
    module = queue_script()
    workspaces = track_acquisition_workspaces(module, tmp_path, monkeypatch)
    body = pdf_bytes()
    mock_http(monkeypatch, body)
    dest = tmp_path / "corpus/paper.pdf"
    original_acquire = module.acquire
    original_replace, original_unlink = publication.os.replace, Path.unlink
    original_rmtree = module.shutil.rmtree
    inner_errors, cleanup_attempts = [], []

    def capture_inner_failure(*args, **kwargs):
        try:
            return original_acquire(*args, **kwargs)
        except publication.PublicationRecoveryError as exc:
            inner_errors.append(exc)
            raise

    def fail_inner_sidecar(source, destination):
        path = Path(destination)
        if path.parent in workspaces and path.name == "paper.meta.json":
            raise OSError("injected inner sidecar publication failure")
        return original_replace(source, destination)

    def fail_inner_rollback(path, *args, **kwargs):
        if path.parent in workspaces and path.name == "paper.pdf":
            raise OSError("injected inner rollback failure")
        return original_unlink(path, *args, **kwargs)

    def cleanup_would_fail(path, *args, **kwargs):
        if Path(path).resolve() in workspaces:
            cleanup_attempts.append(Path(path))
            raise OSError("injected acquisition workspace cleanup failure")
        return original_rmtree(path, *args, **kwargs)

    monkeypatch.setattr(module, "acquire", capture_inner_failure)
    monkeypatch.setattr(publication.os, "replace", fail_inner_sidecar)
    monkeypatch.setattr(Path, "unlink", fail_inner_rollback)
    monkeypatch.setattr(module.shutil, "rmtree", cleanup_would_fail)
    with pytest.raises(publication.PublicationRecoveryError) as failure:
        module._acquire("paper", URL, dest, CITATION, [])
    recovery = failure.value.recovery_dir
    try:
        assert len(inner_errors) == 1 and failure.value is inner_errors[0]
        assert cleanup_attempts == []
        assert len(workspaces) == 1 and workspaces[0].is_dir()
        assert (workspaces[0] / "paper.pdf").read_bytes() == body
        assert (recovery / "manifest.json").exists()
        assert str(workspaces[0]) in "\n".join(failure.value.__notes__)
        assert not dest.exists() and not dest.with_suffix(".meta.json").exists()
    finally:
        original_rmtree(recovery)
        for workspace in workspaces:
            original_rmtree(workspace)


def test_normal_acquisition_cleanup_failure_is_visible_and_retains_workspace(
    tmp_path, monkeypatch
):
    module = queue_script()
    workspaces = track_acquisition_workspaces(module, tmp_path, monkeypatch)
    body = pdf_bytes()
    mock_http(monkeypatch, body)
    dest = tmp_path / "corpus/paper.pdf"
    original_rmtree = module.shutil.rmtree
    cleanup_attempts = []

    def refuse_owned_cleanup(path, *args, **kwargs):
        if Path(path).resolve() in workspaces:
            cleanup_attempts.append(Path(path))
            raise OSError("injected normal workspace cleanup failure")
        return original_rmtree(path, *args, **kwargs)

    monkeypatch.setattr(module.shutil, "rmtree", refuse_owned_cleanup)
    with pytest.raises(
        publication.PublicationRecoveryError,
        match="Temporary acquisition cleanup failed",
    ) as failure:
        module._acquire("paper", URL, dest, CITATION, [])
    try:
        assert len(workspaces) == 1 and workspaces[0].is_dir()
        assert cleanup_attempts == workspaces
        assert failure.value.recovery_dir == workspaces[0]
        assert dest.read_bytes() == (workspaces[0] / "paper.pdf").read_bytes() == body
        assert (
            dest.with_suffix(".meta.json").read_bytes()
            == (workspaces[0] / "paper.meta.json").read_bytes()
        )
    finally:
        for workspace in workspaces:
            original_rmtree(workspace)


def staged_fixture(tmp_path, name, content):
    paths = SchemaBuildPaths(tmp_path / "inputs/schema", tmp_path / "outputs")
    paths.schema.mkdir(parents=True)
    assert paths.output_root is not None
    destination = paths.output_root / name

    def render(staged):
        assert staged.output_root is not None
        (staged.output_root / name).write_bytes(content)
        return []

    return paths, destination, render


@pytest.mark.parametrize("explicit_validator", [False, True])
def test_shared_publisher_binary_requires_explicit_allowlisted_validator(
    tmp_path, explicit_validator
):
    body = KINDS["pdf"][2]
    paths, destination, render = staged_fixture(tmp_path, "fixture.pdf", body)
    seen = []

    def validate(path):
        assert path.read_bytes() == body
        seen.append(path)

    if explicit_validator:
        assert publication.staged_publish(
            paths, [destination], render, artifact_validators={destination: validate}
        ) == [destination]
        assert len(seen) == 1 and destination.read_bytes() == body
    else:
        with pytest.raises(ValueError, match="Unsupported generated artifact"):
            publication.staged_publish(paths, [destination], render)
        assert not destination.exists()


@pytest.mark.parametrize(
    "name,content", [("fixture.json", b"{"), ("fixture.csv", b"name,value\nonly_one\n")]
)
def test_custom_validator_cannot_bypass_standard_json_or_csv_validation(
    tmp_path, name, content
):
    paths, destination, render = staged_fixture(tmp_path, name, content)
    with pytest.raises(ValueError):
        publication.staged_publish(
            paths,
            [destination],
            render,
            artifact_validators={destination: lambda path: None},
        )
    assert not destination.exists()


def test_custom_validator_cannot_expand_publication_destinations(tmp_path):
    paths, destination, render = staged_fixture(
        tmp_path, "fixture.pdf", KINDS["pdf"][2]
    )
    with pytest.raises(ValueError):
        publication.staged_publish(
            paths,
            [destination],
            render,
            artifact_validators={destination.with_name("other.pdf"): lambda path: None},
        )
    assert not destination.exists()


def test_cli_uses_explicit_corpus_from_foreign_cwd(tmp_path, monkeypatch, capsys):
    foreign = tmp_path / "foreign-cwd"
    foreign.mkdir()
    corpus = tmp_path / "selected-corpus"
    body = KINDS["website"][2]
    mock_http(monkeypatch, body, "website")
    monkeypatch.chdir(foreign)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "acquire",
            "paper",
            URL,
            "--kind",
            "website",
            "--corpus-dir",
            str(corpus),
            "--commit-sha",
            "synthetic-pin",
        ],
    )
    acquisition.main()
    assert "fetched" in capsys.readouterr().out
    assert (corpus / "paper.html").read_bytes() == body
    assert (
        json.loads((corpus / "paper.meta.json").read_text())["commit_sha"]
        == "synthetic-pin"
    )
    assert not list(foreign.iterdir())
