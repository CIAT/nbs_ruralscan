"""Evaluate numeric T4 rows against supplied arrays; no raster acquisition.

Ordinal profiles require explicit selection. Unknown ranges, boundaries and NaNs
remain unknown. Source scores are ordinal, not calibrated suitability probabilities.
"""

from __future__ import annotations
import json
import numpy as np


def evaluate_numeric(row, values, *, profile_id=None, pool_id=None):
    params = row["relationship_params"]
    if isinstance(params, str):
        params = json.loads(params)
    x = np.asarray(values, dtype=float)
    result = np.full(x.shape, np.nan)
    if pool_id is not None:
        if profile_id is not None:
            raise ValueError("Choose a profile or a harmonized pool, not both")
        pools = [
            p
            for p in params.get("harmonization", {}).get("pools", [])
            if p["pool_id"] == pool_id
        ]
        if len(pools) != 1:
            raise ValueError("Unknown or duplicate harmonized pool")
        # Ties and exclusion conflicts have score=None and remain unknown.
        selected = {
            "relationship_type": "piecewise",
            "relationship_params": {
                "profiles": [{"profile_id": pool_id, "intervals": pools[0]["cells"]}]
            },
        }
        return evaluate_numeric(selected, x, profile_id=pool_id)
    if row["relationship_type"] == "threshold":
        cut = params.get("threshold")
        if isinstance(cut, bool) or not isinstance(cut, (float, int)):
            raise ValueError(
                "Numeric threshold required; legal category masks need their own adapter"
            )
        result = (x >= cut if params["above_is_suitable"] else x <= cut).astype(float)
    elif row["relationship_type"] == "piecewise" and "profiles" in params:
        if profile_id is None:
            return result
        profiles = [p for p in params["profiles"] if p["profile_id"] == profile_id]
        if len(profiles) != 1:
            raise ValueError("Unknown or duplicate numeric profile")
        count = np.zeros(x.shape, dtype=int)
        for band in profiles[0]["intervals"]:
            mask = np.isfinite(x)
            if band["lower"] is not None:
                mask &= (
                    x >= band["lower"] if band["lower_inclusive"] else x > band["lower"]
                )
            if band["upper"] is not None:
                mask &= (
                    x <= band["upper"] if band["upper_inclusive"] else x < band["upper"]
                )
            result = np.where(
                mask, np.nan if band["score"] is None else band["score"], result
            )
            count += mask
        result = np.where(count == 1, result, np.nan)
    elif row["relationship_type"] == "piecewise" and "points" in params:
        points = np.asarray(params["points"], dtype=float)
        result = np.interp(x, points[:, 0], points[:, 1], left=np.nan, right=np.nan)
    else:
        raise ValueError("Unsupported numeric relationship")
    return np.where(np.isfinite(x), result, np.nan)
