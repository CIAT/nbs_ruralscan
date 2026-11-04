"""Descriptive cross-source table; no cross-source response/weight calibration."""

import html
import json
from collections import defaultdict
from statistics import median

# Presentation crosswalk for unambiguous names in the recorded weight models.
# Depth, soil-type, nutrient stocks and minimum/maximum temperature remain separate.
ALIASES = {
    "precipitation": "annual_precipitation",
    "mean_temperature": "mean_annual_temperature",
    "aridity": "aridity_index",
    "reference_evapotranspiration": "evapotranspiration_ref",
    "available_water_capacity": "soil_available_water_capacity",
    "soil_cec": "soil_cation_exchange_capacity",
}


def obj(value, default=None):
    return json.loads(value) if isinstance(value, str) and value else (value or default)


def aggregate(catalogue, inclusion, models, mappings, ontology):
    records = [
        r for r in catalogue["records"] if r["claim_scope"] == "practice_technology"
    ]
    by_var = defaultdict(list)
    for r in records:
        by_var[r["variable"]].append(r)
    use = [
        r
        for r in inclusion
        if r["module"] == "M1"
        and r["system"] == "all_systems"
        and r["claim_scope"] == "practice_technology"
        and r["review_lane"] == "all_recorded"
    ]
    uses = {r["variable"]: r for r in use if r["level"] == "variable"}
    groups = {r["group"]: r for r in use if r["level"] == "group"}
    weight_rows = defaultdict(list)
    group_weights = defaultdict(list)
    unmapped = []
    for m in models:
        if m["status"] != "calculated":
            continue
        sums = defaultdict(float)
        excluded = []
        for v in m["variables"]:
            canonical = ALIASES.get(v["variable"], v["variable"])
            group = ontology.get(canonical, {}).get("group_id")
            if not group:
                excluded.append(v["variable"])
            else:
                sums[(group, v["scope"])] += v["whole_model_share"]
            weight_rows[canonical].append(
                {
                    "model_id": m["model_id"],
                    "source_id": m["source_id"],
                    "scope": v["scope"],
                    "raw_variable": v["variable"],
                    "share": v["whole_model_share"],
                    "relative_to_equal": v["hierarchy_adjusted_ratio"],
                    "provenance": m["provenance"],
                    "native_weight_paths": [
                        {"path": p["path"], "source_weight": p["source_weight"]}
                        for p in m.get("paths", [])
                        if p["variable"] == v["variable"] and p["scope"] == v["scope"]
                    ],
                }
            )
        for (group, scope), share in sums.items():
            group_weights[group].append(
                {
                    "model_id": m["model_id"],
                    "source_id": m["source_id"],
                    "scope": scope,
                    "share": share,
                    "unmapped_model_variables": excluded,
                    "interpretation": "Sum of mapped variable shares; partial where unmapped variables remain. Not the study's declared group weight.",
                }
            )
        if excluded:
            unmapped.append({"model_id": m["model_id"], "variables": excluded})
    functions = defaultdict(list)
    eid_source = {r["evidence_id"]: r["source_id"] for r in catalogue["records"]}
    for m in mappings:
        if m["role"] != "suitability_score":
            continue
        options = obj(m["function_options"], [])
        sources = sorted(
            {
                eid_source[e]
                for o in options
                for e in o["evidence_ids"]
                if e in eid_source
            }
        )
        functions[m["variable"]].append(
            {
                "family": m["system"],
                "sources": sources,
                "function_options": len(options),
                "mapping_id": m["rule_id"],
            }
        )
    rows = []
    for variable, claims in sorted(by_var.items()):
        group = ontology.get(variable, {}).get("group_id", "unmapped")
        directions = defaultdict(set)
        for r in claims:
            rel = obj(r["relationship"], {})
            direction = rel.get("direction")
            # Only explicit directional vocabulary; no conversion from classes/context.
            if direction in {
                "increasing",
                "decreasing",
                "optimum_range",
                "non_monotonic",
            } and r["compilation_disposition"] not in {
                "observed_presence",
                "observed_site_description_not_response",
                "mapped_area_statistic_not_response",
                "importance_weight_not_response",
            }:
                directions[(r["suitability_family_id"], direction)].add(r["source_id"])
        per_scope = defaultdict(lambda: defaultdict(list))
        for w in weight_rows[variable]:
            per_scope[w["scope"]][w["source_id"]].append(w)
        summaries = []
        for scope, studies in per_scope.items():
            # Alternative models from one source do not become multiple study votes.
            source_shares = [median(w["share"] for w in ws) for ws in studies.values()]
            source_ratios = [
                median(w["relative_to_equal"] for w in ws) for ws in studies.values()
            ]
            summaries.append(
                {
                    "scope": scope,
                    "reporting_sources": len(studies),
                    "median_source_share": median(source_shares),
                    "source_share_range": [min(source_shares), max(source_shares)],
                    "median_relative_to_equal": median(source_ratios),
                    "relative_range": [min(source_ratios), max(source_ratios)],
                }
            )
        rows.append(
            {
                "variable": variable,
                "group": group,
                "group_use": groups.get(group),
                "variable_use": uses.get(variable),
                "claim_sources": sorted({r["source_id"] for r in claims}),
                "direction_by_family": [
                    {"family": f, "direction": d, "sources": sorted(ss)}
                    for (f, d), ss in sorted(directions.items())
                ],
                "weight_summary": summaries,
                "study_weights": weight_rows[variable],
                "mapped_group_weights": group_weights[group],
                "function_support": functions[variable],
                "evidence_ids": [r["evidence_id"] for r in claims],
            }
        )
    return {
        "rows": rows,
        "unmapped_weight_variables": unmapped,
        "presentation_aliases": ALIASES,
        "weight_models": [
            {
                "model_id": m["model_id"],
                "source_id": m["source_id"],
                "status": m["status"],
            }
            for m in models
        ],
        "method": "Descriptive medians: one median per reporting source across its alternative models, then across sources within the same model scope. Not independent-study validation or a runtime weighting recommendation. Group shares sum only mapped variables, without renormalization.",
    }


