"""Complete generations remain readable across retries, failure and process races."""

import hashlib
import json
import multiprocessing
import os
from unittest.mock import patch

import pytest

from nbs_ruralscan.recipe import release_store as store


def members(value):
    return {"inputs/config.json": value, "compiled/T4.csv": value + b"\n"}


def test_pins_survive_selection_and_identical_publication_is_a_noop(tmp_path):
    first = store.publish_release(tmp_path, members(b"one"))
    pointer = tmp_path / "current.json"
    pointer_before = pointer.stat()
    assert first.files == ("compiled/T4.csv", "inputs/config.json")
    manifest = tmp_path / "generations" / first.release_id / "manifest.json"
    assert hashlib.sha256(manifest.read_bytes()).hexdigest() == first.release_id
    reordered = dict(reversed(list(members(b"one").items())))
    repeat = store.publish_release(tmp_path, reordered)
    assert repeat.release_id == first.release_id
    assert (pointer.stat().st_ino, pointer.stat().st_mtime_ns) == (
        pointer_before.st_ino,
        pointer_before.st_mtime_ns,
    )
    second = store.publish_release(tmp_path, members(b"two"))
    assert second.release_id != first.release_id
    assert store.open_release(tmp_path).release_id == second.release_id
    assert first.read_bytes("compiled/T4.csv") == b"one\n"
    assert first.path_for("inputs/config.json").read_bytes() == b"one"
    assert (
        store.open_release(tmp_path, first.release_id).read_bytes("inputs/config.json")
        == b"one"
    )
    assert store.publish_release(tmp_path, reordered).release_id == first.release_id
    assert store.open_release(tmp_path).release_id == first.release_id
    assert second.read_bytes("compiled/T4.csv") == b"two\n"
    with pytest.raises(KeyError):
        first.read_bytes("../current.json")


@pytest.mark.parametrize(
    "name",
    [
        "",
        "../escape",
        "a/../b",
        "/absolute",
        "trailing/",
        "a//b",
        "./b",
        "C:/drive",
        "a\\b",
        "bad\0name",
        "NUL.csv",
        "file.",
        "dir/space ",
    ],
)
def test_unsafe_logical_name_is_rejected_before_writing(tmp_path, name):
    with pytest.raises(ValueError):
        store.publish_release(tmp_path / "store", {name: b""})
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    "paths",
    [
        ("dir", "dir/a"),
        ("T4.csv", "t4.csv"),
        ("Tables/T4.csv", "tables/T6.csv"),
        ("méthode.csv", "me\u0301thode.csv"),
    ],
)
def test_logical_file_and_directory_aliases_refused(tmp_path, paths):
    with pytest.raises(ValueError, match="Conflicting"):
        store.publish_release(tmp_path, dict.fromkeys(paths, b""))
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    "damage",
    [
        "missing",
        "extra-file",
        "extra-directory",
        "digest",
        "hardlink",
        "symlink",
        "manifest",
    ],
)
def test_damaged_generation_refused_by_reader_and_new_publisher(tmp_path, damage):
    root = tmp_path / "store"
    release = store.publish_release(root, members(b"test"))
    leaf = release.path_for("inputs/config.json")
    pointer = (root / "current.json").read_bytes()
    if damage == "missing":
        leaf.unlink()
    elif damage == "extra-file":
        leaf.with_name("other").write_text("not listed")
    elif damage == "extra-directory":
        leaf.with_name("empty_extra").mkdir()
    elif damage == "digest":
        leaf.write_bytes(b"oops")
    elif damage in {"symlink", "hardlink"}:
        outside = tmp_path / "outside"
        leaf.rename(outside)
        if damage == "symlink":
            leaf.symlink_to(outside)
        else:
            os.link(outside, leaf)
    else:
        (root / "generations" / release.release_id / "manifest.json").write_text("{}")
    for action in (
        lambda: store.open_release(root),
        lambda: store.publish_release(root, members(b"new")),
    ):
        with pytest.raises((ValueError, FileNotFoundError)):
            action()
    assert (root / "current.json").read_bytes() == pointer
    if damage in {"missing", "digest", "hardlink", "symlink"}:
        with pytest.raises((ValueError, FileNotFoundError)):
            release.read_bytes("inputs/config.json")


@pytest.mark.parametrize(
    "value",
    [
        b"garbage",
        b'{"format_version":2,"release_id":"new"}',
        b'{"format_version":1,"release_id":"../other"}',
        b'{"format_version":1,"release_id":"' + b"0" * 64 + b'"}\n',
    ],
)
def test_bad_pointer_cannot_be_followed_or_overwritten(tmp_path, value):
    store.publish_release(tmp_path, members(b"ready"))
    pointer = tmp_path / "current.json"
    pointer.write_bytes(value)
    with pytest.raises((ValueError, FileNotFoundError)):
        store.open_release(tmp_path)
    with pytest.raises((ValueError, FileNotFoundError)):
        store.publish_release(tmp_path, members(b"other"))
    assert pointer.read_bytes() == value


