"""T4 compilation with explicit data, policy, baseline and output paths.

This adapter preserves the existing synthesis semantics. It does not decide
ownership of mixed authored/generated T4 rows or publish an accepted release.
"""

from __future__ import annotations

import csv
import io
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .evidence import EvidenceUnit
from .family import FamilyResult, save_family, synthesise_family
from ..schema_tools.generate import _csv_to_rows


@dataclass(frozen=True)
class T4BuildInputs:
    """Input identity is independent of the executing compiler's installation."""

    evidence: Path
    sources: Path
    ontology: Path
    crop_scope_policy: Path
    numeric_policy: Path
    audited_recipe: Path

    @classmethod
    def from_root(cls, root: Path, nbs_id: str) -> T4BuildInputs:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", nbs_id):
            raise ValueError("Invalid NbS identifier")
        schema = Path(root).resolve() / "schema"
        return cls(
            evidence=schema / "registers/EV_evidence_register.csv",
            sources=schema / "registers/SRC_source_register.csv",
            ontology=schema / "registers/VONT_variable_ontology.csv",
            crop_scope_policy=schema / "lookups/crop_scope_policy.csv",
            numeric_policy=schema / "lookups/t4_numeric_compilation_policy.csv",
            audited_recipe=schema / "recipes" / nbs_id / "T4_suitability_mappings.csv",
        )

    def paths(self) -> tuple[Path, ...]:
        return (
            self.evidence,
            self.sources,
            self.ontology,
            self.crop_scope_policy,
            self.numeric_policy,
            self.audited_recipe,
        )


# T4 column order, as frozen in schema/structure/columns.json
T4_FIELDS = [
    "mapping_id",
    "nbs_id",
    "dataset_id",
    "suitability_dimension",
    "relationship_type",
    "relationship_params",
    "uncertainty_pct",
    "context_overrides",
    "is_scenario_candidate",
    "scenario_label",
    "scenario_description",
    "has_future_projection",
    "baseline_dataset_id",
    "future_dataset_ids",
    "weight_default",
    "weight_adjustable",
    "justification",
    "variable",
    "suitability_family_id",
    "evidence_ids",
    "n_sources",
    "corpus_n",
    "paper_support_pct",
]


