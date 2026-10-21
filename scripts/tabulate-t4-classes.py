#!/usr/bin/env python3
"""Expose source categorical gates/ranks and current T4 class maps without inventing scores."""

from __future__ import annotations

import argparse
import csv
import html
import json

import numpy as np

from nbs_ruralscan.runtime.categorical import evaluate_family
from nbs_ruralscan.runtime.host_inputs import plan_family_inputs
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pipeline/t4_audit/agroforestry/final_audit"
RANKS = (
    "very_high",
    "very_good",
    "highly_suitable",
    "not_suitable",
    "unsuitable",
    "next_class",
    "moderate",
    "marginal",
    "restricted",
    "suitable",
    "medium",
    "good",
    "high",
    "low",
)


def text(value):
    return (
        json.dumps(value, ensure_ascii=False)
        if isinstance(value, (dict, list))
        else str(value)
    )


def class_entries(rel):
    """Return source class/range, source rating, explicit score, raw field.

    Presentation only: no unit conversion, score normalization or dataset crosswalk.
    Unrecognized encodings return an explicit unresolved row with original payload.
    """
    result = []
    grouped = {}
    for key, value in rel.items():
        if key == "class_map" and isinstance(value, dict):
            result.extend(
                (str(code), "", text(score), key) for code, score in value.items()
            )
        elif (
            isinstance(value, list)
            and value
            and all(isinstance(v, dict) and "range" in v for v in value)
        ):
            result.extend(
                (
                    text(v["range"]),
                    text(v.get("label", ""))
                    + ("; rank " + text(v["rank"]) if "rank" in v else ""),
                    "",
                    key,
                )
                for v in value
            )
        elif key == "classes" and isinstance(value, dict):
            result.extend(
                (text(category), label, "", key) for label, category in value.items()
            )
        elif key.startswith("group") and isinstance(value, dict):
            result.extend(
                (str(category), f"{key}: rank {rank}", "", key)
                for category, rank in value.items()
            )
        elif "class" in key and isinstance(value, (str, list)):
            if (
                isinstance(value, str)
                and ":" in value
                and all(":" in p for p in value.split(","))
            ):
                result.extend(
                    (
                        part.split(":", 1)[1].strip(),
                        part.split(":", 1)[0].strip(),
                        "",
                        key,
                    )
                    for part in value.split(",")
                )
            else:
                values = value if isinstance(value, list) else value.split(",")
                result.extend(
                    (str(v).strip(), str(rel.get("direction", key)), "", key)
                    for v in values
                )
        elif any(key.startswith(rank + "_") for rank in RANKS):
            rank = next(rank for rank in RANKS if key.startswith(rank + "_"))
            grouped.setdefault(rank, {})[key] = value
        elif key in {
            "gating_condition",
            "required_cover",
            "applicable_land_use",
            "favoured_class",
            "topsoil_texture",
            "subsoil_texture",
        }:
            values = value if isinstance(value, list) else [value]
            result.extend(
                (text(v), str(rel.get("direction", key)), "", key) for v in values
            )
    for rank, fields in grouped.items():
        codes = {k: v for k, v in fields.items() if k.endswith(("_code", "_codes"))}
        if len(codes) == 1 and len(fields) == 1:
            key, value = next(iter(codes.items()))
            result.extend((v.strip(), rank, "", key) for v in str(value).split(","))
        else:
            result.append(
                (text(fields), rank, "", "grouped source fields; bounds not repaired")
            )
    return result or [("", "No explicit category mapping encoded", "", "unresolved")]


