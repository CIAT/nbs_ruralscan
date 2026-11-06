"""On-demand review hydration publishes only guarded, immutable cache outputs."""

import csv
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import threading
from types import SimpleNamespace
import urllib.request

import pytest

from nbs_ruralscan.ingest.source_publication import SourceSnapshot
from nbs_ruralscan.schema_tools import publication
from nbs_ruralscan.schema_tools import review_server as server


SID = "fixture"
URL = "https://github.com/example/repo/blob/1234567890/source.R"
RAW_URL = "https://raw.githubusercontent.com/example/repo/1234567890/source.R"


@pytest.fixture
def selected(tmp_path, monkeypatch):
    root = tmp_path / "selected"
    sources = root / "schema/registers/SRC_source_register.csv"
    sources.parent.mkdir(parents=True)
    with sources.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["source_id", "url", "library_path"])
        writer.writeheader()
        writer.writerow(
            dict(source_id=SID, url=URL, library_path="collection/fixture.pdf")
        )
    corpus = tmp_path / "independent-cache"
    library = tmp_path / "independent-library"
    source = library / "collection/fixture.pdf"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"%PDF-1.4 synthetic local fixture")
    monkeypatch.setattr(server, "ROOT", root)
    monkeypatch.setattr(server, "CACHE", corpus)
    monkeypatch.setattr(server, "_library_root", lambda: library)
    return SimpleNamespace(
        sources=sources, corpus=corpus, library=library, source=source
    )


def mock_fetch(monkeypatch, body=b"threshold = 4\n", *, status=200, action=None):
    calls = []

    class Response:
        def __init__(self):
            self.status = status

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self, limit):
            assert limit == 4_000_000
            if action:
                action()
            return body

    def fetch(request, timeout):
        calls.append((request.full_url, request.get_header("User-agent"), timeout))
        return Response()

    monkeypatch.setattr(urllib.request, "urlopen", fetch)
    return calls


def test_default_pdf_copy_preserves_source_and_register_bytes(selected):
    before = selected.sources.read_bytes(), selected.source.read_bytes()
    result = server._resolve_pdf(SID)
    assert result is not None
    assert result == selected.corpus / "fixture.pdf"
    assert result.read_bytes() == before[1]
    assert (selected.sources.read_bytes(), selected.source.read_bytes()) == before


@pytest.mark.parametrize("body", [b"threshold = 4\n", b"legacy \xff\xfe", b""])
def test_code_fetch_preserves_raw_bytes_and_transport_policy(
    selected, monkeypatch, body
):
    calls = mock_fetch(monkeypatch, body)
    result = server._ensure_code_snapshot(SID)
    assert result is not None
    assert result == selected.corpus / "fixture.txt"
    assert result.read_bytes() == body
    assert calls == [(RAW_URL, "nbs-ruralscan-review-server", 15)]


def test_explicit_paths_ignore_compiler_defaults(selected, tmp_path, monkeypatch):
    monkeypatch.setattr(server, "ROOT", tmp_path / "unrelated")
    monkeypatch.setattr(server, "CACHE", tmp_path / "poison-cache")
    monkeypatch.setattr(server, "_library_root", lambda: None)
    mock_fetch(monkeypatch)
    kwargs = dict(sources=selected.sources, corpus=selected.corpus)
    pdf = server._resolve_pdf(SID, library=selected.library, **kwargs)
    code = server._ensure_code_snapshot(SID, **kwargs)
    assert pdf is not None and pdf.is_file()
    assert code is not None and code.is_file()
    assert not server.CACHE.exists()


@pytest.mark.parametrize(
    "extensions,expected",
    [([".html", ".md"], ".html"), ([".txt", ".html", ".md"], ".txt"), ([".md"], ".md")],
)
def test_existing_code_precedence_skips_fetch(
    selected, monkeypatch, extensions, expected
):
    selected.corpus.mkdir()
    for extension in extensions:
        (selected.corpus / (SID + extension)).write_bytes(extension.encode())
    calls = mock_fetch(monkeypatch)
    assert server._ensure_code_snapshot(SID) == selected.corpus / (SID + expected)
    assert not calls


def test_existing_pdf_does_not_need_register_or_library(selected):
    selected.corpus.mkdir()
    cached = selected.corpus / "fixture.pdf"
    cached.write_bytes(b"existing raw bytes")
    selected.sources.unlink()
    selected.source.unlink()
    assert server._resolve_pdf(SID) == cached
    assert cached.read_bytes() == b"existing raw bytes"


