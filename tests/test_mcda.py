"""Tests for the MCDA math core (port of spatMCDA.R)."""

import numpy as np
import pytest

from nbs_ruralscan.runtime.mcda import (
    ahp_consistency_ratio,
    ahp_matrix_from_weights,
    ahp_weights,
    critic_weights,
    entropy_weights,
    quartile_classify,
    reconcile_weights,
    sensitivity_perturb,
    weighted_overlay,
)


def test_critic_weights_sum_to_one():
    rng = np.random.default_rng(0)
    m = rng.random((200, 4))
    w = critic_weights(m)
    assert np.isclose(w.sum(), 1.0)
    assert w.shape == (4,)
    assert (w > 0).all()


def test_critic_weights_higher_for_higher_variance():
    """Criterion with higher variance + low correlation gets more weight."""
    rng = np.random.default_rng(1)
    n = 500
    high_var = rng.normal(0.5, 0.3, n)
    low_var = rng.normal(0.5, 0.05, n)
    m = np.column_stack([high_var, low_var])
    w = critic_weights(m)
    assert w[0] > w[1]


def test_entropy_weights_sum_to_one():
    rng = np.random.default_rng(2)
    m = rng.random((300, 5)) + 0.01  # strictly positive
    w = entropy_weights(m)
    assert np.isclose(w.sum(), 1.0)
    assert (w > 0).all()


def test_ahp_weights_from_consistent_matrix():
    """A perfectly consistent matrix recovers the input weights."""
    target = np.array([0.5, 0.25, 0.15, 0.10])
    A = ahp_matrix_from_weights(target)
    recovered = ahp_weights(A)
    assert np.allclose(recovered, target, atol=1e-6)
    assert ahp_consistency_ratio(A) < 1e-6


def test_ahp_consistency_ratio_inconsistent():
    """Random matrix should fail CR < 0.10 most of the time."""
    A = np.array(
        [
            [1, 9, 1 / 5],
            [1 / 9, 1, 7],
            [5, 1 / 7, 1],
        ]
    )
    assert ahp_consistency_ratio(A) > 0.10


def test_reconcile_alpha_zero_uses_objective_only():
    ahp = np.array([0.5, 0.5])
    critic = np.array([0.7, 0.3])
    w = reconcile_weights(ahp=ahp, critic=critic, alpha=0.0)
    assert np.allclose(w, [0.7, 0.3])


def test_reconcile_alpha_one_uses_subjective_only():
    ahp = np.array([0.4, 0.6])
    critic = np.array([0.1, 0.9])
    w = reconcile_weights(ahp=ahp, critic=critic, alpha=1.0)
    assert np.allclose(w, ahp)


def test_reconcile_default_alpha_blends():
    ahp = np.array([0.5, 0.5])
    critic = np.array([0.7, 0.3])
    entropy = np.array([0.6, 0.4])
    w = reconcile_weights(ahp=ahp, critic=critic, entropy=entropy, alpha=0.4)
    obj = np.mean([critic, entropy], axis=0)
    expected = 0.4 * ahp + 0.6 * obj
    expected = expected / expected.sum()
    assert np.allclose(w, expected)


def test_reconcile_rejects_unnormalised_input():
    with pytest.raises(ValueError):
        reconcile_weights(ahp=np.array([0.1, 0.2]), alpha=0.5)


def test_weighted_overlay_shape():
    stack = np.random.rand(10, 12, 3)
    w = np.array([0.5, 0.3, 0.2])
    out = weighted_overlay(stack, w)
    assert out.shape == (10, 12)


def test_weighted_overlay_constant_stack():
    stack = np.ones((4, 5, 3))
    w = np.array([0.5, 0.3, 0.2])
    out = weighted_overlay(stack, w)
    assert np.allclose(out, 1.0)


def test_weighted_overlay_rejects_dim_mismatch():
    with pytest.raises(ValueError):
        weighted_overlay(np.ones((2, 2, 3)), np.array([0.5, 0.5]))


def test_sensitivity_perturb_variance_nonneg():
    rng = np.random.default_rng(42)
    stack = rng.random((6, 6, 3))
    w = np.array([0.4, 0.4, 0.2])
    res = sensitivity_perturb(stack, w, n=20, scale=0.1, seed=42)
    assert res.mean.shape == (6, 6)
    assert (res.variance >= 0).all()
    assert (res.weights_max >= res.weights_min).all()


def test_quartile_classify_classes_are_1_to_4():
    rng = np.random.default_rng(7)
    s = rng.random((20, 20))
    classes, legend = quartile_classify(s)
    assert classes.shape == s.shape
    unique = set(classes.flatten().tolist())
    assert unique <= {0, 1, 2, 3, 4}
    # Roughly quartile-balanced
    assert abs((classes == 1).sum() - 100) < 30
    assert legend == {
        1: "Unsuitable",
        2: "Marginal",
        3: "Moderate",
        4: "Highly Suitable",
    }


def test_quartile_classify_handles_nan():
    s = np.array([[0.1, np.nan, 0.5], [0.3, 0.7, 0.9]])
    classes, _ = quartile_classify(s)
    # NaN → class 0
    assert classes[0, 1] == 0
