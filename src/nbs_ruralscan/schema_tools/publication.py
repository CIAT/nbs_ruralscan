"""Stage complete generator output, then install with recoverable file rollback.

Use stable inputs and one writer per output root. Individual replacements are
atomic; readers can still see mixed generations during installation. This is
not a crash-safe transaction or a lock shared with the review server.
"""

from collections.abc import Callable
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


def _manifest(root: Path, names: list[Path]) -> dict[str, dict]:
    entries = list(root.rglob("*"))
    if any(path.is_symlink() for path in entries):
        raise ValueError("Staged output contains a symlink")
    found = {path.relative_to(root) for path in entries if path.is_file()}
    if found != set(names):
        raise ValueError(
            "Staged artifact set changed: "
            f"missing={sorted(map(str, set(names) - found))}, "
            f"unexpected={sorted(map(str, found - set(names)))}"
        )
    result = {}
    for name in names:
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
        else:
            raise ValueError(f"Unsupported generated artifact: {name}")
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
) -> list[Path]:
    """Render all artifacts before touching outputs; keep recovery on rollback failure.

    The frozen artifact list is the allowlist, not the renderer's changed list.
    Existing bytes seed history and stable timestamps. Unrelated files survive.
    """
    paths.preflight(destinations)
    output = paths.output_root or paths.source_root
    names = [path.relative_to(output) for path in destinations]
    if len(set(names)) != len(names):
        raise ValueError("Duplicate generated destinations")
    before = {name: _state(output / name) for name in names}
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
                if (
                    _state(output / name) != before[name]
                    or _digest(backup) != previous[0]
                ):
                    raise ValueError(f"Output changed while staging: {output / name}")
        render(SchemaBuildPaths(paths.schema, stage, paths.corpus))
        manifest = _manifest(stage, names)
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
            if previous is None or previous[0] != manifest[str(name)]["sha256"]
        ]
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
        for name in changed:
            destination = output / name
            paths.preflight([destination])
            if _state(destination) != before[name]:
                raise ValueError(f"Output changed during installation: {destination}")
            replacement_state = _state(prepared[name])
            # Register the attempt before the syscall: an interrupt can arrive
            # after replacement succeeds but before Python bookkeeping resumes.
            installed[name] = replacement_state
            os.replace(prepared[name], destination)
        return [output / name for name in changed]
    except BaseException as error:
        failures = []
        for name, installed_state in reversed(list(installed.items())):
            destination = output / name
            try:
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
