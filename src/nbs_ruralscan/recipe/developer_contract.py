"""Build a derived developer contract from a verified corpus regeneration.

No raster acquisition, review decisions, or new analytical defaults are made here.
The authoritative source is the CSV corpus, compilation policies and recipe design.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import subprocess
import tempfile
import os
from collections import Counter
from pathlib import Path

from .developer_corpus import rebuild
from .run_policy import compile_policies, reference_scores
from .harmonization import harmonize
from .importance import compare_importance, load_weight_models
from .evidence import EvidenceUnit
from .numeric_bands import source_completion
from .inclusion import inclusion_estimates
from ..runtime.binding import Binding, resolve_binding
from ..runtime.categorical import evaluate_categorical
from ..runtime.numeric import evaluate_numeric

VERSION = "0.2.0"
PACKAGE_VERSION = "0.1.4"


def read_csv(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def obj(value, default=None):
    return json.loads(value) if isinstance(value, str) and value else value or default


def stable_json(value):
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        + "\n"
    )


def fingerprint(value):
    return hashlib.sha256(stable_json(value).encode()).hexdigest()


def country_labels(context):
    """Exact recorded country tokens, never substring or inferred ISO matching."""
    raw = obj(context, {}).get("study_country", "")
    values = raw if isinstance(raw, list) else [raw]
    return sorted(
        {
            str(part).strip()
            for value in values
            for part in re.split(r"[;,|]", str(value))
            if part.strip()
        }
    )


def study_context(unit, source):
    return {
        "study_country": source.get("study_country", ""),
        **obj(unit.get("context"), {}),
    }


def country_match(context, countries):
    return not countries or bool(
        {c.casefold() for c in country_labels(context)}
        & {c.casefold() for c in countries}
    )


def _binding(variable, recipe_dataset, bindings, catalog, ontology, contexts):
    note, used, resolution = "Recipe fallback; no matching BIND row", None, None
    # Refuse ambiguous best matches rather than relying on CSV row order.
    candidates = [
        b
        for b in bindings
        if b.variable == variable
        and (b.scope_type == "global" or b.scope_id in contexts)
    ]
    ranks = {(b.specificity, b.preference_rank) for b in candidates}
    if any(
        len(
            {
                (b.dataset_id, b.band, b.status)
                for b in candidates
                if (b.specificity, b.preference_rank) == rank
            }
        )
        > 1
        for rank in ranks
    ):
        raise ValueError(
            f"Ambiguous BIND precedence for {variable}: review matching ranks"
        )
    try:
        resolution = resolve_binding(
            sorted(bindings, key=lambda b: b.binding_id), variable, contexts
        )
        used = resolution.fell_back_to or resolution.winning_binding
        dataset_id = resolution.dataset_id
        note = resolution.prompt or used.fitness_note
    except KeyError:
        dataset_id = recipe_dataset or None
    ds = catalog.get(dataset_id, {})
    ont = ontology.get(variable, {})
    documented = (
        obj(ds.get("access_params"), {}).get("variable_inputs", {}).get(variable)
    )
    return {
        "dataset_id": dataset_id,
        "recipe_dataset_id": recipe_dataset or None,
        "binding_id": used.binding_id if used else None,
        "preferred_binding_id": resolution.winning_binding.binding_id
        if resolution
        else None,
        "band": used.band or None if used else None,
        "asset": ds.get("gee_asset_id") or ds.get("download_url") or None,
        "documented_input": documented,
        "access_type": ds.get("access_type"),
        "native_resolution_m": ds.get("spatial_resolution_m") or None,
        "time_period": ds.get("time_period") or None,
        "source_unit": None,
        "canonical_unit": ont.get("canonical_unit") or None,
        "scale_offset": None,
        "temporal_reducer": None,
        "source_unit_status": "Consumer must verify native band units and scaling; canonical units are not native units",
        "derive_then_aggregate": ont.get("derive_then_aggregate", "").lower() == "true",
        "min_meaningful_resolution_m": ont.get("min_meaningful_resolution_m") or None,
        "needs_upload": resolution.needs_upload if resolution else dataset_id is None,
        "prompt": note,
        "limitations": ds.get("limitations", ""),
        "preparation": [ds["preprocessing_notes"]]
        if ds.get("preprocessing_notes")
        else [],
        "binding_differs_from_recipe": bool(
            recipe_dataset and dataset_id != recipe_dataset
        ),
        "access_validation": "Not fetched; developer dataset_access.csv must identify representation, band, scaling and temporal reduction",
    }


def _options(row, evidence, sources, countries):
    params = obj(row["relationship_params"], {})
    profiles = [
        p
        for p in params.get("profiles", [])
        if country_match(p.get("context", {}), countries)
    ]
    options: list[dict] = []
    for p in profiles:
        options.append(
            {
                **(
                    {"source_completions": p["source_completions"]}
                    if p.get("source_completions")
                    else {}
                ),
                "function_id": "profile:" + p["profile_id"],
                "kind": "source_profile",
                "label": p["source_id"],
                "unit": p["unit"],
                "intervals": p["intervals"],
                "parameters": {
                    "outside_domain": "unknown",
                    "conflicting_boundaries": "unknown",
                    "interpolation": "none",
                },
                "context": p.get("context", {}),
                "context_id": p.get("context_id", ""),
                "system_id": p.get("system_id") or row["suitability_family_id"],
                "evidence_ids": p.get("evidence_ids", [p["evidence_id"]]),
                "source_ids": [p["source_id"]],
                "origin_ids": [p["origin_id"]],
                "applicability_note": p.get("applicability_note", ""),
                "score_policy": p.get("score_policy"),
            }
        )
    # A filtered pool is recomputed from retained members; never copy its full-corpus scores.
    for pool in harmonize(profiles)["pools"]:
        members = [p for p in profiles if p["profile_id"] in pool["profile_ids"]]
        options.append(
            {
                "function_id": "pool:" + pool["pool_id"],
                "kind": "harmonized_pool",
                "label": "Compatible evidence combined: "
                + ", ".join(sorted({p["source_id"] for p in members})),
                "unit": members[0]["unit"],
                "intervals": pool["cells"],
                "parameters": {
                    "outside_domain": "unknown",
                    "conflicting_boundaries": "unknown",
                    "interpolation": "none",
                    "pool": pool,
                },
                "context": {
                    "study_country": sorted(
                        {
                            c
                            for p in members
                            for c in country_labels(p.get("context", {}))
                        }
                    )
                },
                "context_id": pool["context_id"],
                "system_id": pool["system_id"],
                "evidence_ids": sorted(
                    {
                        eid
                        for p in members
                        for eid in p.get("evidence_ids", [p["evidence_id"]])
                    }
                ),
                "source_ids": sorted({p["source_id"] for p in members}),
                "origin_ids": sorted({p["origin_id"] for p in members}),
                "applicability_note": "Conditional scoping pool; explicit target applicability decision required",
                "score_policy": pool["score_policy"],
            }
        )
    if "class_map" in params:
        options.append(
            {
                "function_id": "configured:" + row["mapping_id"],
                "kind": "categorical_gate",
                "label": "Reviewed host eligibility rule",
                "unit": "dataset class code",
                "intervals": [],
                "parameters": params,
                "context": {},
                "evidence_ids": obj(row["evidence_ids"], []),
                "source_ids": sorted(
                    {evidence[e]["source_id"] for e in obj(row["evidence_ids"], [])}
                ),
                "applicability_note": "Authored system gate retained independently of the evidence-country filter",
            }
        )
    elif row["relationship_type"] == "threshold" and isinstance(
        params.get("threshold"), (int, float)
    ):
        band_ids = {
            eid
            for p in params.get("profiles", [])
            for eid in p.get("evidence_ids", [p["evidence_id"]])
        }
        ids = sorted(set(obj(row["evidence_ids"], [])) - band_ids)
        if ids and all(
            country_match(
                study_context(evidence[e], sources[evidence[e]["source_id"]]), countries
            )
            for e in ids
        ):
            cut, above = params["threshold"], params["above_is_suitable"]
            intervals = [
                {
                    "lower": None,
                    "upper": cut,
                    "lower_inclusive": False,
                    "upper_inclusive": not above,
                    "score": 0 if above else 1,
                },
                {
                    "lower": cut,
                    "upper": None,
                    "lower_inclusive": above,
                    "upper_inclusive": False,
                    "score": 1 if above else 0,
                },
            ]
            options.append(
                {
                    "function_id": "typed:" + row["mapping_id"],
                    "kind": "numeric_threshold",
                    "label": "Separate synthesized binary response (not a legal mask)",
                    "unit": None,
                    "intervals": intervals,
                    "parameters": {"threshold": cut, "above_is_suitable": above},
                    "context": {
                        "study_country": sorted(
                            {
                                c
                                for e in ids
                                for c in country_labels(
                                    study_context(
                                        evidence[e], sources[evidence[e]["source_id"]]
                                    )
                                )
                            }
                        )
                    },
                    "evidence_ids": ids,
                    "source_ids": sorted({evidence[e]["source_id"] for e in ids}),
                    "applicability_note": "Alternative to graded source profiles; never selected implicitly",
                }
            )
    for option in options:
        linked = set(option["evidence_ids"])
        missing = []
        for unit in evidence.values():
            parent = obj(unit.get("context"), {}).get("table_continuation_of")
            if parent in linked and unit["evidence_id"] not in linked:
                missing.append(
                    {
                        "evidence_id": unit["evidence_id"],
                        "page": unit.get("page"),
                        "relationship": obj(unit.get("relationship"), {}),
                        "review_state": unit.get("review_state")
                        or (
                            "approved"
                            if str(unit.get("reviewer_ok")).lower() == "true"
                            else "awaiting_review"
                        ),
                    }
                )
        option["completeness"] = {
            "status": "partial" if missing else "no_known_missing_continuation",
            "missing_continuations": sorted(missing, key=lambda u: u["evidence_id"]),
        }
    return sorted(options, key=lambda o: o["function_id"])


def _fixture(option):
    """Exact breakpoints, adjacent samples and NaN; evaluation uses existing executor."""
    bands = option["intervals"]
    if not bands:
        return None
    breaks = sorted(
        {b[k] for b in bands for k in ("lower", "upper") if b[k] is not None}
    )
    values = set(breaks)
    for x in breaks:
        values.update((math.nextafter(x, -math.inf), math.nextafter(x, math.inf)))
    values.update((a + b) / 2 for a, b in zip(breaks, breaks[1:]))
    if breaks:
        values.update(
            (breaks[0] - max(1, abs(breaks[0])), breaks[-1] + max(1, abs(breaks[-1])))
        )
    raw = sorted(values) + [float("nan")]
    row = {
        "relationship_type": "piecewise",
        "relationship_params": {
            "profiles": [{"profile_id": option["function_id"], "intervals": bands}]
        },
    }
    result = evaluate_numeric(row, raw, profile_id=option["function_id"])
    return {
        "function_id": option["function_id"],
        "input": [None if math.isnan(x) else x for x in raw],
        "expected": [None if math.isnan(x) else float(x) for x in result],
        "null_semantics": "JSON null maps to unknown/NaN; intervals are stepwise, never interpolated",
    }


def _gate_fixtures(row, option, evidence):
    """Synthetic classes and host states, evaluated by the existing gate contract."""
    import numpy as np

    params = option["parameters"]
    codes = sorted(float(c) for c in params["class_map"])
    codes += [max(codes) + 1, float("nan")]
    names = sorted(
        {
            name
            for names in params.get("class_requirements", {}).values()
            for name in names
        }
    )
    meta = {
        name: {
            "dataset_id": "synthetic_conformance_input",
            "source_reference": "Generated array fixture; no geographic observation",
            **{
                k: v[0] if isinstance(v, list) else v
                for k, v in params.get("required_mask_metadata", {})
                .get(name, {})
                .items()
            },
        }
        for name in names
    }
    result = []
    for state, value in (
        ("host_present", 1.0),
        ("host_absent", 0.0),
        ("host_unknown", float("nan")),
    ):
        masks = {name: np.full(len(codes), value) for name in names}
        score = evaluate_categorical(
            row,
            codes,
            dataset_id=row["dataset_id"],
            masks=masks,
            mask_metadata=meta,
            evidence=evidence,
        )
        result.append(
            {
                "rule_id": row["mapping_id"],
                "function_id": option["function_id"],
                "case": state,
                "dataset_id": row["dataset_id"],
                "input": [None if math.isnan(v) else v for v in codes],
                "host_masks": {
                    name: [None if math.isnan(v) else float(v) for v in values]
                    for name, values in masks.items()
                },
                "mask_metadata": meta,
                "expected": [None if math.isnan(v) else float(v) for v in score.values],
                "expected_status": score.status.tolist(),
                "null_semantics": "JSON null maps to unknown/NaN; missing host data affects only classes which require it",
            }
        )
    return result


def build_contract(
    root,
    *,
    nbs="agroforestry",
    country=None,
    evidence_countries=(),
    contexts=(),
    selection: dict | None = None,
):
    root = Path(root)
    if not re.fullmatch(r"[a-z][a-z0-9_]*", nbs):
        raise ValueError("Invalid NbS identifier")
    if country is not None and not re.fullmatch(r"[A-Z]{3}", country):
        raise ValueError(
            "Target country must use its three-letter uppercase BIND country identifier, e.g. HTI"
        )
    corpus = rebuild(root, nbs)
    evidence = {r["evidence_id"]: r for r in corpus["evidence"]}
    completion_policies = {
        r["evidence_id"]: r
        for r in read_csv(root / "schema/lookups/t4_numeric_compilation_policy.csv")
    }
    completion_units = {}
    for eid, raw_unit in evidence.items():
        if eid not in completion_policies:
            continue
        typed = {
            k: v for k, v in raw_unit.items() if k in EvidenceUnit.__dataclass_fields__
        }
        for key in ("relationship", "context"):
            typed[key] = obj(typed.get(key), {})
        typed["reviewer_ok"] = str(typed.get("reviewer_ok")).lower() == "true"
        typed["page"] = int(typed["page"]) if typed.get("page") else None
        completion_units[eid] = EvidenceUnit(**typed)
    sources = {r["source_id"]: r for r in corpus["sources"]}
    inputs = list(corpus["inputs"])

    def load(path):
        inputs.append(path)
        return read_csv(root / path)

    ontology = {
        r["canonical_variable_id"]: r
        for r in load("schema/registers/VONT_variable_ontology.csv")
    }
    catalog = {r["dataset_id"]: r for r in load("schema/T1_data_registry.csv")}
    bindings = [
        Binding(**(r | {"preference_rank": int(r["preference_rank"])}))
        for r in load("schema/registers/BIND_dataset_binding.csv")
    ]
    families = load("schema/registers/FAM_family_registry.csv")
    geographic = load("schema/T7_geographic_context.csv")
    allowed_contexts = {r["context_id"] for r in geographic} | {
        b.scope_id for b in bindings if b.scope_type != "global"
    }
    if set(contexts) - allowed_contexts:
        raise ValueError(
            f"Unknown geographic contexts: {sorted(set(contexts) - allowed_contexts)}"
        )
    target_contexts = set(contexts) | ({country} if country else set())
    labels = sorted(
        {
            c
            for u in evidence.values()
            if u["nbs_id"] == nbs
            for c in country_labels(study_context(u, sources[u["source_id"]]))
        }
    )
    by_label = {c.casefold(): c for c in labels}
    if any(c.casefold() not in by_label for c in evidence_countries):
        raise ValueError(
            "Unknown evidence-country label; use exact recorded name from --list-evidence-countries, not an inferred ISO code"
        )
    evidence_countries = sorted({by_label[c.casefold()] for c in evidence_countries})
    cohort = [
        u
        for u in evidence.values()
        if u["nbs_id"] == nbs
        and country_match(study_context(u, sources[u["source_id"]]), evidence_countries)
    ]
    inclusion = inclusion_estimates(cohort, sources, ontology, nbs)
    selection = selection or {"contract_version": VERSION, "selections": {}}
    if (
        set(selection) - {"contract_version", "selections"}
        or selection.get("contract_version") != VERSION
        or not isinstance(selection.get("selections"), dict)
    ):
        raise ValueError(
            "Selection document requires contract_version and selections only"
        )
    unknown = set(selection["selections"]) - {r["mapping_id"] for r in corpus["rows"]}
    if unknown:
        raise ValueError(f"Unknown selected mapping IDs: {sorted(unknown)}")
    rows, fixtures = [], []
    for raw in corpus["rows"]:
        params, ont = (
            obj(raw["relationship_params"], {}),
            ontology.get(raw["variable"], {}),
        )
        system, rule_id = raw["suitability_family_id"], raw["mapping_id"]
        operational = raw.get("is_scenario_candidate", "").lower() == "true"
        role = (
            "operational_scenario"
            if operational
            else "eligibility_gate"
            if "class_map" in params
            else "suitability_score"
            if params.get("profiles")
            else "hard_exclusion"
        )
        options = _options(raw, evidence, sources, evidence_countries)
        for option in options:
            option["unit"] = option.get("unit") or ont.get("canonical_unit")
            option["fingerprint"] = fingerprint(option)
            fixture = _fixture(option)
            if fixture:
                fixtures.append({"rule_id": rule_id, **fixture})
            if option["kind"] == "categorical_gate":
                fixtures.extend(_gate_fixtures(raw, option, evidence))
        pick = selection["selections"].get(rule_id, {})
        if set(pick) - {
            "function_id",
            "function_fingerprint",
            "target_system",
            "applicability_country",
            "applicability_note",
            "decision_reference",
            "runtime_weight",
        }:
            raise ValueError(f"Unsupported selection fields for {rule_id}")
        selected = next(
            (o for o in options if o["function_id"] == pick.get("function_id")), None
        )
        blockers, notes = [], []
        applicability = "not_selected"
        if pick:
            if (
                selected is None
                or pick.get("function_fingerprint") != selected["fingerprint"]
            ):
                raise ValueError(
                    f"Missing or stale function selection for {rule_id}; regenerate template"
                )
            if selected["completeness"]["status"] == "partial":
                raise ValueError(
                    f"Incomplete source function: resolve table continuation for {rule_id}"
                )
            if (
                not pick.get("decision_reference")
                or not pick.get("applicability_note")
                or pick.get("applicability_country") != country
            ):
                raise ValueError(
                    f"Selection needs matching target country, applicability note and decision reference: {rule_id}"
                )
            chosen_system = pick.get("target_system")
            named = {
                f["suitability_family_id"]
                for f in families
                if f["nbs_id"] == nbs
                and "cross_family" not in f["suitability_family_id"]
            }
            if chosen_system not in named or (
                "cross_family" not in system and chosen_system != system
            ):
                raise ValueError(f"Invalid target system for {rule_id}")
            applicability = "explicit_decision_recorded"
        elif role == "eligibility_gate":
            selected = options[0]
            applicability = "recipe_host_design"
        elif role == "suitability_score":
            blockers.append(
                "Choose one response option and record its applicability to the target system and context"
            )
            if not options:
                blockers.append(
                    "No numeric response survives the evidence-country filter"
                )
        elif operational:
            blockers.append(
                "Configured 0–1 scenario endpoints are placeholders; raw-variable scale, direction and operational combination need confirmation"
            )
        else:
            blockers.append(
                "Supply an assessed legal-exclusion mask with target rules, provenance and coverage; protected-area category alone is insufficient"
                if params.get("legal_mask_contract")
                else "Legal category threshold requires explicit category adapter and system coverage decision"
            )
        if any(o["completeness"]["status"] == "partial" for o in options):
            notes.append(
                "An incomplete source option is shown for inspection only; resolve its table continuation before selection"
            )
        if "cross_family" in system and not pick:
            blockers.append(
                "System applicability unresolved; never inherit this rule into every system automatically"
            )
        dataset = _binding(
            raw["variable"],
            raw["dataset_id"],
            bindings,
            catalog,
            ontology,
            target_contexts,
        )
        if dataset["dataset_id"] and dataset["dataset_id"] not in catalog:
            raise ValueError(f"Dataset absent from T1: {dataset['dataset_id']}")
        if dataset["binding_differs_from_recipe"]:
            blockers.append(
                "BIND selects a different dataset from the recipe; verify variable, band, unit and temporal equivalence before execution"
            )
        if dataset["dataset_id"] is None:
            blockers.append("Dataset or local upload is required")
        dependencies = {}
        for name, spec in params.get("host_bindings", {}).items():
            required = spec.get("variables", [])
            dependencies[name] = {
                "spec": spec,
                "inputs": {
                    v: _binding(v, "", bindings, catalog, ontology, target_contexts)
                    for v in required + spec.get("supporting_variables", [])
                },
            }
            if any(
                dependencies[name]["inputs"][v]["dataset_id"] is None for v in required
            ):
                notes.append(
                    f"{name}: local input required only on the classes which reference it; other classes remain evaluable"
                )
        weight = pick.get("runtime_weight")
        if weight is not None and (
            role != "suitability_score"
            or isinstance(weight, bool)
            or not isinstance(weight, (int, float))
            or not math.isfinite(weight)
            or not 0 <= weight <= 1
        ):
            raise ValueError(f"Invalid runtime weight for {rule_id}")
        if role == "suitability_score" and weight is None:
            notes.append(
                "Final criterion set and normalized runtime weight remain a run-level decision"
            )
        linked = obj(raw["evidence_ids"], [])
        for eid in linked:
            u = evidence.get(eid)
            if (
                not u
                or u["review_state"] == "dropped"
                or (
                    u["reviewer_ok"].lower() != "true"
                    and not (
                        eid in completion_units
                        and source_completion(
                            completion_units[eid], completion_units, completion_policies
                        )
                    )
                )
            ):
                raise ValueError(
                    f"Recipe links unapproved, dropped or missing evidence: {eid}"
                )
        notes.append(
            "Native units, scaling, time reduction and data access must be verified in the developer's dataset adapter"
        )
        if evidence_countries and role != "suitability_score":
            notes.append(
                "Authored host/legal/scenario design retained independently of the study-country filter"
            )
        rows.append(
            {
                "rule_id": rule_id,
                "nbs": nbs,
                "system": system,
                "target_system": pick.get("target_system", system),
                "practices": [
                    f["name"] for f in families if f["suitability_family_id"] == system
                ],
                "spatial_product_types": sorted(
                    {
                        f["spatial_product_type"]
                        for f in families
                        if f["suitability_family_id"] == system
                    }
                ),
                "theme": raw["suitability_dimension"].replace("_constraint", ""),
                "variable_group": ont.get("group_id", "unmapped"),
                "variable": raw["variable"],
                "unit": ont.get("canonical_unit"),
                "module": "M2b" if operational else "M1",
                "role": role,
                "function_id": selected["function_id"] if selected else None,
                "function_type": selected["kind"]
                if selected
                else "selection_required"
                if options
                else "unresolved",
                "function_options": options,
                "declared_relationship": {
                    "type": raw["relationship_type"],
                    "params": {
                        k: v
                        for k, v in params.items()
                        if k not in {"profiles", "harmonization"}
                    },
                },
                "context_overrides": obj(raw.get("context_overrides"), []),
                "dataset": dataset,
                "host_inputs": dependencies,
                "gate_input_contract": params.get("input_contract")
                or params.get("legal_mask_contract"),
                "weight": {
                    "configured_default": float(raw["weight_default"])
                    if raw.get("weight_default")
                    else None,
                    "basis": "Equal-weight synthesis placeholder; not evidence-derived"
                    if role == "suitability_score"
                    else "Excluded from core weighted overlay",
                    "runtime_weight": weight,
                },
                "status": "blocked" if blockers else "conditional",
                "blockers": blockers,
                "notes": notes,
                "applicability_status": applicability,
                "selection_decision": pick or None,
                "evidence_ids": linked,
                "selected_evidence_ids": selected["evidence_ids"] if selected else [],
                "unknown_policy": "Propagate unknown; do not fill, extrapolate or renormalize missing criteria",
                "exclusion_policy": "Masks remain separate; zero suitability score is not a legal exclusion",
            }
        )
    # Retain operational variables without executable mappings; never silently drop them.
    configured = {r["variable"] for r in rows if r["module"] == "M2b"}
    operational = [
        u
        for u in cohort
        if u["use_role"] == "operational_risk" and u["review_state"] != "dropped"
    ]
    for variable in sorted({u["variable"] for u in operational} - configured):
        members = [u for u in operational if u["variable"] == variable]
        ont = ontology.get(variable, {})
        rows.append(
            {
                "rule_id": f"reference__{nbs}__{variable}",
                "nbs": nbs,
                "system": "See evidence contexts",
                "target_system": None,
                "theme": "operational",
                "variable_group": ont.get("group_id", "unmapped"),
                "variable": variable,
                "unit": ont.get("canonical_unit"),
                "module": "M2b",
                "role": "reference_only",
                "function_id": None,
                "function_type": "not_calibrated",
                "function_options": [],
                "dataset": _binding(
                    variable, "", bindings, catalog, ontology, target_contexts
                ),
                "host_inputs": {},
                "weight": {
                    "configured_default": None,
                    "basis": "Evidence only; no runtime weight",
                    "runtime_weight": None,
                },
                "status": "reference_only",
                "blockers": [
                    "No configured executable response; retain variable use, direction and importance as evidence"
                ],
                "notes": [],
                "evidence_ids": sorted(u["evidence_id"] for u in members),
                "selected_evidence_ids": [],
            }
        )
    selected_scores = [
        r for r in rows if r["role"] == "suitability_score" and r["function_id"]
    ]
    selected_keys = [(r["target_system"], r["variable"]) for r in selected_scores]
    if len(selected_keys) != len(set(selected_keys)):
        raise ValueError(
            "Duplicate selected criterion: choose one mapping/function per target system and variable"
        )
    for system in {r["target_system"] for r in selected_scores}:
        weights = [
            r["weight"]["runtime_weight"]
            for r in selected_scores
            if r["target_system"] == system
        ]
        if any(w is not None for w in weights) and (
            None in weights
            or not math.isclose(
                sum(w for w in weights if w is not None), 1, abs_tol=1e-9
            )
        ):
            raise ValueError(
                f"Selected weights for {system} must all be supplied and sum to one"
            )
    decisions = [
        {
            "rule_id": r["rule_id"],
            "module": r["module"],
            "issues": r["blockers"],
            "implementation_requirements": r["notes"],
        }
        for r in rows
    ]
    # Weight diagnostics are rebuilt from source trees, never copied from old report CSVs.
    importance, importance_path = (
        [],
        "pipeline/t4_audit/agroforestry/importance_2026-10-21/source_weight_trees.csv",
    )
    if nbs == "agroforestry":
        inputs.append(importance_path)
        for model in load_weight_models(root / importance_path):
            sid = model["source_id"]
            if country_match(
                {"study_country": sources.get(sid, {}).get("study_country", "")},
                evidence_countries,
            ):
                importance.append(
                    {
                        "model_id": model["model_id"],
                        "source_id": sid,
                        "provenance": model["provenance"],
                        **compare_importance(model),
                    }
                )
    for row in rows:
        row["soil_input_reviews"] = [
            {
                "evidence_id": eid,
                "source_id": evidence[eid]["source_id"],
                **obj(evidence[eid].get("context"), {})["soil_input_review"],
            }
            for eid in row["evidence_ids"]
            if obj(evidence[eid].get("context"), {}).get("soil_input_review")
        ]
        row["study_use"] = [
            item
            for item in inclusion
            if item["system"] == "all_systems"
            and item["claim_scope"] == "practice_technology"
            and item["module"] == row["module"]
            and item["group"] == row["variable_group"]
            and (item["level"] == "group" or item["variable"] == row["variable"])
        ]
        row["source_importance"] = [
            {"model_id": model["model_id"], "source_id": model["source_id"], **item}
            for model in importance
            for item in model["variables"]
            if item["variable"] == row["variable"]
        ]
    accountability = []
    referenced = {eid for r in rows for eid in r["evidence_ids"]}
    for u in evidence.values():
        if u["nbs_id"] != nbs or (
            u["use_role"] not in {"structural_suitability", "operational_risk"}
            and u["evidence_id"] not in referenced
        ):
            continue
        accountability.append(
            {
                **u,
                "study_countries": country_labels(
                    study_context(u, sources[u["source_id"]])
                ),
                "matches_evidence_country": country_match(
                    study_context(u, sources[u["source_id"]]), evidence_countries
                ),
                "linked_mapping_ids": sorted(
                    r["rule_id"] for r in rows if u["evidence_id"] in r["evidence_ids"]
                ),
                "function_ids": sorted(
                    o["function_id"]
                    for r in rows
                    for o in r["function_options"]
                    if u["evidence_id"] in o["evidence_ids"]
                ),
                "citation": sources[u["source_id"]]["citation"],
            }
        )
    policy_path = f"schema/recipes/{nbs}/T4_run_policy.csv"
    policies = (
        compile_policies(load(policy_path), rows)
        if (root / policy_path).exists()
        else []
    )
    policy_fixtures = []
    for policy in policies:
        # Synthetic scores exercise the approved policy, not a geographic transfer.
        values = [0.25] + [0.9] * (len(policy["criteria"]) - 1)
        scores = dict(zip((c["rule_id"] for c in policy["criteria"]), values))
        for host, excluded, fraction in [
            (True, False, 0.3),
            (False, False, None),
            (None, False, None),
            (True, True, None),
            (True, None, None),
        ]:
            policy_fixtures.append(
                {
                    "policy_id": policy["policy_id"],
                    "scores": scores,
                    "host": host,
                    "excluded": excluded,
                    "eligible_fraction": fraction,
                    "expected": reference_scores(
                        policy,
                        scores,
                        host=host,
                        excluded=excluded,
                        eligible_fraction=fraction,
                    ),
                }
            )
        missing: dict[str, float | None] = dict(scores)
        missing[next(iter(missing))] = None
        policy_fixtures.append(
            {
                "policy_id": policy["policy_id"],
                "scores": missing,
                "host": True,
                "excluded": False,
                "eligible_fraction": None,
                "expected": reference_scores(
                    policy, missing, host=True, excluded=False
                ),
            }
        )
    contract = {
        "version": VERSION,
        "nbs": nbs,
        "target_country": country,
        "contexts": sorted(target_contexts),
        "evidence_countries": evidence_countries,
        "available_evidence_countries": labels,
        "country_filter_semantics": "Exact recorded country tokens, case-insensitive, OR across repeated flags. No inferred aliases: India and IND can select different records; include both explicitly. Missing geography remains unknown. Study country does not establish target applicability.",
        "rows": rows,
        "selection": selection,
        "summary": {
            "configured_rows": len(corpus["rows"]),
            "display_rows": len(rows),
            "functions": sum(len(r["function_options"]) for r in rows),
            "statuses": dict(Counter(r["status"] for r in rows)),
            "raster_validation": "Not run; Diego and Brayden own implementation and pilot testing",
        },
        "run_contract": {
            "execution_ready": False,
            "baseline": "Current CIAT implementation: weighted linear combination plus separate gates; original minimum-factor design differs",
            "aggregation_selection": "Approved policies below fix analytical choices; target applicability and input readiness remain separate",
            "approved_policies": policies,
            "criteria": "Select one function per system and canonical criterion; resolve correlated groups before assigning weights",
            "weight_validation": "Final selected nonnegative M1 score weights sum to one; masks and operational factors excluded",
            "missing_values": "Fixed criterion set; propagate unknown; no per-pixel renormalization",
            "host_combination": "AND within a configured host branch; permitted perennial host crops OR; preserve fractions and driver; no area double-counting",
            "required_developer_checks": [
                "Dataset access/band/native-unit/scale/time contracts",
                "Explicit system and contextual transfer decisions",
                "Selected function fingerprints",
                "Full criterion set, aggregation and weights",
                "Known excluded, unknown and scored outputs kept distinct",
            ],
        },
    }
    return {
        "contract": contract,
        "decisions": decisions,
        "fixtures": fixtures,
        "policy_fixtures": policy_fixtures,
        "inclusion": inclusion,
        "importance": importance,
        "evidence": accountability,
        "synthesis_report": corpus["synthesis_report"],
        "inputs": sorted(set(inputs)),
    }


def _write_csv(path, rows):
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(
            {
                k: json.dumps(v, ensure_ascii=False, sort_keys=True, allow_nan=False)
                if isinstance(v, (dict, list))
                else v
                for k, v in row.items()
            }
            for row in rows
        )


def _package_inputs(root, nbs):
    inputs = {
        "schema/registers/EV_evidence_register.csv",
        "schema/registers/SRC_source_register.csv",
        "schema/registers/VONT_variable_ontology.csv",
        "schema/registers/BIND_dataset_binding.csv",
        "schema/registers/FAM_family_registry.csv",
        "schema/T1_data_registry.csv",
        "schema/T7_geographic_context.csv",
        "schema/lookups/crop_scope_policy.csv",
        "schema/lookups/t4_numeric_compilation_policy.csv",
        f"schema/recipes/{nbs}/T4_suitability_mappings.csv",
        "methodology/T4_developer_contract.md",
        "handoff/agroforestry-t4/IMPLEMENTATION.md",
        "handoff/agroforestry-t4/START_HERE.md",
        "handoff/agroforestry-t4/DATASET_INPUTS.md",
        "scripts/synthesise-recipe.py",
        "scripts/build-t4-developer.py",
        "src/nbs_ruralscan/schema_tools/generate.py",
        "pyproject.toml",
        "uv.lock",
    }
    if nbs == "agroforestry":
        inputs.add(
            "pipeline/t4_audit/agroforestry/importance_2026-10-21/source_weight_trees.csv"
        )
    policy_path = f"schema/recipes/{nbs}/T4_run_policy.csv"
    if (root / policy_path).exists():
        inputs.add(policy_path)
    inputs.add("schema/structure/columns.json")
    inputs |= {
        str(p.relative_to(root))
        for directory in ("src/nbs_ruralscan/recipe", "src/nbs_ruralscan/runtime")
        for p in (root / directory).glob("*.py")
    }
    return inputs


def write_package(root, output, **kwargs):
    """Build transactionally; never publish partial output or mismatched input hashes."""
    root, output = Path(root), Path(output)
    resolved = output.resolve()
    if resolved == root.resolve() or any(
        resolved == (root / p).resolve() or (root / p).resolve() in resolved.parents
        for p in ("schema", "src", "scripts", "tests", "methodology", "pipeline")
    ):
        raise ValueError(
            "Output must not overwrite authoritative inputs or source code"
        )
    if output.exists() and any(output.iterdir()):
        raise ValueError(
            "Output directory must be empty; publish a new version or build into a temporary directory"
        )
    inputs = _package_inputs(root, kwargs.get("nbs", "agroforestry"))
    before = {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest()
        for name in sorted(inputs)
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    # Sibling staging keeps publication on one filesystem, including on Windows.
    with tempfile.TemporaryDirectory(
        prefix=".t4-developer-build-", dir=output.parent
    ) as directory:
        stage = Path(directory)
        manifest = _write_package(root, stage, **kwargs)
        after = {
            name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in sorted(inputs)
        }
        if before != after or manifest["input_sha256"] != before:
            raise RuntimeError(
                "T4 inputs changed during build; no package published; rerun against a stable checkout"
            )
        if output.exists():
            output.rmdir()  # Refuses nonempty directories, including concurrent writes.
        os.rename(stage, output)  # Atomic directory publication; never overwrite files.
    return manifest


def _write_package(root, output, **kwargs):
    """Deterministic artifacts. Manifest hashes inputs/code and every output except itself."""
    from .developer_view import render_developer_view

    root, output = Path(root), Path(output)
    resolved = output.resolve()
    if any(
        resolved == (root / p).resolve() or (root / p).resolve() in resolved.parents
        for p in ("schema", "src", "scripts", "tests", "methodology", "pipeline")
    ):
        raise ValueError(
            "Output must not overwrite authoritative inputs or source code"
        )
    if output.exists() and any(output.iterdir()):
        raise ValueError(
            "Output directory must be empty; publish a new version or build into a temporary directory"
        )
    result = build_contract(root, **kwargs)
    output.mkdir(parents=True, exist_ok=True)
    contract = result["contract"]
    paths = {
        "developer_contract.json": contract,
        "decisions.json": result["decisions"],
        "conformance_examples.json": result["fixtures"],
        "policy_conformance.json": result["policy_fixtures"],
        "source_importance.json": result["importance"],
        "synthesis_report.json": result["synthesis_report"],
        "run_contract.json": contract["run_contract"],
        "selection_template.json": {
            "contract_version": VERSION,
            "selections": {},
        },
    }
    for name, value in paths.items():
        (output / name).write_text(stable_json(value), encoding="utf-8")
    _write_csv(output / "developer_table.csv", contract["rows"])
    _write_csv(
        output / "function_options.csv",
        [
            {"rule_id": r["rule_id"], **o}
            for r in contract["rows"]
            for o in r["function_options"]
        ],
    )
    _write_csv(
        output / "function_intervals.csv",
        [
            {
                "rule_id": r["rule_id"],
                "function_id": o["function_id"],
                "unit": o["unit"],
                **band,
            }
            for r in contract["rows"]
            for o in r["function_options"]
            for band in o["intervals"]
        ],
    )
    _write_csv(output / "inclusion.csv", result["inclusion"])
    _write_csv(output / "evidence_accounting.csv", result["evidence"])
    (output / "T4_suitability_mappings.csv").write_bytes(
        (
            root / f"schema/recipes/{contract['nbs']}/T4_suitability_mappings.csv"
        ).read_bytes()
    )
    for name, relative in {
        "datasets.csv": "schema/T1_data_registry.csv",
        "dataset_bindings.csv": "schema/registers/BIND_dataset_binding.csv",
        "variables.csv": "schema/registers/VONT_variable_ontology.csv",
        "practice_vocabulary.csv": "schema/registers/FAM_family_registry.csv",
    }.items():
        (output / name).write_bytes((root / relative).read_bytes())
    (output / "index.html").write_text(
        render_developer_view(contract), encoding="utf-8"
    )
    (output / "README.md").write_text(
        "# T4 developer contract\n\n"
        "Start with [the implementation task brief](START_HERE.md), [developer table](developer_table.csv), [implementation notes](IMPLEMENTATION.md) and [method](METHOD.md). "
        "Use the existing Evidence Query dashboard for ongoing inspection; [offline table and plots](index.html) are a pinned package snapshot.\n\n"
        f"This package contains {contract['summary']['configured_rows']} configured mappings and {contract['summary']['display_rows'] - contract['summary']['configured_rows']} operational evidence-only rows. "
        "It is an implementation handoff, not a completed spatial run. Select response functions and record applicability before execution. "
        "Blocked means an analytical or binding choice remains; conditional means the function is configured but input/adapter checks remain.\n\n"
        "- `developer_contract.json`: mappings, explicit function options, dataset bindings, host dependencies and readiness.\n"
        "- `developer_table.csv`: same rows for inspection; nested fields are JSON, not free-text instructions.\n"
        "- `function_options.csv` and `function_intervals.csv`: join by `(rule_id, function_id)`.\n"
        "- `T4_suitability_mappings.csv`: unchanged full-corpus recipe snapshot; NEVER apply it as the filtered or resolved contract.\n"
        "- `inclusion.csv` and `source_importance.json`: evidence diagnostics, not runtime weights.\n"
        "- `conformance_examples.json`: expected numeric and host-gate responses for adapter tests; null means unknown.\n"
        "- `run_contract.json` and `policy_conformance.json`: approved analytical policy and scalar aggregation/gate checks; target transfer remains required.\n"
        "- `manifest.json` and `VERSION`: source revision, exact inputs, filters, selections and output hashes.\n\n"
        "Developer implementation remains in Diego/Brayden's repository. This bundle does not fetch spatial data, alter review decisions, select a universal function, or run MCDA. "
        "CIAT source registers remain authoritative.\n",
        encoding="utf-8",
    )
    docs = {
        "METHOD.md": "methodology/T4_developer_contract.md",
        "IMPLEMENTATION.md": "handoff/agroforestry-t4/IMPLEMENTATION.md",
        "START_HERE.md": "handoff/agroforestry-t4/START_HERE.md",
        "DATASET_INPUTS.md": "handoff/agroforestry-t4/DATASET_INPUTS.md",
    }
    for dest, source in docs.items():
        # Source files remain report-ready Markdown; bundle links work when relocated.
        def link(match):
            label, target = match.groups()
            if "://" in target or target.startswith("#"):
                return match.group(0)
            path, _, fragment = target.partition("#")
            resolved = (root / source).parent.joinpath(path).resolve()
            try:
                relative = resolved.relative_to(root.resolve()).as_posix()
            except ValueError:
                return match.group(0)
            local = next(
                (dest for dest, path in docs.items() if path == relative), None
            )
            package_prefix = (
                f"handoff/{contract['nbs']}-t4/developer-v{PACKAGE_VERSION}/"
            )
            if relative.startswith(package_prefix):
                candidate = relative.removeprefix(package_prefix)
                if (output / candidate).is_file() or candidate == "manifest.json":
                    local = candidate
            if local:
                return f"[{label}]({local}" + ("#" + fragment if fragment else "") + ")"
            return (
                f"[{label}](https://github.com/CIAT/nbs_ruralscan/blob/RELEASE_REVISION/{relative}"
                + ("#" + fragment if fragment else "")
                + ")"
            )

        text = re.sub(
            r"\[([^\]]+)\]\(([^)]+)\)",
            link,
            (root / source).read_text(encoding="utf-8"),
        )
        (output / dest).write_text(text, encoding="utf-8")
    inputs = set(result["inputs"]) | _package_inputs(root, contract["nbs"])
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    for dest in docs:
        path = output / dest
        path.write_text(
            path.read_text(encoding="utf-8").replace("RELEASE_REVISION", revision),
            encoding="utf-8",
        )
    manifest = {
        "contract_version": VERSION,
        "package_version": PACKAGE_VERSION,
        "source_commit": revision,
        "filters": {
            "country": contract["target_country"],
            "contexts": contract["contexts"],
            "evidence_countries": contract["evidence_countries"],
        },
        "selection": contract["selection"],
        "summary": contract["summary"],
        "input_sha256": {
            name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in sorted(inputs)
        },
        "output_sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(output.iterdir())
            if p.is_file()
        },
    }
    (output / "manifest.json").write_text(stable_json(manifest), encoding="utf-8")
    (output / "VERSION").write_text(
        f"developer-v{PACKAGE_VERSION}\ncontract_version={VERSION}\nsource_commit={revision}\ninput_manifest=manifest.json\n",
        encoding="utf-8",
    )
    # VERSION is part of the hashed payload too.
    manifest["output_sha256"]["VERSION"] = hashlib.sha256(
        (output / "VERSION").read_bytes()
    ).hexdigest()
    (output / "manifest.json").write_text(stable_json(manifest), encoding="utf-8")
    return manifest


def verify_package(root, output):
    """Verify pinned inputs and outputs independently of the current branch HEAD."""
    root, output = Path(root).resolve(), Path(output).resolve()
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    for directory, hashes in (
        (root, manifest["input_sha256"]),
        (output, manifest["output_sha256"]),
    ):
        for name, expected in hashes.items():
            path = (directory / name).resolve()
            if (
                directory not in path.parents
                or not path.is_file()
                or hashlib.sha256(path.read_bytes()).hexdigest() != expected
            ):
                raise ValueError(f"Package hash verification failed: {name}")
    return manifest
