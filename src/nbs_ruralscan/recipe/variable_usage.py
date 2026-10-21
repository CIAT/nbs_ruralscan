"""Report verified model use independently of numeric-response admissibility."""

from __future__ import annotations

import json
from collections import defaultdict
from math import prod


def variable_usage(evidence, sources):
    """One paper vote per variable/scope, not one vote per extracted record.

    A rejected response can still document model use. Only explicit source-verified
    model_use metadata qualifies; missing metadata means unverified, not non-use.
    Importance remains source-specific and never changes runtime default weights.
    """
    grouped = defaultdict(list)
    for unit in evidence:
        context = unit.get("context") or {}
        if isinstance(context, str):
            context = json.loads(context)
        use = context.get("model_use", {})
        if use.get("verified") is not True:
            continue
        sid = unit["source_id"]
        source = sources.get(sid, {})
        paper = source.get("doi") or sid
        grouped[
            (unit["variable"], use.get("scope", unit["claim_scope"]), paper)
        ].append((unit, use))
    records = []
    for (variable, scope, paper), items in sorted(grouped.items()):
        paths = {tuple(use.get("weight_path_pct", [])) for _, use in items}
        for _, use in items:
            paths.update(tuple(p) for p in use.get("weight_alternatives_pct", []))
        conflict = len(paths) > 1 or any(use.get("weight_conflict") for _, use in items)
        methods = {use["method"] for _, use in items}
        path = next(iter(paths)) if len(paths) == 1 and not conflict else ()
        branches = set()
        for unit, _ in items:
            context = unit.get("context") or {}
            if isinstance(context, str):
                context = json.loads(context)
            if context.get("branch"):
                branches.add(context["branch"])
        effective = (
            100 * prod(w / 100 for w in path) if path and len(branches) <= 1 else None
        )
        records.append(
            {
                "variable": variable,
                "claim_scope": scope,
                "paper_key": paper,
                "source_id": items[0][0]["source_id"],
                "evidence_ids": sorted({u["evidence_id"] for u, _ in items}),
                "families": sorted({u["suitability_family_id"] for u, _ in items}),
                "method": "; ".join(sorted(methods)),
                "weight_path_pct": list(path),
                "effective_model_weight_pct": round(effective, 6)
                if effective is not None
                else None,
                "weight_conflict": conflict,
                "weight_branches": sorted(branches),
                "branch_aggregation_unresolved": len(branches) > 1,
                "reported_weight_paths_pct": [list(p) for p in sorted(paths)],
                "pages": sorted({use["page"] for _, use in items}),
                "note": (
                    "Source-checked model use; human review pending. "
                    if any(
                        str(u.get("reviewer_ok", "")).lower() != "true"
                        for u, _ in items
                    )
                    else "Human-reviewed model-use evidence. "
                )
                + "Not agreement on thresholds. Weight is source-specific; nested soil paths may describe one branch only.",
            }
        )
    return records


def summarize_usage(records):
    result = []
    for variable in sorted({r["variable"] for r in records}):
        selected = [r for r in records if r["variable"] == variable]
        general = {
            r["paper_key"]
            for r in selected
            if r["claim_scope"] == "practice_technology"
        }
        scoped = {
            r["paper_key"]
            for r in selected
            if r["claim_scope"] in {"species_specific", "crop_specific"}
        }
        result.append(
            {
                "variable": variable,
                "verified_general_model_papers": len(general),
                "verified_crop_species_model_papers": len(scoped),
                "verified_species_selection_model_papers": len(
                    {
                        r["paper_key"]
                        for r in selected
                        if r["claim_scope"] == "species_selection"
                    }
                ),
                "source_ids": sorted({r["source_id"] for r in selected}),
            }
        )
    return result
