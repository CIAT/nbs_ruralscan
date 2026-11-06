"""Create-only publication never replaces immutable or competing output files."""

import json
from pathlib import Path
import shutil

import pytest

from nbs_ruralscan.schema_tools import publication
from nbs_ruralscan.schema_tools.build_paths import SchemaBuildPaths


def tree(root):
    return {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}


@pytest.fixture
def batch(tmp_path, monkeypatch):
    paths = SchemaBuildPaths(tmp_path / "inputs/schema", tmp_path / "outputs")
    paths.schema.mkdir(parents=True)
    (paths.schema / "input.csv").write_text("id\nsynthetic\n")
    assert paths.output_root is not None
    mutable = paths.output_root / "derived.json"
    immutable = paths.output_root / "library/source.json"
    queue = paths.output_root / "queue.csv"
    mutable.parent.mkdir(parents=True)
    mutable.write_text('{"generation":"old"}\n')
    queue.write_text("source_id,status\nsynthetic,pending\n")
    contents = {
        mutable: b'{"generation":"new"}\n',
        immutable: b'{"artifact":"synthetic immutable bytes"}\n',
        queue: b"source_id,status\nsynthetic,acquired\n",
    }
    scratch = tmp_path / "recovery"
    scratch.mkdir()
    original_mkdtemp = publication.tempfile.mkdtemp
    monkeypatch.setattr(
        publication.tempfile,
        "mkdtemp",
        lambda **kwargs: original_mkdtemp(dir=scratch, **kwargs),
    )

    def render(staged):
        assert staged.output_root is not None and paths.output_root is not None
        for destination, body in contents.items():
            output = staged.output_root / destination.relative_to(paths.output_root)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(body)
        return []

    return paths, [mutable, immutable, queue], render, contents, scratch


def publish(batch, **kwargs):
    paths, destinations, render, _, _ = batch
    return publication.staged_publish(
        paths,
        destinations,
        render,
        create_only_destinations=(destinations[1],),
        **kwargs,
    )


def test_new_immutable_file_uses_exclusive_sibling_link_and_queue_is_last(
    batch, monkeypatch
):
    paths, destinations, _, contents, scratch = batch
    original_link, original_replace = publication.os.link, publication.os.replace
    operations = []

    def link(source, destination):
        assert Path(source).parent == Path(destination).parent
        assert Path(source).name.startswith(".nbs-publish-")
        operations.append(("link", Path(destination)))
        return original_link(source, destination)

    def replace(source, destination):
        operations.append(("replace", Path(destination)))
        return original_replace(source, destination)

    monkeypatch.setattr(publication.os, "link", link)
    monkeypatch.setattr(publication.os, "replace", replace)
    assert publish(batch) == destinations
    assert operations == [
        ("replace", destinations[0]),
        ("link", destinations[1]),
        ("replace", destinations[2]),
    ]
    assert {p: p.read_bytes() for p in destinations} == contents
    assert destinations[1].stat().st_nlink == 1
    assert not list(paths.output_root.rglob(".nbs-publish-*"))
    assert not list(scratch.iterdir())


def test_identical_existing_immutable_file_is_noop_and_never_relinked(
    batch, monkeypatch
):
    paths, destinations, _, contents, scratch = batch
    immutable = destinations[1]
    immutable.parent.mkdir(parents=True)
    immutable.write_bytes(contents[immutable])
    immutable.chmod(0o440)
    before = (
        immutable.stat().st_ino,
        immutable.stat().st_mtime_ns,
        immutable.stat().st_mode,
    )
    monkeypatch.setattr(
        publication.os,
        "link",
        lambda *a, **kw: pytest.fail("identical file must not be linked"),
    )
    assert publish(batch) == [destinations[0], destinations[2]]
    assert before == (
        immutable.stat().st_ino,
        immutable.stat().st_mtime_ns,
        immutable.stat().st_mode,
    )
    after = tree(paths.output_root)
    assert publish(batch) == []
    assert tree(paths.output_root) == after
    assert not list(scratch.iterdir())


