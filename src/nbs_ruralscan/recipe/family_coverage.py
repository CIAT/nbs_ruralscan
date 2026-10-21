"""Family-local evidence coverage, without cross-family inheritance or approval."""

import json
from collections import defaultdict


def object_value(value, default):
    return json.loads(value) if isinstance(value, str) and value else value or default


def family_coverage(evidence, mappings, sources, nbs_id):
    cells = defaultdict(lambda: {"units": [], "mappings": [], "dependencies": []})
    for unit in evidence:
        if unit.get("nbs_id") != nbs_id or unit.get("review_state") == "dropped":
            continue
        if unit.get("use_role") != "structural_suitability":
            continue
        # Crop/species evidence has its own policy lane; this general-model
        # inventory must not silently include it as practice evidence.
        if unit.get("claim_scope") != "practice_technology":
            continue
        family = unit["suitability_family_id"]
        if family == "cross_family":
            family = nbs_id + "__cross_family"
        cells[(family, unit["variable"])]["units"].append(unit)
    for mapping in mappings:
        if mapping.get("nbs_id") != nbs_id or mapping.get("is_scenario_candidate") in (
            True,
            "true",
        ):
            continue
        cells[(mapping["suitability_family_id"], mapping["variable"])][
            "mappings"
        ].append(mapping)
        params = object_value(mapping.get("relationship_params"), {})
        required = {
            name
            for names in params.get("class_requirements", {}).values()
            for name in names
        }
        for name in sorted(required):
            spec = params.get("host_bindings", {}).get(name, {})
            for variable in spec.get("variables", [name]):
                cells[(mapping["suitability_family_id"], variable)][
                    "dependencies"
                ].append(
                    {
                        "mapping_id": mapping["mapping_id"],
                        "mask": name,
                        "parent_variable": mapping["variable"],
                        "note": spec.get("note", ""),
                        "operation": spec.get("operation", ""),
                        "evidence_ids": object_value(mapping.get("evidence_ids"), []),
                    }
                )
    result = []
    for (family, variable), cell in sorted(cells.items()):
        papers, reviewed, model_use, directions = set(), set(), set(), defaultdict(set)
        ids = []
        observed = set()
        for unit in cell["units"]:
            source = sources.get(unit["source_id"], {})
            lineage = source.get("doi") or unit["source_id"]
            papers.add(lineage)
            if str(unit.get("reviewer_ok")).lower() == "true":
                reviewed.add(lineage)
            ids.append(unit["evidence_id"])
            context = object_value(unit.get("context"), {})
            use = context.get("model_use", {})
            if (
                use.get("verified") is True
                and use.get("scope", unit["claim_scope"]) == "practice_technology"
            ):
                model_use.add(lineage)
            relationship = object_value(unit.get("relationship"), {})
            if relationship.get("type") == "observed_presence":
                observed.add(lineage)
            direction = relationship.get("direction")
            if direction in {
                "increasing",
                "decreasing",
                "optimum_range",
                "non_monotonic",
            }:
                directions[lineage].add(direction)
        direction_counts = defaultdict(int)
        for values in directions.values():
            direction_counts[
                next(iter(values)) if len(values) == 1 else "conflicting_within_source"
            ] += 1
        result.append(
            dict(
                family=family,
                required_input_for=cell["dependencies"],
                variable=variable,
                evidence_papers=len(papers),
                reviewed_papers=len(reviewed),
                observed_presence_papers=len(observed),
                verified_model_use_papers=len(model_use),
                direction_counts=dict(direction_counts),
                evidence_ids=sorted(ids),
                source_ids=sorted({u["source_id"] for u in cell["units"]}),
                mapping_ids=[m["mapping_id"] for m in cell["mappings"]],
                relationship_types=sorted(
                    {m["relationship_type"] for m in cell["mappings"]}
                ),
                configured_weights=[m["weight_default"] for m in cell["mappings"]],
                mapping_evidence_ids=sorted(
                    {
                        eid
                        for m in cell["mappings"]
                        for eid in object_value(m.get("evidence_ids"), [])
                    }
                ),
            )
        )
    return result
