"""Expose source claims independently of numeric compilation eligibility.

This view reports stored evidence, not inferred directions or executable rules.
"""

import json
from collections import Counter, defaultdict


def _obj(value):
    if isinstance(value, dict):
        return value
    return json.loads(value) if value else {}


def relationship_signals(row):
    rel = _obj(row.get("relationship"))
    direction = rel.get("direction", "")
    stated_direction = bool(
        direction and direction not in {"unclear", "not_reported", "unknown"}
    )
    # Detect stored source classes without interpreting their numeric/categorical meaning.
    classes = any(
        value not in (None, "", [], {})
        and (
            "class" in key
            or key
            in {
                "thresholds",
                "very_high",
                "high",
                "moderate",
                "very_good_code",
                "good_codes",
                "required_cover",
                "gate",
            }
        )
        for key, value in rel.items()
    )
    return {
        "source_direction": direction,
        "has_stated_direction": stated_direction,
        "has_source_classes": classes,
        "source_shape": rel.get("source_shape", rel.get("shape", "")),
    }


def build_catalogue(evidence, dispositions, mappings):
    """Account for every non-dropped structural claim, including species/crop lanes."""
    dispositions = {r["evidence_id"]: r for r in dispositions}
    links = defaultdict(list)
    for row in mappings:
        ids = row.get("evidence_ids") or []
        if isinstance(ids, str):
            ids = json.loads(ids)
        for eid in ids:
            links[eid].append(row.get("mapping_id", row.get("rule_id")))
    records = []
    for row in evidence:
        if (
            row.get("use_role") != "structural_suitability"
            or row.get("review_state") == "dropped"
        ):
            continue
        eid = row["evidence_id"]
        disposition = dispositions.get(eid, {}).get("disposition", "not_accounted")
        signal = relationship_signals(row)
        linked = links[eid]
        focus = not linked and disposition in {
            "selection_only",
            "qualitative_relationship",
            "class_or_gate_requires_mapping",
        }
        record = {
            key: row.get(key, "")
            for key in (
                "evidence_id",
                "source_id",
                "citation",
                "variable",
                "suitability_family_id",
                "claim_scope",
                "evidence_type",
                "reviewer_ok",
                "relationship",
                "context",
                "quote",
                "page",
                "locator_type",
                "locator",
                "lineage_of",
                "justification_quote",
                "justification_page",
                "taxon",
            )
        }

        record.update(signal)
        record.update(
            {
                "compilation_disposition": disposition,
                "linked_mapping_ids": linked,
                "focus_review": focus,
                "visibility_flag": disposition == "selection_only"
                and bool(
                    signal["has_stated_direction"]
                    or signal["has_source_classes"]
                    or signal["source_shape"]
                ),
                "runtime_authorization": "None granted by this catalogue",
            }
        )
        records.append(record)
    assert len({r["evidence_id"] for r in records}) == len(records), (
        "Duplicate evidence IDs"
    )
    return {
        "summary": {
            "structural_claims": len(records),
            "explicitly_linked_claims": sum(
                bool(r["linked_mapping_ids"]) for r in records
            ),
            "focus_claims": sum(r["focus_review"] for r in records),
            "selection_only_with_relationship_content": sum(
                r["visibility_flag"] for r in records
            ),
            "scopes": dict(Counter(r["claim_scope"] for r in records)),
        },
        "records": records,
    }


def render_catalogue(catalogue):
    from .relationship_summary import render

    return render(catalogue)
