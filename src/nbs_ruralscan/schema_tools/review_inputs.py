"""Track selected inputs through one local review operation."""

from collections.abc import Iterable
import os
from pathlib import Path

from nbs_ruralscan.schema_tools.build_paths import SchemaBuildPaths
from nbs_ruralscan.schema_tools.publication import _state


class ReviewInputs:
    """Bind the files read by one import/build, including missing optional inputs."""

    def __init__(self, files: Iterable[Path] = ()):
        self.states: dict[Path, tuple | None] = {}
        self.include(files)

    def include(self, files: Iterable[Path]) -> None:
        for path in files:
            path = Path(os.path.abspath(path))
            if path not in self.states:
                SchemaBuildPaths(path.parent / "schema").preflight([path])
                self.states[path] = _state(path)

    def verify(self) -> None:
        for path, state in self.states.items():
            SchemaBuildPaths(path.parent / "schema").preflight([path])
            if _state(path) != state:
                raise ValueError(f"Review input changed during preparation: {path}")

    def check_outputs(self, paths: Iterable[Path]) -> None:
        inputs = {str(p.resolve()).casefold() for p in self.states}
        names = [str(p.resolve()).casefold() for p in paths]
        if len(set(names)) != len(names) or inputs.intersection(names):
            raise ValueError("Review input/output paths alias")
