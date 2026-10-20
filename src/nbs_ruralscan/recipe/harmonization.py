"""Combine explicitly compatible, standardized step profiles without filling gaps.

Scores and compatible-pool assignments come from schema policy. A summary retains
median bounds rather than choosing a side of a tie. It is never a hard exclusion.
"""

from __future__ import annotations

import math
from collections import defaultdict


def standardize(bands, policy):
    """Preserve source scores; missing semantic crosswalks produce unknown scores."""
    if policy.get("score_kind") not in {"ordinal", "comparable_cardinal"}:
        raise ValueError("unsupported_score_meaning")
    scores = policy.get("class_scores", {})
    if any(
        isinstance(v, bool)
        or not isinstance(v, (int, float))
        or not math.isfinite(v)
        or not 0 <= v <= 1
        for v in scores.values()
    ):
        raise ValueError("invalid_class_scores")
    for band in bands:
        band["legacy_score"] = band["score"]
        key = band["label"].strip().lower().replace(" ", "_")
        band["source_score"] = policy.get("source_scores", {}).get(key)
        if policy["score_kind"] == "comparable_cardinal":
            lo, hi = policy.get("source_min"), policy.get("source_max")
            if (
                not policy.get("meaning_verified")
                or not isinstance(lo, (int, float))
                or not isinstance(hi, (int, float))
                or not math.isfinite(lo)
                or not math.isfinite(hi)
                or hi <= lo
            ):
                raise ValueError("cardinal_scale_definition_required")
            original = band["source_score"]
            if original is not None and (
                not isinstance(original, (int, float))
                or not math.isfinite(original)
                or not lo <= original <= hi
            ):
                raise ValueError("source_score_outside_declared_scale")
            band["score"] = None if original is None else (original - lo) / (hi - lo)
            band["score_basis"] = (
                "declared_cardinal_scale"
                if original is not None
                else "missing_source_score"
            )
            continue
        band["score"] = scores.get(key)
        band["score_basis"] = (
            "schema_class_convention" if key in scores else "unresolved_class_meaning"
        )


def value_at(profile, x):
    hits = []
    for b in profile["intervals"]:
        lo, hi = b["lower"], b["upper"]
        if (lo is None or x > lo or (x == lo and b["lower_inclusive"])) and (
            hi is None or x < hi or (x == hi and b["upper_inclusive"])
        ):
            hits.append(b["score"])
    # Ambiguous shared endpoints remain unknown, matching source-profile runtime.
    if len(hits) != 1 or None in hits:
        return None
    return hits[0]


def median_bounds(pairs):
    """Return the complete weighted-median set, including an exact half-weight gap."""
    if not pairs:
        return None, None
    grouped = defaultdict(float)
    for score, weight in pairs:
        if not math.isfinite(weight) or weight <= 0:
            raise ValueError("invalid_source_weight")
        grouped[score] += weight
    values = sorted(grouped)
    half = math.fsum(grouped.values()) / 2
    cumulative = 0.0
    for i, score in enumerate(values):
        cumulative += grouped[score]
        if math.isclose(cumulative, half, rel_tol=1e-12, abs_tol=0):
            return score, values[i + 1] if i + 1 < len(values) else score
        if cumulative > half:
            return score, score
    raise AssertionError("median not found")


