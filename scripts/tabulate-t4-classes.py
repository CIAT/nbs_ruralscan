#!/usr/bin/env python3
"""Expose source categorical gates/ranks and current T4 class maps without inventing scores."""

from __future__ import annotations

import argparse
import csv
import html
import json
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
    with path.open() as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
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
                    "compiler_status": dispositions[u["evidence_id"]][
                        "approved_status"
                    ],
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
                    "mapping_id": u["mapping_id"],
                    "evidence_ids": u["evidence_ids"],
                    "validation": "NO LINKED EVIDENCE"
                    if not u["evidence_ids"]
                    else "Requires applicability and coding review",
                    "justification": u["justification"],
                }
            )
    write_csv(directory / "categorical_source_classes.csv", source_rows)
    write_csv(directory / "categorical_current_t4.csv", current)
    columns = [
        "variable",
        "family",
        "source_category_or_range",
        "source_rating_or_role",
        "review_status",
        "compiler_status",
        "claim_scope",
        "source_id",
        "page",
    ]
    land = [r for r in source_rows if r["variable"] == "land_cover"]
    other = [r for r in source_rows if r["variable"] != "land_cover"]
    page = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>T4 categorical class tables</title><style>body{font:15px system-ui;margin:30px;color:#183a34;background:#f6f8f7}section{background:white;padding:20px;margin:20px 0;border:1px solid #ceded7;overflow:auto}table{border-collapse:collapse;width:100%}td,th{border:1px solid #cbd8d2;padding:9px;text-align:left;vertical-align:top;min-width:100px}th{background:#e5f0ea;position:sticky;top:0}td{white-space:pre-wrap;overflow-wrap:anywhere}h1{font-size:29px}.warning{border-left:5px solid #ad6822;padding:14px;background:#fff0dd}input{font:inherit;padding:10px;min-width:360px}a{color:#066956}</style><h1>Land-use and other categorical classes</h1><p>Branch audit · Source classes remain visible even when no executable score exists.</p><p><a href="t4-pipeline-audit.html">Full evidence audit</a></p><p class="warning">Current land-cover design row describes an eligibility filter but uses graduated scores: tree cover 1.0, cropland 0.5. It has no evidence IDs. These are existing configuration values, not validated recovered thresholds. No analytical rule changed by this report.</p><section><h2>Current configured categorical T4</h2>"""
    page += table(
        current,
        [
            "variable",
            "family",
            "dataset_id",
            "dataset_code",
            "existing_label",
            "current_score",
            "validation",
        ],
    )
    page += f"""</section><p>{len(records)} active evidence records represented in {len(source_rows)} source-class/gate rows. Every selected record retained, including those with no encoded classes.</p><p>Source ranks and numeric bands are preserved exactly. Blank scores remain unknown. Class codes from HWSD, CDL, WorldCover or a study-specific legend are not interchangeable. Source approval does not establish a target-dataset crosswalk.</p><input id="search" aria-label="Filter source classes" placeholder="Filter source tables by family, variable or source"><section class="source"><h2>Land-use / land-cover source table</h2>"""
    page += table(land, columns)
    page += (
        '</section><section class="source"><h2>Other categories and ordinal bands</h2>'
        + table(other, columns)
    )
    page += """</section><section><h2>Required compilation contract</h2><ol><li>Keep one record per family × variable × source class, with source label/code, role (eligible, excluded, ordinal rank, or observed only), context and evidence ID.</li><li>Resolve source classes against a named dataset and version. Missing codes remain unknown; they must not default to exclusion.</li><li>For explicit applicability gates, record eligible/excluded semantics separately from graded preference. Ordinary forest cover is not proof of existing agroforestry.</li><li>For ordinal classes, retain source ranks until a documented 0–1 scoring convention is agreed. Regional exclusions, crop-specific classes and observed-presence records must not become universal gates.</li><li>Compile only validated mappings to T4 ranked_classes. Existing placeholder scores require replacement through an evidence-backed family-specific decision.</li></ol><p>Examples needing attention: Castle cropland/pasture gates require class mapping; Nath drainage codes need their legend; the Singh land-cover 1–4 / 5–7 record shares its quote with a soil-quality record and needs source-context verification. Seja land-use allocation percentages and the Nath NDVI quote tagged land_cover are not categorical eligibility rules.</p></section><script>document.getElementById('search').addEventListener('input',e=>{const q=e.target.value.toLowerCase();document.querySelectorAll('.source tbody tr').forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(q))})</script></html>"""
    (ROOT / "docs/review/t4-categorical-tables.html").write_text(page)
    print(
        json.dumps(
            {
                "records": len(records),
                "source_rows": len(source_rows),
                "land_cover_rows": len(land),
                "current_t4_classes": len(current),
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=OUT)
    main(parser.parse_args().directory)
