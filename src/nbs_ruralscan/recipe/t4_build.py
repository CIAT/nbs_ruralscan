"""T4 compilation with explicit data, policy, baseline and output paths.

For declared practices, authored settings, design rows and reviewed holds are
independent of the accepted mapping CSV. Legacy snapshots can still be rebuilt.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from copy import deepcopy
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from .table_fields import T4_FIELDS
from ..ingest.source_publication import SourceSnapshot
from .evidence import EvidenceUnit
from .family import FamilyResult, save_family, synthesise_family
from .binding_requirements import (
    matching_input_requirement,
    params as binding_params,
    row_binding_requirement,
)
from .calibration_requirements import calibration_requirement
from ..schema_tools.generate import _coerce, _csv_to_rows
from ..schema_tools.specialist_records import parse_json


T4_JSON_FIELDS = (
    "relationship_params",
    "evidence_ids",
    "context_overrides",
    "future_dataset_ids",
)


def mapping_json(row: dict, field: str):
    """Read an embedded T4 value, rejecting ambiguous keys and nonfinite numbers."""
    try:
        return parse_json(row.get(field) or "null")
    except ValueError as exc:
        raise ValueError(f"Invalid {field} for {row['mapping_id']}: {exc}") from exc


_CONFIG_KINDS = ("authored_mappings", "mapping_settings", "review_holds")
_RELEASE_FLAGS = ("run_policy", "effect_prose")


def _config_rows(path: Path, columns) -> list[dict[str, str]]:
    if path.absolute() != path.resolve() or (
        path.exists() and path.stat().st_nlink != 1
    ):
        raise ValueError(f"Redirected T4 configuration input: {path}")
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, strict=True)
        if reader.fieldnames != list(columns):
            raise ValueError(f"Invalid T4 configuration columns in {path}")
        rows = list(reader)
    if any(None in r or None in r.values() for r in rows):
        raise ValueError(f"Malformed T4 configuration record in {path}")
    return rows


def _declaration(index: Path, nbs_id: str) -> dict[str, bool] | None:
    flags = (*_CONFIG_KINDS, *_RELEASE_FLAGS)
    table = _config_rows(index, ["nbs_id", *flags])
    by_practice = {r["nbs_id"]: r for r in table}
    if len(by_practice) != len(table) or any(
        not re.fullmatch(r"[a-z][a-z0-9_]*", r["nbs_id"])
        or any(r[k] not in {"true", "false"} for k in flags)
        for r in table
    ):
        raise ValueError(f"Invalid practice or file declaration in {index}")
    row = by_practice.get(nbs_id)
    if row is None:
        return None
    return {k: row[k] == "true" for k in flags}


@dataclass(frozen=True)
class T4BuildInputs:
    """Input identity is independent of the executing compiler's installation."""

    evidence: Path
    sources: Path
    ontology: Path
    crop_scope_policy: Path
    numeric_policy: Path
    audited_recipe: Path
    definition_index: Path | None = None
    authored_mappings: Path | None = None
    mapping_settings: Path | None = None
    review_holds: Path | None = None
    family_registry: Path | None = None

    @classmethod
    def from_root(
        cls, root: Path, nbs_id: str, *, require_authored: bool = False
    ) -> T4BuildInputs:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", nbs_id):
            raise ValueError("Invalid NbS identifier")
        schema = Path(root).resolve() / "schema"
        audited = schema / "recipes" / nbs_id / "T4_suitability_mappings.csv"
        folder = schema / "recipe_inputs/t4"
        index = folder / "practices.csv"
        selected = {}
        if folder.exists() or require_authored:
            declared = _declaration(index, nbs_id)
            if declared is None:
                if require_authored or audited.exists() or (folder / nbs_id).exists():
                    raise ValueError(
                        f"T4 inputs are not declared for {nbs_id} in {index}"
                    )
                # Unregistered new recipes can still preview evidence without weights or gates.
            else:
                selected["definition_index"] = index
                selected["family_registry"] = (
                    schema / "registers/FAM_family_registry.csv"
                )
                for name in _CONFIG_KINDS:
                    path = folder / nbs_id / f"{name}.csv"
                    if declared[name]:
                        if not path.is_file():
                            raise FileNotFoundError(
                                f"Missing declared T4 input: {path}"
                            )
                        selected[name] = path
                    elif path.exists():
                        raise ValueError(f"Undeclared T4 configuration file: {path}")
        return cls(
            evidence=schema / "registers/EV_evidence_register.csv",
            sources=schema / "registers/SRC_source_register.csv",
            ontology=schema / "registers/VONT_variable_ontology.csv",
            crop_scope_policy=schema / "lookups/crop_scope_policy.csv",
            numeric_policy=schema / "lookups/t4_numeric_compilation_policy.csv",
            audited_recipe=audited,
            **selected,
        )

    def release_settings(self, nbs_id: str) -> dict[str, bool]:
        """Explicit optional products. Legacy snapshots do not declare release settings."""
        declared = (
            _declaration(self.definition_index, nbs_id)
            if self.definition_index
            else None
        )
        if declared is None:
            raise ValueError(f"Missing release settings for {nbs_id}")
        return {k: declared[k] for k in _RELEASE_FLAGS}

    def authored_paths(self) -> tuple[Path, ...]:
        return tuple(
            path
            for path in (
                self.definition_index,
                self.authored_mappings,
                self.mapping_settings,
                self.review_holds,
            )
            if path is not None
        )

    def compilation_paths(self) -> tuple[Path, ...]:
        """Actual analytical inputs. Legacy snapshots use their mixed mapping CSV."""
        return (
            self.evidence,
            self.sources,
            self.ontology,
            self.crop_scope_policy,
            self.numeric_policy,
            *(
                (self.family_registry,)
                if self.definition_index and self.family_registry
                else ()
            ),
            *(self.authored_paths() or (self.audited_recipe,)),
        )

    def paths(self) -> tuple[Path, ...]:
        """All inputs to an audited rebuild, including the comparison baseline."""
        return tuple(dict.fromkeys((*self.compilation_paths(), self.audited_recipe)))


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
    _, _, holds = _configuration(nbs_id, inputs)
    return _preserve_mapping_review_holds(out, holds)


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


