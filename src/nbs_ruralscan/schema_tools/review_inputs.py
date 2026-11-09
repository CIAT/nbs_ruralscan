"""Track selected inputs through one local review operation."""

from collections.abc import Iterable
import os
from pathlib import Path

from nbs_ruralscan.schema_tools.build_paths import SchemaBuildPaths
from nbs_ruralscan.schema_tools.publication import _state


def _input_state(path: Path) -> tuple | None:
    # Keep the original spelling for later checks. A link followed by ".." can
    # select a different file from the lexically shortened path.
    normalized = Path(os.path.abspath(path))
    if normalized != path.resolve():
        raise ValueError(f"Review input contains a symlink: {path}")
    SchemaBuildPaths(normalized.parent / "schema").preflight([normalized])
    return _state(normalized)


class ReviewInputs:
    """Bind the files read by one import/build, including missing optional inputs."""

    def __init__(self, files: Iterable[Path] = ()):
        self.states: dict[Path, tuple | None] = {}
        self.include(files)

    def include(self, files: Iterable[Path]) -> None:
        for path in files:
            path = Path(path).absolute()
            if path not in self.states:
                self.states[path] = _input_state(path)

    def verify(self) -> None:
        for path, state in self.states.items():
            if _input_state(path) != state:
                raise ValueError(f"Review input changed during preparation: {path}")

    def check_outputs(self, paths: Iterable[Path]) -> None:
        inputs = {str(p.resolve()).casefold() for p in self.states}
        names = [str(p.resolve()).casefold() for p in paths]
        if len(set(names)) != len(names) or inputs.intersection(names):
            raise ValueError("Review input/output paths alias")
