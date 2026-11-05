"""Failure injection for staged derived artifacts, without touching source data."""

import json
from pathlib import Path
import shutil
import stat

import pytest

from nbs_ruralscan.schema_tools import publication
from nbs_ruralscan.schema_tools.build_paths import SchemaBuildPaths


@pytest.fixture
def setup(tmp_path, monkeypatch):
    paths = SchemaBuildPaths(tmp_path / "inputs/schema", tmp_path / "outputs")
    paths.schema.mkdir(parents=True)
    (paths.schema / "source.csv").write_text("name\nsource\n")
    names = [Path("schema/first.json"), Path("docs/nested/second.json")]
    assert paths.output_root is not None
    destinations = [paths.output_root / name for name in names]
    # Keep private recovery workspaces visible to these tests only.
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    mkdtemp = publication.tempfile.mkdtemp
    monkeypatch.setattr(
        publication.tempfile, "mkdtemp", lambda **kw: mkdtemp(dir=scratch, **kw)
    )

    def render(staged):
        for name in names:
            path = staged.output_root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('{"generation": "new"}\n')
        return []  # Publication verifies actual artifacts, not this changed list.

    return paths, destinations, render, scratch


def populate(destinations):
    for path in destinations:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('{"generation": "old"}\n')
        path.chmod(0o640)


def inventory(root):
    return {
        str(path.relative_to(root)): (
            path.read_bytes(),
            stat.S_IMODE(path.stat().st_mode),
            path.stat().st_mtime_ns,
        )
        if path.is_file()
        else "directory"
        for path in root.rglob("*")
    }


@pytest.mark.parametrize("existing", [False, True])
def test_complete_build_preserves_inputs_other_files_and_unchanged_outputs(
    setup, existing
):
    paths, destinations, render, scratch = setup
    if existing:
        populate(destinations)
        unrelated = paths.output_root / "do-not-touch.txt"
        unrelated.write_text("other owner")
    inputs_before = inventory(paths.source_root)
    assert publication.staged_publish(paths, destinations, render) == destinations
    assert inventory(paths.source_root) == inputs_before
    for path in destinations:
        assert json.loads(path.read_text()) == {"generation": "new"}
        assert stat.S_IMODE(path.stat().st_mode) == (0o640 if existing else 0o644)
    after = inventory(paths.output_root)
    assert publication.staged_publish(paths, destinations, render) == []
    assert inventory(paths.output_root) == after
    assert not list(scratch.iterdir())
    if existing:
        assert unrelated.read_text() == "other owner"


@pytest.mark.parametrize("existing", [False, True])
def test_late_compiler_failure_keeps_previous_output_or_absence(setup, existing):
    paths, destinations, render, scratch = setup
    if existing:
        populate(destinations)
    before = inventory(paths.output_root)

    def fail(staged):
        render(staged)
        raise RuntimeError("late compiler failure")

    with pytest.raises(RuntimeError, match="late compiler failure"):
        publication.staged_publish(paths, destinations, fail)
    assert inventory(paths.output_root) == before
    assert paths.output_root.exists() == existing
    assert not list(scratch.iterdir())


@pytest.mark.parametrize("existing", [False, True])
def test_failed_second_replace_rolls_back_bytes_modes_times_and_new_directories(
    setup, monkeypatch, existing
):
    paths, destinations, render, scratch = setup
    if existing:
        populate(destinations)
    before = inventory(paths.output_root)
    replace = publication.os.replace
    calls = []

    def fail_second(source, dest):
        # Even with a different staging filesystem, installation uses a sibling.
        assert Path(source).parent == Path(dest).parent
        calls.append(dest)
        if len(calls) == 2:
            raise OSError("injected publication failure")
        replace(source, dest)

    monkeypatch.setattr(publication.os, "replace", fail_second)
    with pytest.raises(OSError, match="injected publication failure"):
        publication.staged_publish(paths, destinations, render)
    assert inventory(paths.output_root) == before
    assert paths.output_root.exists() == existing
    assert not list(scratch.iterdir())


