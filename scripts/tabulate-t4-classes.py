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
    for source in source_rows:
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

    live = read_csv(ROOT / "schema/recipes/agroforestry/T4_suitability_mappings.csv")
    registry = read_csv(ROOT / "schema/registers/FAM_family_registry.csv")
    rows = []
    for row in live:
        params = json.loads(row["relationship_params"] or "{}")
        family = row["suitability_family_id"]
        practices = [r for r in registry if r["suitability_family_id"] == family]
        selected = params.get("applicable_subpractices")
        practice = "; ".join(
            r["name"]
            for r in practices
            if selected is None or r["subpractice_id"] in selected
        )
        if selected is None:
            practice = "Family scope: " + practice
        role = (
            "M2b scenario"
            if row["is_scenario_candidate"].lower() == "true"
            else "Hard exclusion"
            if row["suitability_dimension"] == "operational_constraint"
            else "Host eligibility"
            if row["relationship_type"] == "ranked_classes"
            else "Biophysical suitability"
        )
        if "class_map" in params:
            parts = []
            for code, score in params["class_map"].items():
                label = params.get("class_labels", {}).get(code, code)
                requires = params.get("class_requirements", {}).get(code, [])
                parts.append(
                    f"{label}: {score}"
                    + (" if " + " AND ".join(requires) if requires else "")
                )
            rule = "; ".join(parts) + "; unmapped = unknown"
            kind = "Categorical mask"
        elif isinstance(params.get("threshold"), (int, float)):
            unit = ontology.get(row["variable"], {}).get("canonical_unit", "")
            rule = (
                ("> " if params.get("above_is_suitable") else "≤ ")
                + str(params["threshold"])
                + " "
                + unit
            )
            kind = "Continuous input / threshold"
        else:
            rule = row["relationship_type"] + ": " + json.dumps(params)
            kind = (
                "Retained scenario" if role == "M2b scenario" else "Category exclusion"
            )
        rows.append(
            {
                "Family": family.removeprefix("agroforestry__")
                .replace("_", " ")
                .capitalize(),
                "Subpractice / scope": practice,
                "Crop parameter": params.get("host_crop", "—"),
                "Variable": row["variable"],
                "Role": role,
                "Type": kind,
                "Rule": rule,
                "Dataset": row["dataset_id"],
                "details": {
                    "Mapping ID": row["mapping_id"],
                    "Evidence IDs": row["evidence_ids"] or "No linked evidence IDs",
                    "Source count": row["n_sources"],
                    "Justification (stored)": row["justification"],
                    "Parameters": params,
                },
            }
        )
    page = render_overview(rows, binding_rows, current, coverage, source_rows)
    (ROOT / "docs/review/t4-categorical-tables.html").write_text(page, encoding="utf-8")
    print(json.dumps({"live_rows": len(rows), "source_rows": len(source_rows)}))


def render_overview(rows, bindings, classes, coverage, sources):
    """Single T4 overview; technical exports remain available behind disclosure."""
    payload = json.dumps(rows, ensure_ascii=False).replace("<", "\\u003c")
    page = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Agroforestry · T4</title>
