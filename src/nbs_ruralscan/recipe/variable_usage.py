"""Report verified model use independently of numeric-response admissibility."""

from __future__ import annotations

import json
from collections import defaultdict
from math import prod


def _object(value):
    return json.loads(value) if isinstance(value, str) and value else (value or {})


def _paper_key(sid, sources):
    doi = (sources.get(sid, {}).get("doi") or "").strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if doi.startswith(prefix):
            doi = doi[len(prefix) :].strip()
    return doi or sid


def _model_origin(unit, sources, by_id):
    """Follow explicit model-use lineage only, never borrow response lineage."""
    current, visited = unit, set()
    while True:
        eid = current["evidence_id"]
        if eid in visited:
            return None, "Model-use lineage cycle"
        visited.add(eid)
        use = _object(current.get("context")).get("model_use", {})
        target = use.get("lineage_of")
        if not target:
            return _paper_key(
                current["source_id"], sources
            ), "Reported model source; independence not assessed"
        if target in by_id:
            current = by_id[target]
            if (
                _object(current.get("context")).get("model_use", {}).get("verified")
                is not True
            ):
                return None, "Model-use lineage target lacks verified model use"
        elif target in sources:
            return _paper_key(
                target, sources
            ), "Explicit model-source reference; independence not assessed"
        else:
            return None, "Unresolved model-use lineage target: " + str(target)


def _study_context(unit):
    context = _object(unit.get("context"))
    use = context.get("model_use", {})
    result = {
        k: context[k]
        for k in (
            "study_country",
            "study_location",
            "study_area",
            "aez",
            "farming_system",
            "host_system",
            "source_scope",
        )
        if context.get(k)
    }
    result["suitability_family_id"] = unit.get("suitability_family_id", "")
    if unit.get("taxon"):
        result["taxon"] = unit["taxon"]
    explicit = use.get("context_id") or context.get("t4_assessment", {}).get(
        "context_id"
    )
    if explicit:
        result["context_id"] = explicit
    return result


def variable_usage(evidence, sources):
    """One paper vote per variable/scope, not one vote per extracted record.

    A rejected response can still document model use. Only explicit source-verified
    model_use metadata qualifies; missing metadata means unverified, not non-use.
    Importance remains source-specific and never changes runtime default weights.
    """
    evidence = list(evidence)
    by_id = {u["evidence_id"]: u for u in evidence}
    grouped = defaultdict(list)
    for unit in evidence:
        context = unit.get("context") or {}
        if isinstance(context, str):
            context = json.loads(context)
        use = context.get("model_use", {})
        if use.get("verified") is not True:
            continue
        sid = unit["source_id"]
        paper = _paper_key(sid, sources)
        context_key = json.dumps(_study_context(unit), sort_keys=True)
        grouped[
            (
                unit["variable"],
                use.get("scope", unit["claim_scope"]),
                paper,
                context_key,
            )
        ].append((unit, use))
    records = []
    for (variable, scope, paper, context_key), items in sorted(grouped.items()):
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
        reviewed = sorted(
            u["evidence_id"]
            for u, _ in items
            if u.get("review_state") != "dropped"
            and str(u.get("reviewer_ok", "")).lower() == "true"
        )
        pending = sorted(
            u["evidence_id"]
            for u, _ in items
            if u.get("review_state") != "dropped"
            and str(u.get("reviewer_ok", "")).lower() != "true"
        )
        quarantined = sorted(
            u["evidence_id"] for u, _ in items if u.get("review_state") == "dropped"
        )
        status = (
            "reviewed" if reviewed else ("pending" if pending else "quarantined_only")
        )
        origins = [_model_origin(u, sources, by_id) for u, _ in items]
        origin_ids = sorted({origin for origin, _ in origins if origin})
        lineage_holds = sorted({reason for origin, reason in origins if origin is None})
        records.append(
            {
                "variable": variable,
                "claim_scope": scope,
                "paper_key": paper,
                "source_id": items[0][0]["source_id"],
                "source_ids": sorted({u["source_id"] for u, _ in items}),
                "study_context": json.loads(context_key),
                "model_origin_ids": origin_ids,
                "model_origin_holds": lineage_holds,
                "origin_status": "held"
                if lineage_holds
                else "recorded_not_independence_verified",
                "response_lineage": sorted(
                    {u["lineage_of"] for u, _ in items if u.get("lineage_of")}
                ),
                "evidence_ids": sorted({u["evidence_id"] for u, _ in items}),
                "families": sorted({u["suitability_family_id"] for u, _ in items}),
                "model_use_review_status": status,
                "reviewed_evidence_ids": reviewed,
                "pending_evidence_ids": pending,
                "quarantined_evidence_ids": quarantined,
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
                "note": {
                    "reviewed": "Model use is carried by at least one active human-reviewed record. ",
                    "pending": "Source-checked model use; human review pending. ",
                    "quarantined_only": "Model use retained only in quarantined records; not active reviewed support. ",
                }[status]
                + (
                    "Additional records remain pending; not all reported weights are human-approved. "
                    if reviewed and pending
                    else ""
                )
                + (
                    "Quarantined records retained for traceability. "
                    if quarantined
                    else ""
                )
                + "Review status is record-level; later metadata corrections may still need review. Not agreement on thresholds. Weight is source-specific; nested soil paths may describe one branch only.",
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
        review_counts = {}
        for label, scopes in (
            ("general", {"practice_technology"}),
            ("crop_species", {"species_specific", "crop_specific"}),
            ("species_selection", {"species_selection"}),
        ):
            eligible = [r for r in selected if r["claim_scope"] in scopes]
            reviewed = {
                r["paper_key"]
                for r in eligible
                if r.get("model_use_review_status") == "reviewed"
            }
            pending = {
                r["paper_key"]
                for r in eligible
                if r.get("model_use_review_status", "pending") == "pending"
            } - reviewed
            quarantined = {r["paper_key"] for r in eligible} - reviewed - pending
            for status, papers in (
                ("reviewed", reviewed),
                ("pending", pending),
                ("quarantined_only", quarantined),
            ):
                review_counts[f"{status}_{label}_model_papers"] = len(papers)
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
                **review_counts,
                "recorded_general_model_origins": len(
                    {
                        origin
                        for r in selected
                        if r["claim_scope"] == "practice_technology"
                        for origin in r.get("model_origin_ids", [])
                    }
                ),
                "general_papers_with_origin_holds": len(
                    {
                        r["paper_key"]
                        for r in selected
                        if r["claim_scope"] == "practice_technology"
                        and r.get("model_origin_holds")
                    }
                ),
                "source_ids": sorted(
                    {
                        sid
                        for r in selected
                        for sid in r.get("source_ids", [r["source_id"]])
                    }
                ),
            }
        )
    return result
