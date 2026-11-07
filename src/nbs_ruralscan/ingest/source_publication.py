"""Publish an explicitly named source bundle with adapter-owned validation.

Capture before fetching/preparing content. This handles caught failures under
stable inputs and a single writer; it is not a lock or a crash-safe transaction.
"""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import os
from pathlib import Path

from nbs_ruralscan.schema_tools.build_paths import SchemaBuildPaths
from nbs_ruralscan.schema_tools.publication import _state, staged_publish


def _absolute(path: Path) -> Path:
    return Path(os.path.abspath(path))


@dataclass(frozen=True)
class SourceSnapshot:
    paths: tuple[Path, ...]
    states: tuple[tuple | None, ...]

    @classmethod
    def capture(cls, paths) -> "SourceSnapshot":
        paths = tuple(_absolute(path) for path in paths)
        if not paths or len({path.parent for path in paths}) != 1:
            raise ValueError("Source bundle files must share one directory")
        if len({str(path.resolve()).casefold() for path in paths}) != len(paths):
            raise ValueError("Source bundle destinations alias")
        SchemaBuildPaths(paths[0].parent / "schema").preflight(list(paths))
        return cls(paths, tuple(_state(path) for path in paths))

    def assert_unchanged(self) -> None:
        SchemaBuildPaths(self.paths[0].parent / "schema").preflight(list(self.paths))
        if tuple(_state(path) for path in self.paths) != self.states:
            raise ValueError("Source bundle changed during preparation")

    def publish(
        self,
        contents: Mapping[Path, bytes],
        validate: Callable[[Path], None],
        *,
        create_only: bool = False,
        dry_run: bool = False,
    ) -> list[Path]:
        """Validate the staged directory before installing this exact file set."""
        normalized = {_absolute(path): body for path, body in contents.items()}
        if len(normalized) != len(contents) or set(normalized) != set(self.paths):
            raise ValueError("Source bundle contents differ from captured destinations")
        self.assert_unchanged()
        context = SchemaBuildPaths(self.paths[0].parent / "schema")

        def render(staged: SchemaBuildPaths) -> list[Path]:
            self.assert_unchanged()
            assert staged.output_root is not None
            for path in self.paths:
                (staged.output_root / path.name).write_bytes(normalized[path])
            return []

        return staged_publish(
            context,
            list(self.paths),
            render,
            create_only_destinations=self.paths if create_only else (),
            artifact_validators={
                path: lambda p: validate(p.parent) for path in self.paths
            },
            dry_run=dry_run,
        )