<style>
*{box-sizing:border-box}body{font:15px system-ui;color:#183a34;background:#f7f9f8;margin:24px}
h1{margin-bottom:8px}p{max-width:1000px;line-height:1.5}.muted{color:#52675e}
.notice{padding:12px 16px;border-left:4px solid #b47b31;background:#fff5e5}
.table-wrap{overflow:auto;background:white;border:1px solid #d6e0da;margin:16px 0}
table{border-collapse:collapse;width:100%}td,th{padding:10px;border-bottom:1px solid #dce5df;text-align:left;vertical-align:top}
th{background:#eaf1ed}th button{border:0;background:none;text-align:left;font:inherit;font-weight:650;cursor:pointer;padding:0}
th input{display:block;width:100%;min-width:115px;margin-top:8px;padding:6px;border:1px solid #aabdb2;border-radius:4px}
td{min-width:120px;max-width:370px;overflow-wrap:anywhere}td:nth-child(2){min-width:200px}td:nth-child(7){min-width:280px}
button,select{font:inherit;padding:7px}details{margin:12px 0}summary{cursor:pointer;font-weight:600}
pre{white-space:pre-wrap;font:13px system-ui}a{color:#08694d}.toolbar{display:flex;gap:14px;align-items:center;flex-wrap:wrap}
</style></head><body><h1>Agroforestry T4</h1>
<p class="muted">Current recipe · 17 rows: 1 numeric biophysical rule, 7 host gates, 1 retained hard exclusion, 8 M2b scenarios.</p>
<p class="notice"><strong>Continuous suitability remains incomplete.</strong> Only slope has a published numeric biophysical rule: ≤19.3° for planted silvoarable, from one regional source. Previous rainfall, pH, soil-depth, canopy and temperature bounds were retired during audit. They are not hidden elsewhere in this table. Host masks establish compatibility, not graded suitability.</p>
<div class="toolbar"><label>Show <select id="role"><option value="">All T4 rows</option><option>Biophysical suitability</option><option>Host eligibility</option><option>Hard exclusion</option><option>M2b scenario</option></select></label><button id="reset">Reset filters</button><span id="count" aria-live="polite"></span><a href="t4-pipeline-audit.html">Evidence audit / unresolved records</a></div>
<p class="muted">Click a column heading to sort; type below it to filter. Family scope lists registered practices, not independent practice-level validation. Coffee, cocoa and tea are crop parameters, not subfamilies.</p>
<div class="table-wrap"><table id="main"><thead></thead><tbody></tbody></table></div>
<p class="muted">M2b scenarios stay outside structural suitability. Protected-area exclusion still needs legal category-mask handling and scope review. Missing host inputs remain unknown. Support percentages are unavailable because the screened-source denominator is unknown.</p>
<details><summary>How to read this table and its inputs</summary><p>T4 is the rule table. Categorical rows expand into dataset codes; continuous rows specify numeric responses. Dataset bindings tell the runtime which data and bands supply the inputs. These are different views of the same configuration, not alternative versions of T4.</p><p>Host gates require aligned datasets and additional masks. Shaded crops combine by OR while retaining crop fractions. Linear placement requires boundaries and a locally justified width. Silvopasture requires GPW grassland plus local grazing confirmation.</p></details>
<details><summary>Technical detail — bindings, class codes and diagnostic checks</summary>
<p>For implementation review. The runtime check uses synthetic class codes with no host masks supplied. It verifies missing context stays unknown; it is not a geographic run, evidence-strength measure, or pilot result.</p>
"""
    for title, data, columns in [
        (
            "Dataset bindings — additional host inputs",
            bindings,
            ["family", "mask", "variable", "dataset_id", "band", "note"],
        ),
        (
            "Expanded categorical codes",
            classes,
            [
                "family",
                "dataset_code",
                "existing_label",
                "current_score",
                "required_host_masks",
            ],
        ),
        (
            "Synthetic missing-input diagnostic",
            coverage,
            [
                "family",
                "dataset_id",
                "dataset_code",
                "value_without_host_masks",
                "runtime_status",
            ],
        ),
        (
            "Source categories — evidence, not configured rules",
            sources,
            [
                "family",
                "variable",
                "source_category_or_range",
                "source_rating_or_role",
                "review_status",
                "evidence_id",
            ],
        ),
    ]:
        page += (
            "<details><summary>"
            + title
            + '</summary><div class="table-wrap">'
            + table(data, columns)
            + "</div></details>"
        )
    page += (
        '</details><script id="rows" type="application/json">' + payload + "</script>"
    )
    page += """<script>
const rows=JSON.parse(document.getElementById('rows').textContent);
const keys=Object.keys(rows[0]).filter(k=>k!=='details'), filters={};let sortKey='',direction=1;
const head=document.querySelector('#main thead'),body=document.querySelector('#main tbody');
const tr=document.createElement('tr');
keys.concat(['Evidence / details']).forEach(key=>{const th=document.createElement('th');
if(keys.includes(key)){const b=document.createElement('button');b.textContent=key+' ↕';b.onclick=()=>{direction=sortKey===key?-direction:1;sortKey=key;head.querySelectorAll('th').forEach(t=>t.removeAttribute('aria-sort'));th.setAttribute('aria-sort',direction===1?'ascending':'descending');render()};th.append(b);
const input=document.createElement('input');input.setAttribute('aria-label','Filter '+key);input.placeholder='Filter…';input.oninput=()=>{filters[key]=input.value.toLowerCase();render()};th.append(input)}else{th.textContent=key}tr.append(th)});head.append(tr);
function render(){const role=document.getElementById('role').value;let visible=rows.filter(r=>(!role||r.Role===role)&&keys.every(k=>!filters[k]||String(r[k]).toLowerCase().includes(filters[k])));
if(sortKey)visible.sort((a,b)=>direction*String(a[sortKey]).localeCompare(String(b[sortKey]),undefined,{numeric:true}));body.replaceChildren();
visible.forEach(r=>{const tr=document.createElement('tr');keys.forEach(k=>{const td=document.createElement('td');td.textContent=r[k];tr.append(td)});
const td=document.createElement('td'),d=document.createElement('details'),s=document.createElement('summary'),pre=document.createElement('pre');s.textContent='Inspect';pre.textContent=JSON.stringify(r.details,null,2);d.append(s,pre);td.append(d);tr.append(td);body.append(tr)});document.getElementById('count').textContent=visible.length+' / '+rows.length+' rows'}
document.getElementById('role').onchange=render;document.getElementById('reset').onclick=()=>{keys.forEach(k=>delete filters[k]);head.querySelectorAll('input').forEach(i=>i.value='');document.getElementById('role').value='';sortKey='';head.querySelectorAll('th').forEach(t=>t.removeAttribute('aria-sort'));render()};render();
</script></body></html>"""
    return page


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=OUT)
    main(parser.parse_args().directory)
