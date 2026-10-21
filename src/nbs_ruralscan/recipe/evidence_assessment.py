"""Separate source use, directional evidence and calibration for reviewed tables.

This is an evidence report, not a response compiler or runtime weighting rule.
"""

from collections import defaultdict
import json

DIRECTIONS = {"increasing", "decreasing", "optimum_range", "non_monotonic", "unclear"}


def obj(value):
    return json.loads(value or "{}") if isinstance(value, str) else value or {}


def assessments(units, sources):
    """Deduplicate within scope/context/lineage; keep pending and approved distinct."""
    by_id = {u["evidence_id"]: u for u in units}

    def origin(unit):
        seen = set()
        current = unit
        while current.get("lineage_of"):
            parent = current["lineage_of"]
            if parent in seen:
                return "lineage_cycle:" + unit["evidence_id"]
            seen.add(parent)
            if parent in by_id:
                current = by_id[parent]
            else:
                return str(sources.get(parent, {}).get("doi") or parent).lower()
        sid = current["source_id"]
        return str(sources.get(sid, {}).get("doi") or sid).lower()

    grouped = defaultdict(list)
    for unit in units:
        c = obj(unit.get("context"))
        audit = c.get("t4_assessment", {})
        if not audit.get("source_checked") or unit.get("review_state") == "dropped":
            continue
        key = (
            unit["variable"],
            audit.get("scope", unit["claim_scope"]),
            unit["suitability_family_id"],
            audit.get("context_id") or unit["source_id"],
            origin(unit),
        )
        grouped[key].append(unit)
    records = []
    for (variable, scope, family, context, paper), items in sorted(grouped.items()):
        approved = [u for u in items if str(u.get("reviewer_ok")).lower() == "true"]
        pending = [u for u in items if str(u.get("reviewer_ok")).lower() != "true"]

        def directions(rows):
            return sorted(
                {obj(u.get("relationship")).get("direction") for u in rows} & DIRECTIONS
            )

        records.append(
            {
                "variable": variable,
                "scope": scope,
                "family": family,
                "context_id": context,
                "independent_source": paper,
                "source_ids": sorted({u["source_id"] for u in items}),
                "evidence_ids": sorted({u["evidence_id"] for u in items}),
                "variable_use_confirmed": any(
                    obj(u.get("context")).get("model_use", {}).get("verified") is True
                    for u in items
                ),
                "approved_directions": directions(approved),
                "pending_directions": directions(pending),
                "direction_conflict": len(set(directions(items)) - {"unclear"}) > 1,
                "approved_paper_vote": bool(approved),
                "pending_only_paper_vote": not approved and bool(pending),
                "calibration_status": sorted(
                    {
                        obj(u.get("context"))["t4_assessment"].get(
                            "calibration_status", "not_assessed"
                        )
                        for u in items
                    }
                ),
                "note": "Direction counts describe source claims within this context; no cross-context pooling, curve or runtime weight is implied.",
            }
        )
    return records
