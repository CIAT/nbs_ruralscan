"""Compile reviewed ordinal numeric bands using an explicit schema policy.

Never extrapolate a low class, interpolate ranks, or infer family applicability.
"""

from __future__ import annotations

import json
import re
from dataclasses import replace

from .synthesis import SynthesisReport, _harmonise, _weight, _resolve_root_origin
from .harmonization import harmonize, standardize

NUMBER = r"-?(?:\d+(?:\.\d*)?|\.\d+)"


def bounds(raw, reverse=False):
    """Parse source intervals. Reversed bounds and compound ORs require review."""
    raw = str(raw).strip().replace("%", "").replace("–", "-").replace("−", "-")
    m = re.fullmatch(rf"([<>]=?|[≤≥])\s*({NUMBER})", raw)
    if m:
        op, number = m.groups()
        return (
            (None, float(number), False, "=" in op or op == "≤")
            if op[0] in "<≤"
            else (float(number), None, "=" in op or op == "≥", False)
        )
    m = re.fullmatch(rf"({NUMBER})\s*-\s*({NUMBER})", raw)
    if m and reverse and float(m[1]) > float(m[2]):
        return float(m[2]), float(m[1]), True, True
    if not m or float(m[1]) >= float(m[2]):
        raise ValueError("ambiguous_or_reversed_interval")
    return float(m[1]), float(m[2]), True, True


def _interval(low, high, label, scale, includes_low=True, includes_high=True):
    key = label.strip().lower().replace(" ", "_")
    if key not in scale:
        raise ValueError("unknown_ordinal_label")
    if low is not None and high is not None and low >= high:
        raise ValueError("ambiguous_or_reversed_interval")
    return {
        "lower": low,
        "upper": high,
        "lower_inclusive": includes_low,
        "upper_inclusive": includes_high,
        "label": label,
        "rank": scale[key],
        "score": scale[key] / max(scale.values()),
    }


def parse_profiles(rel, policy):
    scale = json.loads(policy["ordinal_scale"])
    if (
        not scale
        or max(scale.values()) <= 0
        or any(not isinstance(v, (int, float)) or v < 0 for v in scale.values())
    ):
        raise ValueError("invalid_ordinal_scale")
    encoding = policy["encoding"]
    profiles = {}
    if encoding == "labelled_ranges":
        items = rel[policy["field"]]
        if isinstance(items, str):
            items = [
                dict(zip(("label", "range"), p.split(":", 1))) for p in items.split(",")
            ]
        profiles["default"] = [
            _interval(
                *bounds(x["range"], policy.get("range_order") == "descending_allowed")[
                    :2
                ],
                x["label"],
                scale,
                *bounds(x["range"], policy.get("range_order") == "descending_allowed")[
                    2:
                ],
            )
            for x in items
        ]
    elif encoding == "field_ranges":
        mapping = json.loads(policy["field"])
        profiles["default"] = [
            _interval(*bounds(rel[field])[:2], label, scale, *bounds(rel[field])[2:])
            for label, field in mapping.items()
        ]
    elif encoding == "favourable_above":
        profiles["default"] = [
            _interval(rel["favorable_above"], None, "favourable", scale, False, False)
        ]
    elif encoding == "named_bounds":
        bands = []
        for label in scale:
            fields = {
                k.removeprefix(label + "_"): v
                for k, v in rel.items()
                if k.startswith(label + "_")
            }
            lo = next(
                (
                    v
                    for k, v in fields.items()
                    if k in {"low", "min", "min_C", "min_deg"}
                ),
                None,
            )
            hi = next(
                (
                    v
                    for k, v in fields.items()
                    if k in {"high", "max", "max_C", "max_deg"}
                ),
                None,
            )
            if "threshold_C" in fields:
                if policy["threshold_direction"] != "below":
                    raise ValueError("threshold_direction_required")
                hi = fields["threshold_C"]
            if lo is not None or hi is not None:
                bands.append(_interval(lo, hi, label, scale))
        profiles["default"] = bands
    elif encoding == "grouped_ranges":
        for group, items in rel.items():
            if not group.startswith("group") or not isinstance(items, dict):
                continue
            bands = []
            for raw, rank in items.items():
                labels = [label for label, value in scale.items() if value == rank]
                if len(labels) != 1:
                    raise ValueError("unknown_ordinal_rank")
                low, high, il, ih = bounds(raw)
                bands.append(_interval(low, high, labels[0], scale, il, ih))
            profiles[group] = bands
    else:
        raise ValueError("unsupported_band_encoding")
    for bands in profiles.values():
        if not bands:
            raise ValueError("no_numeric_bands")
        bands.sort(key=lambda b: float("-inf") if b["lower"] is None else b["lower"])
        for a, b in zip(bands, bands[1:]):
            if a["upper"] is None or b["lower"] is None or a["upper"] > b["lower"]:
                raise ValueError("overlapping_source_intervals")
    return profiles


