"""Tests for ``ellipsoid_fit``."""

from __future__ import annotations

import numpy as np
import pytest

from sccs.calibration.ellipsoid import ellipsoid_fit


def _synthetic_distorted_sphere(
    n: int = 800,
    M_true: np.ndarray | None = None,
    offset_true: np.ndarray | None = None,
    radius: float = 50.0,
    seed: int = 0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate raw readings: ``raw = M_true^{-1} @ true_on_sphere + offset``."""
    rng = np.random.default_rng(seed)
    pts = rng.normal(size=(n, 3))
    pts /= np.linalg.norm(pts, axis=1, keepdims=True)
    pts *= radius

    if M_true is None:
        M_true = np.diag([1.2, 0.9, 1.05])
    if offset_true is None:
        offset_true = np.array([15.0, -5.0, 2.0])

    raw = (np.linalg.inv(M_true) @ pts.T).T + offset_true
    return raw, M_true, offset_true


def test_recovers_sphere_after_calibration():
    raw, _M, _off = _synthetic_distorted_sphere()
    matrix, offset = ellipsoid_fit(raw, target_magnitude=50.0)
    calibrated = (matrix @ (raw - offset).T).T
    radii = np.linalg.norm(calibrated, axis=1)
    assert abs(np.mean(radii) - 50.0) < 0.5
    assert np.std(radii) < 0.5


def test_recovers_offset_close_to_truth():
    raw, _M, offset_true = _synthetic_distorted_sphere()
    _matrix, offset = ellipsoid_fit(raw, target_magnitude=50.0)
    np.testing.assert_allclose(offset, offset_true, atol=0.5)


def test_works_for_general_rotation_and_scale():
    rng = np.random.default_rng(42)
    # Random orthogonal rotation + diagonal scale.
    rot, _ = np.linalg.qr(rng.normal(size=(3, 3)))
    M_true = rot @ np.diag([1.3, 0.8, 1.1]) @ rot.T
    offset_true = np.array([-7.0, 12.0, 4.0])
    raw, _, _ = _synthetic_distorted_sphere(M_true=M_true, offset_true=offset_true)

    matrix, offset = ellipsoid_fit(raw, target_magnitude=50.0)
    calibrated = (matrix @ (raw - offset).T).T
    radii = np.linalg.norm(calibrated, axis=1)
    assert abs(np.mean(radii) - 50.0) < 0.5
    assert np.std(radii) < 0.5


def test_rejects_bad_shape():
    with pytest.raises(ValueError):
        ellipsoid_fit(np.zeros((100, 2)))


def test_rejects_too_few_points():
    with pytest.raises(ValueError):
        ellipsoid_fit(np.zeros((5, 3)))
