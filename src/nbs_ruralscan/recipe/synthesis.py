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


def _deg_to_pct(v: float) -> float:
    return round(math.tan(math.radians(v)) * 100.0, 1)


def _harmonise(unit: EvidenceUnit, canonical_unit: str) -> dict[str, float]:
    """Return the unit's threshold params converted to the canonical unit."""
    rel = unit.relationship or {}
    src_unit = str(rel.get("unit", canonical_unit)).lower()

    canon = canonical_unit.lower()
    conv_pct_to_deg = (canon in {"degrees", "deg"}) and src_unit in _PCT_UNITS
    conv_deg_to_pct = (canon in _PCT_UNITS) and src_unit in {"degrees", "deg"}

    out: dict[str, float] = {}
    for k in _PARAMS:
        if k in rel and isinstance(rel[k], (int, float)):
            val = float(rel[k])
            if conv_pct_to_deg:
                out[k] = _pct_to_deg(val)
            elif conv_deg_to_pct:
                out[k] = _deg_to_pct(val)
            else:
                out[k] = val
    return out


# Grey literature (WOCAT/CG/FAO/NGO/project reports) is positively — optimistically —
# biased and not peer-reviewed (#63): discount its weight in the weighted-median
# reconciliation so it can't inflate the consensus. Directional: hardest on benefit/effect
# claims (T6 — advocacy-prone), light on biophysical thresholds (a slope/soil limit isn't
# advocacy). Grey still COUNTS in n_sources (support is untouched) — it just can't dominate
# the median bounds. Defensible defaults; tune per RFC (mirrors TIER_W/BASIS_W).
GREY_DISCOUNT = {
    "nbs_effect": 0.4,  # T6 effect / economic / adoption-success ranges → big haircut
    "structural_suitability": 0.9,  # T4 biophysical envelope → barely discounted
    "climate_risk": 0.6,  # T2/T3 hazard → moderate
}
_DEFAULT_GREY_DISCOUNT = 0.6


def _weight(unit: EvidenceUnit, tier: str, category: str = "") -> float:
    w = TIER_W.get(tier, 0.5) * BASIS_W.get(unit.claim_basis, 0.5)
    if (category or "").lower() == "grey":
        w *= GREY_DISCOUNT.get(unit.use_role, _DEFAULT_GREY_DISCOUNT)
    return w


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
    categories: dict[str, str] | None = None,
) -> dict[str, float]:
    """Weighted-median per threshold param across contributing units."""
    categories = categories or {}
    params: dict[str, float] = {}
    for key in _PARAMS:
        pairs = [
            (ph[key], _weight(u, t, categories.get(u.source_id, "")))
            for (u, t, ph) in contribs
            if key in ph
        ]
        m = _weighted_median(pairs)
        if m is not None:
            params[key] = m
    return params


def _resolve_root_origin(
    unit: EvidenceUnit,
    units_by_ev_id: dict[str, EvidenceUnit],
    units_by_source: dict[str, list[EvidenceUnit]],
) -> str:
    """Resolve the ultimate primary source_id or external identifier by following lineage_of."""
    visited = {unit.evidence_id, unit.source_id}
    curr_lineage = unit.lineage_of

    while curr_lineage:
        if curr_lineage in visited:
            return curr_lineage
        visited.add(curr_lineage)

        # Is the lineage pointer an evidence ID?
        if curr_lineage in units_by_ev_id:
            parent = units_by_ev_id[curr_lineage]
            if not parent.lineage_of:
                return parent.source_id
            curr_lineage = parent.lineage_of
        # Is the lineage pointer a source ID that we have in the current synthesis?
        elif curr_lineage in units_by_source:
            # Take the first one in the list as representative to trace lineage
            parent = units_by_source[curr_lineage][0]
            if not parent.lineage_of:
                return parent.source_id
            curr_lineage = parent.lineage_of
        else:
            # External or unresolved source/evidence ID. It is the root.
            return curr_lineage

    return unit.source_id


def _dedupe_lineage(
    units: list[EvidenceUnit],
    tiers: dict[str, str],
    report: SynthesisReport,
    categories: dict[str, str] | None = None,
) -> list[EvidenceUnit]:
    """Collapse citation echoes: keep one highest-weight unit per origin source."""
    categories = categories or {}
    units_by_ev_id = {u.evidence_id: u for u in units if u.evidence_id}
    units_by_source: dict[str, list[EvidenceUnit]] = {}
    for u in units:
        units_by_source.setdefault(u.source_id, []).append(u)

    by_origin: dict[str, list[EvidenceUnit]] = {}
    for u in units:
        origin = _resolve_root_origin(u, units_by_ev_id, units_by_source)
        by_origin.setdefault(origin, []).append(u)

    kept: list[EvidenceUnit] = []
    for origin, group in by_origin.items():
        # Sort group: prioritize units with lineage_of == None (the primary study)
        # and then by weight (tier * claim_basis)
        def sort_key(u: EvidenceUnit) -> tuple[int, float]:
            is_primary = 1 if not u.lineage_of else 0
            w = _weight(
                u, tiers.get(u.source_id, "medium"), categories.get(u.source_id, "")
            )
            return (is_primary, w)

        group.sort(key=sort_key, reverse=True)
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
    categories: dict[str, str] | None = None,
) -> tuple[dict[str, Any], SynthesisReport]:
    """Reconcile evidence units for one (family × variable) into a T4 row."""
    rep = SynthesisReport()
    categories = categories or {}

    # 1) scope filter — practice-level suitability + M2b operational levers.
    # operational_risk vars (enabling-environment) are distinct variables from the structural
    # ones, so they synthesise into their own rows; family.py keeps them OUT of the MCDA
    # support/selection surface (var_support is built over structural_suitability only) and
    # they carry suitability_dimension=operational_constraint as the flagged M2b section.
    _EMITTABLE_ROLES = {"structural_suitability", "operational_risk"}
    kept: list[EvidenceUnit] = []
    for u in units:
        if u.use_role not in _EMITTABLE_ROLES:
            rep.dropped.append((u.evidence_id, f"use_role={u.use_role} (not T4/M2b)"))
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
    kept = _dedupe_lineage(kept, tiers, rep, categories)
    rep.used = [u.evidence_id for u in kept]

    # 3) harmonise + contributions
    contribs = [
        (u, tiers.get(u.source_id, "medium"), _harmonise(u, canonical_unit))
        for u in kept
    ]
    global_params = _reconcile(contribs, categories)

    # 4) uncertainty from spread of values across all parameters (widen, never narrow); humility bumps
    unc = 10.0
    for key in _PARAMS:
        vals = [ph[key] for (u, t, ph) in contribs if key in ph]
        if len(vals) >= 2 and global_params.get(key):
            denom = global_params[key]
            if denom != 0:
                spread_pct = (max(vals) - min(vals)) / abs(denom) * 100
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
