"""EO-derived farming-system classifier (T7 `farming_system` vocab, v0.3.0+).

Six-class scoping-grade classifier:
`cropping_rainfed` · `cropping_irrigated` · `mixed_crop_livestock` ·
`agro_pastoral` · `pastoral_rangeland` · `tree_perennial`.

Decision tree (priority order — first match wins):

    1. tree-perennial dominant → tree_perennial
    2. cropland present + irrigation share ≥ thr_irrigation → cropping_irrigated
    3. cropland present + livestock density ≥ thr_livestock_mixed → mixed_crop_livestock
    4. cropland present (low livestock, low irrigation) → cropping_rainfed
    5. no cropland + livestock density ≥ thr_livestock_pastoral → pastoral_rangeland
    6. no cropland + livestock density between thr_livestock_agro and pastoral → agro_pastoral
    7. otherwise → "other" (rare; flag for review)

Inputs are aligned float arrays at the analysis grid (caller's
responsibility). Cropland is binary (or fractional); livestock is TLU/km² (or
species density); irrigation is fraction equipped (0-1); tree-perennial is
binary mask or fractional canopy.

Thresholds default to documented v0.3.0 scoping-grade values; override per AOI
via `Thresholds`.

Companion: `methodology/farming_system_classifier.md`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Class id constants
CROPPING_RAINFED = "cropping_rainfed"
CROPPING_IRRIGATED = "cropping_irrigated"
MIXED_CROP_LIVESTOCK = "mixed_crop_livestock"
AGRO_PASTORAL = "agro_pastoral"
PASTORAL_RANGELAND = "pastoral_rangeland"
TREE_PERENNIAL = "tree_perennial"
OTHER = "other"

CLASSES = (
    CROPPING_RAINFED,
    CROPPING_IRRIGATED,
    MIXED_CROP_LIVESTOCK,
    AGRO_PASTORAL,
    PASTORAL_RANGELAND,
    TREE_PERENNIAL,
    OTHER,
)


@dataclass
class Thresholds:
    """v0.3.0 scoping-grade defaults; document any AOI overrides."""

    cropland_present: float = 0.10
    """Cropland fraction above which the pixel counts as cropland (0-1)."""

    irrigation_share: float = 0.20
    """GMIA irrigation share above which cropland is `cropping_irrigated`."""

    livestock_mixed_tlu_per_km2: float = 5.0
    """GLW ruminant TLU/km² above which cropland is mixed_crop_livestock."""

    livestock_agro_tlu_per_km2: float = 5.0
    """GLW ruminant TLU/km² above which non-cropland is agro_pastoral."""

    livestock_pastoral_tlu_per_km2: float = 20.0
    """GLW ruminant TLU/km² above which non-cropland is pastoral_rangeland."""

    tree_perennial_dominant: float = 0.50
    """Tree-perennial fraction above which the pixel is tree_perennial."""


def classify_pixel(
    cropland_frac: float,
    irrigation_frac: float,
    livestock_tlu_per_km2: float,
    tree_perennial_frac: float,
    thresholds: Thresholds | None = None,
) -> str:
    """Classify a single pixel per the decision tree."""
    t = thresholds or Thresholds()

    if tree_perennial_frac >= t.tree_perennial_dominant:
        return TREE_PERENNIAL

    cropland = cropland_frac >= t.cropland_present
    if cropland and irrigation_frac >= t.irrigation_share:
        return CROPPING_IRRIGATED
    if cropland and livestock_tlu_per_km2 >= t.livestock_mixed_tlu_per_km2:
        return MIXED_CROP_LIVESTOCK
    if cropland:
        return CROPPING_RAINFED

    # not cropland
    if livestock_tlu_per_km2 >= t.livestock_pastoral_tlu_per_km2:
        return PASTORAL_RANGELAND
    if livestock_tlu_per_km2 >= t.livestock_agro_tlu_per_km2:
        return AGRO_PASTORAL
    return OTHER


def classify_arrays(
    cropland_frac: Any,
    irrigation_frac: Any,
    livestock_tlu_per_km2: Any,
    tree_perennial_frac: Any,
    thresholds: Thresholds | None = None,
) -> list[list[str]]:
    """Classify a 2-D grid (lists of lists or numpy arrays).

    Returns a 2-D list of class ids the same shape as the input. Caller may
    convert to a numpy array of dtype=object or a categorical raster.
    """
    rows = len(cropland_frac)
    out: list[list[str]] = []
    for i in range(rows):
        row: list[str] = []
        for j in range(len(cropland_frac[i])):
            row.append(
                classify_pixel(
                    float(cropland_frac[i][j]),
                    float(irrigation_frac[i][j]),
                    float(livestock_tlu_per_km2[i][j]),
                    float(tree_perennial_frac[i][j]),
                    thresholds=thresholds,
                )
            )
        out.append(row)
    return out
