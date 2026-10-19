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
    # Preserve the original encoding; classification is advisory, never conversion.
    if any("class" in k or "gating" in k for k in rel):
        return "", {}, "class_or_gate_requires_mapping"
    if any(numeric(v) or isinstance(v, (dict, list)) for v in rel.values()):
        return "", {}, "unsupported_numeric_encoding"
    return "", {}, "qualitative_relationship"
