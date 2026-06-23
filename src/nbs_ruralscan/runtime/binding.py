"""Context-aware dataset resolution — the runtime side of the **BIND** registry.

A global recipe binds each variable to a default dataset; a country / AEZ / region can
override it with a better local one (BIND registry, `schema/spec.md`). At run time, given
an AOI's set of geographic contexts (from T7), `resolve_binding` picks the **most-specific**
matching binding, breaking ties by `preference_rank`:

    admin_region > admin_country > hydrobasin > farming_system > aez > global

If the winning binding is `catalogued`/`community`, that dataset is used. If it is
`requires_upload` (a better local dataset is known but not yet in the catalogue), the
resolver falls back to the best catalogued binding so the pipeline can still run, and
raises a **`needs_upload` flag** carrying a prompt — the signal the notebook / wireframe
turns into "Sierra Leone has a better cocoa map; upload it to override the global default."

Stdlib only; reads `schema/registers/BIND_dataset_binding.json`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

# Most-specific-context-wins precedence (higher = more specific). Mirrors spec.md → BIND.
_SCOPE_PRECEDENCE: dict[str, int] = {
    "global": 0,
    "aez": 1,
    "farming_system": 2,
    "hydrobasin": 3,
    "admin_country": 4,
    "admin_region": 5,
}
_FETCHABLE = ("catalogued", "community")


@dataclass(frozen=True)
class Binding:
    """One BIND row."""

    binding_id: str
    variable: str
    scope_type: str
    scope_id: str  # "" when scope_type == "global"
    dataset_id: str  # "" when status == requires_upload
    preference_rank: int
    status: str  # catalogued | community | requires_upload
    fitness_note: str = ""

    @property
    def specificity(self) -> int:
        return _SCOPE_PRECEDENCE.get(self.scope_type, 0)


@dataclass
class Resolution:
    """Outcome of resolving one variable for an AOI."""

    variable: str
    dataset_id: (
        str | None
    )  # the dataset to USE now (None only if no catalogued option exists)
    winning_binding: Binding  # the most-specific match (may be requires_upload)
    needs_upload: bool  # a better local dataset is wanted but must be supplied
    fell_back_to: (
        Binding | None
    )  # the catalogued binding actually supplying data, if needs_upload
    prompt: str | None  # user-facing message when needs_upload (else None)


def load_bindings(schema_root: str | Path) -> list[Binding]:
    """Load the BIND registry (JSON) into `Binding` objects."""
    path = Path(schema_root) / "registers" / "BIND_dataset_binding.json"
    rows = json.loads(path.read_text(encoding="utf-8"))
    return [
        Binding(
            binding_id=r["binding_id"],
            variable=r["variable"],
            scope_type=r["scope_type"],
            scope_id=str(r.get("scope_id") or ""),
            dataset_id=str(r.get("dataset_id") or ""),
            preference_rank=int(r["preference_rank"]),
            status=r["status"],
            fitness_note=str(r.get("fitness_note") or ""),
        )
        for r in rows
    ]


def _matches(b: Binding, aoi_contexts: set[str]) -> bool:
    return b.scope_type == "global" or b.scope_id in aoi_contexts


def _rank(b: Binding) -> tuple[int, int]:
    # sort key: most specific first, then lowest preference_rank
    return (-b.specificity, b.preference_rank)


def resolve_binding(
    bindings: list[Binding], variable: str, aoi_contexts: set[str]
) -> Resolution:
    """Resolve the dataset for `variable` over an AOI's `aoi_contexts` (a set of T7 ids)."""
    candidates = sorted(
        (b for b in bindings if b.variable == variable and _matches(b, aoi_contexts)),
        key=_rank,
    )
    if not candidates:
        raise KeyError(f"no BIND row matches variable {variable!r} for {aoi_contexts}")

    winner = candidates[0]
    if winner.status in _FETCHABLE and winner.dataset_id:
        return Resolution(variable, winner.dataset_id, winner, False, None, None)

    # Winner needs upload — fall back to the best catalogued/community option that has data.
    fallback = next(
        (b for b in candidates if b.status in _FETCHABLE and b.dataset_id), None
    )
    note = winner.fitness_note or "a better local dataset is preferred here"
    prompt = (
        f"{variable}: preferred dataset for this AOI requires upload ({note}). "
        + (
            f"Using fallback '{fallback.dataset_id}' meanwhile."
            if fallback
            else "No catalogued fallback available."
        )
    )
    return Resolution(
        variable=variable,
        dataset_id=fallback.dataset_id if fallback else None,
        winning_binding=winner,
        needs_upload=True,
        fell_back_to=fallback,
        prompt=prompt,
    )


def resolve_all(
    bindings: list[Binding], variables: list[str], aoi_contexts: set[str]
) -> tuple[dict[str, Resolution], list[str]]:
    """Resolve many variables; return (resolutions, upload-prompts) for the AOI.

    The prompt list is the AOI's data-gap report — the better-but-uncatalogued datasets the
    user could supply.
    """
    resolutions = {v: resolve_binding(bindings, v, aoi_contexts) for v in variables}
    prompts = [r.prompt for r in resolutions.values() if r.needs_upload and r.prompt]
    return resolutions, prompts
