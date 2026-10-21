"""Diagnostic within-study importance ratios; never runtime weights.

Inputs are complete, source-provenanced additive weighting trees. Numerical
weights belong in data, not this implementation. No cross-study pooling here.
"""

from collections import defaultdict
from math import isfinite


def compare_importance(model):
    """Return path and variable comparisons, or explicit holds for invalid inputs.

    Flat path ratios use leaf slots. Where additive duplicate variables are
    consolidated, flat variable ratios use distinct variables after consolidation.
    Hierarchical benchmarks always retain the original source tree.
    """
    holds = []
    seen = set()
    sums = {}

    def validate(node):
        identity = node.get("id")
        if not identity or identity in seen:
            holds.append("Missing or duplicate node identity")
        seen.add(identity)
        children = node.get("children")
        if children is None:
            if not node.get("variable") or not node.get("scope"):
                holds.append(f"{identity}: missing variable or scope")
            return
        if not children or node.get("children_complete") is not True:
            holds.append(f"{identity}: sibling inventory incomplete")
        weights = [c.get("weight") for c in children]
        if any(
            isinstance(w, bool)
            or not isinstance(w, (int, float))
            or not isfinite(w)
            or w < 0
            for w in weights
        ):
            holds.append(f"{identity}: missing, negative or non-finite weight")
        elif sum(weights) <= 0:
            holds.append(f"{identity}: zero total weight")
        else:
            sums[identity] = sum(weights)
        for child in children:
            validate(child)

    if model.get("additive") is not True:
        holds.append("Additive combination not established")
    if model.get("weight_scale") != "nonnegative_ratio":
        holds.append("Comparable ratio-scale weights not established")
    validate(model["tree"])
    if holds:
        return {"status": "held", "holds": holds, "paths": [], "variables": []}
    paths = []

    def walk(node, contribution, benchmark, route, local_ratio=None):
        children = node.get("children")
        if children is None:
            paths.append(
                dict(
                    node_id=node["id"],
                    variable=node["variable"],
                    scope=node["scope"],
                    path=route,
                    source_weight=node["weight"],
                    whole_model_share=contribution,
                    equal_hierarchy_share=benchmark,
                    within_group_ratio=local_ratio,
                    hierarchy_adjusted_ratio=contribution / benchmark,
                )
            )
            return
        n = len(children)
        for child in children:
            share = child["weight"] / sums[node["id"]]
            walk(
                child,
                contribution * share,
                benchmark / n,
                route + [child["id"]],
                share * n,
            )

    walk(model["tree"], 1.0, 1.0, [])
    groups = defaultdict(list)
    for path in paths:
        path["flat_path_ratio"] = path["whole_model_share"] * len(paths)
        groups[(path["variable"], path["scope"])].append(path)
    variables = []
    for (variable, scope), branches in sorted(groups.items()):
        value = sum(b["whole_model_share"] for b in branches)
        benchmark = sum(b["equal_hierarchy_share"] for b in branches)
        variables.append(
            dict(
                variable=variable,
                scope=scope,
                branch_count=len(branches),
                whole_model_share=value,
                equal_hierarchy_share=benchmark,
                flat_variable_ratio=value * len(groups),
                hierarchy_adjusted_ratio=value / benchmark,
                within_group_ratios=[b["within_group_ratio"] for b in branches],
            )
        )
    for item in variables:
        item["source_importance_rank"] = 1 + sum(
            v["whole_model_share"] > item["whole_model_share"] + 1e-12
            for v in variables
        )
    return {
        "status": "calculated",
        "holds": [],
        "paths": paths,
        "variables": variables,
        "leaf_count": len(paths),
        "distinct_variable_scope_count": len(groups),
        "source_sibling_sums": sums,
        "note": "Within-study diagnostics only. No independent source votes or runtime weights are created.",
    }


def load_weight_models(path):
    """Load audit trees, refusing orphaned, cyclic or duplicate source nodes."""
    import csv

    grouped = defaultdict(list)
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            grouped[row["model_id"]].append(row)
    models = []
    for model_id, rows in grouped.items():
        nodes = {r["node_id"]: r for r in rows}
        roots = [r for r in rows if not r["parent_id"]]
        if len(nodes) != len(rows) or len(roots) != 1:
            raise ValueError(f"{model_id}: duplicate nodes or invalid root count")
        if any(r["parent_id"] and r["parent_id"] not in nodes for r in rows):
            raise ValueError(f"{model_id}: orphan node")
        visited = set()

        def build(row):
            identity = row["node_id"]
            if identity in visited:
                raise ValueError(f"{model_id}: repeated/cyclic node")
            visited.add(identity)
            node = dict(id=identity, variable=row["variable"], scope=row["scope"])
            if row["weight"]:
                node["weight"] = float(row["weight"])
            children = [r for r in rows if r["parent_id"] == identity]
            if children or row["children_complete"]:
                node["children"] = [build(r) for r in children]
                node["children_complete"] = row["children_complete"] == "true"
            return node

        root = roots[0]
        tree = build(root)
        if len(visited) != len(nodes):
            raise ValueError(f"{model_id}: disconnected/cyclic nodes")
        models.append(
            dict(
                model_id=model_id,
                source_id=root["source_id"],
                additive=root.get("combination") == "additive",
                weight_scale=root.get("weight_scale"),
                tree=tree,
                provenance={
                    k: root[k] for k in ("page", "table", "lineage", "artifact_sha256")
                },
                labels={r["variable"]: r["label"] for r in rows if r["variable"]},
            )
        )
    return models