def _rd(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _first_dataset(raw: str | None) -> str:
    """VONT candidate_dataset_ids is a JSON list; T4.dataset_id takes the preferred one."""
    try:
        ids = json.loads(raw or "[]")
    except json.JSONDecodeError:
        return ""
    return ids[0] if ids else ""


def synthesise(
    nbs_id: str,
    *,
    inputs: T4BuildInputs,
    approved_only: bool = True,
    screened_sources: dict[str, set[str]] | None = None,
) -> dict[str, FamilyResult]:
    if not re.fullmatch(r"[a-z][a-z0-9_]*", nbs_id):
        raise ValueError("Invalid NbS identifier")
    src, vont = _rd(inputs.sources), _rd(inputs.ontology)
    tiers = {
        r["source_id"]: r["benchmark_tier"].strip().lower()
        for r in src
        if (r["benchmark_tier"] or "").strip()
    }
    categories = {r["source_id"]: r["source_category"] for r in src}
    group_map = {r["canonical_variable_id"]: r["group_id"] for r in vont}
    canonical_units = {r["canonical_variable_id"]: r["canonical_unit"] for r in vont}
    dataset_ids = {
        r["canonical_variable_id"]: _first_dataset(r["candidate_dataset_ids"])
        for r in vont
        if (r["candidate_dataset_ids"] or "[]") != "[]"
    }
    unit_conversions = {
        r["canonical_variable_id"]: json.loads(r["unit_conversions"] or "{}")
        for r in vont
        if (r["unit_conversions"] or "{}") != "{}"
    }

    # SRCH stores overlapping search totals, not screened-source membership.
    # Unknown is explicit; never substitute active/extracted sources or included counts.
    screened_sources = screened_sources or {}
    known = {r["source_id"] for r in src}
    for family, source_ids in screened_sources.items():
        if source_ids - known:
            raise ValueError(
                f"Unknown screened source IDs for {family}: {sorted(source_ids - known)}"
            )

    policies = _rd(inputs.crop_scope_policy)
    numeric_policies = {
        r["evidence_id"]: r for r in _rd(inputs.numeric_policy) if r["nbs_id"] == nbs_id
    }
    units = []
    for row in _csv_to_rows(inputs.evidence):
        if row["nbs_id"] != nbs_id:
            continue
        unit_fields: dict[str, Any] = {
            k: value
            for k, value in {"suitability_family_id": "", **row}.items()
            if k in EvidenceUnit.__dataclass_fields__
        }
        units.append(EvidenceUnit(**unit_fields))
    source_context = {
        r["source_id"]: {
            k: r[k]
            for k in ("study_country", "region", "aez", "farming_system")
            if r[k]
        }
        for r in src
    }
    for unit in units:
        if unit.evidence_id in numeric_policies:
            unit.context = {
                **source_context.get(unit.source_id, {}),
                **(unit.context or {}),
            }
    families = sorted(
        {u.suitability_family_id for u in units if u.suitability_family_id}
    )

    out: dict[str, FamilyResult] = {}
    for family in families:
        fam_units = [u for u in units if u.suitability_family_id == family]
        policy = next(
            (
                r
                for r in policies
                if r["nbs_id"] == nbs_id and r["suitability_family_id"] == family
            ),
            None,
        )
        if policy is None:
            policy = next(
                (
                    r
                    for r in policies
                    if r["nbs_id"] == nbs_id and not r["suitability_family_id"]
                ),
                {},
            )
        out[family] = synthesise_family(
            fam_units,
            tiers,
            family=family,
            corpus_n=screened_sources.get(family),
            group_map=group_map,
            canonical_units=canonical_units,
            dataset_ids=dataset_ids,
            categories=categories,
            unit_conversions=unit_conversions,
            floor_pct=20.0,
            allow_crop_scope=policy.get("allow_crop_scope", "").lower() == "true",
            approved_only=approved_only,
            numeric_policies=numeric_policies,
        )
        out[family].support_basis = (
            "explicit_screened_source_membership"
            if family in screened_sources
            else "unknown_screened_source_membership"
        )
    return out


# Fields a person sets on purpose (model design, not evidence synthesis). A re-run must
# never wipe them: they are carried onto the regenerated row for the same variable.
DESIGN_FIELDS = (
    "is_scenario_candidate",
    "scenario_label",
    "scenario_description",
    "has_future_projection",
    "baseline_dataset_id",
    "future_dataset_ids",
)


def _is_synthesised(row: dict[str, str]) -> bool:
    """A row the engine wrote (as opposed to a hand-set design row: an eligibility
    filter, a hard exclusion mask, an M2b scenario lever)."""
    return (row.get("justification") or "").startswith("Reconciled from")


def _existing_rows(f: Path) -> list[dict[str, str]]:
    if not f.exists():
        return []
    return list(csv.DictReader(io.StringIO(f.read_bytes().decode("utf-8"), newline="")))


def write_recipe(
    nbs_id: str,
    results: dict[str, FamilyResult],
    vont_rows: list[dict[str, str]],
    *,
    inputs: T4BuildInputs,
    output_dir: Path,
) -> None:
    if not re.fullmatch(r"[a-z][a-z0-9_]*", nbs_id):
        raise ValueError("Invalid NbS identifier")
    recipe_dir = Path(output_dir)
    recipe_dir.mkdir(parents=True, exist_ok=True)
    existing = _existing_rows(inputs.audited_recipe)
    weights_by_var = {
        (r["suitability_family_id"], r["variable"]): r.get("weight_default", "")
        for r in existing
    }
    design_by_var: dict[tuple[str, str], dict[str, str]] = {}
    for r in existing:
        if any((r.get(k) or "") not in ("", "false") for k in DESIGN_FIELDS):
            design_by_var.setdefault((r["suitability_family_id"], r["variable"]), r)
    ds_by_var = {
        r["canonical_variable_id"]: _first_dataset(r["candidate_dataset_ids"])
        for r in vont_rows
    }

    # Authored, evidence-linked eligibility gates are non-compensatory configuration.
    # Numeric synthesis cannot overwrite a family-specific dataset crosswalk.
    gates = {
        (r["suitability_family_id"], r["variable"]): r
        for r in existing
        if r.get("relationship_type") == "ranked_classes"
        and json.loads(r.get("relationship_params") or "{}").get("mapping_role")
        == "eligibility_gate"
    }
    evidence = {r["evidence_id"]: r for r in _rd(inputs.evidence)}
    for gate in gates.values():
        ids = json.loads(gate.get("evidence_ids") or "[]")
        if not ids:
            raise ValueError(f"Categorical gate lacks evidence: {gate['mapping_id']}")
        for eid in ids:
            unit = evidence.get(eid)
            if (
                unit is None
                or unit["review_state"] == "dropped"
                or unit["reviewer_ok"].lower() != "true"
            ):
                raise ValueError(
                    f"Categorical gate references unapproved/dropped/missing evidence: {eid}"
                )
    csv_rows: list[dict[str, object]] = []
    for family, res in results.items():
        save_family(res, recipe_dir / f"T4_{family}.json")
        for row in res.rows:
            if (family, row["variable"]) in gates:
                continue
            csv_rows.append(
                {
                    "mapping_id": row["mapping_id"],
                    "nbs_id": nbs_id,
                    "dataset_id": ds_by_var.get(row["variable"], ""),
                    "suitability_dimension": row["suitability_dimension"],
                    "relationship_type": row["relationship_type"],
                    "relationship_params": json.dumps(row["relationship_params"]),
                    "uncertainty_pct": row.get("uncertainty_pct", ""),
                    "context_overrides": json.dumps(row.get("context_overrides") or []),
                    "is_scenario_candidate": "false",
                    "scenario_label": "",
                    "scenario_description": "",
                    "has_future_projection": "false",
                    "baseline_dataset_id": "",
                    "future_dataset_ids": "",
                    # Synthesis does not authorise a runtime weighting decision.
                    "weight_default": weights_by_var.get((family, row["variable"]), ""),
                    "weight_adjustable": "true",
                    "justification": row.get("justification", ""),
                    "variable": row["variable"],
                    "suitability_family_id": family,
                    "evidence_ids": json.dumps(row.get("evidence_ids") or []),
                    "n_sources": row.get("n_sources", ""),
                    "corpus_n": row.get("corpus_n", ""),
                    "paper_support_pct": row.get("paper_support_pct", ""),
                }
            )
            carried = design_by_var.get((family, row["variable"]))
            if carried:
                csv_rows[-1].update({k: carried.get(k, "") for k in DESIGN_FIELDS})

    # keep hand-set design rows the engine does not produce (eligibility filters, hard
    # masks, M2b scenario levers); stale synthesised rows are replaced, never kept
    produced = {(str(r["suitability_family_id"]), str(r["variable"])) for r in csv_rows}
    kept = [
        r
        for r in existing
        if not _is_synthesised(r)
        and (r.get("suitability_family_id", ""), r["variable"]) not in produced
    ]
    for row in kept:
        preserved: dict[str, object] = {k: row.get(k, "") for k in T4_FIELDS}
        # Retained design/crosswalk rows have no verified screened-source calculation.
        # Do not perpetuate historical search-total percentages across regeneration.
        preserved["corpus_n"] = ""
        preserved["paper_support_pct"] = ""
        csv_rows.append(preserved)

    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=T4_FIELDS, lineterminator="\n")
    w.writeheader()
    w.writerows(csv_rows)
    (recipe_dir / "T4_suitability_mappings.csv").write_bytes(
        buf.getvalue().encode("utf-8")
    )