def read_csv(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def table(rows, columns):
    return (
        "<table><thead><tr>"
        + "".join("<th>" + html.escape(c) + "</th>" for c in columns)
        + "</tr></thead><tbody>"
        + "".join(
            "<tr>"
            + "".join(
                "<td>" + html.escape(str(r.get(c, ""))) + "</td>" for c in columns
            )
            + "</tr>"
            for r in rows
        )
        + "</tbody></table>"
    )


def main(directory=OUT):
    directory = Path(directory)
    ontology = {
        r["canonical_variable_id"]: r
        for r in read_csv(ROOT / "schema/registers/VONT_variable_ontology.csv")
    }
    class_ids = {r["evidence_id"] for r in read_csv(directory / "class_evidence.csv")}
    dispositions = {
        r["evidence_id"]: r for r in read_csv(directory / "record_reconciliation.csv")
    }
    source_rows = []
    records = []
    for u in read_csv(ROOT / "schema/registers/EV_evidence_register.csv"):
        unit = ontology.get(u["variable"], {}).get("canonical_unit", "")
        if (
            u["nbs_id"] != "agroforestry"
            or u["review_state"] == "dropped"
            or u["use_role"] != "structural_suitability"
        ):
            continue
        if (
            u["evidence_id"] not in class_ids
            and unit not in {"categorical", "class"}
            and not unit.startswith("ordinal")
        ):
            continue
        records.append(u)
        rel = json.loads(u["relationship"] or "{}")
        for category, rating, score, field in class_entries(rel):
            source_rows.append(
                {
                    "variable": u["variable"],
                    "family": u["suitability_family_id"],
                    "source_category_or_range": category,
                    "source_rating_or_role": rating,
                    "explicit_source_score": score,
                    "dataset_code_mapping": "UNRESOLVED: verify source coding against target dataset",
                    "review_status": "approved"
                    if u["reviewer_ok"].lower() == "true"
                    else "unresolved",
                    "compiler_status": dispositions.get(u["evidence_id"], {}).get(
                        "approved_status", "awaiting_reconciliation"
                    ),
                    "claim_scope": u["claim_scope"],
                    "source_id": u["source_id"],
                    "evidence_id": u["evidence_id"],
                    "page": u["page"],
                    "source_field": field,
                    "context": u["context"],
                    "raw_relationship": u["relationship"],
                    "quote": u["quote"],
                }
            )
    evidence = {
        r["evidence_id"]: r
        for r in read_csv(ROOT / "schema/registers/EV_evidence_register.csv")
    }
    current = []
    for u in read_csv(ROOT / "schema/recipes/agroforestry/T4_suitability_mappings.csv"):
        if u["relationship_type"] != "ranked_classes":
            continue
        params = json.loads(u["relationship_params"])
        for code, score in params.get("class_map", {}).items():
            current.append(
                {
                    "variable": u["variable"],
                    "family": u["suitability_family_id"],
                    "dataset_id": u["dataset_id"],
                    "dataset_code": code,
                    "existing_label": params.get("class_labels", {}).get(code, ""),
                    "current_score": score,
                    "required_host_masks": ", ".join(
                        params.get("class_requirements", {}).get(code, [])
                    ),
                    "mapping_id": u["mapping_id"],
                    "evidence_ids": u["evidence_ids"],
                    "validation": "NO LINKED EVIDENCE"
                    if not json.loads(u["evidence_ids"] or "[]")
                    else (
                        (
                            "Blocked: pending mapping review"
                            if params.get("mapping_review_status", "approved")
                            != "approved"
                            else "Executable; approved evidence"
                        )
                        if all(
                            evidence.get(eid, {}).get("reviewer_ok", "").lower()
                            == "true"
                            and evidence[eid]["review_state"] != "dropped"
                            for eid in json.loads(u["evidence_ids"])
                        )
                        else "Blocked: pending evidence review"
                    ),
                    "justification": u["justification"],
                }
            )
    linked = {}
    for configured in current:
        for eid in json.loads(configured["evidence_ids"] or "[]"):
            linked.setdefault(eid, set()).add(configured["mapping_id"])
    numeric_links = {}
    for mapping in read_csv(
        ROOT / "schema/recipes/agroforestry/T4_suitability_mappings.csv"
    ):
        if mapping["suitability_dimension"] == "biophysical_constraint":
            for eid in json.loads(mapping["evidence_ids"] or "[]"):
                numeric_links.setdefault(eid, []).append(mapping["mapping_id"])
    for source in source_rows:
        if source["evidence_id"] in numeric_links:
            source["dataset_code_mapping"] = (
                "Compiled numeric source profile: "
                + ", ".join(numeric_links[source["evidence_id"]])
            )
        if source["evidence_id"] in linked:
            source["dataset_code_mapping"] = (
                "Covered subset only; see configured mappings: "
                + ", ".join(sorted(linked[source["evidence_id"]]))
            )
    coverage = []
    families = sorted(
        {
            r["suitability_family_id"]
            for r in read_csv(ROOT / "schema/registers/FAM_family_registry.csv")
            if r["nbs_id"] == "agroforestry"
        }
    )
    gate_rows = [
        r
        for r in read_csv(
            ROOT / "schema/recipes/agroforestry/T4_suitability_mappings.csv"
        )
        if r["relationship_type"] == "ranked_classes"
    ]
    for family in families:
        configured = [r for r in gate_rows if r["suitability_family_id"] == family]
        dataset_ids = {r["dataset_id"] for r in configured}
        dataset_id = (
            next(iter(dataset_ids)) if len(dataset_ids) == 1 else "esa_worldcover_2021"
        )
        codes = (
            sorted(
                {
                    int(code)
                    for r in configured
                    for code in json.loads(r["relationship_params"])["class_labels"]
                }
            )
            if configured
            else [10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100]
        )
        result = evaluate_family(
            ROOT / "schema",
            "agroforestry",
            family,
            {dataset_id: np.array(codes)},
        )
        for i, code in enumerate(codes):
            coverage.append(
                {
                    "family": family,
                    "spatial_product_type": result.spatial_product_type,
                    "dataset_id": dataset_id,
                    "dataset_code": code,
                    "value_without_host_masks": "unknown"
                    if np.isnan(result.values[i])
                    else int(result.values[i]),
                    "runtime_status": result.status[i],
                    "mapping_ids": ", ".join(result.mapping_ids),
                }
            )
    (directory / "executable_categories").mkdir(exist_ok=True)
    write_csv(directory / "executable_categories/family_execution.csv", coverage)
    write_csv(directory / "categorical_source_classes.csv", source_rows)
    write_csv(directory / "categorical_current_t4.csv", current)
    binding_rows = []
    for family in families:
        plans = plan_family_inputs(ROOT / "schema", "agroforestry", family, set())
        for mask, plan in plans.items():
            for variable, item in plan["inputs"].items():
                dataset = item["dataset"] or {}
                binding_rows.append(
                    {
                        "family": family,
                        "mask": mask,
                        "mask_status": plan["status"],
                        "variable": variable,
                        "dataset_id": item["dataset_id"] or "upload required",
                        "band": item["band"],
                        "source": dataset.get("download_url", ""),
                        "note": item["prompt"]
                        or item["winning_binding"]["fitness_note"],
                    }
                )
    write_csv(directory / "executable_categories/dataset_bindings.csv", binding_rows)

    from nbs_ruralscan.schema_tools.t4_review_view import render

    from nbs_ruralscan.recipe.variable_usage import variable_usage, summarize_usage

    usage = variable_usage(
        read_csv(ROOT / "schema/registers/EV_evidence_register.csv"),
        {
            r["source_id"]: r
            for r in read_csv(ROOT / "schema/registers/SRC_source_register.csv")
        },
    )
    for name, records in (
        ("verified_model_use.csv", usage),
        ("variable_use_summary.csv", summarize_usage(usage)),
    ):
        if records:
            with (directory / name).open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle, fieldnames=list(records[0]), lineterminator="\n"
                )
                writer.writeheader()
                writer.writerows(
                    {
                        k: json.dumps(v) if isinstance(v, (list, dict)) else v
                        for k, v in row.items()
                    }
                    for row in records
                )
    from nbs_ruralscan.recipe.direction_usage import write_direction_report

    write_direction_report(
        ROOT,
        read_csv(ROOT / "schema/registers/EV_evidence_register.csv"),
        {
            r["source_id"]: r
            for r in read_csv(ROOT / "schema/registers/SRC_source_register.csv")
        },
    )
    page = render(ROOT, read_csv, table, binding_rows, coverage)
    (ROOT / "docs/review/t4-categorical-tables.html").write_text(page, encoding="utf-8")
    print(json.dumps({"source_rows": len(source_rows)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=OUT)
    main(parser.parse_args().directory)
