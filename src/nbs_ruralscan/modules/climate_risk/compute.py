"""M2 climate-risk math — pure transforms, arrays in / array out.

No network, no disk, no schema reads (that's the runner's job). Every function takes
already-loaded, grid-aligned ``xarray.DataArray``s and returns one. Unit-testable with
synthetic arrays, exactly like ``runtime/mcda.py``.

Maps to the M2 spec sub-steps (``methodology/modules/M2_climate_risk.md`` §6):
arithmetic plumbing (§6.5 weighted sum, §6.6 delta) is implemented; the genuine
methodology choices — fuzzy-membership standardisation (§6.2) and the Mode-B
vulnerability composition (§6.4) — are left as stubs for Brayden to author + justify
in Session C. The composition *operator* (§6.5) defaults to the spec's suggested
per-hazard ``H × E``; change ``how`` to revisit.
"""

from __future__ import annotations

from functools import reduce

import xarray as xr


def normalize_01(da: xr.DataArray) -> xr.DataArray:
    """Min–max rescale to 0–1 over the AOI (NaN-safe). Flat input → all zeros."""
    lo, hi = da.min(skipna=True), da.max(skipna=True)
    rng = hi - lo
    return xr.where(rng > 0, (da - lo) / rng, 0.0)


def standardize_hazard(da: xr.DataArray, params: dict) -> xr.DataArray:
    """Raw hazard metric → 0–1 hazard score via a fuzzy-membership curve (spec §6.2).

    ``params`` carries the curve type + breakpoints from ``T4.relationship_params`` /
    the recipe (the 5 inherited membership functions: sigmoid, linear, Gaussian, bell,
    inverted-sigmoid — v2 plan §4).

    TODO(Brayden, Session C): implement + document the membership choice. Consider
    delegating to a shared membership module so M1 and M2 use the same curves.
    """
    raise NotImplementedError("fuzzy-membership standardisation — author in Session C")


def combine_hazard_exposure(
    hazard: xr.DataArray, exposure: xr.DataArray, how: str = "multiply"
) -> xr.DataArray:
    """Per-hazard combine of a 0–1 hazard score with its 0–1 exposure (spec §6.5).

    Default ``multiply`` is the spec's suggested Mode-A operator (H × E). ``add`` and
    ``geometric_mean`` are offered for the sensitivity analysis Brayden will document.
    """
    if how == "multiply":
        return hazard * exposure
    if how == "add":
        return normalize_01(hazard + exposure)
    if how == "geometric_mean":
        return (hazard * exposure) ** 0.5
    raise ValueError(f"unknown combine op: {how!r}")


def composite_risk(
    per_hazard: dict[str, xr.DataArray], weights: dict[str, float]
) -> xr.DataArray:
    """Weighted sum across per-hazard risk layers, renormalised to 0–1 (spec §6.5).

    ``weights`` are the T2 hazard weights (need not pre-sum to 1; normalised here).
    """
    if not per_hazard:
        raise ValueError("no per-hazard layers to composite")
    total = sum(weights[h] for h in per_hazard)
    weighted = [(weights[h] / total) * da for h, da in per_hazard.items()]
    return normalize_01(reduce(lambda a, b: a + b, weighted))


def vulnerability_composite(
    sensitivity: xr.DataArray,
    adaptive_capacity: xr.DataArray,
    how: str = "geometric_mean",
) -> xr.DataArray:
    """Mode-B only: V = f(Sensitivity, Adaptive Capacity), 0–1, higher = more vulnerable (§6.4).

    TODO(Brayden, Session C): pick + justify the composition (weighted geometric mean /
    additive / PCA-derived). Skipped entirely in Mode A.
    """
    raise NotImplementedError("Mode-B vulnerability composition — author in Session C")


def apply_vulnerability(
    risk: xr.DataArray, vulnerability: xr.DataArray
) -> xr.DataArray:
    """Mode-B: fold vulnerability into the H×E risk surface (spec §6.5), renormalised."""
    return normalize_01(risk * vulnerability)


def delta(future: xr.DataArray, baseline: xr.DataArray) -> xr.DataArray:
    """Future − baseline risk (spec §6.6). Inputs share the grid; output is signed."""
    return future - baseline
