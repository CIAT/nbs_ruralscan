"""T4 synthesis — Evidence units → one T4 suitability row.

Deterministic, auditable reconciliation (method §6 + §6.1). Steps:
scope-filter → lineage-dedupe → harmonise to canonical unit → tier×claim_basis
weighting → weighted-median thresholds → uncertainty from spread (widen, never
narrow) → context overrides → justification citing evidence_ids.

Source *tier* is looked up from the Source Register (passed in as `tiers`), never
stored on the unit (spec.md). The synthesiser writes shape params only from units
already allowed to carry them (the extractor/validator enforce that upstream).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from .evidence import EvidenceUnit

# weighting tables (defensible defaults; tune per RFC)
TIER_W = {"high": 1.0, "medium": 0.6, "low": 0.35}
BASIS_W = {
    "primary_measured": 1.0,
    "table": 0.9,
    "modelled": 0.7,
    "figure_read": 0.6,
    "expert_assertion": 0.5,
    "cited_secondary": 0.4,
}
_PARAMS = ("abs_min", "opt_low", "opt_high", "abs_max")
_PCT_UNITS = {"pct", "%", "percent"}


@dataclass
class SynthesisReport:
    used: list[str] = field(default_factory=list)  # evidence_ids contributing
    dropped: list[tuple[str, str]] = field(
        default_factory=list
    )  # (evidence_id, reason)
    collapsed: list[tuple[str, str]] = field(default_factory=list)  # (echo_id, origin)
    notes: list[str] = field(default_factory=list)


def _pct_to_deg(v: float) -> float:
    return round(math.degrees(math.atan(v / 100.0)), 1)


def _harmonise(unit: EvidenceUnit, canonical_unit: str) -> dict[str, float]:
    """Return the unit's threshold params converted to the canonical unit."""
    rel = unit.relationship or {}
    src_unit = str(rel.get("unit", canonical_unit)).lower()
    conv = (
        canonical_unit == "degrees" or canonical_unit == "deg"
    ) and src_unit in _PCT_UNITS
    out: dict[str, float] = {}
    for k in _PARAMS:
        if k in rel and isinstance(rel[k], (int, float)):
            out[k] = _pct_to_deg(float(rel[k])) if conv else float(rel[k])
    return out


def _weight(unit: EvidenceUnit, tier: str) -> float:
    return TIER_W.get(tier, 0.5) * BASIS_W.get(unit.claim_basis, 0.5)


def _weighted_median(pairs: list[tuple[float, float]]) -> float | None:
    if not pairs:
        return None
    pairs = sorted(pairs, key=lambda x: x[0])
    total = sum(w for _, w in pairs)
    if total <= 0:
        return None
    acc = 0.0
    for v, w in pairs:
        acc += w
        if acc >= total / 2:
            return round(v, 1)
    return round(pairs[-1][0], 1)


def _reconcile(
    contribs: list[tuple[EvidenceUnit, str, dict[str, float]]],
) -> dict[str, float]:
    """Weighted-median per threshold param across contributing units."""
    params: dict[str, float] = {}
    for key in _PARAMS:
        pairs = [(ph[key], _weight(u, t)) for (u, t, ph) in contribs if key in ph]
        m = _weighted_median(pairs)
        if m is not None:
            params[key] = m
    return params


def _dedupe_lineage(
    units: list[EvidenceUnit], tiers: dict[str, str], report: SynthesisReport
) -> list[EvidenceUnit]:
    """Collapse citation echoes: keep one highest-weight unit per origin source."""
    by_origin: dict[str, list[EvidenceUnit]] = {}
    for u in units:
        origin = u.lineage_of or u.source_id
        by_origin.setdefault(origin, []).append(u)
    kept: list[EvidenceUnit] = []
    for origin, group in by_origin.items():
        group.sort(
            key=lambda u: _weight(u, tiers.get(u.source_id, "medium")), reverse=True
        )
        kept.append(group[0])
        for echo in group[1:]:
            report.collapsed.append((echo.evidence_id, origin))
    return kept


