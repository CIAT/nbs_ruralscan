"""Stage an allowlisted file set, then install with recoverable file rollback.

Use stable inputs and one writer per output root. Individual replacements are
atomic; readers can still see mixed generations during installation. This is
not a crash-safe transaction or a lock shared with the review server.
"""

from collections.abc import Callable, Mapping
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile

from nbs_ruralscan.schema_tools.build_paths import SchemaBuildPaths


class PublicationRecoveryError(RuntimeError):
    """Incomplete rollback or cleanup needs operator attention."""

    def __init__(self, recovery_dir: Path, failures: list[str]):
        self.recovery_dir = recovery_dir
        super().__init__(
            f"Publication recovery required. Keep recovery copies at {recovery_dir}. "
            "Stop writers and reconcile these paths before rebuilding:\n"
            + "\n".join(failures)
        )


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _state(path: Path) -> tuple | None:
    if not path.exists():
        return None
    info = path.stat()
    return (
        _digest(path),
        info.st_size,
        info.st_mode,
        info.st_mtime_ns,
        info.st_dev,
        info.st_ino,
    )


def _manifest(
    root: Path,
    names: list[Path],
    optional: set[Path],
    markdown: frozenset[Path] = frozenset(),
    artifact_validators: Mapping[Path, Callable[[Path], None]] | None = None,
) -> dict[str, dict]:
    artifact_validators = artifact_validators or {}
    entries = list(root.rglob("*"))
    if any(path.is_symlink() for path in entries):
        raise ValueError("Staged output contains a symlink")
    found = {path.relative_to(root) for path in entries if path.is_file()}
    required = set(names) - optional
    if not required.issubset(found) or not found.issubset(names):
        raise ValueError(
            "Staged artifact set changed: "
            f"missing={sorted(map(str, required - found))}, "
            f"unexpected={sorted(map(str, found - set(names)))}"
        )
    result = {}
    for name in names:
        if name not in found:
            continue
        path = root / name
        if path.stat().st_nlink != 1:
            raise ValueError(f"Staged artifact is not independent: {name}")
        if path.suffix == ".json":
            json.loads(path.read_text(encoding="utf-8"))
        elif path.suffix == ".csv":
            with path.open(newline="", encoding="utf-8") as stream:
                rows = csv.reader(stream, strict=True)
                header = next(rows, [])
                if not header or any(len(row) != len(header) for row in rows):
                    raise ValueError(f"Invalid staged CSV: {name}")
        elif name in markdown and path.suffix == ".md":
            path.read_text(encoding="utf-8")  # Strict text decoding; no execution.
        elif name not in artifact_validators:
            raise ValueError(f"Unsupported generated artifact: {name}")
        if name in artifact_validators:
            artifact_validators[name](path)
        result[str(name)] = {"sha256": _digest(path), "size": path.stat().st_size}
    return result


def _make_parents(parent: Path, created: list[Path]) -> None:
    missing = []
    while not parent.exists():
        missing.append(parent)
        parent = parent.parent
    for path in reversed(missing):
        path.mkdir()
        created.append(path)


def _replacement(source: Path, destination: Path, mode: int) -> Path:
    """Copy onto the destination filesystem before using os.replace."""
    fd, name = tempfile.mkstemp(prefix=".nbs-publish-", dir=destination.parent)
    os.close(fd)
    temp = Path(name)
    try:
        shutil.copy2(source, temp)
        temp.chmod(mode)
        if _digest(temp) != _digest(source):
            raise ValueError(f"Publication copy differs: {destination}")
        return temp
    except BaseException:
        temp.unlink(missing_ok=True)
        raise