@pytest.mark.parametrize(
    "function", [server._ensure_code_snapshot, server._resolve_pdf]
)
@pytest.mark.parametrize("sid", ["../outside", "/absolute", "bad/source"])
def test_unsafe_ids_return_missing_without_writes(selected, monkeypatch, function, sid):
    calls = mock_fetch(monkeypatch)
    assert function(sid) is None
    assert not selected.corpus.exists() and not calls


@pytest.mark.parametrize(
    "library_path", ["../outside.pdf", "/outside.pdf", r"..\outside.pdf"]
)
def test_library_escape_is_rejected(selected, library_path):
    selected.sources.write_text(
        "source_id,url,library_path\nfixture,," + library_path + "\n", encoding="utf-8"
    )
    assert server._resolve_pdf(SID) is None
    assert not selected.corpus.exists()


@pytest.mark.parametrize(
    "extension,function",
    [(".txt", server._ensure_code_snapshot), (".pdf", server._resolve_pdf)],
)
def test_redirected_cached_leaf_is_not_used(selected, tmp_path, extension, function):
    selected.corpus.mkdir()
    outside = tmp_path / "outside"
    outside.write_bytes(b"unchanged")
    (selected.corpus / (SID + extension)).symlink_to(outside)
    assert function(SID) is None
    assert outside.read_bytes() == b"unchanged"


def test_library_symlink_is_not_copied(selected, tmp_path):
    selected.source.unlink()
    outside = tmp_path / "outside.pdf"
    outside.write_bytes(b"outside")
    selected.source.symlink_to(outside)
    assert server._resolve_pdf(SID) is None
    assert not selected.corpus.exists()


def test_case_aliased_source_register_is_not_published(tmp_path, monkeypatch):
    source = tmp_path / "fixture.TXT"
    source.write_text(f"source_id,url\nfixture,{URL}\n", encoding="utf-8")
    if (tmp_path / "fixture.txt").exists():
        pytest.skip("Case-insensitive filesystem already sees the existing file")
    calls = mock_fetch(monkeypatch)
    assert server._ensure_code_snapshot(SID, sources=source, corpus=tmp_path) is None
    assert not calls and not (tmp_path / "fixture.txt").exists()


def test_changed_register_during_fetch_blocks_publication(selected, monkeypatch):
    changed = selected.sources.read_bytes() + b"other,,\n"
    mock_fetch(monkeypatch, action=lambda: selected.sources.write_bytes(changed))
    assert server._ensure_code_snapshot(SID) is None
    assert selected.sources.read_bytes() == changed
    assert not selected.corpus.exists()


def test_register_change_between_snapshot_and_read_is_rejected(selected, monkeypatch):
    original_read = Path.read_bytes
    reads = 0

    def read(path):
        nonlocal reads
        data = original_read(path)
        if path == selected.sources:
            reads += 1
            if reads == 1:
                path.write_bytes(data + b"other,,\n")
        return data

    monkeypatch.setattr(Path, "read_bytes", read)
    calls = mock_fetch(monkeypatch)
    assert server._ensure_code_snapshot(SID) is None
    assert not calls and not selected.corpus.exists()


def test_library_change_after_read_is_rejected(selected, monkeypatch):
    original_publish = SourceSnapshot.publish
    changed = b"competing library revision"

    def publish(snapshot, *args, **kwargs):
        selected.source.write_bytes(changed)
        return original_publish(snapshot, *args, **kwargs)

    monkeypatch.setattr(SourceSnapshot, "publish", publish)
    assert server._resolve_pdf(SID) is None
    assert selected.source.read_bytes() == changed
    assert not selected.corpus.exists()


@pytest.mark.parametrize("extension", [".txt", ".html", ".md"])
def test_competing_code_snapshot_is_preserved(selected, monkeypatch, extension):
    competitor = selected.corpus / (SID + extension)

    def competing():
        selected.corpus.mkdir()
        competitor.write_bytes(b"competing snapshot")

    mock_fetch(monkeypatch, action=competing)
    assert server._ensure_code_snapshot(SID) is None
    assert list(selected.corpus.iterdir()) == [competitor]
    assert competitor.read_bytes() == b"competing snapshot"


