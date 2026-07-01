"""M2 runner — the one place that ties schema + loaders + compute together.

This is the reusable "do climate risk for an AOI" entry point, called by both the Colab
pilot notebook (the contract deliverable) and the Claude-Code backend. It owns I/O and
sequencing; all the math lives in ``compute`` and stays array-in/array-out.

Flow (M2 spec §6): resolve hazards (T3) → for each hazard pull + standardise its layers
(T2/T1 via binding + data_loaders) → combine with exposure → weighted composite → repeat
for future scenarios → delta → summary table.

Status: scaffold. The compute plumbing is real; the schema reads (``_relevant_hazards`` etc.)
await ``runtime/schema_loader`` and the per-NbS T2/T3 tables, so they raise until authored.
Keeping them as named seams documents the contract in code.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import xarray as xr

from nbs_ruralscan.data_loaders import GeoBox

from . import compute


@dataclass
class M2Result:
    """What M2 hands downstream (Opportunity Space view, M4 hotspots)."""

    composites: dict[str, xr.DataArray] = field(
        default_factory=dict
    )  # scenario → 0–1 risk
    per_hazard: dict[str, xr.DataArray] = field(
        default_factory=dict
    )  # "hazard__scenario" → risk
    deltas: dict[str, xr.DataArray] = field(
        default_factory=dict
    )  # scenario → future − baseline
    meta: dict = field(
        default_factory=dict
    )  # mode, scenarios, combine op, double-count decisions


def run_climate_risk(
    grid: GeoBox,
    nbs_id: str,
    *,
    mode: str = "mode_a",
    scenarios: tuple[str, ...] = ("baseline",),
    combine: str = "multiply",
) -> M2Result:
    """Compute the rural climate-risk surface(s) for ``nbs_id`` over ``grid``.

    ``mode``: ``mode_a`` (Hazard × Exposure, default) | ``mode_b`` (× Vulnerability).
    ``scenarios``: must include ``baseline``; any ``future_*`` also produces a delta.
    """
    if "baseline" not in scenarios:
        raise ValueError("scenarios must include 'baseline'")

    hazards = _relevant_hazards(nbs_id)  # §6.1 (T3)
    weights = _hazard_weights(nbs_id)  # §6.5 (T2)
    exposure = _exposure_stack(
        nbs_id, grid
    )  # §6.3 (T2/T1) — baseline only, reused across scenarios
    vuln = _vulnerability(nbs_id, grid) if mode == "mode_b" else None  # §6.4

    result = M2Result(
        meta={"mode": mode, "scenarios": list(scenarios), "combine": combine}
    )
    for scenario in scenarios:
        per_hazard = {}
        for hazard in hazards:  # §6.2 assemble + standardise each hazard
            raw = _hazard_layer(nbs_id, hazard, grid, scenario)
            score = compute.standardize_hazard(raw, _params(nbs_id, hazard))
            risk = compute.combine_hazard_exposure(score, exposure[hazard], how=combine)
            per_hazard[hazard] = risk
            result.per_hazard[f"{hazard}__{scenario}"] = risk
        composite = compute.composite_risk(per_hazard, weights)  # §6.5
        if vuln is not None:
            composite = compute.apply_vulnerability(composite, vuln)
        result.composites[scenario] = composite
        if scenario != "baseline":  # §6.6
            result.deltas[scenario] = compute.delta(
                composite, result.composites["baseline"]
            )
    return result


# --- schema seams (await runtime/schema_loader + per-NbS T2/T3) ------------------
# Each is the documented contract from the M2 spec; implement against the schema, not
# hardcoded rules (AGENTS.md: "Pipeline reads from schema").


def _relevant_hazards(nbs_id: str) -> list[str]:
    """§6.1 — T3 rows for nbs_id where a hazard is listed → hazard ids."""
    raise NotImplementedError("read T3 via schema_loader")


def _hazard_weights(nbs_id: str) -> dict[str, float]:
    """§6.5 — per-hazard weights from T2."""
    raise NotImplementedError("read T2 weights via schema_loader")


def _hazard_layer(
    nbs_id: str, hazard: str, grid: GeoBox, scenario: str
) -> xr.DataArray:
    """§6.2 — resolve the hazard's variable (binding) and pull it onto grid for this scenario."""
    raise NotImplementedError(
        "resolve_binding(var, contexts) → load(dataset_id, grid, ...)"
    )


def _exposure_stack(nbs_id: str, grid: GeoBox) -> dict[str, xr.DataArray]:
    """§6.3 — exposure layer per hazard (baseline only); pulled via binding + load()."""
    raise NotImplementedError("read T2 exposure rows → load() each onto grid")


def _vulnerability(nbs_id: str, grid: GeoBox) -> xr.DataArray:
    """§6.4 — Mode-B vulnerability composite (excludes opportunity_space_only vars)."""
    raise NotImplementedError("Mode-B only — read T2 sensitivity/AC rows")


def _params(nbs_id: str, hazard: str) -> dict:
    """Membership params for a hazard's standardisation (T4.relationship_params)."""
    raise NotImplementedError("read membership params via schema_loader")
