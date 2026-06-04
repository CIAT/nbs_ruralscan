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
    corpus_n: int
    rows: list[dict[str, Any]] = field(default_factory=list)  # enriched T4 rows
    selection: list[SelectionRow] = field(
        default_factory=list
    )  # incl. soft-floor flags
    groups: dict[str, Support] = field(default_factory=dict)  # group-level prevalence
    reports: dict[str, SynthesisReport] = field(default_factory=dict)  # per variable


def synthesise_family(
    units: list[EvidenceUnit],
    tiers: dict[str, str],
    *,
    family: str,
    corpus_n: int,
    group_map: dict[str, str],
    canonical_units: dict[str, str] | None = None,
    dataset_ids: dict[str, str] | None = None,
    ml_important: set[str] | None = None,
    floor_pct: float = 20.0,
    allow_crop_scope: bool = False,
) -> FamilyResult:
    """Reconcile all of a family's evidence into enriched T4 rows + a selection table.

    `corpus_n` is the count of papers screened for the family (denominator for support).
    `canonical_units`/`dataset_ids` map variable → its canonical unit / T1 dataset.
    """
    canonical_units = canonical_units or {}
    dataset_ids = dataset_ids or {}

    # support is measured over the structural-suitability candidates (what T4 considers)
    t4_units = [u for u in units if u.use_role == "structural_suitability"]
    var_support = variable_support(t4_units, corpus_n)
    groups = group_support(t4_units, group_map, corpus_n)
    selection = selection_table(
        var_support, floor_pct=floor_pct, ml_important=ml_important
    )

    by_var: dict[str, list[EvidenceUnit]] = defaultdict(list)
    for u in units:
        by_var[u.variable].append(u)

    rows: list[dict[str, Any]] = []
    reports: dict[str, SynthesisReport] = {}
    for variable, var_units in by_var.items():
        row, rep = synthesise_t4_row(
            var_units,
            tiers,
            variable=variable,
            family=family,
            canonical_unit=canonical_units.get(variable, "native"),
            dataset_id=dataset_ids.get(variable),
            allow_crop_scope=allow_crop_scope,
        )
        if not row[
            "relationship_params"
        ]:  # nothing survived scope filter → skip the row, keep the report
            reports[variable] = rep
            continue
        attach_support(row, var_support)
        rows.append(row)
        reports[variable] = rep

    rows.sort(key=lambda r: r.get("paper_support_pct", 0.0), reverse=True)
    return FamilyResult(
        family=family,
        corpus_n=corpus_n,
        rows=rows,
        selection=selection,
        groups=groups,
        reports=reports,
    )


def save_family(result: FamilyResult, path: str | Path) -> Path:
    """Write the enriched T4 rows for a family to JSON (the recipe's T4 slice)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.rows, ensure_ascii=False, indent=2))
    return path
