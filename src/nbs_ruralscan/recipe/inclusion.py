"""Observed model-variable inclusion, with explicit denominators and review lanes."""

from collections import defaultdict
from .variable_usage import _object, _paper_key


def inclusion_estimates(evidence, sources, ontology, nbs_id="agroforestry"):
    """Reporting-paper frequencies, not independent agreement or runtime weights.

    Cohort: papers with at least one active, explicitly verified structural model
    input in the selected scope/system. A missing entry is unknown, not non-use.
    Reviewed estimates require reviewed numerator records; an approval on another
    variable cannot approve this variable. Group numerators union papers once.
    """
    cohorts = defaultdict(list)
    for row in evidence:
        if (
            row.get("nbs_id") != nbs_id
            or row.get("use_role") != "structural_suitability"
            or row.get("review_state") == "dropped"
        ):
            continue
        use = _object(row.get("context")).get("model_use", {})
        if use.get("verified") is not True:
            continue
        scope = use.get("scope", row.get("claim_scope", ""))
        family = row.get("suitability_family_id", "")
        if family == "cross_family":
            family = nbs_id + "__cross_family"
        for system in {"all_systems", family}:
            cohorts[(scope, system)].append(row)
    result = []
    for (scope, system), rows in sorted(cohorts.items()):
        for lane in ("reviewed", "all_recorded"):
            eligible = [
                r
                for r in rows
                if lane == "all_recorded"
                or str(r.get("reviewer_ok", "")).lower() == "true"
            ]
            denominator = {_paper_key(r["source_id"], sources) for r in eligible}

            def stats(selected, base):
                papers = {_paper_key(r["source_id"], sources) for r in selected}
                return {
                    "n": len(papers),
                    "N": len(base),
                    "percent": round(100 * len(papers) / len(base), 1)
                    if base
                    else None,
                    "paper_keys": sorted(papers),
                    "denominator_paper_keys": sorted(base),
                    "evidence_ids": sorted({r["evidence_id"] for r in selected}),
                }

            groups = {
                ontology.get(r["variable"], {}).get("group_id") or "unmapped"
                for r in rows
            }
            for group in sorted(groups):
                members = {
                    r["variable"]
                    for r in rows
                    if (ontology.get(r["variable"], {}).get("group_id") or "unmapped")
                    == group
                }
                group_rows = [r for r in eligible if r["variable"] in members]
                group_papers = {_paper_key(r["source_id"], sources) for r in group_rows}
                result.append(
                    {
                        "claim_scope": scope,
                        "system": system,
                        "review_lane": lane,
                        "level": "group",
                        "group": group,
                        "variable": "",
                        **stats(group_rows, denominator),
                        "within_group_N": None,
                        "within_group_percent": None,
                    }
                )
                for variable in sorted(members):
                    selected = [r for r in group_rows if r["variable"] == variable]
                    value = stats(selected, denominator)
                    result.append(
                        {
                            "claim_scope": scope,
                            "system": system,
                            "review_lane": lane,
                            "level": "variable",
                            "group": group,
                            "variable": variable,
                            **value,
                            "within_group_N": len(group_papers),
                            "within_group_percent": round(
                                100 * value["n"] / len(group_papers), 1
                            )
                            if group_papers
                            else None,
                        }
                    )
    return result