def summarize_at(profiles, x):
    """One independent origin, one vote; internal conflicts remain missing."""
    origins = defaultdict(list)
    for p in profiles:
        origins[p["origin_id"]].append(p)
    pairs, contributors, flags = [], [], []
    eligible_weight = 0.0
    for origin, members in sorted(origins.items()):
        # A citation echo must not increase the origin's authority.
        weights = {p["source_weight"] for p in members}
        if len(weights) != 1:
            raise ValueError("origin_weight_conflict")
        weight = next(iter(weights))
        if not math.isfinite(weight) or weight <= 0:
            raise ValueError("invalid_source_weight")
        eligible_weight += weight
        values = {value_at(p, x) for p in members}
        values.discard(None)
        if len(values) > 1:
            flags.append("within_origin_conflict")
        elif values:
            pairs.append((next(iter(values)), weight))
            contributors.append(origin)
    low, high = median_bounds(pairs)
    scores = [v for v, _ in pairs]
    if not pairs:
        flags.append("no_evidence_at_value")
    elif len(pairs) == 1:
        flags.append("single_source")
    if len(pairs) < len(origins):
        flags.append("partial_coverage")
    if low != high:
        flags.append("median_tie")
    if scores and min(scores) == 0 and max(scores) > 0:
        flags.append("exclusion_conflict")
    if scores and min(scores) != max(scores):
        flags.append("source_disagreement")
    return dict(
        median_lower=low,
        median_upper=high,
        score=low if low == high and "exclusion_conflict" not in flags else None,
        source_min=min(scores) if scores else None,
        source_max=max(scores) if scores else None,
        n_sources=len(pairs),
        eligible_sources=len(origins),
        weight_coverage=sum(w for _, w in pairs) / eligible_weight
        if eligible_weight
        else 0,
        origins=contributors,
        flags=sorted(set(flags)),
    )


def combine_profiles(profiles):
    """Exact breakpoint partition for one explicitly approved compatible pool."""
    if not profiles:
        raise ValueError("empty_pool")
    for field in (
        "pool_id",
        "system_id",
        "context_id",
        "variable",
        "unit",
        "score_policy",
    ):
        values = {p.get(field) for p in profiles}
        if len(values) != 1 or not next(iter(values)):
            raise ValueError("incompatible_or_missing_" + field)
    if any(not p.get("compatibility_approved") for p in profiles):
        raise ValueError("compatibility_not_approved")
    if any(not p.get("origin_id") for p in profiles):
        raise ValueError("independent_origin_required")
    breaks = sorted(
        {
            b[k]
            for p in profiles
            for b in p["intervals"]
            for k in ("lower", "upper")
            if b[k] is not None
        }
    )
    cells = []
    edges = [None, *breaks, None]
    for lo, hi in zip(edges, edges[1:]):
        x = (
            (lo + hi) / 2
            if lo is not None and hi is not None
            else (
                hi - max(1, abs(hi))
                if hi is not None
                else (lo + max(1, abs(lo)) if lo is not None else 0)
            )
        )
        cells.append(
            dict(
                lower=lo,
                upper=hi,
                lower_inclusive=False,
                upper_inclusive=False,
                **summarize_at(profiles, x),
            )
        )
    for x in breaks:
        cells.append(
            dict(
                lower=x,
                upper=x,
                lower_inclusive=True,
                upper_inclusive=True,
                **summarize_at(profiles, x),
            )
        )
    cells.sort(
        key=lambda c: (
            float("-inf") if c["lower"] is None else c["lower"],
            not c["lower_inclusive"],
        )
    )
    return dict(
        pool_id=profiles[0]["pool_id"],
        system_id=profiles[0]["system_id"],
        context_id=profiles[0]["context_id"],
        profile_ids=sorted(p["profile_id"] for p in profiles),
        cells=cells,
        hard_exclusion=False,
        selection="explicit",
        score_policy=profiles[0]["score_policy"],
    )


def harmonize(profiles):
    pools, review = defaultdict(list), []
    for p in profiles:
        if not p.get("pool_id") or not p.get("compatibility_approved"):
            review.append(
                dict(
                    profile_id=p["profile_id"],
                    reason=p.get("pool_review") or "compatibility_review_required",
                )
            )
        elif any(b["score"] is None for b in p["intervals"]):
            review.append(
                dict(profile_id=p["profile_id"], reason="unresolved_class_meaning")
            )
        else:
            pools[p["pool_id"]].append(p)
    summaries = []
    for pool_id, members in sorted(pools.items()):
        try:
            summaries.append(combine_profiles(members))
        except ValueError as exc:
            review.append(dict(pool_id=pool_id, reason=str(exc)))
    for p in profiles:
        if any(b["score"] is None for b in p["intervals"]):
            review.append(
                dict(profile_id=p["profile_id"], reason="unresolved_class_meaning")
            )
    return dict(pools=summaries, review=review)
