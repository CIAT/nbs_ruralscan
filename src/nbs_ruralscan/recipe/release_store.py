"""Immutable local recipe generations and a single atomically replaced current pointer.

A release ID hashes the canonical v1 manifest, including every logical member's
name, byte length and SHA-256. A reader opens one generation and never follows
the current pointer again. Independent publishers share a short SQLite lock
only while installing and selecting a complete generation. A failed selection
can leave a verified, unselected generation available for retry.
"""

from collections.abc import Callable, Mapping
from contextlib import closing, contextmanager
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import sqlite3
import stat
import tempfile
from types import MappingProxyType
import unicodedata

from nbs_ruralscan.ingest.integrity import atomic_write


_VERSION = 1
_SHA256 = re.compile(r"[0-9a-f]{64}")
_ILLEGAL = re.compile(r'[\x00-\x1f<>:"\\|?*]')


def _json_bytes(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "ascii"
    )


def _plain_dir(path: Path) -> None:
    if path != path.resolve() or not stat.S_ISDIR(path.lstat().st_mode):
        raise ValueError(f"Expected a directory without redirected paths: {path}")


def _read_file(path: Path) -> bytes:
    if path != path.resolve():
        raise ValueError(f"Redirected release file: {path}")
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError(f"Expected an independent regular release file: {path}")
    return path.read_bytes()


def _store_root(store: Path) -> Path:
    # The caller can select a mounted parent (such as /tmp on macOS). Reject a
    # redirected store leaf and a '..' whose meaning depends on following a link.
    path = Path(store).absolute()
    if path.is_symlink() or (
        ".." in path.parts and Path(os.path.abspath(path)).resolve() != path.resolve()
    ):
        raise ValueError(f"Redirected release store: {path}")
    return path.resolve()


def _validate_id(release_id: str) -> None:
    if not isinstance(release_id, str) or not _SHA256.fullmatch(release_id):
        raise ValueError(f"Invalid release ID: {release_id!r}")


def _logical_names(names) -> None:
    if not names:
        raise ValueError("A release needs at least one file")
    seen = {}
    for name in names:
        if not isinstance(name, str):
            raise ValueError("Release member names must be strings")
        parts = name.split("/")
        for index, part in enumerate(parts):
            if (
                not part
                or part in {".", ".."}
                or part.endswith((".", " "))
                or _ILLEGAL.search(part)
                or PureWindowsPath(part).is_reserved()
            ):
                raise ValueError(f"Invalid logical release path: {name!r}")
            prefix = "/".join(parts[: index + 1])
            key = unicodedata.normalize("NFC", prefix).casefold()
            entry = (prefix, index == len(parts) - 1)
            if seen.setdefault(key, entry) != entry:
                raise ValueError(f"Conflicting logical release paths at {prefix!r}")


def _fingerprint(body: bytes) -> tuple[int, str]:
    return len(body), hashlib.sha256(body).hexdigest()


def _manifest(records: Mapping[str, tuple[int, str]]) -> bytes:
    return _json_bytes(
        {
            "format_version": _VERSION,
            "files": {
                key: {"size": size, "sha256": digest}
                for key, (size, digest) in records.items()
            },
        }
    )


@dataclass(frozen=True)
class PinnedRelease:
    """A verified generation. Reads continue to use this ID after another publication."""

    release_id: str
    _generation: Path
    _records: Mapping[str, tuple[int, str]]

    @property
    def files(self) -> tuple[str, ...]:
        return tuple(self._records)

    def read_bytes(self, name: str) -> bytes:
        """Read an inventoried member and verify the bytes actually returned."""
        expected = self._records[name]
        path = self._generation / "files" / name
        data = _read_file(path)
        if _fingerprint(data) != expected:
            raise ValueError(f"Release integrity check failed for {name!r}")
        return data

    def path_for(self, name: str) -> Path:
        """Return this generation's path after checking that member's current bytes."""
        self.read_bytes(name)
        return self._generation / "files" / name