def test_rollback_failure_retains_manifest_and_original_bytes(setup, monkeypatch):
    paths, destinations, render, scratch = setup
    populate(destinations)
    replace = publication.os.replace
    count = 0

    def fail_after_first(source, dest):
        nonlocal count
        count += 1
        if count > 1:
            raise OSError("disk unavailable")
        replace(source, dest)

    monkeypatch.setattr(publication.os, "replace", fail_after_first)
    with pytest.raises(publication.PublicationRecoveryError) as caught:
        publication.staged_publish(paths, destinations, render)
    recovery = caught.value.recovery_dir
    assert recovery in list(scratch.iterdir())
    assert str(destinations[0]) in str(caught.value)
    manifest = json.loads((recovery / "manifest.json").read_text())
    assert manifest["output_root"] == str(paths.output_root)
    for name, entry in manifest["artifacts"].items():
        assert publication._digest(recovery / "artifacts" / name) == entry["sha256"]
        assert json.loads((recovery / "before" / name).read_text()) == {
            "generation": "old"
        }
    assert json.loads(destinations[0].read_text()) == {"generation": "new"}
    assert json.loads(destinations[1].read_text()) == {"generation": "old"}
    shutil.rmtree(recovery)


def test_interrupt_after_replace_before_return_restores_previous_files(
    setup, monkeypatch
):
    paths, destinations, render, scratch = setup
    populate(destinations)
    before = inventory(paths.output_root)
    replace = publication.os.replace
    interrupted = False

    def interrupt_after_replace(source, destination):
        nonlocal interrupted
        replace(source, destination)
        if not interrupted:
            interrupted = True
            raise KeyboardInterrupt("after replacement")

    monkeypatch.setattr(publication.os, "replace", interrupt_after_replace)
    with pytest.raises(KeyboardInterrupt, match="after replacement"):
        publication.staged_publish(paths, destinations, render)
    assert inventory(paths.output_root) == before
    assert not list(scratch.iterdir())


def test_cleanup_error_cannot_hide_incomplete_rollback(setup, monkeypatch):
    paths, destinations, render, scratch = setup
    populate(destinations)
    replace = publication.os.replace
    unlink = Path.unlink
    count = 0

    def fail_after_first(source, dest):
        nonlocal count
        count += 1
        if count > 1:
            raise OSError("disk unavailable")
        replace(source, dest)

    def refuse_cleanup(path, *args, **kwargs):
        if (
            path.name.startswith(".nbs-publish-")
            and path.parent == destinations[1].parent
        ):
            raise PermissionError("temporary cleanup refused")
        return unlink(path, *args, **kwargs)

    monkeypatch.setattr(publication.os, "replace", fail_after_first)
    monkeypatch.setattr(Path, "unlink", refuse_cleanup)
    with pytest.raises(publication.PublicationRecoveryError) as caught:
        publication.staged_publish(paths, destinations, render)
    assert str(caught.value.recovery_dir) in str(caught.value)
    assert "temporary cleanup refused" in "\n".join(caught.value.__notes__)
    assert (caught.value.recovery_dir / "before/schema/first.json").exists()


def test_output_drift_during_compilation_is_not_overwritten(setup):
    paths, destinations, render, scratch = setup
    populate(destinations)
    first = destinations[0].read_bytes()

    def competing_writer(staged):
        render(staged)
        destinations[1].write_text('{"generation": "other writer"}\n')

    with pytest.raises(ValueError, match="changed during compilation"):
        publication.staged_publish(paths, destinations, competing_writer)
    assert destinations[0].read_bytes() == first
    assert "other writer" in destinations[1].read_text()
    assert not list(scratch.iterdir())