@pytest.mark.parametrize(
    "function,extension",
    [(server._resolve_pdf, ".pdf"), (server._ensure_code_snapshot, ".txt")],
)
def test_failed_exclusive_install_rolls_back_new_cache(
    selected, monkeypatch, function, extension
):
    mock_fetch(monkeypatch)
    original_link = publication.os.link

    def link(source, destination):
        original_link(source, destination)
        raise OSError("synthetic interruption after exclusive install")

    monkeypatch.setattr(publication.os, "link", link)
    assert function(SID) is None
    assert not (selected.corpus / (SID + extension)).exists()
    assert not selected.corpus.exists()


@pytest.mark.parametrize(
    "function", [server._resolve_pdf, server._ensure_code_snapshot]
)
def test_recovery_error_is_never_swallowed(selected, monkeypatch, function, tmp_path):
    mock_fetch(monkeypatch)
    error = publication.PublicationRecoveryError(tmp_path / "recovery", ["fixture"])

    def fail(*args, **kwargs):
        raise error

    monkeypatch.setattr(SourceSnapshot, "publish", fail)
    with pytest.raises(publication.PublicationRecoveryError) as caught:
        function(SID)
    assert caught.value is error


@pytest.mark.parametrize("status", [403, 404, 500])
def test_http_failure_returns_missing_without_cache(selected, monkeypatch, status):
    mock_fetch(monkeypatch, status=status)
    assert server._ensure_code_snapshot(SID) is None
    assert not selected.corpus.exists()


@pytest.mark.parametrize(
    "function,extension",
    [(server._resolve_pdf, ".pdf"), (server._ensure_code_snapshot, ".txt")],
)
def test_concurrent_same_source_preview_hydrates_once(
    selected, monkeypatch, function, extension
):
    calls = mock_fetch(monkeypatch)
    first_prepared = threading.Event()
    second_attempted = threading.Event()
    release_first = threading.Event()
    real_lock = server._HYDRATION_LOCK
    published = []
    original_publish = SourceSnapshot.publish

    class ObservedLock:
        def __enter__(self):
            if first_prepared.is_set():
                second_attempted.set()
            real_lock.acquire()

        def __exit__(self, *args):
            real_lock.release()

    def held_publish(snapshot, *args, **kwargs):
        published.append(snapshot.paths)
        first_prepared.set()
        assert release_first.wait(5), "test did not release the first hydration"
        return original_publish(snapshot, *args, **kwargs)

    monkeypatch.setattr(server, "_HYDRATION_LOCK", ObservedLock())
    monkeypatch.setattr(SourceSnapshot, "publish", held_publish)
    with ThreadPoolExecutor(max_workers=2) as workers:
        first = workers.submit(function, SID)
        try:
            assert first_prepared.wait(5)
            second = workers.submit(function, SID)
            assert second_attempted.wait(5)
        finally:
            release_first.set()
        target = selected.corpus / (SID + extension)
        assert first.result(timeout=5) == target
        assert second.result(timeout=5) == target
    assert len(published) == 1
    assert len(calls) == (1 if extension == ".txt" else 0)
    assert target.exists()


@pytest.mark.parametrize(
    "function", [server._resolve_pdf, server._ensure_code_snapshot]
)
@pytest.mark.parametrize("outcome", ["success", "missing", "recovery_error"])
def test_hydration_lock_released_after_every_outcome(
    selected, monkeypatch, function, outcome, tmp_path
):
    mock_fetch(monkeypatch)
    if outcome == "missing":
        selected.sources.unlink()
    elif outcome == "recovery_error":
        error = publication.PublicationRecoveryError(tmp_path / "recovery", ["fixture"])

        def fail(*args, **kwargs):
            raise error

        monkeypatch.setattr(SourceSnapshot, "publish", fail)
    with ThreadPoolExecutor(max_workers=1) as worker:
        future = worker.submit(function, SID)
        if outcome == "recovery_error":
            with pytest.raises(publication.PublicationRecoveryError):
                future.result(timeout=5)
        else:
            result = future.result(timeout=5)
            assert (result is not None) == (outcome == "success")
    acquired = server._HYDRATION_LOCK.acquire(blocking=False)
    assert acquired, "hydration lock remained owned by the worker"
    server._HYDRATION_LOCK.release()


def test_hydration_lock_is_reentrant():
    lock = server._HYDRATION_LOCK
    with lock:
        acquired = lock.acquire(blocking=False)
        assert acquired
        lock.release()
