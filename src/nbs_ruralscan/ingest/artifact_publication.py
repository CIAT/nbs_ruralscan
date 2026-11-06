"""Recoverable publication of one acquired artifact and its provenance sidecar.

Capture the destination pair before fetching. Use stable inputs and one writer;
this catches observed drift and rolls back caught failures, but is not a lock,
crash-safe transaction or simultaneous-reader guarantee.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path

from nbs_ruralscan.ingest.integrity import validate_body, validate_source_id
from nbs_ruralscan.schema_tools.build_paths import SchemaBuildPaths
from nbs_ruralscan.schema_tools.publication import staged_publish


_EXTENSIONS = {"pdf": ".pdf", "website": ".html", "markdown": ".md"}


def _state(path: Path) -> tuple | None:
    if not path.exists():
        return None
    info = path.stat()
    return (
        hashlib.sha256(path.read_bytes()).hexdigest(),
        info.st_size,
        info.st_mode,
        info.st_mtime_ns,
        info.st_dev,
        info.st_ino,
    )


def _preflight(artifact: Path, sidecar: Path) -> SchemaBuildPaths:
    if artifact.parent != sidecar.parent:
        raise ValueError("Acquired artifact and sidecar must share a directory")
    if str(artifact.resolve()).casefold() == str(sidecar.resolve()).casefold():
        raise ValueError("Acquired artifact and sidecar destinations alias")
    context = SchemaBuildPaths(artifact.parent / "schema")
    context.preflight([artifact, sidecar])
    return context


@dataclass(frozen=True)
class PairSnapshot:
    artifact: Path
    sidecar: Path
    artifact_state: tuple | None
    sidecar_state: tuple | None

    @classmethod
    def capture(cls, artifact: Path, sidecar: Path) -> PairSnapshot:
        artifact = Path(os.path.abspath(artifact))
        sidecar = Path(os.path.abspath(sidecar))
        _preflight(artifact, sidecar)
        return cls(artifact, sidecar, _state(artifact), _state(sidecar))

    def assert_unchanged(self) -> None:
        _preflight(self.artifact, self.sidecar)
        if (_state(self.artifact), _state(self.sidecar)) != (
            self.artifact_state,
            self.sidecar_state,
        ):
            raise ValueError("Acquisition pair changed while preparing download")


def publish_pair(
    snapshot: PairSnapshot,
    body: bytes,
    metadata: bytes,
    *,
    source_id: str,
    url: str,
    kind: str,
    commit_sha: str | None = None,
) -> None:
    """Validate and publish exactly this pair, retaining original sidecar bytes."""
    validate_source_id(source_id)
    if kind not in _EXTENSIONS:
        raise ValueError(f"Unsupported acquired artifact kind: {kind!r}")
    if (
        snapshot.artifact.name != source_id + _EXTENSIONS[kind]
        or snapshot.sidecar.name != source_id + ".meta.json"
    ):
        raise ValueError("Acquisition pair filenames do not match source identity/kind")

    def validate_pair(artifact: Path) -> None:
        content = artifact.read_bytes()
        validate_body(content, kind)
        record = json.loads(
            (artifact.parent / snapshot.sidecar.name).read_text(encoding="utf-8")
        )
        expected = {
            "source_id": source_id,
            "url": url,
            "kind": kind,
            "sha1": hashlib.sha1(content).hexdigest(),
            "bytes": len(content),
            "commit_sha": commit_sha,
        }
        if not isinstance(record, dict) or any(
            record.get(key) != value for key, value in expected.items()
        ):
            raise ValueError("Acquired artifact/provenance mismatch")

    snapshot.assert_unchanged()
    context = _preflight(snapshot.artifact, snapshot.sidecar)

    def render(staged: SchemaBuildPaths) -> list[Path]:
        # Compare again inside publication after its original-state snapshot;
        # an intervening writer must never become an accepted replacement base.
        snapshot.assert_unchanged()
        assert staged.output_root is not None
        (staged.output_root / snapshot.artifact.name).write_bytes(body)
        (staged.output_root / snapshot.sidecar.name).write_bytes(metadata)
        return []

    staged_publish(
        context,
        [snapshot.artifact, snapshot.sidecar],
        render,
        artifact_validators={snapshot.artifact: validate_pair},
    )
