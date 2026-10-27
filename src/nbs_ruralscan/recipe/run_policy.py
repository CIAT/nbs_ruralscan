"""Validate schema-authored analytical policies without granting target transfer."""

import math
from collections import defaultdict


def compile_policies(records, rows):
    indexed = {r["rule_id"]: r for r in rows}
    groups = defaultdict(list)
    for record in records:
        groups[record["policy_id"]].append(record)
    policies = []
    shared = (
        "nbs_id",
        "system",
        "output_label",
        "aggregation",
        "sensitivity_aggregation",
        "missing_values",
        "gate_policy",
        "applicability",
        "decision_reference",
    )
    for policy_id, members in groups.items():
        first = members[0]
        if any(any(r[k] != first[k] for k in shared) for r in members):
            raise ValueError("Inconsistent policy metadata")
        supported = {
            "aggregation": "weighted_linear_combination",
            "sensitivity_aggregation": "minimum",
            "missing_values": "propagate_unknown",
            "gate_policy": "separate_host_and_legal_masks",
            "applicability": "target_transfer_required",
        }
        if (
            any(first[k] != v for k, v in supported.items())
            or not first["decision_reference"]
        ):
            raise ValueError("Unsupported or unauthorized run policy")
        criteria, budgets, totals, seen, holds = [], {}, defaultdict(float), set(), []
        for r in members:
            row = indexed.get(r["rule_id"])
            if (
                row is None
                or row["role"] != "suitability_score"
                or row["system"] != first["system"]
            ):
                raise ValueError(
                    "Run policy requires numeric criteria from its named system"
                )
            if r["rule_id"] in seen or r["variable_group"] != row["variable_group"]:
                raise ValueError("Duplicate criterion or incompatible variable group")
            seen.add(r["rule_id"])
            weight, budget = float(r["criterion_weight"]), float(r["group_weight"])
            if not all(math.isfinite(v) and 0 < v <= 1 for v in (weight, budget)):
                raise ValueError("Policy weights must be finite and positive")
            group = r["variable_group"]
            if group in budgets and budgets[group] != budget:
                raise ValueError("Inconsistent group budget")
            budgets[group] = budget
            totals[group] += weight
            option = next(
                (
                    o
                    for o in row["function_options"]
                    if o["function_id"] == r["function_id"]
                ),
                None,
            )
            available = (
                option is not None
                and option["fingerprint"] == r["function_fingerprint"]
            )
            if not available:
                holds.append(
                    f"{r['rule_id']}: approved function missing or fingerprint changed; revalidate policy"
                )
            criterion = {
                k: r[k]
                for k in (
                    "rule_id",
                    "function_id",
                    "function_fingerprint",
                    "variable_group",
                )
            }
            criterion.update(weight=weight, function_verified=available)
            criteria.append(criterion)
            row["approved_policy"] = {
                "policy_id": policy_id,
                **criterion,
                "applicability": first["applicability"],
            }
        if not math.isclose(sum(budgets.values()), 1, abs_tol=1e-9) or any(
            not math.isclose(totals[g], budgets[g], abs_tol=1e-9) for g in budgets
        ):
            raise ValueError(
                "Criterion weights must match group budgets summing to one"
            )
        policies.append(
            {
                "policy_id": policy_id,
                **{k: first[k] for k in shared},
                "criteria": criteria,
                "group_budgets": budgets,
                "status": "blocked_function_changed"
                if holds
                else "approved_pending_target_and_inputs",
                "execution_ready": False,
                "holds": holds
                + [
                    "Target applicability, dataset contracts, host inputs and legal mask must be resolved before a spatial run"
                ],
            }
        )
    return policies


def reference_scores(policy, scores, *, host, excluded, eligible_fraction=None):
    """Scalar conformance oracle, not a raster runner or transfer authorization."""
    if (
        host is not None
        and type(host) is not bool
        or excluded is not None
        and type(excluded) is not bool
    ):
        raise ValueError("Host and exclusion states must be true, false or unknown")
    if eligible_fraction is not None and (
        not math.isfinite(eligible_fraction) or not 0 <= eligible_fraction <= 1
    ):
        raise ValueError("Eligible fraction must lie in [0, 1]")
    expected = {c["rule_id"] for c in policy["criteria"]}
    if set(scores) != expected:
        raise ValueError("Scores must match the fixed criterion set")
    if any(
        v is not None and (not math.isfinite(v) or not 0 <= v <= 1)
        for v in scores.values()
    ):
        raise ValueError("Scores must lie in [0, 1] or be unknown")
    result = {
        "status": "unknown",
        "score": None,
        "minimum": None,
        "eligible_fraction": eligible_fraction,
    }
    if excluded is True or host is False:
        return result | {"status": "excluded"}
    if host is None or excluded is None or any(v is None for v in scores.values()):
        return result
    return result | {
        "status": "scored",
        "score": sum(scores[c["rule_id"]] * c["weight"] for c in policy["criteria"]),
        "minimum": min(scores.values()),
    }
