"""Execute schema-owned categorical membership and non-compensatory eligibility gates.

Unknown codes, missing host masks, and unresolved evidence propagate as NaN.
The caller supplies aligned arrays; land-use meanings never live in Python code.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import numpy as np


@dataclass
class CategoricalResult:
    values: np.ndarray
    status: np.ndarray
    mapping_ids: tuple[str, ...] = ()
    spatial_product_type: str = ""
    driver_crops: np.ndarray | None = None
    applicable_subpractices: tuple[str, ...] = ()
    crop_fractions: dict[str, np.ndarray] | None = None


def _object(value):
    return json.loads(value) if isinstance(value, str) else value


def evaluate_categorical(
    row: dict,
    data,
    *,
    dataset_id: str,
    masks: Mapping[str, np.ndarray] | None = None,
    mask_metadata: Mapping[str, dict] | None = None,
    evidence: Mapping[str, dict] | None = None,
    approved_only: bool = True,
) -> CategoricalResult:
    """Map exact dataset codes, then apply required boolean host conditions.

    Masks use 1/0/NaN = confirmed/absent/unknown and must match input shape.
    Schema-declared fraction masks accept [0,1], with a schema presence threshold.
    Zero is exclusion from this gate, not overall suitability. No implicit default.
    """
    if row.get("relationship_type") != "ranked_classes":
        raise ValueError("Expected ranked_classes")
    if row.get("dataset_id") != dataset_id:
        raise ValueError(
            "Dataset mismatch: categorical codes require an explicit crosswalk"
        )
    params = _object(row.get("relationship_params") or {})
    class_map = params.get("class_map")
    if not isinstance(class_map, dict) or not class_map:
        raise ValueError("class_map must be a nonempty mapping")
    scores = {}
    for key, score in class_map.items():
        if (
            isinstance(score, bool)
            or not isinstance(score, (int, float))
            or not np.isfinite(score)
            or not 0 <= score <= 1
        ):
            raise ValueError(
                "Categorical scores must be explicit finite numbers in [0,1]"
            )
        scores[str(key)] = float(score)
    arr = np.asarray(data)
    if np.issubdtype(arr.dtype, np.number):
        numeric_codes = []
        for code in scores:
            try:
                numeric_codes.append(float(code))
            except ValueError:
                continue
        if len(numeric_codes) != len(set(numeric_codes)):
            raise ValueError("Duplicate numeric class codes")
    values = np.full(arr.shape, np.nan)
    status = np.full(arr.shape, "unmapped_class", dtype=object)
    result = CategoricalResult(values, status, (row.get("mapping_id", ""),))
    ids = _object(row.get("evidence_ids") or [])
    if not isinstance(ids, list) or not all(isinstance(eid, str) for eid in ids):
        raise ValueError("evidence_ids must be a list of identifiers")
    if evidence is None or not ids:
        status[...] = "missing_evidence"
        return result
    for eid in ids:
        ev = evidence.get(eid)
        if not ev or ev.get("review_state") == "dropped":
            status[...] = "unavailable_evidence"
            return result
        if approved_only and str(ev.get("reviewer_ok", "")).lower() != "true":
            status[...] = "pending_evidence_review"
            return result
    if approved_only and params.get("mapping_review_status", "approved") != "approved":
        status[...] = "pending_mapping_review"
        return result
    gate = params.get("mapping_role") == "eligibility_gate"
    if gate and any(score not in (0, 1) for score in scores.values()):
        raise ValueError("Eligibility gates require binary scores")
    masks = masks or {}
    requirements = params.get("class_requirements", {})
    if not isinstance(requirements, dict) or set(requirements) - set(scores):
        raise ValueError("Requirements must refer to mapped classes")
    for code, score in scores.items():
        # Raster numeric codes compare numerically without truncating fractional values.
        if np.issubdtype(arr.dtype, np.number):
            try:
                match = arr == float(code)
            except ValueError:
                continue
        else:
            match = arr.astype(str) == code
        values[match] = score
        status[match] = "excluded" if gate and score == 0 else "mapped"
        names = requirements.get(code, [])
        if not isinstance(names, list) or not all(isinstance(n, str) for n in names):
            raise ValueError("Class requirements must be a list of mask names")
        for name in names:
            mask = np.asarray(masks.get(name, np.full(arr.shape, np.nan)), dtype=float)
            if mask.shape != arr.shape:
                raise ValueError(f"Mask {name} shape does not match input")
            fractional = params.get("mask_value_types", {}).get(name) == "fraction"
            invalid = (mask < 0) | (mask > 1) if fractional else ~np.isin(mask, [0, 1])
            if np.any(np.isfinite(mask) & invalid) or np.any(np.isinf(mask)):
                raise ValueError(
                    f"Mask {name} must contain {'fractions in [0,1]' if fractional else '0, 1'} or NaN"
                )
            if fractional:
                threshold = params.get("mask_presence_thresholds", {}).get(name)
                if not isinstance(threshold, (float, int)) or not 0 <= threshold < 1:
                    raise ValueError(
                        "Fraction mask requires a schema presence threshold in [0,1)"
                    )
                mask = np.where(
                    np.isnan(mask), np.nan, (mask > threshold).astype(float)
                )
            expected = params.get("required_mask_metadata", {}).get(name)
            if expected:
                meta = (mask_metadata or {}).get(name, {})
                reason = ""
                if not meta.get("dataset_id") or not meta.get("source_reference"):
                    reason = "missing_mask_provenance"
                elif any(
                    meta.get(k) not in v if isinstance(v, list) else meta.get(k) != v
                    for k, v in expected.items()
                ):
                    reason = "incompatible_host_data"
                if reason:
                    unresolved = match & (values != 0)
                    values[unresolved] = np.nan
                    status[unresolved] = reason
                    continue
            absent = match & (mask == 0)
            unknown = match & np.isnan(mask) & (values != 0)
            values[absent] = 0
            status[absent] = "host_absent"
            values[unknown] = np.nan
            status[unknown] = "missing_host_context"
    fraction_name = params.get("host_fraction_mask")
    if fraction_name:
        fraction = np.asarray(
            masks.get(fraction_name, np.full(arr.shape, np.nan)), dtype=float
        )
        result.crop_fractions = {
            params["host_crop"]: np.where(
                values == 0, 0, np.where(values == 1, fraction, np.nan)
            )
        }
    return result


def apply_eligibility(suitability, gate):
    """Hard exclusions cannot be compensated by a high score on another criterion."""
    s = np.asarray(suitability, dtype=float)
    g = np.asarray(gate, dtype=float)
    if s.shape != g.shape:
        raise ValueError("Suitability and eligibility shapes must match")
    if np.any(np.isfinite(g) & ~np.isin(g, [0, 1])) or np.any(np.isinf(g)):
        raise ValueError("Eligibility must be 0, 1 or NaN")
    return np.where(g == 0, 0, np.where(g == 1, s, np.nan))


def evaluate_family(
    schema_root,
    nbs_id,
    family,
    datasets: Mapping[str, np.ndarray],
    *,
    masks=None,
    mask_metadata=None,
    crop=None,
    approved_only=True,
) -> CategoricalResult:
    """Execute configured family gates from generated T4 JSON; never borrow a family.

    A dataset array is required to define output shape even when a gate is absent.
    Missing evidence/configuration returns explicit unknown; qualitative families
    cannot yield an area mask. Caller retains spatial_product_type for reporting.
    """
    root = Path(schema_root)
    if not datasets:
        raise ValueError("Supply at least one aligned dataset array for output shape")
    shape = np.asarray(next(iter(datasets.values()))).shape
    if any(np.asarray(a).shape != shape for a in datasets.values()):
        raise ValueError("All datasets must be aligned with identical shapes")
    fams = json.loads(
        (root / "registers/FAM_family_registry.json").read_text(encoding="utf-8")
    )
    products = {
        r["spatial_product_type"]
        for r in fams
        if r["nbs_id"] == nbs_id and r["suitability_family_id"] == family
    }
    if len(products) != 1:
        raise ValueError("Unknown or ambiguous family")
    product = next(iter(products))
    empty = CategoricalResult(
        np.full(shape, np.nan),
        np.full(shape, "no_categorical_evidence", dtype=object),
        (),
        product,
    )
    if product == "qualitative_only":
        empty.status[...] = "qualitative_only"
        return empty
    rows = json.loads(
        (root / f"recipes/{nbs_id}/T4_suitability_mappings.json").read_text(
            encoding="utf-8"
        )
    )
    gates = [
        r
        for r in rows
        if r.get("suitability_family_id") == family
        and r.get("relationship_type") == "ranked_classes"
        and r.get("relationship_params", {}).get("mapping_role") == "eligibility_gate"
    ]
    if crop is not None:
        configured_crops = {r["relationship_params"].get("host_crop") for r in gates}
        if crop not in configured_crops:
            raise ValueError("Crop has no configured categorical mapping")
        gates = [
            r
            for r in gates
            if r["relationship_params"].get("host_crop") in (None, crop)
        ]
    if not gates:
        return empty
    evidence = {
        r["evidence_id"]: r
        for r in json.loads(
            (root / "registers/EV_evidence_register.json").read_text(encoding="utf-8")
        )
    }
    parts = []
    for row in gates:
        ds = row["dataset_id"]
        if ds not in datasets:
            part = CategoricalResult(
                np.full(shape, np.nan),
                np.full(shape, "missing_dataset", dtype=object),
                (row["mapping_id"],),
            )
        else:
            part = evaluate_categorical(
                row,
                datasets[ds],
                dataset_id=ds,
                masks=masks,
                mask_metadata=mask_metadata,
                evidence=evidence,
                approved_only=approved_only,
            )
        parts.append((row["relationship_params"].get("host_crop"), part))
    common = [part for host, part in parts if host is None]
    crops = sorted({host for host, _ in parts if host is not None})
    subpractices = tuple(
        sorted(
            {
                sub
                for r in gates
                for sub in r["relationship_params"].get("applicable_subpractices", [])
            }
        )
    )
    if not crops:
        result = _and_gates(common, shape)
    else:
        variants = [
            _and_gates(common + [part for host, part in parts if host == name], shape)
            for name in crops
        ]
        stack = np.stack([r.values for r in variants])
        yes = np.any(stack == 1, axis=0)
        no = np.all(stack == 0, axis=0)
        values = np.where(yes, 1, np.where(no, 0, np.nan))
        status = np.full(shape, "excluded", dtype=object)
        status[yes] = "eligible"
        unknown = ~yes & ~no
        for variant in variants:
            hit = unknown & np.isnan(variant.values)
            status[hit] = variant.status[hit]
        # Retain all tied eligible crops; unknown alternatives never erase a known pass.
        drivers = np.full(shape, "", dtype=object)
        for name, variant in zip(crops, variants):
            hit = variant.values == 1
            drivers[hit] = np.where(drivers[hit] == "", name, drivers[hit] + "|" + name)
        result = CategoricalResult(values, status, driver_crops=drivers)
    if crops:
        result.crop_fractions = {}
        for name, variant in zip(crops, variants):
            candidates = [
                part.crop_fractions[name]
                for host, part in parts
                if host == name and part.crop_fractions and name in part.crop_fractions
            ]
            fraction = candidates[0] if candidates else np.full(shape, np.nan)
            result.crop_fractions[name] = np.where(
                variant.values == 0, 0, np.where(variant.values == 1, fraction, np.nan)
            )
    result.mapping_ids = tuple(r["mapping_id"] for r in gates)
    result.spatial_product_type = product
    result.applicable_subpractices = subpractices
    return result


def _and_gates(parts, shape):
    values = np.ones(shape)
    status = np.full(shape, "eligible", dtype=object)
    for part in parts:
        # false AND unknown = false; unknown AND true = unknown
        zero = (values == 0) | (part.values == 0)
        unknown = ~zero & (np.isnan(values) | np.isnan(part.values))
        status[unknown & np.isnan(part.values)] = part.status[
            unknown & np.isnan(part.values)
        ]
        status[zero] = "excluded"
        values = np.where(zero, 0, np.where(unknown, np.nan, 1))
    return CategoricalResult(values, status)
