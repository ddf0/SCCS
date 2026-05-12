# `sccs.calibration.ellipsoid`

Defined in [`src/sccs/calibration/ellipsoid.py`](../../src/sccs/calibration/ellipsoid.py).

## `ellipsoid_fit(points, target_magnitude=1.0) -> (matrix, offset)`

Algebraic least-squares ellipsoid fit (Li & Griffiths, 2004).

### Inputs

| Parameter | Type | Notes |
| --- | --- | --- |
| `points` | `np.ndarray (N, 3)` | Raw magnetometer readings sampled while the sensor was rotated through many orientations in a homogeneous field. ``N ≥ 10`` is required; ``N ≥ 500`` is the practical minimum for stable fits. |
| `target_magnitude` | `float` | Desired sphere radius after calibration — usually the magnitude of the local geomagnetic field in µT. |

### Returns

- `matrix` — `np.ndarray (3, 3)`
- `offset` — `np.ndarray (3,)`

such that `matrix @ (raw - offset)` lies on a sphere of radius
`target_magnitude`.

### Algorithm sketch

1. Set up the algebraic form
   `a x² + b y² + c z² + 2d xy + 2e xz + 2f yz + 2g x + 2h y + 2i z = 1`
   over `N` rows of design matrix `D` and solve `D · v = 1` by
   ordinary least squares.
2. Recover the quadric matrix `A` (3×3) and the linear term
   `[g, h, i]`. The centre satisfies `A · centre = -[g, h, i]`.
3. Translate the quadric to the centre, normalise by the constant
   term, eigendecompose. Eigenvalues give `1 / r²` of the principal
   semi-axes; eigenvectors give the orientation.
4. The calibration matrix is `target_magnitude · V · diag(1/r) · Vᵀ`,
   which simultaneously rotates the ellipsoid into axis alignment and
   scales each axis to the requested radius.

### Failure modes

- Raises `ValueError` for the wrong shape or fewer than 10 points.
- Raises `ValueError` if the fitted surface is not an ellipsoid
  (negative eigenvalues or non-positive constant). This typically
  indicates pathologically distributed samples (e.g. all points on a
  great circle).

### Usage

```python
from sccs.calibration.ellipsoid import ellipsoid_fit

raw_samples = collect_raw_readings()        # (N, 3), N ~ 800
M, offset = ellipsoid_fit(raw_samples, target_magnitude=50.0)

# Persist for the runtime driver:
mag.load_calibration(M, offset)
```