def compile_bands(
    units, policies, canonical_unit, conversions, *, tiers=None, categories=None
):
    profiles, used, unresolved = [], [], []
    tiers, categories = tiers or {}, categories or {}
    by_id = {u.evidence_id: u for u in units}
    by_source = {}
    for unit in units:
        by_source.setdefault(unit.source_id, []).append(unit)
    for u in units:
        policy = policies[u.evidence_id]
        # Preserve the explicit audited hold reason, including duplicate responses.
        # The evidence-type gate still prevents selection-only records compiling.
        if policy["action"] != "compile":
            unresolved.append((u.evidence_id, policy["reason"]))
            continue
        if u.evidence_type not in {"literature_relationship", "expert"}:
            unresolved.append((u.evidence_id, "selection_only"))
            continue
        try:
            parsed = parse_profiles(u.relationship or {}, policy)
            hp = policy.get("harmonization") or {}
            if isinstance(hp, str):
                hp = json.loads(hp)
            origin = _resolve_root_origin(u, by_id, by_source)
            origin_units = [x for x in units if x.source_id == origin]
            if origin_units:
                weight = max(
                    _weight(
                        x,
                        tiers.get(x.source_id, "medium"),
                        categories.get(x.source_id, ""),
                    )
                    for x in origin_units
                )
            else:
                weight = _weight(
                    u, tiers.get(u.source_id, "medium"), categories.get(u.source_id, "")
                )
            converted_profiles = []
            for group, bands in parsed.items():
                if (
                    hp.get("expected_class_count")
                    and len(bands) != hp["expected_class_count"]
                ):
                    raise ValueError("incomplete_source_class_table")
                if hp:
                    standardize(bands, hp)
                for band in bands:
                    for key in ("lower", "upper"):
                        if band[key] is not None:
                            probe = replace(
                                u,
                                relationship={
                                    "abs_max": band[key],
                                    "unit": policy["input_unit"],
                                },
                            )
                            value = _harmonise(
                                probe,
                                canonical_unit,
                                conversions,
                                SynthesisReport(),
                                precise=True,
                            )
                            if not value:
                                raise ValueError(
                                    "numeric_band_unit_conversion_required"
                                )
                            band[key] = value["abs_max"]
                converted_profiles.append(
                    {
                        "profile_id": u.evidence_id
                        + ("" if group == "default" else "__" + group),
                        "source_id": u.source_id,
                        "continuation_of": hp.get("continuation_of", ""),
                        "evidence_ids": [u.evidence_id],
                        "page_locators": {u.evidence_id: u.page},
                        "evidence_id": u.evidence_id,
                        "context": u.context or {},
                        "source_group": group,
                        "ordinal_scale": json.loads(policy["ordinal_scale"]),
                        "applicability_note": policy["applicability_note"],
                        "unit": canonical_unit,
                        "intervals": bands,
                        "origin_id": origin,
                        "source_weight": weight,
                        "variable": u.variable,
                        "score_policy": hp.get("version", "legacy_rank_max"),
                        "pool_id": hp.get("pool_id", ""),
                        "system_id": hp.get("system_id", ""),
                        "context_id": hp.get("context_id", ""),
                        "compatibility_approved": hp.get(
                            "compatibility_approved", False
                        ),
                        "applicability_review": hp.get("applicability_review", {}),
                        "pool_review": hp.get(
                            "pool_review", "compatibility_review_required"
                        ),
                    }
                )
            profiles.extend(converted_profiles)
            used.append(u.evidence_id)
        except (ValueError, KeyError, TypeError) as exc:
            unresolved.append((u.evidence_id, str(exc)))
    profiles, rejected = join_continuations(profiles)
    unresolved.extend(rejected)
    used = [eid for eid in used if eid not in {eid for eid, _ in rejected}]
    return (
        {
            "profiles": profiles,
            "profile_selection": "explicit",
            "outside_domain": "unknown",
            "conflicting_boundaries": "unknown",
            "score_policy": "per_profile_schema_policy",
            "harmonization": harmonize(profiles),
            "score_interpretation": "Relative suitability convention; source ranks retained; not probability or measured performance",
        }
        if profiles
        else {},
        used,
        unresolved,
    )


def join_continuations(profiles):
    """Join explicitly linked table fragments without inventing cross-page quotes.

    Only identical source, variable, context and scale may continue a response.
    Missing/unapproved parents and overlaps remain explicit unresolved records.
    """
    bases = {p["profile_id"]: p for p in profiles if not p.get("continuation_of")}
    rejected = []
    for part in profiles:
        parent_id = part.get("continuation_of")
        if not parent_id:
            continue
        parent = bases.get(parent_id)
        keys = (
            "source_id",
            "variable",
            "unit",
            "ordinal_scale",
            "score_policy",
            "origin_id",
            "system_id",
            "context_id",
            "pool_id",
        )
        if parent is None or any(parent[k] != part[k] for k in keys):
            rejected.append(
                (part["evidence_id"], "incompatible_or_missing_table_continuation")
            )
            continue
        bands = sorted(
            parent["intervals"] + part["intervals"],
            key=lambda b: float("-inf") if b["lower"] is None else b["lower"],
        )
        if any(
            a["upper"] is None or b["lower"] is None or a["upper"] > b["lower"]
            for a, b in zip(bands, bands[1:])
        ):
            rejected.append((part["evidence_id"], "overlapping_table_continuation"))
            continue
        parent["intervals"] = bands
        parent["evidence_ids"] = sorted(
            set(parent["evidence_ids"] + part["evidence_ids"])
        )
        parent["page_locators"].update(part["page_locators"])
    return list(bases.values()), rejected
