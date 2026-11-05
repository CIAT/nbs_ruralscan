"""Explicit paths for CIAT-layout inputs and generated artifacts.

Input ownership and layout are unchanged. A relocated build publishes only
derived files; it cannot change its source snapshot or select another compiler.
"""

from dataclasses import dataclass
from pathlib import Path
import subprocess


def source_revision(root: Path, *, short: bool = False) -> str:
    """Identify this snapshot, never an unrelated current/ancestor checkout."""
    root = root.resolve()
    try:
        top = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        if Path(top).resolve() != root:
            return "unknown"
        return subprocess.run(
            ["git", "rev-parse", *(["--short"] if short else []), "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


@dataclass(frozen=True)
class SchemaBuildPaths:
    schema: Path
    output_root: Path | None = None
    corpus: Path | None = None

    def __post_init__(self):
        object.__setattr__(self, "schema", Path(self.schema).resolve())
        for name in ("output_root", "corpus"):
            value = getattr(self, name)
            if value is not None:
                object.__setattr__(self, name, Path(value).resolve())

    @property
    def source_root(self) -> Path:
        return self.schema.parent

    @property
    def schema_output(self) -> Path:
        return (
            self.output_root / "schema" if self.output_root is not None else self.schema
        )

    @property
    def docs_output(self) -> Path:
        return (
            self.output_root if self.output_root is not None else self.source_root
        ) / "docs"

    def preflight(self, destinations: list[Path]) -> None:
        """Validate every destination before any mutation, including symlink escapes."""
        if self.output_root is not None:
            protected = {self.source_root, Path(__file__).resolve().parents[3]}
            if self.corpus is not None:
                protected.add(self.corpus)
            for root in protected:
                if (
                    self.output_root == root
                    or self.output_root.is_relative_to(root)
                    or root.is_relative_to(self.output_root)
                ):
                    raise ValueError(
                        f"Output root overlaps protected inputs/compiler: {root}"
                    )
        for destination in destinations:
            # Reject redirected generated leaves/parents even inside an allowed root.
            if destination.absolute() != destination.resolve():
                raise ValueError(
                    f"Generated destination contains a symlink: {destination}"
                )
            if destination.exists() and (
                not destination.is_file() or destination.stat().st_nlink > 1
            ):
                raise ValueError(
                    f"Generated destination is not an independent file: {destination}"
                )
            for parent in destination.parents:
                if parent.exists() and not parent.is_dir():
                    raise ValueError(
                        f"Generated destination parent is not a directory: {parent}"
                    )
            if self.output_root is not None and not destination.is_relative_to(
                self.output_root
            ):
                raise ValueError(
                    f"Generated destination escapes output root: {destination}"
                )