def test_other_writer_change_during_install_is_preserved_with_recovery(
    setup, monkeypatch
):
    paths, destinations, render, scratch = setup
    populate(destinations)
    replace = publication.os.replace
    count = 0

    def competing_writer(source, dest):
        nonlocal count
        count += 1
        if count == 2:
            destinations[0].write_text('{"generation": "other writer"}\n')
            raise OSError("publication failed")
        replace(source, dest)

    monkeypatch.setattr(publication.os, "replace", competing_writer)
    with pytest.raises(
        publication.PublicationRecoveryError, match="not overwriting another writer"
    ) as caught:
        publication.staged_publish(paths, destinations, render)
    assert "other writer" in destinations[0].read_text()
    shutil.rmtree(caught.value.recovery_dir)


@pytest.mark.parametrize("defect", ["missing", "unexpected", "invalid_json", "symlink"])
def test_invalid_manifest_cannot_publish(setup, defect):
    paths, destinations, render, scratch = setup

    def bad_output(staged):
        render(staged)
        path = staged.schema_output / "first.json"
        if defect == "missing":
            path.unlink()
        elif defect == "unexpected":
            (staged.schema_output / "extra.json").write_text("[]\n")
        elif defect == "invalid_json":
            path.write_text("{")
        else:
            path.unlink()
            path.symlink_to(paths.schema / "source.csv")

    with pytest.raises(ValueError):
        publication.staged_publish(paths, destinations, bad_output)
    assert not paths.output_root.exists()
    assert not list(scratch.iterdir())


def test_preparation_failure_creates_no_published_files(setup, monkeypatch):
    paths, destinations, render, scratch = setup
    original = publication._replacement

    def fail_copy(source, destination, mode):
        if destination == destinations[1]:
            raise OSError("out of space")
        return original(source, destination, mode)

    monkeypatch.setattr(publication, "_replacement", fail_copy)
    with pytest.raises(OSError, match="out of space"):
        publication.staged_publish(paths, destinations, render)
    assert not paths.output_root.exists()
    assert not list(scratch.iterdir())


def test_absent_optional_output_stays_absent_and_repeat_is_noop(setup):
    paths, destinations, _, scratch = setup

    def render(staged):
        path = staged.schema_output / "first.json"
        path.parent.mkdir(parents=True)
        path.write_text("{}\n")
        return []

    assert publication.staged_publish(
        paths, destinations, render, optional_destinations=(destinations[1],)
    ) == [destinations[0]]
    assert not destinations[1].exists()
    before = inventory(paths.output_root)

    def noop(staged):
        return []

    assert (
        publication.staged_publish(
            paths, destinations, noop, optional_destinations=tuple(destinations)
        )
        == []
    )
    assert inventory(paths.output_root) == before
    assert not list(scratch.iterdir())


def test_existing_optional_output_cannot_be_deleted(setup):
    paths, destinations, render, scratch = setup
    populate(destinations)
    before = inventory(paths.output_root)

    def missing(staged):
        render(staged)
        (staged.docs_output / "nested/second.json").unlink()
        return []

    with pytest.raises(ValueError, match="missing="):
        publication.staged_publish(
            paths, destinations, missing, optional_destinations=tuple(destinations)
        )
    assert inventory(paths.output_root) == before
    assert not list(scratch.iterdir())


def test_optional_outside_allowlist_refused_before_render(setup):
    paths, destinations, _, scratch = setup
    with pytest.raises(ValueError, match="Optional destinations"):
        publication.staged_publish(
            paths,
            destinations,
            lambda _: pytest.fail("Must not render"),
            optional_destinations=(paths.output_root / "other.json",),
        )
    assert not list(scratch.iterdir())


def test_concurrent_creation_of_skipped_optional_output_refuses_publication(setup):
    paths, destinations, _, scratch = setup
    populate(destinations[:1])
    before = destinations[0].read_bytes()

    def render(staged):
        (staged.schema_output / "first.json").write_text("{}\n")
        destinations[1].parent.mkdir(parents=True)
        destinations[1].write_text('{"concurrent": true}\n')
        return []

    with pytest.raises(ValueError, match="changed during compilation"):
        publication.staged_publish(
            paths, destinations, render, optional_destinations=(destinations[1],)
        )
    assert destinations[0].read_bytes() == before
    assert json.loads(destinations[1].read_text()) == {"concurrent": True}
    assert not list(scratch.iterdir())
