"""Conservative T4 relationship decoding. Never infer scores from class labels.

Only explicit canonical shapes are executable. Legacy class tables and gates remain
reviewable payloads until their units, coding and response semantics are resolved.
"""

from __future__ import annotations

import math
from typing import Any


def numeric(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def decode(rel: dict) -> tuple[str, dict, str]:
    """Return type, params, unresolved reason (empty on success)."""
    kind = rel.get("type") or rel.get("shape")
    if kind == "observed_presence":
        return "", {}, "observed_presence"
    if "class_map" in rel:
        scores = rel["class_map"]
        if (
            isinstance(scores, dict)
            and scores
            and all(numeric(v) and 0 <= v <= 1 for v in scores.values())
        ):
            return "ranked_classes", {"class_map": scores}, ""
        return "", {}, "invalid_class_scores"
    if "points" in rel:
        raw = rel["points"]
        points: list[list[Any]] = []
        if not isinstance(raw, list) or len(raw) < 2:
            return "", {}, "invalid_piecewise_points"
        for p in raw:
            if (
                not isinstance(p, list)
                or len(p) != 2
                or not numeric(p[0])
                or not numeric(p[1])
                or not 0 <= p[1] <= 1
            ):
                return "", {}, "invalid_piecewise_points"
            points.append(p)
        if any(a[0] >= b[0] for a, b in zip(points, points[1:])):
            return "", {}, "invalid_piecewise_points"
        return "piecewise", {"points": points}, ""
    if numeric(rel.get("threshold")):
        above = rel.get("above_is_suitable")
        if not isinstance(above, bool):
            # Only explicit exclusion semantics; 'below' alone might describe an
            # optimum, observation, or scenario and must not imply a hard cutoff.
            above = {"exclude_above": False, "exclude_below": True}.get(
                str(rel.get("direction", ""))
            )
        if isinstance(above, bool):
            return (
                "threshold",
                {"threshold": rel["threshold"], "above_is_suitable": above},
                "",
            )
    params = {
        k: rel[k]
        for k in ("abs_min", "opt_low", "opt_high", "abs_max")
        if numeric(rel.get(k))
    }
    if params:
        return "trapezoidal", params, ""
    if not rel:
        return "", {}, "selection_only_or_missing_relationship"
    if any(
        k in rel for k in ("threshold_values_degrees", "max_threshold_range_pct_low")
    ):
        return "", {}, "scenario_grid_requires_parameter_choice"
    if any(
        k in rel
        for k in (
            "context_value",
            "rainfall_gradient_mm_y",
            "median_tree_density_per_ha",
            "pct_plots_eroded",
            "pct_grassland",
            "share_land_degraded_pct",
        )
    ):
        return "", {}, "observed_site_description_not_response"
    if "natural_recovery_years_low" in rel:
        return "", {}, "implementation_duration_not_response"
    if "weight" in rel or any(
        k.startswith("AHP_weight") or k == "ahp_weight" or "importance" in k
        for k in rel
    ):
        return "", {}, "importance_weight_not_response"
    if "% suitability area" in str(rel.get("unit", "")):
        return "", {}, "mapped_area_statistic_not_response"
    # Preserve the original encoding; classification is advisory, never conversion.
    if any(
        "class" in k or "gating" in k or k.endswith(("_code", "_codes")) or k == "gate"
        for k in rel
    ):
        return "", {}, "class_or_gate_requires_mapping"

    def contains_number(value):
        if numeric(value):
            return True
        if isinstance(value, dict):
            return any(contains_number(v) for v in value.values())
        if isinstance(value, list):
            return any(contains_number(v) for v in value)
        return False

    if contains_number(rel):
        return "", {}, "unsupported_numeric_encoding"
    return "", {}, "qualitative_relationship"