def render(data):
    def esc(x):
        return html.escape(str(x))

    def nice(x):
        return str(x).replace("agroforestry__", "").replace("_", " ")

    def freq(r):
        return f"{r['n']}/{r['N']} ({r['percent']}%)" if r else "Not documented"

    out = [
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Agroforestry — aggregated T4 evidence</title>',
        "<style>body{font:15px/1.5 system-ui;margin:28px;color:#183c36;background:#f5f8f7}table{border-collapse:collapse;width:100%;background:white}th,td{padding:12px;border:1px solid #d4dfd9;vertical-align:top;text-align:left;min-width:135px}th{background:#e4eee8}h1{font-size:28px}summary{cursor:pointer}pre{white-space:pre-wrap;max-width:600px}small{display:block;color:#52675e}input{font:inherit;padding:10px;width:320px}.scroll{overflow:auto}.warn{background:#fff1d2;padding:12px}</style>",
        "<h1>Agroforestry: aggregated T4 evidence</h1><p>One row per variable. General-practice evidence only; family-specific responses remain separate within each row.</p>",
        '<p><a href="index.html">Numeric functions and plots</a> · <a href="source_relationships.html">Source evidence</a> · <a href="aggregate_evidence.csv">Download aggregate table</a> · <a href="aggregate_evidence.json">Full aggregate data</a></p>',
        '<p class="warn">Study use, relative importance and support for a calibrated function are different measures. Weight summaries cover reconstructed weight models, not every evidence source; other reported weights may remain uncompiled. Missing weights mean unknown, not zero. Regional and FMNR practitioner models are not pooled. No aggregate below becomes a runtime weight.</p>',
        "<details><summary>How to read the aggregation</summary><p>Use counts come from explicitly verified model-use records, deduplicated by reporting paper. Denominator is the recorded model-use cohort, not all papers in the library; absence is unknown. All recorded includes unreviewed inputs. Group use counts a paper once across its variables.</p><p>Relative importance is the source hierarchy-adjusted ratio to equal weighting: 1× means equal-share benchmark, above 1× means higher source-model importance. Whole-model shares retain the original model denominator, including operational criteria. For each scope, alternative models are first summarized within source; medians/ranges then describe reporting sources, not independent replicates. Different regions and variable sets limit comparison.</p><p>Group weight cells show mapped-group sums per original model. Where some raw variables lack an unambiguous ontology mapping, these sums are partial and explicitly labelled; they are not the original declared group weights. No residual is redistributed.</p><p>Directional counts cover explicit increasing/decreasing/optimum/nonmonotonic fields only; qualitative prose and coded classes remain in source evidence. Function counts are distinct source IDs per existing mapping, not option counts or global validation.</p></details>",
        '<p><input id="search" placeholder="Find variable or group" aria-label="Find variable or group"></p><div class="scroll"><table><thead><tr><th>Variable / group</th><th>Group use across studies</th><th>Variable use</th><th>Relative importance</th><th>Study weights</th><th>Relationship across sources</th><th>Function support</th></tr></thead><tbody>',
    ]
    for r in data["rows"]:
        out.append(
            f'<tr class="variable"><td><strong>{esc(nice(r["variable"]))}</strong><small>{esc(nice(r["group"]))}</small></td><td>{freq(r["group_use"])}'
        )
        out.append("<details><summary>Mapped group weights</summary>")
        for g in r["mapped_group_weights"]:
            partial = (
                "partial" if g["unmapped_model_variables"] else "all variables mapped"
            )
            out.append(
                f"<p>{esc(g['model_id'])}: {100 * g['share']:.1f}% ({partial})</p>"
            )
        if not r["mapped_group_weights"]:
            out.append("Not documented")
        out.append("</details></td><td>" + freq(r["variable_use"]))
        if r["variable_use"]:
            v = r["variable_use"]
            out.append(
                f"<small>Within group: {v['n']}/{v['within_group_N']} studies</small>"
            )
        out.append("</td><td>")
        for w in r["weight_summary"]:
            out.append(
                f"<p>{esc(nice(w['scope']))}: <strong>{w['median_relative_to_equal']:.2f}×</strong><small>Range {w['relative_range'][0]:.2f}–{w['relative_range'][1]:.2f}×; {w['reporting_sources']} reporting sources</small></p>"
            )
        if not r["weight_summary"]:
            out.append("No mapped weight model")
        out.append("</td><td>")
        for w in r["weight_summary"]:
            out.append(
                f"<p>{esc(nice(w['scope']))}: median {100 * w['median_source_share']:.1f}%<small>Source-median range {100 * w['source_share_range'][0]:.1f}–{100 * w['source_share_range'][1]:.1f}%</small></p>"
            )
        out.append("<details><summary>Original model shares and provenance</summary>")
        for w in r["study_weights"]:
            out.append(
                f"<p>{esc(w['model_id'])}: {100 * w['share']:.2f}% whole-model share; {w['relative_to_equal']:.2f}×<small>Original weights (native scale, by path): {esc(w['native_weight_paths'])}</small><small>{esc(w['provenance'])}</small></p>"
            )
        out.append("</details></td><td>")
        for d in r["direction_by_family"]:
            out.append(
                f"<p>{esc(nice(d['family']))}: {esc(nice(d['direction']))} — {len(d['sources'])} sources<small>{esc(', '.join(d['sources']))}</small></p>"
            )
        if not r["direction_by_family"]:
            out.append(
                "No aggregated explicit direction; inspect classes/qualitative context."
            )
        out.append("</td><td>")
        for f in r["function_support"]:
            out.append(
                f"<p>{esc(nice(f['family']))}: <strong>{len(f['sources'])} studies</strong><small>{esc(', '.join(f['sources']))}</small></p>"
            )
        if not r["function_support"]:
            out.append("No numeric function compiled")
        out.append(
            f"<details><summary>Traceability</summary><p>{esc(', '.join(r['claim_sources']))}</p><small>{esc(', '.join(r['evidence_ids']))}</small></details></td></tr>"
        )
    out.append(
        "</tbody></table></div><details><summary>Weight concepts not yet mapped</summary><pre>"
        + esc(json.dumps(data["unmapped_weight_variables"], indent=2))
        + "</pre></details>"
    )
    out.append(
        "<script>document.getElementById('search').addEventListener('input',function(){const q=this.value.toLowerCase();for(const r of document.querySelectorAll('.variable'))r.hidden=!r.textContent.toLowerCase().includes(q);});</script></html>"
    )
    return "\n".join(out)