@pytest.mark.parametrize("dry_run", [False, True])
def test_existing_different_immutable_bytes_refuse_before_any_install(
    batch, monkeypatch, dry_run
):
    paths, destinations, _, _, scratch = batch
    immutable = destinations[1]
    immutable.parent.mkdir(parents=True)
    immutable.write_bytes(b'{"artifact":"prior immutable edition"}\n')
    before = tree(paths.output_root)
    monkeypatch.setattr(
        publication.os, "link", lambda *a, **kw: pytest.fail("must not link")
    )
    monkeypatch.setattr(
        publication.os, "replace", lambda *a, **kw: pytest.fail("must not replace")
    )
    with pytest.raises(ValueError, match="Create-only destination differs"):
        publish(batch, dry_run=dry_run)
    assert tree(paths.output_root) == before
    assert not list(scratch.iterdir())


def test_successful_create_only_dry_run_does_not_create_library_directory(batch):
    paths, destinations, _, _, scratch = batch
    before = tree(paths.output_root)
    assert publish(batch, dry_run=True) == destinations
    assert tree(paths.output_root) == before
    assert not destinations[1].parent.exists()
    assert not list(scratch.iterdir())


@pytest.mark.parametrize("point", ["before_link", "after_link", "after_unlink"])
@pytest.mark.parametrize("error_type", [OSError, KeyboardInterrupt])
def test_caught_link_or_unlink_interrupt_restores_other_files_and_removes_owned_links(
    batch, monkeypatch, point, error_type
):
    paths, destinations, _, _, scratch = batch
    immutable = destinations[1]
    original_link, original_unlink = publication.os.link, Path.unlink
    prepared = []
    failed = False

    def link(source, destination):
        nonlocal failed
        if Path(destination) != immutable:
            return original_link(source, destination)
        prepared.append(Path(source))
        if point == "before_link":
            failed = True
            raise error_type("injected immutable installation failure")
        original_link(source, destination)
        if point == "after_link":
            assert Path(source).stat().st_nlink == immutable.stat().st_nlink == 2
            failed = True
            raise error_type("injected immutable installation failure")

    def unlink(path, *args, **kwargs):
        nonlocal failed
        result = original_unlink(path, *args, **kwargs)
        if point == "after_unlink" and path in prepared and not failed:
            failed = True
            raise error_type("injected immutable installation failure")
        return result

    monkeypatch.setattr(publication.os, "link", link)
    monkeypatch.setattr(Path, "unlink", unlink)
    before = tree(paths.output_root)
    with pytest.raises(error_type, match="injected immutable installation failure"):
        publish(batch)
    assert failed
    assert tree(paths.output_root) == before
    assert not immutable.parent.exists()
    assert not list(paths.output_root.rglob(".nbs-publish-*"))
    assert not list(scratch.iterdir())


@pytest.mark.parametrize("after_queue_replace", [False, True])
def test_queue_failure_after_immutable_creation_rolls_back_whole_batch(
    batch, monkeypatch, after_queue_replace
):
    paths, destinations, _, _, scratch = batch
    original_replace = publication.os.replace
    failed = False

    def fail_queue(source, destination):
        nonlocal failed
        if Path(destination) == destinations[2] and not failed:
            assert destinations[1].stat().st_nlink == 1
            failed = True
            if after_queue_replace:
                original_replace(source, destination)
            raise OSError("injected queue persistence failure")
        return original_replace(source, destination)

    monkeypatch.setattr(publication.os, "replace", fail_queue)
    before = tree(paths.output_root)
    with pytest.raises(OSError, match="injected queue persistence failure"):
        publish(batch)
    assert failed and tree(paths.output_root) == before
    assert not destinations[1].exists()
    assert not list(paths.output_root.rglob(".nbs-publish-*"))
    assert not list(scratch.iterdir())