_SETTING_FIELDS = [
    "mapping_id",
    "nbs_id",
    "suitability_family_id",
    "variable",
    "weight_default",
    "weight_adjustable",
    *DESIGN_FIELDS,
]
_AUTHORED_FIELDS = [k for k in T4_FIELDS if k not in {"corpus_n", "paper_support_pct"}]


def _configuration(nbs_id: str, inputs: T4BuildInputs):
    """Return authored full rows, per-variable settings and reviewed hold snapshots."""
    if inputs.definition_index is None:
        if inputs.authored_paths():
            raise ValueError("T4 authored inputs require a practice declaration")
        existing = _existing_rows(inputs.audited_recipe)
        return [r for r in existing if not _is_synthesised(r)], existing, existing

    declared = _declaration(inputs.definition_index, nbs_id)
    if declared is None or any(
        declared[k] != (getattr(inputs, k) is not None) for k in _CONFIG_KINDS
    ):
        raise ValueError(
            f"T4 configuration selection differs from the declaration for {nbs_id}"
        )
    authored = (
        _config_rows(inputs.authored_mappings, _AUTHORED_FIELDS)
        if inputs.authored_mappings
        else []
    )
    settings = (
        _config_rows(inputs.mapping_settings, _SETTING_FIELDS)
        if inputs.mapping_settings
        else []
    )
    holds = _config_rows(inputs.review_holds, T4_FIELDS) if inputs.review_holds else []
    for name, rows in zip(_CONFIG_KINDS, (authored, settings, holds), strict=True):
        if declared[name] and not rows:
            raise ValueError(f"Declared T4 configuration is empty: {name}")
    all_rows = [*authored, *settings, *holds]
    if len({r["mapping_id"] for r in all_rows}) != len(all_rows) or any(
        r["nbs_id"] != nbs_id
        or not r["mapping_id"].strip()
        or not r["variable"].strip()
        or not r["suitability_family_id"].strip()
        for r in all_rows
    ):
        raise ValueError(
            f"Duplicate, incomplete or wrong-practice T4 configuration for {nbs_id}"
        )
    if inputs.family_registry is None:
        raise ValueError("Declared T4 inputs require the family registry")
    families = {
        r["suitability_family_id"]
        for r in _rd(inputs.family_registry)
        if r["nbs_id"] == nbs_id
    }
    variables = {r["canonical_variable_id"] for r in _rd(inputs.ontology)}
    for r in all_rows:
        if r["suitability_family_id"] not in families or r["variable"] not in variables:
            raise ValueError(
                f"Unknown T4 family or variable for {nbs_id}: {r['mapping_id']} "
                f"({r['suitability_family_id']}, {r['variable']})"
            )
        for field in T4_JSON_FIELDS:
            if r.get(field):
                mapping_json(r, field)
        if any(
            r[k] not in {"true", "false"}
            for k in (
                "weight_adjustable",
                "is_scenario_candidate",
                "has_future_projection",
            )
        ):
            raise ValueError(f"Invalid T4 boolean setting for {r['mapping_id']}")
        if r["weight_default"] != "" and not 0 <= float(r["weight_default"]) <= 1:
            raise ValueError(f"Invalid default weight for {r['mapping_id']}")
    if any(
        r["mapping_id"] != f"{r['suitability_family_id']}__{r['variable']}"
        for r in settings
    ):
        raise ValueError(
            "A compiled T4 setting requires the matching family and variable mapping ID"
        )
    authored_scopes = {(r["suitability_family_id"], r["variable"]) for r in authored}
    configured_scopes = [
        (r["suitability_family_id"], r["variable"]) for r in [*settings, *holds]
    ]
    if len(set(configured_scopes)) != len(
        configured_scopes
    ) or authored_scopes.intersection(configured_scopes):
        raise ValueError(
            f"Duplicate T4 settings for the same family and variable in {nbs_id}"
        )
    if any(
        not (row_binding_requirement(r) or calibration_requirement(r)) for r in holds
    ):
        raise ValueError(
            "A reviewed hold snapshot requires a mapping-level binding or calibration hold"
        )
    if any(row_binding_requirement(r) or calibration_requirement(r) for r in authored):
        raise ValueError("Mapping review holds belong in review_holds.csv")
    return authored, all_rows, holds


