#!/usr/bin/env python3
"""Build a versioned, reviewable T4 first pass from authoritative CSVs."""

import csv
import hashlib
import html
import json
from pathlib import Path
import shutil
import subprocess

from nbs_ruralscan.runtime.binding import Binding, resolve_binding
from nbs_ruralscan.schema_tools.t4_review_view import interval_text

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
DEST = ROOT / "handoff/agroforestry-t4" / ("v" + VERSION)
AUDIT = "pipeline/t4_audit/agroforestry/final_audit/"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write(path, rows):
    if not rows:
        raise ValueError(f"Empty release table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build(root, destination, version=VERSION):
    inputs = [
        "schema/recipes/agroforestry/T4_suitability_mappings.csv",
        "schema/registers/VONT_variable_ontology.csv",
        "schema/registers/BIND_dataset_binding.csv",
        "schema/T1_data_registry.csv",
        "schema/registers/EV_evidence_register.csv",
        "schema/registers/SRC_source_register.csv",
        AUDIT + "record_reconciliation.csv",
        AUDIT + "executable_categories/dataset_bindings.csv",
        "pipeline/t4_audit/agroforestry/importance_2026-10-21/comparison.csv",
    ]
    t4, vont, bind, datasets, evidence, sources, reconciliation, hosts, importance = [
        read(root / p) for p in inputs
    ]
    ontology = {r["canonical_variable_id"]: r for r in vont}
    catalog = {r["dataset_id"]: r for r in datasets}
    ev = {r["evidence_id"]: r for r in evidence}
    src = {r["source_id"]: r for r in sources}
    bindings = [
        Binding(**(r | {"preference_rank": int(r["preference_rank"])})) for r in bind
    ]
    destination.mkdir(parents=True, exist_ok=True)
    rules = []
    selected_datasets = set()
    referenced = set()
    for row in t4:
        variable = row["variable"]
        ont = ontology.get(variable, {})
        params = json.loads(row["relationship_params"] or "{}")
        profiles = params.get("profiles", [])
        operational = row["is_scenario_candidate"].lower() == "true"
        kind = (
            "Operational scenario"
            if operational
            else "Categorical host gate"
            if "class_map" in params
            else "Numeric response"
            if profiles
            else "Hard exclusion"
        )
        rules_text = []
        for profile in profiles:
            rules_text.append(
                profile["source_id"]
                + ": "
                + "; ".join(
                    interval_text(b, profile["unit"]) for b in profile["intervals"]
                )
            )
        if not profiles:
            rules_text.append(row["justification"])
        if profiles and isinstance(params.get("threshold"), (int, float)):
            rules_text.append(
                f"Existing default threshold: {params['threshold']}; source responses require explicit selection."
            )
        status = (
            "Source response and geographic transfer must be selected; gaps remain unknown"
            if profiles
            else "Configured; requires aligned inputs"
            if kind == "Categorical host gate"
            else "Outside core suitability"
            if operational
            else "Legal-mask adapter and family coverage unresolved; not executable through categorical host evaluator"
        )
        if "cross_family" in row["suitability_family_id"]:
            status += "; agroforestry system must be specified"
        if any(b["score"] is None for p in profiles for b in p["intervals"]):
            status += "; unresolved class scores"
        configured = row["dataset_id"]
        selected_datasets.add(configured)
        try:
            resolved = resolve_binding(bindings, variable, set())
            default = resolved.dataset_id or "Upload required"
            binding_note = resolved.prompt or resolved.winning_binding.fitness_note
        except KeyError:
            default = configured
            binding_note = "No global BIND override; recipe dataset retained"
        if default in catalog:
            selected_datasets.add(default)
        if default != configured:
            status += "; reconcile recipe and runtime dataset binding before execution"
            binding_note += "; BIND differs from recipe dataset: resolve in runtime, do not silently substitute units/bands"
        ds = catalog.get(default, {})
        ids = json.loads(row["evidence_ids"] or "[]")
        referenced.update(ids)
        missing = set(ids) - ev.keys()
        if missing:
            raise ValueError(f"Missing evidence: {sorted(missing)}")
        sids = sorted({ev[eid]["source_id"] for eid in ids})
        rules.append(
            dict(
                mapping_id=row["mapping_id"],
                kind=kind,
                theme=row["suitability_dimension"]
                .replace("_constraint", "")
                .replace("_", " "),
                variable_group=ont.get("group_id", "Unmapped"),
                system=row["suitability_family_id"]
                .replace("agroforestry__", "")
                .replace("cross_family", "System not specified")
                .replace("_", " "),
                variable=variable,
                label=ont.get("label", variable),
                canonical_unit=ont.get("canonical_unit", ""),
                rules=" | ".join(rules_text),
                status=status,
                recipe_dataset=configured,
                global_binding_dataset=default,
                spatial_resolution_m=ds.get("spatial_resolution_m", ""),
                time_period=ds.get("time_period", ""),
                dataset_choice_note=binding_note,
                dataset_limitations=ds.get("limitations", ""),
                weight_default=row["weight_default"],
                weight_note="Configured runtime weight; source-relative importance is reported separately",
                contributing_source_ids="; ".join(sids),
                evidence_ids="; ".join(ids),
                source_citations=" | ".join(src[sid]["citation"] for sid in sids),
            )
        )
    write(destination / "T4_review.csv", rules)
    shutil.copyfile(root / inputs[0], destination / "T4_suitability_mappings.csv")
    # CSV snapshots preserve authoritative values. No generated schema JSON is edited.
    host_vars = {r["variable"] for r in hosts}
    variables = {r["variable"] for r in rules} | host_vars
    selected_datasets.update(
        r["dataset_id"] for r in hosts if r["dataset_id"] in catalog
    )
    write(
        destination / "variables.csv",
        [r for r in vont if r["canonical_variable_id"] in variables],
    )
    write(
        destination / "dataset_bindings.csv",
        [r for r in bind if r["variable"] in variables],
    )
    selected_datasets.update(
        r["dataset_id"] for r in bind if r["variable"] in variables
    )
    for variable in variables:
        selected_datasets.update(
            json.loads(ontology.get(variable, {}).get("candidate_dataset_ids") or "[]")
        )
    write(
        destination / "datasets.csv",
        [r for r in datasets if r["dataset_id"] in selected_datasets],
    )
    write(destination / "host_inputs.csv", hosts)
    write(destination / "source_relative_importance.csv", importance)
    accounts = {r["evidence_id"]: r for r in reconciliation}
    accounting = []
    for row in evidence:
        if row["nbs_id"] != "agroforestry" or row["use_role"] not in {
            "structural_suitability",
            "operational_risk",
        }:
            continue
        prior = accounts.get(row["evidence_id"], {})
        disposition = (
            "quarantined"
            if row["review_state"] == "dropped"
            else "live_T4_reference"
            if row["evidence_id"] in referenced
            else prior.get("final_disposition", "needs_reconciliation")
        )
        accounting.append(
            {
                k: row[k]
                for k in (
                    "evidence_id",
                    "source_id",
                    "variable",
                    "suitability_family_id",
                    "use_role",
                    "reviewer_ok",
                    "review_state",
                )
            }
            | {
                "disposition": disposition,
                "reason": prior.get("disposition_reason", ""),
            }
        )
    write(destination / "evidence_accounting.csv", accounting)
    kinds = {
        kind: sum(r["kind"] == kind for r in rules)
        for kind in sorted({r["kind"] for r in rules})
    }
    gaps = sorted(
        {r["variable"] for r in hosts if r["dataset_id"] == "upload required"}
    )
    conflicts = sorted(
        {
            r["variable"]
            for r in rules
            if r["recipe_dataset"] != r["global_binding_dataset"]
        }
    )
    manifest = {
        "version": version,
        "status": "First-pass configuration release; not pilot-validated",
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip(),
        "row_counts": kinds,
        "numeric_variables": sorted(
            {r["variable"] for r in rules if r["kind"] == "Numeric response"}
        ),
        "required_local_inputs": gaps,
        "binding_differences": conflicts,
        "unreconciled_records": [
            r["evidence_id"]
            for r in accounting
            if r["disposition"] == "needs_reconciliation"
        ],
        "input_sha256": {
            p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in inputs
        },
    }
    manifest["output_sha256"] = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(destination.glob("*.csv"))
    }
    (destination / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    esc = html.escape
    page = f"""<!doctype html><html lang="en"><meta charset="utf-8"><title>Agroforestry T4 v{esc(version)}</title>
<style>body{{font:16px system-ui;color:#234237;margin:24px;background:#f6f9f7}}table{{border-collapse:collapse;width:100%;background:white}}td,th{{padding:12px;border:1px solid #d5ded8;vertical-align:top;text-align:left}}th{{background:#e1ece5;position:sticky;top:0}}details{{max-width:650px}}input,select{{padding:10px;margin:8px}}.scroll{{max-height:70vh;overflow:auto}}p{{max-width:1100px}}</style>
<h1>Agroforestry T4 — first pass v{esc(version)}</h1>
<p><b>{kinds.get("Numeric response", 0)} numeric rows · {kinds.get("Categorical host gate", 0)} host gates · {kinds.get("Hard exclusion", 0)} hard exclusion.</b> {kinds.get("Operational scenario", 0)} operational scenarios kept separate. Configuration ready for inspection; field applicability and pilot execution remain to validate.</p>
<p>Hierarchy: suitability theme → variable group → canonical measurement → dataset. Aliases stay in variables.csv. Related proxies remain separate until context-specific selection; dataset resolution alone does not establish quality. Source importance stays separate from runtime weights.</p>
<details><summary>Remaining limitations and required inputs</summary><p>Numeric rows retain regional source profiles; they are not universal pooled curves. FMNR rainfall remains contextual evidence, without an executable rainfall cutoff. Soil pH/source boundary conflicts remain held. Local inputs: {esc(", ".join(gaps))}. Recipe/BIND differences: {esc(", ".join(conflicts))}. Read dataset notes before execution. No pilot run performed.</p></details>
<p><a href="T4_review.csv">Readable table CSV</a> · <a href="T4_suitability_mappings.csv">Authoritative T4 snapshot</a> · <a href="evidence_accounting.csv">Every evidence record</a> · <a href="source_relative_importance.csv">Relative importance within studies</a> · <a href="host_inputs.csv">Host dataset requirements</a> · <a href="manifest.json">Version and hashes</a></p>
<input id="search" placeholder="Filter variable, system, theme or dataset" aria-label="Search release"><label><input id="operational" type="checkbox">Show operational scenarios</label>
<div class="scroll"><table><thead><tr><th>Theme / group</th><th>System</th><th>Variable</th><th>Rule and evidence</th><th>Dataset</th><th>Use status</th></tr></thead><tbody>"""
    for r in rules:
        page += (
            '<tr data-operational="'
            + str(r["kind"] == "Operational scenario").lower()
            + '"><td>'
            + esc(r["theme"] + " / " + r["variable_group"].replace("_", " "))
            + "</td><td>"
            + esc(r["system"])
            + "</td><td>"
            + esc(r["label"])
            + "</td><td>"
            + esc(r["kind"])
            + "<details><summary>Rule and sources</summary><p>"
            + esc(r["rules"])
            + "</p><p>"
            + esc(r["source_citations"] or "Design/policy configuration")
            + "</p></details></td><td>"
            + esc(r["global_binding_dataset"])
            + "<br>"
            + esc(str(r["spatial_resolution_m"]) + " m; " + r["time_period"])
            + "<details><summary>Choice and limitations</summary>"
            + esc(r["dataset_choice_note"] + " " + r["dataset_limitations"])
            + "</details></td><td>"
            + esc(r["status"])
            + "</td></tr>"
        )
    page += """</tbody></table></div><script>function filter(){const q=document.querySelector('#search').value.toLowerCase();for(const r of document.querySelectorAll('tbody tr'))r.hidden=(!document.querySelector('#operational').checked&&r.dataset.operational==='true')||!r.textContent.toLowerCase().includes(q)}document.querySelector('#search').oninput=filter;document.querySelector('#operational').onchange=filter;filter();</script></html>"""
    (destination / "index.html").write_text(page, encoding="utf-8")
    return manifest


if __name__ == "__main__":
    print(json.dumps(build(ROOT, DEST), indent=2))
