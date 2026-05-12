"""Ellipsoid fitting for magnetometer calibration.

Implements the algebraic least-squares method of Li & Griffiths (2004).
Given a cloud of "raw" magnetometer readings collected while rotating
the sensor through many orientations in a homogeneous field, the
algorithm recovers an affine transform

    B_calibrated = M @ (B_raw - offset)

such that the calibrated points lie on a sphere of radius
``target_magnitude``.
"""

from __future__ import annotations

import numpy as np


def ellipsoid_fit(
    points: np.ndarray, target_magnitude: float = 1.0
) -> tuple[np.ndarray, np.ndarray]:
    """Recover ``M`` (3×3) and ``offset`` (3,) from raw points.

    Parameters
    ----------
    points
        Array of shape ``(N, 3)`` with N ≥ 10. Larger N gives better
        conditioning.
    target_magnitude
        Desired sphere radius after calibration (typically the
        magnitude of the local geomagnetic field in µT).

    Returns
    -------
    (matrix, offset)
        Such that ``matrix @ (raw - offset)`` lies on a sphere of
        radius ``target_magnitude``.
    """
    points = np.asarray(points, dtype=float)
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError("points must be (N, 3)")
    n = points.shape[0]
    if n < 10:
        raise ValueError(f"need at least 10 points, got {n}")

    x, y, z = points[:, 0], points[:, 1], points[:, 2]

    # Algebraic form
    #   a x² + b y² + c z² + 2d xy + 2e xz + 2f yz + 2g x + 2h y + 2i z = 1.
    D = np.column_stack(
        [
            x * x,
            y * y,
            z * z,
            2 * x * y,
            2 * x * z,
            2 * y * z,
            2 * x,
            2 * y,
            2 * z,
        ]
    )
    ones = np.ones(n)
    coeffs, *_ = np.linalg.lstsq(D, ones, rcond=None)
    a, b, c, d, e, f, g, h, i = coeffs

    # Quadratic form matrix and linear term.
    A = np.array(
        [
            [a, d, e],
            [d, b, f],
            [e, f, c],
        ]
    )
    lin = np.array([g, h, i])

    # Ellipsoid centre: A * centre = -lin.
    centre = -np.linalg.solve(A, lin)

    # Substitute back to find the constant of the centred quadric:
    #   (x - centre)^T A (x - centre) = 1 + centre^T A centre.
    const = 1.0 + centre @ A @ centre
    if const <= 0:
        raise ValueError("fitted surface is not an ellipsoid (non-positive constant)")

    # Normalise so that the surface equation reads x'^T A_n x' = 1.
    A_n = A / const

    # Eigendecomposition gives principal axes and semi-axis lengths.
    eigvals, eigvecs = np.linalg.eigh(A_n)
    if np.any(eigvals <= 0):
        raise ValueError("fitted surface is not an ellipsoid (non-positive eigenvalues)")

    radii = 1.0 / np.sqrt(eigvals)
    # Transformation that maps the ellipsoid to a unit sphere, then
    # scales to the requested magnitude.
    matrix = target_magnitude * (eigvecs @ np.diag(1.0 / radii) @ eigvecs.T)
    return matrix, centre