def _dataset_binding_hold(row: dict[str, Any]) -> str:
    """Honor reviewed row/profile requirements instead of falling back to a proxy."""
    requirement = matching_input_requirement(row)
    return requirement["reason"] if requirement else ""


def _retained_hold_row(baseline, calibration):
    row = {key: _coerce(value) for key, value in baseline.items() if value != ""}
    # The historical number of sources screened is not a denominator for this round.
    row["corpus_n"] = None
    row["paper_support_pct"] = None
    note = (
        "Retained approved calibration hold; no new numeric synthesis or approval."
        if calibration
        else "Retained approved binding hold only; no new numeric synthesis or approval."
    )
    if note not in row.get("justification", ""):
        row["justification"] = (row.get("justification") or "") + " " + note
    return row


def _preserve_mapping_review_holds(results, existing):
    """Keep mapping-specific input/calibration decisions across synthesis rounds.

    An absent held row is retained as blocked configuration, not as newly
    synthesized or approved evidence. Otherwise its hold would disappear and a
    later round could silently restore an ontology candidate or a held response.
    Binding-only holds preserve fresh numerical content. Calibration holds retain
    the reviewed configuration until an explicit superseding decision.
    """
    held = {}
    for row in existing:
        requirement = row_binding_requirement(row)
        calibration = calibration_requirement(row)
        if requirement or calibration:
            if row["mapping_id"] in held:
                raise ValueError("Duplicate mapping review hold")
            held[row["mapping_id"]] = (row, requirement, calibration)
    out = {
        family: replace(res, rows=deepcopy(res.rows)) for family, res in results.items()
    }
    seen = set()
    for family, res in out.items():
        for row in res.rows:
            if row["mapping_id"] in held:
                baseline, requirement, calibration = held[row["mapping_id"]]
                if (
                    baseline["suitability_family_id"] != family
                    or baseline["variable"] != row["variable"]
                ):
                    raise ValueError("Mapping review hold scope changed")
                if calibration:
                    # A new synthesis is not authorization to release a numerical
                    # hold. Retain the reviewed configuration and its source links.
                    # Native source profiles remain in the evidence/audit records.
                    row.clear()
                    row.update(_retained_hold_row(baseline, calibration))
                relationship = deepcopy(binding_params(row))
                adaptation = relationship.setdefault("reviewed_adaptation", {})
                if not isinstance(adaptation, dict):
                    raise ValueError("Invalid reviewed adaptation")
                if requirement:
                    adaptation["dataset_binding"] = deepcopy(requirement)
                row["relationship_params"] = relationship
                seen.add(row["mapping_id"])
    for mapping_id in sorted(held.keys() - seen):
        baseline, _, calibration = held[mapping_id]
        family = baseline["suitability_family_id"]
        out.setdefault(family, FamilyResult(family=family, corpus_n=None)).rows.append(
            _retained_hold_row(baseline, calibration)
        )
    for result in out.values():
        for row in result.rows:
            reason = _dataset_binding_hold(row)
            if reason:
                row["dataset_id"] = ""
                note = "Dataset binding unresolved; requires matching input: " + reason
                if note not in row.get("justification", ""):
                    row["justification"] = (row.get("justification") or "") + " " + note
    return out