def _open_generation(directory: Path, release_id: str) -> PinnedRelease:
    _plain_dir(directory)
    raw = _read_file(directory / "manifest.json")
    if hashlib.sha256(raw).hexdigest() != release_id:
        raise ValueError(f"Release manifest does not match generation {release_id}")
    document = json.loads(raw)
    if (
        not isinstance(document, dict)
        or type(document.get("format_version")) is not int
        or document["format_version"] != _VERSION
    ):
        raise ValueError("Unsupported release manifest version")
    inventory = document.get("files")
    if not isinstance(inventory, dict):
        raise ValueError("Invalid release file inventory")
    _logical_names(inventory)
    files = directory / "files"
    _plain_dir(files)
    if {item.name for item in directory.iterdir()} != {"manifest.json", "files"}:
        raise ValueError(f"Unexpected members in release {release_id}")
    names: list[str] = sorted(inventory)
    expected = {files / name for name in names}
    parents = {
        ancestor for leaf in expected for ancestor in leaf.relative_to(files).parents
    }
    expected.update(files / parent for parent in parents if parent != Path("."))
    if set(files.rglob("*")) != expected:
        raise ValueError(
            f"Release member set differs from the manifest for {release_id}"
        )
    records = {name: _fingerprint(_read_file(files / name)) for name in names}
    if raw != _manifest(records):
        raise ValueError(f"Release integrity check failed for generation {release_id}")
    return PinnedRelease(release_id, directory, MappingProxyType(records))


def _current_id(root: Path) -> str:
    raw = _read_file(root / "current.json")
    pointer = json.loads(raw)
    if (
        not isinstance(pointer, dict)
        or type(pointer.get("format_version")) is not int
        or pointer["format_version"] != _VERSION
    ):
        raise ValueError("Unsupported release pointer version")
    release_id = pointer.get("release_id")
    _validate_id(release_id)
    if raw != _json_bytes({"format_version": _VERSION, "release_id": release_id}):
        raise ValueError("Release pointer is not in the canonical format")
    return release_id


def open_release(store: Path, release_id: str | None = None) -> PinnedRelease:
    """Select current once, or reopen an earlier explicit release. Verify every file."""
    root = _store_root(store)
    _plain_dir(root)
    if release_id is None:
        release_id = _current_id(root)
    _validate_id(release_id)
    generations = root / "generations"
    _plain_dir(generations)
    return _open_generation(generations / release_id, release_id)


@contextmanager
def _publishing(root: Path):
    # An OS-released reservation also works between independent Python processes.
    lock = root / ".publish.lock"
    if os.path.lexists(lock):
        info = lock.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError(f"Invalid release publication lock: {lock}")
    with closing(sqlite3.connect(lock, timeout=30)) as db:
        db.execute("BEGIN IMMEDIATE")
        yield


def publish_release(
    store: Path,
    files: Mapping[str, bytes],
    *,
    verify_inputs: Callable[[], None] | None = None,
) -> PinnedRelease:
    """Publish explicit bytes. Concurrent writers select in publication-lock order.

    verify_inputs, when supplied, runs before staging and immediately before
    selecting the generation. A retry of the current content skips pointer writes.
    """
    members = dict(files)
    _logical_names(members)
    records = {}
    for name, body in members.items():
        if not isinstance(body, bytes):
            raise TypeError(f"Release member {name!r} must contain bytes")
        records[name] = _fingerprint(body)
    manifest = _manifest(records)
    release_id = hashlib.sha256(manifest).hexdigest()
    if verify_inputs is not None:
        verify_inputs()

    root = _store_root(store)
    root.mkdir(parents=True, exist_ok=True)
    _plain_dir(root)
    generations = root / "generations"
    generations.mkdir(exist_ok=True)
    _plain_dir(generations)
    destination = generations / release_id
    with tempfile.TemporaryDirectory(prefix=".preparing-", dir=root) as work:
        stage = Path(work) / release_id
        for name, body in members.items():
            staged = stage / "files" / name
            staged.parent.mkdir(parents=True, exist_ok=True)
            staged.write_bytes(body)
        (stage / "manifest.json").write_bytes(manifest)
        _open_generation(stage, release_id)
        with _publishing(root):
            current = root / "current.json"
            previous = open_release(root) if os.path.lexists(current) else None
            if previous is not None and previous.release_id == release_id:
                if verify_inputs is not None:
                    verify_inputs()
                return previous
            if not os.path.lexists(destination):
                os.rename(stage, destination)
            result = _open_generation(destination, release_id)
            if verify_inputs is not None:
                verify_inputs()
            pointer = _json_bytes(
                {"format_version": _VERSION, "release_id": release_id}
            )
            try:
                atomic_write(current, pointer)
            except OSError:
                # A failed acknowledgement can follow a completed replacement.
                # Under the writer lock the selected ID settles that outcome.
                if not os.path.lexists(current) or _current_id(root) != release_id:
                    raise
            return result
