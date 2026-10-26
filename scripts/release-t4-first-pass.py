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
VERSION = "0.1.5"
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
    inputs.append("schema/registers/FAM_family_registry.csv")
    ontology = {r["canonical_variable_id"]: r for r in vont}
    catalog = {r["dataset_id"]: r for r in datasets}
    ev = {r["evidence_id"]: r for r in evidence}
    src = {r["source_id"]: r for r in sources}
    bindings = [
        Binding(**(r | {"preference_rank": int(r["preference_rank"])})) for r in bind
    ]
    destination.mkdir(parents=True, exist_ok=True)
    followups_path = (
        "pipeline/t4_audit/agroforestry/original_claim_followups_2026-10-23.json"
    )
    inputs.append(followups_path)
    followups = json.loads((root / followups_path).read_text())["items"]
    write(
        destination / "source_followups.csv",
        [
            {
                key: item.get(key, "")
                for key in (
                    "reporting_evidence_id",
                    "origin",
                    "status",
                    "findings",
                    "next_action",
                    "runtime_effect",
                )
            }
            for item in followups
        ],
    )
    families = read(root / "schema/registers/FAM_family_registry.csv")
    write(
        destination / "practice_vocabulary.csv",
        [r for r in families if r["nbs_id"] == "agroforestry"],
    )
    from nbs_ruralscan.recipe.inclusion import inclusion_estimates
    from nbs_ruralscan.recipe.variable_usage import _paper_key

    inclusion = inclusion_estimates(evidence, src, ontology)
    write(
        destination / "inclusion_estimates.csv",
        [
            {k: json.dumps(v) if isinstance(v, list) else v for k, v in row.items()}
            for row in inclusion
        ],
    )
    inclusion_index = {
        (r["module"], r["level"], r["group"], r["variable"], r["review_lane"]): r
        for r in inclusion
        if r["claim_scope"] == "practice_technology" and r["system"] == "all_systems"
    }

    def inclusion_text(level, group, variable, module="M1"):
        r = inclusion_index.get((module, level, group, variable, "all_recorded"))
        if not r or not r["N"]:
            return "No verified model-use record"
        return f"{r['n']}/{r['N']} studies ({r['percent']}%)"

    def review_text(group, variable, module):
        key = (module, "variable", group, variable)
        recorded = inclusion_index.get((*key, "all_recorded"), {})
        reviewed = inclusion_index.get((*key, "reviewed"), {})
        total = recorded.get("n", 0)
        approved = reviewed.get("n", 0)
        if not total:
            return "No model-use evidence recorded; review completion not assessed"
        if approved == total:
            return f"All {total} have reviewed evidence of variable use"
        return f"{approved} of {total} have reviewed evidence of variable use; {total - approved} lack reviewed evidence"

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
                module="M2b — Operational feasibility"
                if operational
                else "M1 — Core suitability",
                theme=row["suitability_dimension"]
                .replace("_constraint", "")
                .replace("_", " "),
                variable_group=ont.get("group_id", "Unmapped"),
                group_inclusion=inclusion_text(
                    "group",
                    ont.get("group_id", "unmapped"),
                    "",
                    "M2b" if operational else "M1",
                ),
                variable_inclusion=inclusion_text(
                    "variable",
                    ont.get("group_id", "unmapped"),
                    variable,
                    "M2b" if operational else "M1",
                ),
                system=row["suitability_family_id"]
                .replace("agroforestry__", "")
                .replace("cross_family", "System not specified")
                .replace("_", " "),
                practices="; ".join(
                    f["name"]
                    for f in families
                    if f["suitability_family_id"] == row["suitability_family_id"]
                    and "cross_family" not in f["suitability_family_id"]
                ),
                applicability_reason=" | ".join(
                    dict.fromkeys(
                        p.get("applicability_note", "")
                        for p in profiles
                        if p.get("applicability_note")
                    )
                ),
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
    # Surface operational evidence even when no executable scenario is configured.
    configured_operational = {
        r["variable"] for r in rules if r["module"].startswith("M2b")
    }
    operational_units = [
        r
        for r in evidence
        if r["nbs_id"] == "agroforestry"
        and r["use_role"] == "operational_risk"
        and r["review_state"] != "dropped"
    ]
    for variable in sorted(
        {r["variable"] for r in operational_units} - configured_operational
    ):
        units = [r for r in operational_units if r["variable"] == variable]
        ont = ontology.get(variable, {})
        candidates = json.loads(ont.get("candidate_dataset_ids") or "[]")
        dataset = candidates[0] if candidates else "Not bound"
        try:
            resolution = resolve_binding(bindings, variable, set())
            dataset = resolution.dataset_id or "Upload required"
            note = resolution.prompt or resolution.winning_binding.fitness_note
        except KeyError:
            note = "Ontology candidate only; no global BIND resolution or executable T4 scenario"
        if dataset in catalog:
            selected_datasets.add(dataset)
        ds = catalog.get(dataset, {})
        ids = sorted({u["evidence_id"] for u in units})
        sids = sorted({u["source_id"] for u in units})
        record = {k: "" for k in rules[0]}
        record.update(
            mapping_id="inventory__" + variable,
            kind="Operational evidence (not configured)",
            module="M2b — Operational feasibility",
            theme="operational",
            variable_group=ont.get("group_id", "Unmapped"),
            group_inclusion=inclusion_text(
                "group", ont.get("group_id", "unmapped"), "", "M2b"
            ),
            variable_inclusion=inclusion_text(
                "variable", ont.get("group_id", "unmapped"), variable, "M2b"
            ),
            system="Multiple source contexts; no common applicability assumed",
            variable=variable,
            label=ont.get("label", variable),
            canonical_unit=ont.get("canonical_unit", ""),
            rules=f"{len(units)} active evidence records retained. No executable curve or scenario weight is inferred. Inspect evidence IDs and source contexts.",
            status="Evidence inventory only; interpretation, context, dataset and rule require selection before operational use. Excluded from core suitability.",
            global_binding_dataset=dataset,
            spatial_resolution_m=ds.get("spatial_resolution_m", ""),
            time_period=ds.get("time_period", ""),
            dataset_choice_note=note,
            dataset_limitations=ds.get("limitations", ""),
            weight_note="No configured runtime weight",
            contributing_source_ids="; ".join(sids),
            evidence_ids="; ".join(ids),
            source_citations=" | ".join(src[sid]["citation"] for sid in sids),
        )
        rules.append(record)
    numeric_sources = {
        row["mapping_id"]: sorted(
            {
                p["source_id"]
                for p in json.loads(row["relationship_params"] or "{}").get(
                    "profiles", []
                )
            }
        )
        for row in t4
    }
    for record in rules:
        record["review_status"] = review_text(
            record["variable_group"],
            record["variable"],
            "M2b" if record["module"].startswith("M2b") else "M1",
        )
        source_ids = numeric_sources.get(record["mapping_id"], [])
        count = len({_paper_key(sid, src) for sid in source_ids})
        record["numeric_rule_studies"] = (
            f"{count} {'study' if count == 1 else 'studies'}: " + "; ".join(source_ids)
            if count
            else "No numeric source profile in this row"
        )
        related = (
            [u for u in operational_units if u["variable"] == record["variable"]]
            if record["module"].startswith("M2b")
            else []
        )
        record["related_operational_evidence_ids"] = "; ".join(
            sorted({u["evidence_id"] for u in related})
        )
        record["related_operational_sources"] = "; ".join(
            sorted({u["source_id"] for u in related})
        )
        record["related_operational_papers"] = (
            len({_paper_key(u["source_id"], src) for u in related}) if related else ""
        )
        record["related_operational_records"] = len(related) if related else ""
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
        for kind in sorted(
            {r["kind"] for r in rules if not r["mapping_id"].startswith("inventory__")}
        )
    }
    gaps = sorted(
        {r["variable"] for r in hosts if r["dataset_id"] == "upload required"}
    )
    conflicts = sorted(
        {
            r["variable"]
            for r in rules
            if r["recipe_dataset"]
            and r["recipe_dataset"] != r["global_binding_dataset"]
        }
    )
    manifest = {
        "version": version,
        "status": "First-pass configuration release; not pilot-validated",
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip(),
        "row_counts": kinds,
        "operational_evidence_only_rows": sum(
            r["mapping_id"].startswith("inventory__") for r in rules
        ),
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
    manifest["plot_sha256"] = {
        str(p.relative_to(destination)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted((destination / "plots").glob("*"))
        if p.is_file()
    }
    (destination / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    esc = html.escape
    page = f"""<!doctype html><html lang="en"><meta charset="utf-8"><title>Agroforestry T4 v{esc(version)}</title>
<style>body{{font:16px system-ui;color:#234237;margin:24px;background:#f6f9f7}}table{{border-collapse:collapse;width:100%;background:white}}td,th{{padding:12px;border:1px solid #d5ded8;vertical-align:top;text-align:left}}th{{background:#e1ece5;position:sticky;top:0}}details{{max-width:650px}}input,select{{padding:10px;margin:8px}}.scroll{{max-height:70vh;overflow:auto}}p{{max-width:1100px}}</style>
<h1>Agroforestry T4 — first pass v{esc(version)}</h1><p><b>Modules: M1 core suitability + M2b operational feasibility.</b> M2b is required in this analysis but is not added to the core suitability score. This view covers M2b's operational stream; physical-hazard screening still uses T2/T3.</p>
<p><b>{kinds.get("Numeric response", 0)} numeric rows · {kinds.get("Categorical host gate", 0)} host gates · {kinds.get("Hard exclusion", 0)} hard exclusion.</b> {kinds.get("Operational scenario", 0)} operational scenarios plus evidence-only operational variables shown as M2b; excluded from core suitability scoring. Configuration ready for inspection; field applicability and pilot execution remain to validate.</p>
<p>Hierarchy: suitability theme → variable group → canonical measurement → dataset. Aliases stay in variables.csv. Related proxies remain separate until context-specific selection; dataset resolution alone does not establish quality. Source importance stays separate from runtime weights.</p>
<details><summary>Remaining limitations and required inputs</summary><p>Numeric rows retain regional source profiles; they are not universal pooled curves. FMNR rainfall remains contextual evidence, without an executable rainfall cutoff. Soil pH/source boundary conflicts remain held. Local inputs: {esc(", ".join(gaps))}. Recipe/BIND differences: {esc(", ".join(conflicts))}. Read dataset notes before execution. No pilot run performed.</p></details>
<details><summary>What inclusion estimates mean</summary><p>Group inclusion = papers using at least one variable in the group / eligible contributing model papers. Variable inclusion = papers using this variable / the same denominator. A paper counts once even when several group members are used. DOI aliases are deduplicated.</p><p>The displayed cohort is general-practice agroforestry models across systems with at least one active, explicitly verified structural or operational input. Both modules use the same paper denominator; group numerators are module-specific. Displayed study-use fractions include all active verified model-use records. Review status separately counts those studies with at least one approved record of using this variable; it does not claim every extract from those studies is reviewed. Numeric-rule studies count papers supplying profiles in this specific row, not all papers using the variable. Detailed reviewed-only estimates remain in the downloadable counts. Missing extractions are not recorded use, not confirmed non-use. These are bounded observed-inclusion estimates, not systematic-review prevalence, independent agreement, or weights. Full table extraction is incomplete. Shared model origins can still appear in multiple reporting papers. No family transfer is implied.</p><a href="inclusion_estimates.csv">Counts, denominator papers, evidence IDs, system/scope breakdowns and variable-within-group estimates</a></details>
<details><summary>How to read curves, weights and practice names</summary><p>Plots show retained source bands on the common suitability scale, not automatic runtime curves. Open circles exclude endpoints; filled circles include them. Arrows mark unbounded reported tails clipped to the plotting window. Empty regions have no plotted score; overlapping segments remain unresolved. No interpolation is added. A row with a separate default threshold retains that default until a source response is selected.</p><p>Numeric defaults are equal (0.2 in current T4). Masks are gates, not weighted votes. Relative importance ratios compare each variable with its study's equal-importance reference; 1 means equal, 2 means twice that reference. Full study denominators and alternative models remain separate. These ratios are not adopted runtime weights.</p><p>Standard vocabulary: Agroforestry (NbS) → suitability system → practice. Practice membership shown here is registry membership, not proof every source applies to every listed practice. Unassigned evidence is not automatically planted silvoarable. Haile parklands may be planted or regenerated; Chuma is regional; Ahmad NDVI describes mixed systems. Any planted-system assumption must be a separate sensitivity scenario, preserving original classification.</p><a href="practice_vocabulary.csv">Full practice vocabulary</a></details>
<p><a href="T4_review.csv">Readable table CSV</a> · <a href="T4_suitability_mappings.csv">Authoritative T4 snapshot</a> · <a href="evidence_accounting.csv">Every evidence record</a> · <a href="source_relative_importance.csv">Relative importance within studies</a> · <a href="host_inputs.csv">Host dataset requirements</a> · <a href="source_followups.csv">Unresolved original-source checks</a> · <a href="manifest.json">Version and hashes</a></p>
<input id="search" placeholder="Filter variable, system, theme or dataset" aria-label="Search release"><label>Module <select id="module"><option value="all">All modules</option><option value="M1">M1 — Core suitability</option><option value="M2b">M2b — Operational feasibility</option></select></label>
<div class="scroll"><table><thead><tr><th>Module</th><th>Theme</th><th>Variable group</th><th>Studies using variable group</th><th>System / practices</th><th>Variable</th><th>Studies using variable</th><th>Review status</th><th>Studies supplying numeric rules</th><th>Rule and evidence</th><th>Dataset</th><th>Weighting</th><th>Use status</th></tr></thead><tbody>"""
    for r in rules:
        comparison_variable = {
            "annual_precipitation": "precipitation",
            "mean_annual_temperature": "mean_temperature",
            "distance_to_road": "distance_road",
        }.get(r["variable"], r["variable"])
        ratios = [x for x in importance if x["variable"] == comparison_variable]
        importance_html = (
            "<details><summary>Available source-relative importance</summary><p>Diagnostic models; not all contribute to this row. Alternatives are not independent studies.</p>"
            + "".join(
                "<p>"
                + esc(x["model_id"])
                + ": "
                + esc(
                    f"{float(x['hierarchy_adjusted_ratio']):.2f} × equal-hierarchy reference"
                )
                + "</p>"
                for x in ratios
            )
            + "</details>"
            if ratios
            else "<p>No reconstructed within-study ratio for this variable.</p>"
        )
        page += (
            '<tr data-module="'
            + ("M2b" if r["module"].startswith("M2b") else "M1")
            + '"><td>'
            + esc(r["module"])
            + "</td><td>"
            + esc(r["theme"])
            + "</td><td>"
            + esc(r["variable_group"].replace("_", " "))
            + "</td><td>"
            + esc(r["group_inclusion"])
            + "</td><td>"
            + esc(r["system"])
            + "<details><summary>Practice names and applicability</summary>"
            + esc(r["practices"] or "Source does not establish a single system")
            + "<p>"
            + esc(r["applicability_reason"])
            + "</p></details>"
            + "</td><td>"
            + esc(r["label"])
            + "</td><td>"
            + esc(r["variable_inclusion"])
            + "</td><td>"
            + esc(r["review_status"])
            + "</td><td>"
            + esc(r["numeric_rule_studies"])
            + (
                "<p>Retained evidence: "
                + str(r["related_operational_papers"])
                + " papers / "
                + str(r["related_operational_records"])
                + " records</p><details><summary>Related evidence across contexts</summary>"
                + esc(
                    r["related_operational_sources"]
                    + ": "
                    + r["related_operational_evidence_ids"]
                )
                + "<p>Related evidence is not automatically support for a configured scenario or proof of model inclusion.</p></details>"
                if r["related_operational_papers"]
                else ""
            )
            + "</td><td>"
            + esc(r["kind"])
            + (
                (
                    '<a href="plots/'
                    + esc(r["mapping_id"])
                    + '.svg"><img style="display:block;width:360px;max-width:100%" alt="Source suitability bands" src="plots/'
                    + esc(r["mapping_id"])
                    + '.svg"></a>'
                )
                if r["kind"] == "Numeric response"
                else ""
            )
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
            + esc(
                (
                    "Equal numeric default: "
                    + r["weight_default"]
                    + ". Not a literature-derived weight."
                )
                if r["kind"] == "Numeric response"
                else "Mask, not additive weight"
                if r["kind"] in {"Categorical host gate", "Hard exclusion"}
                else "Operational scenario default: " + r["weight_default"]
                if r["weight_default"]
                else "No configured weight"
            )
            + importance_html
            + '<br><a href="source_relative_importance.csv">Within-study importance ratios</a>'
            + "</td><td>"
            + esc(r["status"])
            + "</td></tr>"
        )
    page += """</tbody></table></div><script>function filter(){const q=document.querySelector('#search').value.toLowerCase();for(const r of document.querySelectorAll('tbody tr'))r.hidden=(document.querySelector('#module').value!=='all'&&r.dataset.module!==document.querySelector('#module').value)||!r.textContent.toLowerCase().includes(q)}document.querySelector('#search').oninput=filter;document.querySelector('#module').onchange=filter;filter();</script></html>"""
    (destination / "index.html").write_text(page, encoding="utf-8")
    return manifest


if __name__ == "__main__":
    print(json.dumps(build(ROOT, DEST), indent=2))