@pytest.mark.parametrize("when", ["before_exclusive_link", "during_queue_failure"])
def test_competing_immutable_destination_is_preserved_and_other_outputs_rollback(
    batch, monkeypatch, when
):
    paths, destinations, _, _, scratch = batch
    immutable, queue = destinations[1:]
    competing = b'{"artifact":"different writer"}\n'
    original_link, original_replace = publication.os.link, publication.os.replace
    attempted = False

    def link(source, destination):
        nonlocal attempted
        if Path(destination) == immutable and when == "before_exclusive_link":
            attempted = True
            immutable.write_bytes(competing)
        return original_link(source, destination)

    def replace(source, destination):
        nonlocal attempted
        if Path(destination) == queue and when == "during_queue_failure":
            attempted = True
            immutable.write_bytes(competing)
            raise OSError("queue failed after competing writer edit")
        return original_replace(source, destination)

    monkeypatch.setattr(publication.os, "link", link)
    monkeypatch.setattr(publication.os, "replace", replace)
    previous_mutable = {p: p.read_bytes() for p in (destinations[0], queue)}
    with pytest.raises(publication.PublicationRecoveryError) as failure:
        publish(batch)
    try:
        assert attempted and immutable.read_bytes() == competing
        assert {p: p.read_bytes() for p in previous_mutable} == previous_mutable
        assert str(immutable) in str(failure.value)
        assert (failure.value.recovery_dir / "manifest.json").exists()
        assert not list(paths.output_root.rglob(".nbs-publish-*"))
        assert list(scratch.iterdir()) == [failure.value.recovery_dir]
    finally:
        shutil.rmtree(failure.value.recovery_dir)


def test_immutable_rollback_failure_retains_recovery_and_restores_other_files(
    batch, monkeypatch
):
    paths, destinations, _, contents, scratch = batch
    immutable, queue = destinations[1:]
    original_replace, original_unlink = publication.os.replace, Path.unlink

    def fail_queue(source, destination):
        if Path(destination) == queue:
            raise OSError("injected queue failure")
        return original_replace(source, destination)

    def refuse_immutable_unlink(path, *args, **kwargs):
        if path == immutable:
            raise OSError("injected immutable rollback failure")
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(publication.os, "replace", fail_queue)
    monkeypatch.setattr(Path, "unlink", refuse_immutable_unlink)
    previous_mutable = {p: p.read_bytes() for p in (destinations[0], queue)}
    with pytest.raises(publication.PublicationRecoveryError) as failure:
        publish(batch)
    try:
        assert immutable.read_bytes() == contents[immutable]
        assert immutable.stat().st_nlink == 1
        assert {p: p.read_bytes() for p in previous_mutable} == previous_mutable
        recovery = failure.value.recovery_dir
        manifest = json.loads((recovery / "manifest.json").read_text())
        assert manifest["previous"]["library/source.json"] is None
        assert (recovery / "artifacts/library/source.json").read_bytes() == contents[
            immutable
        ]
        assert str(immutable) in str(failure.value)
        assert list(scratch.iterdir()) == [recovery]
        assert not list(paths.output_root.rglob(".nbs-publish-*"))
    finally:
        shutil.rmtree(failure.value.recovery_dir)


def test_unexpected_third_hardlink_is_not_treated_as_our_owned_pair(batch, monkeypatch):
    paths, destinations, _, contents, _ = batch
    immutable = destinations[1]
    competitor = paths.output_root / "other-owner.json"
    original_link = publication.os.link

    def link_then_share_and_interrupt(source, destination):
        original_link(source, destination)
        if Path(destination) == immutable:
            original_link(destination, competitor)
            raise OSError("interrupted with additional external hardlink")

    monkeypatch.setattr(publication.os, "link", link_then_share_and_interrupt)
    with pytest.raises(publication.PublicationRecoveryError) as failure:
        publish(batch)
    try:
        assert immutable.read_bytes() == competitor.read_bytes() == contents[immutable]
        assert immutable.stat().st_ino == competitor.stat().st_ino
        assert immutable.stat().st_nlink == 2
        assert str(immutable) in str(failure.value)
        assert not list(paths.output_root.rglob(".nbs-publish-*"))
    finally:
        shutil.rmtree(failure.value.recovery_dir)


def test_create_only_destinations_must_belong_to_exact_allowlist(batch):
    paths, destinations, render, _, scratch = batch
    before = tree(paths.output_root)
    with pytest.raises(ValueError, match="Create-only destinations must belong"):
        publication.staged_publish(
            paths,
            destinations,
            render,
            create_only_destinations=(destinations[1].with_name("outside.json"),),
        )
    assert tree(paths.output_root) == before
    assert not list(scratch.iterdir())