def test_unsupported_manifest_fails_even_with_matching_hash(tmp_path):
    pinned = store.publish_release(tmp_path, members(b"test"))
    generation = tmp_path / "generations" / pinned.release_id
    path = generation / "manifest.json"
    manifest = json.loads(path.read_bytes())
    manifest["format_version"] = 2
    raw = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    path.write_bytes(raw)
    new_id = hashlib.sha256(raw).hexdigest()
    generation.rename(generation.with_name(new_id))
    with pytest.raises(ValueError, match="version"):
        store.open_release(tmp_path, new_id)


def test_redirected_generation_parent_never_receives_files(tmp_path):
    root = tmp_path / "store"
    external = tmp_path / "other"
    root.mkdir()
    external.mkdir()
    (root / "generations").symlink_to(external, target_is_directory=True)
    with pytest.raises(ValueError, match="directory"):
        store.publish_release(root, members(b"release"))
    assert list(external.iterdir()) == []


def test_input_drift_before_selection_preserves_old_current_and_retry(tmp_path):
    old = store.publish_release(tmp_path, members(b"old"))
    checks = []

    def changed():
        checks.append("check")
        if len(checks) == 2:
            raise ValueError("input changed")

    with pytest.raises(ValueError, match="input changed"):
        store.publish_release(tmp_path, members(b"new"), verify_inputs=changed)
    assert store.open_release(tmp_path).release_id == old.release_id
    new = store.publish_release(tmp_path, members(b"new"))
    assert new.read_bytes("inputs/config.json") == b"new"
    assert old.read_bytes("inputs/config.json") == b"old"


@pytest.mark.parametrize("switched", [False, True])
def test_pointer_replacement_failure_has_unambiguous_retry(
    tmp_path, monkeypatch, switched
):
    old = store.publish_release(tmp_path, members(b"old"))
    write = store.atomic_write

    def fail(path, body):
        if switched:
            write(path, body)
        raise OSError("injected switch failure")

    with monkeypatch.context() as override:
        override.setattr(store, "atomic_write", fail)
        if switched:
            new = store.publish_release(tmp_path, members(b"new"))
            assert new.release_id == store.open_release(tmp_path).release_id
        else:
            with pytest.raises(OSError, match="switch failure"):
                store.publish_release(tmp_path, members(b"new"))
            assert store.open_release(tmp_path).release_id == old.release_id
    assert (
        store.publish_release(tmp_path, members(b"new")).read_bytes(
            "inputs/config.json"
        )
        == b"new"
    )


def _publish_and_wait(root, channel):
    def pause(_path, _body):
        channel.send("at pointer switch")
        channel.recv()

    with patch.object(store, "atomic_write", pause):
        store.publish_release(root, members(b"new"))


def test_interrupted_process_leaves_old_current_and_retry_releases_lock(tmp_path):
    old = store.publish_release(tmp_path, members(b"old"))
    ctx = multiprocessing.get_context("spawn")
    parent, child = ctx.Pipe()
    process = ctx.Process(target=_publish_and_wait, args=(tmp_path, child))
    process.start()
    child.close()
    try:
        assert parent.poll(15) and parent.recv() == "at pointer switch"
        assert store.open_release(tmp_path).release_id == old.release_id
    finally:
        process.terminate()
        process.join(15)
        parent.close()
    assert not process.is_alive()
    assert store.open_release(tmp_path).release_id == old.release_id
    new = store.publish_release(tmp_path, members(b"new"))
    assert new.read_bytes("inputs/config.json") == b"new"
    assert old.read_bytes("compiled/T4.csv") == b"old\n"


def _contend(root, value, barrier, results):
    barrier.wait(15)
    release = store.publish_release(root, members(value))
    results.put((release.release_id, release.read_bytes("inputs/config.json")))


def test_first_publish_process_race_with_matching_and_different_content(tmp_path):
    root = tmp_path / "new store"
    ctx = multiprocessing.get_context("spawn")
    barrier = ctx.Barrier(3)
    results = ctx.Queue()
    workers = [
        ctx.Process(target=_contend, args=(root, value, barrier, results))
        for value in (b"A", b"B", b"A")
    ]
    for worker in workers:
        worker.start()
    try:
        received = [results.get(timeout=20) for _ in workers]
        for worker in workers:
            worker.join(15)
            assert worker.exitcode == 0
    finally:
        for worker in workers:
            if worker.is_alive():
                worker.terminate()
                worker.join(10)
        results.close()
    ids = dict(received)
    assert sorted(ids.values()) == [b"A", b"B"]
    assert {p.name for p in (root / "generations").iterdir()} == set(ids)
    current = store.open_release(root)
    assert current.read_bytes("compiled/T4.csv") == ids[current.release_id] + b"\n"
    for release_id, value in ids.items():
        pinned = store.open_release(root, release_id)
        assert pinned.read_bytes("inputs/config.json") == value
        assert pinned.read_bytes("compiled/T4.csv") == value + b"\n"
