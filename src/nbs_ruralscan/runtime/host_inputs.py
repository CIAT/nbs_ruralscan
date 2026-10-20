"""Plan schema-owned host inputs; expose unresolved uploads instead of guessing masks.

This module performs no downloads or reprojection. Callers crop data at native support,
retain source metadata, then align masks with the categorical executor's input grid.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from .binding import load_bindings, resolve_binding


def plan_family_inputs(schema_root, nbs_id, family, aoi_contexts):
    """Resolve every declared host mask and supporting layer through BIND.

    The used binding's band accompanies its dataset (including on upload fallback).
    Plans describe dependencies, not proof that a raster has been fetched or a mask
    derived. Local overrides must supply compatible units and provenance.
    """
    root = Path(schema_root)
    rows = json.loads(
        (root / f"recipes/{nbs_id}/T4_suitability_mappings.json").read_text(
            encoding="utf-8"
        )
    )
    registry = {
        r["dataset_id"]: r
        for r in json.loads(
            (root / "T1_data_registry.json").read_text(encoding="utf-8")
        )
    }
    bindings = load_bindings(root)
    plans = {}
    for row in rows:
        if row.get("suitability_family_id") != family:
            continue
        params = row.get("relationship_params", {})
        names = {
            name
            for req in params.get("class_requirements", {}).values()
            for name in req
        }
        for name in sorted(names):
            spec = params.get("host_bindings", {}).get(name)
            if not spec:
                plans[name] = {"status": "missing_binding_contract", "inputs": {}}
                continue
            inputs = {}
            for variable in spec["variables"] + spec.get("supporting_variables", []):
                resolution = resolve_binding(bindings, variable, set(aoi_contexts))
                used = resolution.fell_back_to or resolution.winning_binding
                inputs[variable] = {
                    **asdict(resolution),
                    "band": used.band,
                    "dataset": registry.get(resolution.dataset_id),
                }
            required = [inputs[v] for v in spec["variables"]]
            status = (
                "requires_upload"
                if any(v["dataset_id"] is None for v in required)
                else "ready_to_fetch"
            )
            candidate = {"status": status, "spec": spec, "inputs": inputs}
            if name in plans and plans[name] != candidate:
                raise ValueError(f"Conflicting host binding contracts for {name}")
            plans[name] = candidate
    return plans


def crop_area_fraction(components_ha, pixel_area_ha):
    """Combine schema-selected physical crop areas, then divide by pixel area.

    Components must be disjoint crop components, not duplicate technology totals.
    Preserve unknowns and reject invalid extents; never silently clip over-allocation.
    Pixel areas must use the same grid as input areas, before any resampling.
    """
    if not components_ha:
        raise ValueError("At least one crop-area component is required")
    area = np.asarray(pixel_area_ha, dtype=float)
    parts = [np.asarray(p, dtype=float) for p in components_ha]
    if any(p.shape != area.shape for p in parts):
        raise ValueError("Crop and pixel areas must have identical shapes")
    if np.any(~np.isfinite(area) | (area <= 0)):
        raise ValueError("Pixel area must be positive and finite")
    if any(np.any(np.isinf(p) | (p < 0)) for p in parts):
        raise ValueError("Crop areas must be nonnegative or NaN")
    fraction = np.sum(parts, axis=0) / area
    if np.any(fraction > 1):
        raise ValueError(
            "Crop area exceeds pixel area; check units, overlap and technology totals"
        )
    return fraction
