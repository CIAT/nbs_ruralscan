"""Edit selected historical records on private copies, using the shared publisher."""

from collections.abc import Callable, Iterable, Mapping, Sequence
import os
from pathlib import Path
from typing import TypeVar

from .build_paths import SchemaBuildPaths
from .publication import staged_publish
from .review_inputs import ReviewInputs


_Result = TypeVar("_Result")


def edit_records(
    outputs: Sequence[Path],
    mutate: Callable[[dict[Path, Path]], _Result],
    *,
    inputs: ReviewInputs | None = None,
    verify: Callable[[], None] | None = None,
    dry_run: bool = False,
    optional: Iterable[Path] = (),
    validators: Mapping[Path, Callable[[Path], None]] | None = None,
) -> _Result:
    """Run an edit on private seeded paths, in the declared installation order.

    inputs tracks read-only files and may acquire dependencies during preparation.
    verify can also check membership of input file sets. Optional paths may stay
    absent on a no-op. The returned result describes the validated operation.
    """
    originals = list(map(Path, outputs))
    if not originals:
        raise ValueError("A record edit requires at least one destination")
    spellings = [path.absolute() for path in originals]
    destinations = [Path(os.path.abspath(path)) for path in spellings]
    traversals = [
        (spelling, destination)
        for spelling, destination in zip(spellings, destinations, strict=True)
        if spelling != destination
    ]
    selected = inputs if inputs is not None else ReviewInputs()

    def check_inputs() -> None:
        for spelling, destination in traversals:
            if spelling.resolve() != destination:
                raise ValueError(f"Record destination contains a symlink: {spelling}")
        selected.check_outputs(destinations)
        selected.verify()
        if verify is not None:
            verify()

    root = Path(os.path.commonpath([path.parent for path in destinations]))
    results: list[_Result] = []

    def render(staged: SchemaBuildPaths) -> list[Path]:
        assert staged.output_root is not None
        private = {
            original: staged.output_root / target.relative_to(root)
            for original, target in zip(originals, destinations, strict=True)
        }
        for path in private.values():
            path.parent.mkdir(parents=True, exist_ok=True)
        results.append(mutate(private))
        return []

    check_inputs()
    staged_publish(
        SchemaBuildPaths(root / "schema"),
        destinations,
        render,
        optional_destinations=tuple(Path(os.path.abspath(p)) for p in optional),
        artifact_validators={
            Path(os.path.abspath(p)): fn for p, fn in (validators or {}).items()
        },
        dry_run=dry_run,
        verify_inputs=check_inputs,
    )
    return results[0]
