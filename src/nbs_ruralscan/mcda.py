"""Spatial MCDA — Python port of ``reference/R/spatMCDA.R``.

Pure-numpy math core for the suitability MCDA used in M1 (and shared by M4
hotspots). Each function operates on standardised criterion arrays (already
in 0-1 after the fuzzy-membership transform from `T4.relationship_params`).

Pipes:

    stack (H,W,K)  ─┬─►  critic_weights ──┐
                    ├─►  entropy_weights ─┤
                    └─►  ahp_weights ─────┴─►  reconcile_weights
                                              │
                                              ▼
                                         weighted_overlay (H,W)
                                              │
                                              ├─► quartile_classify (H,W) int
                                              └─► sensitivity_perturb (H,W) variance

Mirrors the R script's steps 6-11 (CRITIC + Entropy + AHP + overlay +
classify + sensitivity). The earlier R steps (1-5: load + align + scale) are
caller-side raster I/O — out of scope here.

Aligned to M1 §13 signature suggestions (pure-numpy; the GEE Image wrapper
is a thin adapter if/when needed).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

# ── 6.4: weight derivation ──


def critic_weights(matrix: np.ndarray) -> np.ndarray:
    """CRITIC weights (Diakoulaki et al. 1995).

    `matrix` is `(n_pixels, n_criteria)`, standardised 0-1 (higher = more
    suitable). NaN-tolerant: rows with any NaN are dropped before stats.

    Returns weights `(n_criteria,)`, normalised to sum to 1.
    """
    arr = np.asarray(matrix, dtype=float)
    mask = ~np.any(np.isnan(arr), axis=1)
    clean = arr[mask]
    if clean.shape[0] < 2:
        raise ValueError("CRITIC needs ≥2 complete rows")
    sd = clean.std(axis=0, ddof=0)
    cor = np.corrcoef(clean, rowvar=False)
    if cor.ndim == 0:  # single-criterion edge case
        cor = np.array([[1.0]])
    cj = sd * (1.0 - cor).sum(axis=0)
    total = cj.sum()
    if total == 0:
        raise ValueError("CRITIC information sum is zero (constant criteria?)")
    return cj / total


def entropy_weights(matrix: np.ndarray) -> np.ndarray:
    """Shannon entropy weights.

    `matrix` `(n_pixels, n_criteria)`, standardised 0-1. Each criterion is
    row-normalised over pixels (column-wise probability mass). Weight =
    (1 - entropy) / Σ (1 - entropy).
    """
    arr = np.asarray(matrix, dtype=float)
    mask = ~np.any(np.isnan(arr), axis=1)
    clean = arr[mask]
    if clean.shape[0] < 2:
        raise ValueError("entropy needs ≥2 complete rows")
    col_sums = clean.sum(axis=0)
    col_sums = np.where(col_sums == 0, 1e-12, col_sums)
    p = clean / col_sums  # column-wise probability mass
    k = 1.0 / np.log(clean.shape[0])
    e = -k * (p * np.log(p + 1e-12)).sum(axis=0)
    d = 1.0 - e
    total = d.sum()
    if total == 0:
        raise ValueError("entropy information sum is zero")
    return d / total


def ahp_consistency_ratio(matrix: np.ndarray) -> float:
    """AHP consistency ratio (Saaty). CR < 0.10 is conventionally acceptable.

    Returns the consistency ratio scalar. NaN if matrix order ≤ 2 (CR
    undefined).
    """
    A = np.asarray(matrix, dtype=float)
    n = A.shape[0]
    if n <= 2:
        return float("nan")
    eig = np.linalg.eigvals(A).real
    lam_max = eig.max()
    ci = (lam_max - n) / (n - 1)
    # Saaty's Random Index for n ≤ 10
    ri_table = {
        1: 0.0,
        2: 0.0,
        3: 0.58,
        4: 0.90,
        5: 1.12,
        6: 1.24,
        7: 1.32,
        8: 1.41,
        9: 1.45,
        10: 1.49,
    }
    ri = ri_table.get(n, 1.49)
    if ri == 0:
        return 0.0
    return float(ci / ri)


def ahp_weights(matrix: np.ndarray) -> np.ndarray:
    """AHP weights from a pairwise-comparison matrix (geometric-mean method).

    Symmetric to the eigenvector method for consistent matrices, more stable
    numerically. Returns weights `(n_criteria,)`, normalised to sum to 1.

    `matrix` must be a square (n, n) pairwise-comparison matrix; diagonal 1.0.
    """
    A = np.asarray(matrix, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("AHP matrix must be square")
    # Geometric mean of each row
    gm = np.exp(np.log(A).mean(axis=1))
    return gm / gm.sum()


def reconcile_weights(
    *,
    ahp: np.ndarray | None = None,
    critic: np.ndarray | None = None,
    entropy: np.ndarray | None = None,
    alpha: float = 0.4,
) -> np.ndarray:
    """Hybrid α-reconciled weights.

    `final = alpha * subjective + (1 - alpha) * objective`, where the
    objective half is the mean of `critic` and `entropy` when both supplied
    (or whichever one is). Subjective = `ahp` if provided.

    All inputs must sum to 1 already (validated). `alpha = 0.4` is the
    framework default (subjective slightly under-weighted; objective gets
    more pull). Returns weights summing to 1.
    """
    if not (0.0 <= alpha <= 1.0):
        raise ValueError("alpha ∈ [0, 1]")
    if ahp is None and critic is None and entropy is None:
        raise ValueError("provide at least one weight vector")

    def _check(v: np.ndarray, name: str) -> np.ndarray:
        arr = np.asarray(v, dtype=float)
        if not np.isclose(arr.sum(), 1.0, atol=1e-3):
            raise ValueError(f"{name} weights must sum to ~1.0; got {arr.sum():.4f}")
        return arr

    obj_parts = []
    if critic is not None:
        obj_parts.append(_check(critic, "critic"))
    if entropy is not None:
        obj_parts.append(_check(entropy, "entropy"))
    obj = np.mean(obj_parts, axis=0) if obj_parts else None

    if ahp is not None and obj is not None:
        sub = _check(ahp, "ahp")
        w = alpha * sub + (1.0 - alpha) * obj
    elif ahp is not None:
        w = _check(ahp, "ahp")
    elif obj is not None:
        w = obj
    else:
        # unreachable — guarded by the initial all-None check
        raise ValueError("no weight vector supplied")
    return w / w.sum()


def ahp_matrix_from_weights(weights: np.ndarray) -> np.ndarray:
    """Construct a perfectly consistent AHP pairwise-comparison matrix from
    a target weight vector (each `a_ij = w_i / w_j`). Mirrors the R script
    §8 "automated AHP matrix from CRITIC" — useful for sanity-checking.
    """
    w = np.asarray(weights, dtype=float)
    return np.outer(w, 1.0 / w)


# ── 6.6: weighted overlay ──


def weighted_overlay(stack: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """Weighted linear combination across criteria.

    `stack` is `(H, W, K)`; `weights` is `(K,)`. Returns `(H, W)` suitability
    surface. NaN-propagating.
    """
    s = np.asarray(stack, dtype=float)
    w = np.asarray(weights, dtype=float)
    if s.shape[-1] != w.shape[0]:
        raise ValueError(f"stack last dim {s.shape[-1]} ≠ weights len {w.shape[0]}")
    if not np.isclose(w.sum(), 1.0, atol=1e-3):
        raise ValueError(f"weights must sum to ~1.0; got {w.sum():.4f}")
    return (s * w).sum(axis=-1)


# ── 6.7: sensitivity perturbation ──


@dataclass
class SensitivityResult:
    mean: np.ndarray  # mean suitability across runs
    variance: np.ndarray  # per-pixel variance — uncertainty proxy
    weights_min: np.ndarray  # per-criterion min weight observed
    weights_max: np.ndarray  # per-criterion max weight observed


def sensitivity_perturb(
    stack: np.ndarray,
    weights: np.ndarray,
    *,
    n: int = 50,
    scale: float = 0.10,
    seed: int | None = None,
) -> SensitivityResult:
    """Per-pixel sensitivity: perturb weights ±`scale` × n times, return
    mean + variance maps. Mirrors the R script's §11 ±10 % perturbation,
    generalised to n runs.
    """
    rng = np.random.default_rng(seed)
    s = np.asarray(stack, dtype=float)
    w0 = np.asarray(weights, dtype=float)
    H, W, K = s.shape
    runs = np.empty((n, H, W), dtype=float)
    ws = np.empty((n, K), dtype=float)
    for i in range(n):
        perturb = w0 * (1.0 + rng.uniform(-scale, scale, size=K))
        perturb = perturb / perturb.sum()
        ws[i] = perturb
        runs[i] = weighted_overlay(s, perturb)
    return SensitivityResult(
        mean=runs.mean(axis=0),
        variance=runs.var(axis=0),
        weights_min=ws.min(axis=0),
        weights_max=ws.max(axis=0),
    )


# ── 6.8: classify ──


def quartile_classify(
    suitability: np.ndarray,
    labels: Sequence[str] = ("Unsuitable", "Marginal", "Moderate", "Highly Suitable"),
) -> tuple[np.ndarray, dict[int, str]]:
    """4-class natural-breaks (quartile) classification.

    Returns `(class_array, legend)` where `class_array` is 1-4 (and 0 for
    NaN / masked-out pixels) and `legend` maps class → label.
    """
    if len(labels) != 4:
        raise ValueError("expected 4 labels (one per quartile)")
    s = np.asarray(suitability, dtype=float)
    valid = ~np.isnan(s)
    q = np.quantile(s[valid], [0.25, 0.5, 0.75])
    classes = np.zeros(s.shape, dtype=np.int8)
    classes[valid & (s <= q[0])] = 1
    classes[valid & (s > q[0]) & (s <= q[1])] = 2
    classes[valid & (s > q[1]) & (s <= q[2])] = 3
    classes[valid & (s > q[2])] = 4
    return classes, {1: labels[0], 2: labels[1], 3: labels[2], 4: labels[3]}