def synthesise_t4_row(
    units: list[EvidenceUnit],
    tiers: dict[str, str],
    *,
    variable: str,
    family: str,
    canonical_unit: str = "degrees",
    dataset_id: str | None = None,
    relationship_type: str = "trapezoidal",
    allow_crop_scope: bool = False,
    context_field: str = "aez",
    override_reltol: float = 0.25,
) -> tuple[dict[str, Any], SynthesisReport]:
    """Reconcile evidence units for one (family × variable) into a T4 row."""
    rep = SynthesisReport()

    # 1) scope filter — practice-level T4 only
    kept: list[EvidenceUnit] = []
    for u in units:
        if u.use_role != "structural_suitability":
            rep.dropped.append((u.evidence_id, f"use_role={u.use_role} (not T4)"))
        elif u.claim_scope == "species_specific" or (
            u.claim_scope == "crop_specific" and not allow_crop_scope
        ):
            rep.dropped.append(
                (
                    u.evidence_id,
                    f"claim_scope={u.claim_scope} → routed to species/crop suitability",
                )
            )
        else:
            kept.append(u)

    # 2) lineage dedupe (anti pseudo-consensus)
    kept = _dedupe_lineage(kept, tiers, rep)
    rep.used = [u.evidence_id for u in kept]

    # 3) harmonise + contributions
    contribs = [
        (u, tiers.get(u.source_id, "medium"), _harmonise(u, canonical_unit))
        for u in kept
    ]
    global_params = _reconcile(contribs)

    # 4) uncertainty from spread of abs_max (widen, never narrow); humility bumps
    maxes = [
        (ph["abs_max"], _weight(u, t)) for (u, t, ph) in contribs if "abs_max" in ph
    ]
    unc = 10.0
    if global_params.get("abs_max") and len(maxes) >= 2:
        vals = [v for v, _ in maxes]
        spread_pct = (max(vals) - min(vals)) / global_params["abs_max"] * 100
        unc = max(unc, round(spread_pct, 0))
    n_independent = len({u.source_id for u in kept})
    if n_independent < 3:
        unc += 10  # thin evidence → less, not more, confidence
        rep.notes.append(
            f"only {n_independent} independent source(s) → uncertainty bumped"
        )
    if kept and all(
        u.claim_basis in {"cited_secondary", "expert_assertion"} for u in kept
    ):
        unc += 10
        rep.notes.append(
            "evidence is all secondary/assertion → uncertainty bumped (publication-bias humility)"
        )
    unc = min(unc, 60.0)

    # 5) context overrides — where a context's reconciled abs_max/opt_high diverges from global
    overrides: list[dict[str, Any]] = []
    ctx_groups: dict[str, list[tuple[EvidenceUnit, str, dict[str, float]]]] = {}
    for c in contribs:
        cid = (c[0].context or {}).get(context_field)
        if cid:
            ctx_groups.setdefault(cid, []).append(c)
    for cid, group in ctx_groups.items():
        cp = _reconcile(group)
        diverges = any(
            k in cp
            and k in global_params
            and global_params[k]
            and abs(cp[k] - global_params[k]) / global_params[k] > override_reltol
            for k in ("abs_max", "opt_high")
        )
        if diverges:
            overrides.append(
                {
                    "context_type": context_field,
                    "context_id": cid,
                    "relationship_params": cp,
                    "note": f"Context-specific evidence ({', '.join(u.evidence_id for u, _, _ in group)}).",
                }
            )

    # 6) justification + row
    just = (
        f"Reconciled from {len(kept)} evidence unit(s) (weighted median, tier×claim_basis). "
        f"Global {global_params}; uncertainty ±{unc:.0f}% from spread. "
        + (f"{len(overrides)} context override(s). " if overrides else "")
        + (f"Dropped {len(rep.dropped)} (scope/role). " if rep.dropped else "")
        + (
            f"Collapsed {len(rep.collapsed)} citation echo(es). "
            if rep.collapsed
            else ""
        )
    )
    row = {
        "mapping_id": f"{family}__{variable}",
        "suitability_family_id": family,
        "variable": variable,
        "variable_unit": canonical_unit,
        "dataset_id": dataset_id,
        "suitability_dimension": "biophysical_constraint",
        "relationship_type": relationship_type,
        "relationship_params": global_params,
        "uncertainty_pct": unc,
        "context_overrides": overrides,
        "justification": just,
        "references": sorted({u.source_id for u in kept}),
        "evidence_ids": rep.used,
    }
    return row, rep