def staged_publish(
    paths: SchemaBuildPaths,
    destinations: list[Path],
    render: Callable[[SchemaBuildPaths], list[Path]],
    *,
    optional_destinations: tuple[Path, ...] = (),
    create_only_destinations: tuple[Path, ...] = (),
    markdown_destinations: tuple[Path, ...] = (),
    artifact_validators: Mapping[Path, Callable[[Path], None]] | None = None,
    dry_run: bool = False,
    verify_inputs: Callable[[], None] | None = None,
) -> list[Path]:
    """Render all artifacts before touching outputs; keep recovery on rollback failure.

    The frozen artifact list is the allowlist, not the renderer's changed list.
    Existing bytes seed history and stable timestamps. Unrelated files survive.
    Optional destinations may stay absent only when absent before staging; this
    never permits deleting an existing file. All allowed paths are drift-checked.
    Markdown is accepted only for explicitly named destinations. A dry run renders
    and validates the same staged set, then returns changes without installation.
    Other artifact formats require a named, read-only validator for each allowed
    destination. Validators add checks; they never bypass CSV/JSON validation.
    Create-only destinations accept identical existing bytes, refuse changes, and
    publish new files exclusively without replacing a competing writer's file.
    Optional verify_inputs checks read-only dependencies after dry-run validation,
    just before installation, and after installation while rollback is available.
    """
    paths.preflight(destinations)
    output = paths.output_root or paths.source_root
    names = [path.relative_to(output) for path in destinations]
    if len(set(names)) != len(names):
        raise ValueError("Duplicate generated destinations")
    if not set(optional_destinations).issubset(destinations):
        raise ValueError(
            "Optional destinations must belong to the publication allowlist"
        )
    if not set(create_only_destinations).issubset(destinations):
        raise ValueError(
            "Create-only destinations must belong to the publication allowlist"
        )
    create_only = frozenset(
        path.relative_to(output) for path in create_only_destinations
    )
    if not set(markdown_destinations).issubset(destinations) or any(
        p.suffix != ".md" for p in markdown_destinations
    ):
        raise ValueError(
            "Markdown destinations must be named .md files in the publication allowlist"
        )
    markdown = frozenset(p.relative_to(output) for p in markdown_destinations)
    validators = dict(artifact_validators or {})
    if not set(validators).issubset(destinations) or any(
        not callable(validate) for validate in validators.values()
    ):
        raise ValueError(
            "Artifact validators must name allowed destinations and be callable"
        )
    validators = {
        path.relative_to(output): validate for path, validate in validators.items()
    }
    before = {name: _state(output / name) for name in names}
    optional = {
        path.relative_to(output)
        for path in optional_destinations
        if before[path.relative_to(output)] is None
    }
    workspace = Path(tempfile.mkdtemp(prefix="ruralscan-publication-"))
    stage, backups = workspace / "artifacts", workspace / "before"
    stage.mkdir()
    created: list[Path] = []
    prepared: dict[Path, Path] = {}
    installed: dict[Path, tuple | None] = {}
    retain = False
    try:
        for name in names:
            previous = before[name]
            if previous is not None:
                backup, staged = backups / name, stage / name
                backup.parent.mkdir(parents=True, exist_ok=True)
                staged.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(output / name, backup)
                shutil.copy2(backup, staged)
                if name in create_only:
                    # Immutable inputs may be read-only; only this private copy
                    # needs to be writable while rendering a comparison.
                    staged.chmod(stat.S_IMODE(previous[2]) | stat.S_IWUSR)
                if (
                    _state(output / name) != before[name]
                    or _digest(backup) != previous[0]
                ):
                    raise ValueError(f"Output changed while staging: {output / name}")
        render(SchemaBuildPaths(paths.schema, stage, paths.corpus))
        manifest = _manifest(stage, names, optional, markdown, validators)
        (workspace / "manifest.json").write_text(
            json.dumps(
                {
                    "output_root": str(output),
                    "artifacts": manifest,
                    "previous": {str(name): state for name, state in before.items()},
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        paths.preflight(destinations)
        for name in names:
            if _state(output / name) != before[name]:
                raise ValueError(f"Output changed during compilation: {output / name}")
        changed = [
            name
            for name, previous in before.items()
            if str(name) in manifest
            and (previous is None or previous[0] != manifest[str(name)]["sha256"])
        ]
        for name in changed:
            if name in create_only and before[name] is not None:
                raise ValueError(f"Create-only destination differs: {output / name}")
        if dry_run:
            if verify_inputs is not None:
                verify_inputs()
            return [output / name for name in changed]
        # Prepare every replacement before installing any file. These temporary
        # files live beside their destination, even when output spans mounts.
        for name in changed:
            destination = output / name
            _make_parents(destination.parent, created)
            previous = before[name]
            mode = stat.S_IMODE(previous[2]) if previous is not None else 0o644
            prepared[name] = _replacement(stage / name, destination, mode)
            if _digest(prepared[name]) != manifest[str(name)]["sha256"]:
                raise ValueError(f"Staged artifact changed: {name}")
        paths.preflight(destinations)
        for name in names:
            if _state(output / name) != before[name]:
                raise ValueError(f"Output changed before installation: {output / name}")
        if verify_inputs is not None:
            verify_inputs()
        for name in changed:
            destination = output / name
            paths.preflight([destination])
            if _state(destination) != before[name]:
                raise ValueError(f"Output changed during installation: {destination}")
            replacement_state = _state(prepared[name])
            # Register the attempt before the syscall: an interrupt can arrive
            # after replacement succeeds but before Python bookkeeping resumes.
            installed[name] = replacement_state
            if name in create_only:
                os.link(prepared[name], destination)
                prepared[name].unlink()
            else:
                os.replace(prepared[name], destination)
        if changed and verify_inputs is not None:
            verify_inputs()
            paths.preflight(destinations)
            for name in names:
                if _state(output / name) != installed.get(name, before[name]):
                    raise ValueError(
                        f"Output changed during installation: {output / name}"
                    )
        return [output / name for name in changed]
    except BaseException as error:
        failures = []
        for name, installed_state in reversed(list(installed.items())):
            destination = output / name
            try:
                if name in create_only:
                    temp = prepared[name]
                    # A caught failure can follow a successful link before its
                    # temporary name is removed. Release only our proven link;
                    # then the normal independent-file preflight remains strict.
                    if (
                        installed_state is not None
                        and destination.absolute() == destination.resolve()
                        and temp.absolute() == temp.resolve()
                        and _state(destination) == installed_state
                        and _state(temp) == installed_state
                        and destination.stat().st_nlink == 2
                        and temp.stat().st_nlink == 2
                    ):
                        temp.unlink()
                paths.preflight([destination])
                current = _state(destination)
                if current == before[name]:
                    continue  # The attempted replacement never took effect.
                if current != installed_state:
                    raise ValueError(
                        "changed after installation; not overwriting another writer"
                    )
                previous = before[name]
                if previous is None:
                    destination.unlink()
                else:
                    restore = _replacement(
                        backups / name, destination, stat.S_IMODE(previous[2])
                    )
                    try:
                        os.replace(restore, destination)
                    finally:
                        restore.unlink(missing_ok=True)
            except BaseException as rollback_error:
                failures.append(f"{destination}: {rollback_error}")
        if failures:
            retain = True
            raise PublicationRecoveryError(workspace, failures) from error
        raise
    finally:
        cleanup_failures = []
        for temp in prepared.values():
            try:
                temp.unlink(missing_ok=True)
            except OSError as cleanup_error:
                cleanup_failures.append(
                    f"Temporary cleanup failed: {temp}: {cleanup_error}"
                )
        # Remove only empty directories that this publication created.
        for directory in reversed(created):
            try:
                directory.rmdir()
            except OSError:
                pass
        if not retain and not cleanup_failures:
            try:
                shutil.rmtree(workspace)
            except OSError as cleanup_error:
                cleanup_failures.append(
                    f"Workspace cleanup failed: {workspace}: {cleanup_error}"
                )
        if cleanup_failures:
            active_error = sys.exception()
            if isinstance(active_error, PublicationRecoveryError):
                active_error.add_note("\n".join(cleanup_failures))
            else:
                raise PublicationRecoveryError(
                    workspace, cleanup_failures
                ) from active_error