def accepted_hold_differences(inputs: T4BuildInputs) -> list[str]:
    """Accepted mapping-level decisions that are absent or different in authored configuration."""
    if inputs.definition_index is None:
        raise ValueError("Hold reconciliation requires declared authored T4 inputs")

    def decisions(rows):
        result = {}
        for row in rows:
            params = mapping_json(row, "relationship_params") or {}
            reviewed = {**row, "relationship_params": params}
            if row_binding_requirement(reviewed) or calibration_requirement(reviewed):
                key = row["mapping_id"]
                if key in result:
                    raise ValueError(f"Duplicate mapping review hold: {key}")
                result[key] = (
                    row["nbs_id"],
                    row["suitability_family_id"],
                    row["variable"],
                    json.dumps(
                        params["reviewed_adaptation"], sort_keys=True, allow_nan=False
                    ),
                )
        return result

    approved = decisions(
        _config_rows(inputs.audited_recipe, T4_FIELDS)
        if inputs.audited_recipe.exists()
        else []
    )
    authored = decisions(
        _config_rows(inputs.review_holds, T4_FIELDS) if inputs.review_holds else []
    )
    return sorted(k for k, decision in approved.items() if authored.get(k) != decision)


def write_recipe(
    nbs_id: str,
    results: dict[str, FamilyResult],
    vont_rows: list[dict[str, str]],
    *,
    inputs: T4BuildInputs,
    output_dir: Path,
    supersede_holds_from: str | None = None,
) -> None:
    if not re.fullmatch(r"[a-z][a-z0-9_]*", nbs_id):
        raise ValueError("Invalid NbS identifier")
    recipe_dir = Path(output_dir)
    output = recipe_dir / "T4_suitability_mappings.csv"
    in_place = output.resolve() == inputs.audited_recipe.resolve()
    if supersede_holds_from is not None and (
        not in_place or inputs.definition_index is None
    ):
        raise ValueError(
            "Superseding accepted holds requires an in-place build with authored inputs"
        )
    watched = (
        SourceSnapshot.capture([output])
        if in_place and inputs.definition_index is not None
        else None
    )
    authored, existing, holds = _configuration(nbs_id, inputs)
    if watched:
        if supersede_holds_from is not None:
            if (
                not inputs.audited_recipe.is_file()
                or hashlib.sha256(inputs.audited_recipe.read_bytes()).hexdigest()
                != supersede_holds_from
            ):
                raise ValueError(
                    "The supplied SHA-256 differs from the accepted mapping; review the current baseline"
                )
        else:
            different = accepted_hold_differences(inputs)
            if different:
                raise ValueError(
                    "Unreconciled accepted T4 review holds: "
                    + ", ".join(different)
                    + ". Reconcile review_holds.csv or review an isolated candidate before superseding the accepted holds."
                )
        watched.assert_unchanged()
    recipe_dir.mkdir(parents=True, exist_ok=True)
    results = _preserve_mapping_review_holds(results, holds)
    # A non-compensatory exclusion may coexist with a score for the same variable.
    assessed_exclusions = [
        r
        for r in authored
        if (params := mapping_json(r, "relationship_params") or {}).get("mapping_role")
        == "hard_exclusion"
        and "input_contract" in params
    ]
    scoring_settings = [r for r in existing if r not in assessed_exclusions]
    adjustable_by_var = {
        (r["suitability_family_id"], r["variable"]): r.get("weight_adjustable", "true")
        for r in scoring_settings
        if inputs.definition_index is not None
        or row_binding_requirement(r)
        or calibration_requirement(r)
    }
    weights_by_var = {
        (r["suitability_family_id"], r["variable"]): r.get("weight_default", "")
        for r in scoring_settings
    }
    design_by_var: dict[tuple[str, str], dict[str, str]] = {}
    for r in scoring_settings:
        if any((r.get(k) or "") not in ("", "false") for k in DESIGN_FIELDS):
            design_by_var.setdefault((r["suitability_family_id"], r["variable"]), r)
    ds_by_var = {
        r["canonical_variable_id"]: _first_dataset(r["candidate_dataset_ids"])
        for r in vont_rows
    }

    # Authored, evidence-linked eligibility gates are non-compensatory configuration.
    # Numeric synthesis cannot overwrite a family-specific dataset crosswalk.
    gate_rows = [
        r
        for r in authored
        if r.get("relationship_type") == "ranked_classes"
        and json.loads(r.get("relationship_params") or "{}").get("mapping_role")
        == "eligibility_gate"
    ]
    gates = {(r["suitability_family_id"], r["variable"]) for r in gate_rows}
    evidence = {r["evidence_id"]: r for r in _rd(inputs.evidence)}
    for gate in gate_rows + assessed_exclusions:
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
                    "dataset_id": ""
                    if _dataset_binding_hold(row)
                    else ds_by_var.get(row["variable"], ""),
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
                    "weight_adjustable": adjustable_by_var.get(
                        (family, row["variable"]), "true"
                    ),
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
        for r in authored
        if r in assessed_exclusions
        or (r.get("suitability_family_id", ""), r["variable"]) not in produced
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
    compiled = buf.getvalue().encode("utf-8")
    if watched:
        watched.publish({output: compiled}, lambda _: watched.assert_unchanged())
    else:
        output.write_bytes(compiled)
