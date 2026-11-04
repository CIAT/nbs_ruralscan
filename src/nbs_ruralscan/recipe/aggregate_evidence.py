"""Descriptive cross-source table; no cross-source response/weight calibration."""

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
