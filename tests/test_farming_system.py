"""Unit tests for the EO-derived farming_system classifier."""

from nbs_ruralscan.runtime.farming_system import (
    AGRO_PASTORAL,
    CROPPING_IRRIGATED,
    CROPPING_RAINFED,
    MIXED_CROP_LIVESTOCK,
    OTHER,
    PASTORAL_RANGELAND,
    TREE_PERENNIAL,
    Thresholds,
    classify_arrays,
    classify_pixel,
)


def test_tree_perennial_wins_first():
    """Tree-perennial dominant pixel overrides everything else."""
    # high cropland + high livestock would normally → mixed_crop_livestock,
    # but tree-perennial dominance trumps
    out = classify_pixel(
        cropland_frac=0.8,
        irrigation_frac=0.3,
        livestock_tlu_per_km2=30,
        tree_perennial_frac=0.7,
    )
    assert out == TREE_PERENNIAL


def test_cropping_irrigated():
    out = classify_pixel(0.5, 0.4, 1.0, 0.0)
    assert out == CROPPING_IRRIGATED


def test_mixed_crop_livestock():
    out = classify_pixel(0.5, 0.05, 10.0, 0.0)
    assert out == MIXED_CROP_LIVESTOCK


def test_cropping_rainfed_default():
    out = classify_pixel(0.5, 0.05, 1.0, 0.0)
    assert out == CROPPING_RAINFED


def test_pastoral_rangeland():
    out = classify_pixel(0.0, 0.0, 25.0, 0.0)
    assert out == PASTORAL_RANGELAND


def test_agro_pastoral():
    out = classify_pixel(0.0, 0.0, 10.0, 0.0)
    assert out == AGRO_PASTORAL


def test_other_when_nothing_present():
    out = classify_pixel(0.0, 0.0, 0.0, 0.0)
    assert out == OTHER


def test_custom_thresholds_override_defaults():
    """Lowering the irrigation threshold flips rainfed → irrigated."""
    base = classify_pixel(0.5, 0.15, 0.0, 0.0)  # default irrigation_share=0.20
    custom = classify_pixel(
        0.5, 0.15, 0.0, 0.0, thresholds=Thresholds(irrigation_share=0.10)
    )
    assert base == CROPPING_RAINFED
    assert custom == CROPPING_IRRIGATED


def test_classify_arrays_returns_grid_shape():
    grid = [[0.0, 0.5], [0.5, 0.0]]
    irr = [[0.0, 0.0], [0.3, 0.0]]
    lvs = [[0.0, 0.0], [0.0, 25.0]]
    tps = [[0.0, 0.0], [0.0, 0.0]]
    out = classify_arrays(grid, irr, lvs, tps)
    assert out == [
        [OTHER, CROPPING_RAINFED],
        [CROPPING_IRRIGATED, PASTORAL_RANGELAND],
    ]
