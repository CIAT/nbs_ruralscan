"""Family-level T4 synthesis — one suitability family's evidence → its recipe rows.

Orchestrates: group evidence units by canonical variable → synthesise one T4 row per
variable (`synthesis`) → enrich with literature prevalence + roll-up (`support`) →
emit the selection table (with the soft-floor flags). The machine version of building
a per-family T4 recipe with full provenance.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .evidence import EvidenceUnit
from .support import (
    SelectionRow,
    Support,
    attach_support,
    group_support,
    selection_table,
    variable_support,
)
from .synthesis import SynthesisReport, synthesise_t4_row


@dataclass
class FamilyResult:
    family: str
    corpus_n: int | None
    rows: list[dict[str, Any]] = field(default_factory=list)  # enriched T4 rows
    selection: list[SelectionRow] = field(
        default_factory=list
    )  # incl. soft-floor flags
    groups: dict[str, Support] = field(default_factory=dict)  # group-level prevalence
    dispositions: dict[str, dict[str, Any]] = field(default_factory=dict)
    crop_results: dict[str, "FamilyResult"] = field(default_factory=dict)
    support_basis: str = "caller_supplied_corpus"
    support_sources: list[str] = field(default_factory=list)
    reports: dict[str, SynthesisReport] = field(default_factory=dict)  # per variable


def is_observed_presence(u: EvidenceUnit) -> bool:
    """A fixed-form practice-database record (see synthesise_family)."""
    rel = u.relationship if isinstance(u.relationship, dict) else {}
    return rel.get("type") == "observed_presence"


def synthesise_family(
    units: list[EvidenceUnit],
    tiers: dict[str, str],
    *,
    family: str,
    corpus_n: int | set[str] | None,
    group_map: dict[str, str],
    canonical_units: dict[str, str] | None = None,
    dataset_ids: dict[str, str] | None = None,
    ml_important: set[str] | None = None,
    floor_pct: float = 20.0,
    allow_crop_scope: bool = False,
    categories: dict[str, str] | None = None,
    unit_conversions: dict[str, dict[str, str]] | None = None,
    approved_only: bool = False,
    crop: str | None = None,
    numeric_policies: dict[str, dict] | None = None,
) -> FamilyResult:
    """Reconcile all of a family's evidence into enriched T4 rows + a selection table.

    `corpus_n` is the count of papers screened for the family (denominator for support).
    `canonical_units`/`dataset_ids` map variable → its canonical unit / T1 dataset.
    `categories` maps source_id → source_category (e.g. "grey") for the grey-lit discount.
    """
    numeric_policies = numeric_policies or {}
    tiers = {sid: tier.strip().lower() for sid, tier in tiers.items()}
    canonical_units = canonical_units or {}
    dataset_ids = dataset_ids or {}
    categories = categories or {}
    unit_conversions = unit_conversions or {}

    if isinstance(corpus_n, set):
        # Validate against the unfiltered family, so approval cannot hide an incomplete
        # denominator. Species-only evidence and observed locations are not candidates.
        required_sources = {
            u.source_id
            for u in units
            if u.review_state != "dropped"
            and not is_observed_presence(u)
            and u.use_role == "structural_suitability"
            and (
                u.claim_scope == "practice_technology"
                or (u.claim_scope == "crop_specific" and allow_crop_scope)
            )
        }
        if required_sources - corpus_n:
            raise ValueError(
                f"Evidence sources absent from screened corpus: {sorted(required_sources - corpus_n)}"
            )

    dispositions = {}
    active = []
    crop_units = defaultdict(list)
    from .numeric_bands import source_completion

    by_id = {u.evidence_id: u for u in units}
    for u in units:
        reason = ""
        completion = None
        if u.review_state == "dropped":
            reason = "qa_dropped"
        elif is_observed_presence(u):
            reason = "observed_presence"
        elif u.use_role not in {"structural_suitability", "operational_risk"}:
            reason = "other_role"
        elif u.claim_scope == "species_specific":
            reason = "species_scope"
        elif u.claim_scope == "crop_specific" and not allow_crop_scope:
            reason = "crop_scope"
        elif approved_only and not u.reviewer_ok:
            completion = source_completion(u, by_id, numeric_policies)
            if not completion:
                reason = "unresolved_review"
        elif u.claim_scope == "crop_specific" and not u.taxon:
            reason = "missing_crop_taxon"
        elif u.claim_scope == "crop_specific" and crop is None:
            reason = "crop_lane"
            crop_units[u.taxon].append(u)
        dispositions[u.evidence_id] = {
            **(
                {"admission_basis": "authorized_source_completion"}
                if completion
                else {}
            ),
            "source_id": u.source_id,
            "variable": u.variable,
            "reviewer_ok": u.reviewer_ok,
            "use_role": u.use_role,
            "status": reason or "pending",
            "relationship": u.relationship,
        }
        if not reason:
            active.append(u)
    units = active
    crop_results = {
        taxon: synthesise_family(
            members,
            tiers,
            family=family,
            corpus_n=corpus_n,
            group_map=group_map,
            canonical_units=canonical_units,
            dataset_ids=dataset_ids,
            ml_important=ml_important,
            floor_pct=floor_pct,
            allow_crop_scope=True,
            categories=categories,
            unit_conversions=unit_conversions,
            approved_only=approved_only,
            crop=taxon,
            numeric_policies=numeric_policies,
        )
        for taxon, members in sorted(crop_units.items())
    }

    # support is measured over the structural-suitability candidates (what T4 considers)
    t4_units = [
        u
        for u in units
        if u.use_role == "structural_suitability"
        and (not approved_only or u.reviewer_ok)
    ]
    var_support = variable_support(t4_units, corpus_n, tiers=tiers)
    groups = group_support(t4_units, group_map, corpus_n, tiers=tiers)
    selection = selection_table(
        var_support, floor_pct=floor_pct, ml_important=ml_important
    )

    by_var: dict[str, list[EvidenceUnit]] = defaultdict(list)
    for u in units:
        by_var[u.variable].append(u)

    rows: list[dict[str, Any]] = []
    reports: dict[str, SynthesisReport] = {}
    for variable, var_units in by_var.items():
        band_units = [u for u in var_units if u.evidence_id in numeric_policies]
        ordinary_units = [u for u in var_units if u.evidence_id not in numeric_policies]
        row, rep = synthesise_t4_row(
            ordinary_units,
            tiers,
            variable=variable,
            family=family,
            canonical_unit=canonical_units.get(variable, "native"),
            dataset_id=dataset_ids.get(variable),
            allow_crop_scope=allow_crop_scope,
            categories=categories,
            unit_conversions=(unit_conversions or {}).get(variable),
        )
        if band_units:
            from .numeric_bands import compile_bands

            params, used, unresolved = compile_bands(
                band_units,
                numeric_policies,
                canonical_units.get(variable, "native"),
                unit_conversions.get(variable),
                tiers=tiers,
                categories=categories,
            )
            rep.unresolved.extend(unresolved)
            if params and row["relationship_params"]:
                # Keep the typed response intact; source profiles/pools are explicit alternatives.
                row["relationship_params"].update(params)
                row["evidence_ids"] = sorted(set(row["evidence_ids"] + used))
                row["references"] = sorted(
                    set(row["references"])
                    | {u.source_id for u in band_units if u.evidence_id in used}
                )
                row["justification"] += (
                    " Reviewed ordinal profiles and conditional scoping pools are retained as explicit alternatives; they do not replace or blend with the standalone typed response."
                )
                rep.used = sorted(set(rep.used + used))
                rep.parameter_evidence["profiles"] = used
            elif params:
                row.update(
                    relationship_type="piecewise",
                    relationship_params=params,
                    evidence_ids=used,
                    uncertainty_pct=20,
                    justification="Reconciled from reviewed ordinal source bands. Explicit source-context profile selection required; no global consensus or automatic cross-family inheritance. Scores follow versioned semantic class conventions; original source ranks and scores retained. Missing class crosswalks remain unknown. Compatible pools require explicit schema approval; weighted median ties and exclusion conflicts remain unresolved. Unreported ranges and conflicting shared boundaries remain unknown. See T4 numeric compilation policy and schema issue #362.",
                    references=sorted(
                        {u.source_id for u in band_units if u.evidence_id in used}
                    ),
                )
                rep.used = used
                rep.parameter_evidence = {"profiles": used}
                rep.notes.append(
                    "Regional profiles retained separately; uncertainty floor 20%, not a measured confidence interval."
                )
        for eid in rep.used:
            dispositions[eid]["status"] = "parameter_contributor"
            if dispositions[eid].get("admission_basis"):
                dispositions[eid]["status"] = "source_verified_continuation"
        for eid, reason in rep.dropped + rep.unresolved:
            dispositions[eid]["status"] = reason
        for eid, origin in rep.collapsed:
            dispositions[eid].update(status="citation_echo", origin=origin)
        if not row[
            "relationship_params"
        ]:  # nothing survived scope filter → skip the row, keep the report
            reports[variable] = rep
            continue
        row["parameter_source_ids"] = sorted(
            {u.source_id for u in var_units if u.evidence_id in rep.used}
        )
        row["n_parameter_sources"] = len(row["parameter_source_ids"])
        attach_support(row, var_support)
        rows.append(row)
        reports[variable] = rep

    rows.sort(key=lambda r: r.get("paper_support_pct") or 0.0, reverse=True)
    return FamilyResult(
        family=family,
        corpus_n=len(corpus_n) if isinstance(corpus_n, set) else corpus_n,
        support_sources=sorted(corpus_n) if isinstance(corpus_n, set) else [],
        rows=rows,
        selection=selection,
        groups=groups,
        reports=reports,
        dispositions=dispositions,
        crop_results=crop_results,
    )


def save_family(result: FamilyResult, path: str | Path) -> Path:
    """Write the enriched T4 rows for a family to JSON (the recipe's T4 slice)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result.rows, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    return path
