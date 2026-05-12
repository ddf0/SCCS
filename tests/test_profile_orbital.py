"""Tests for OrbitalProfile.

Uses a well-known historical ISS TLE (epoch 2014-01-20) with valid
checksums. The reference time ``t0`` is pinned near the TLE epoch so
SGP4 predictions remain meaningful (propagation accuracy degrades
quickly past ~30 days from epoch).
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pytest

from sccs.profile.orbital import OrbitalProfile

ISS_TLE = (
    "ISS (ZARYA)",
    "1 25544U 98067A   14020.93268519  .00009878  00000-0  18200-3 0  5082",
    "2 25544  51.6498 109.4756 0003572 055.9686 274.8005 15.49815350868473",
)

# Pin reference time near the TLE epoch so SGP4 is in its sweet spot.
T0_NEAR_EPOCH = datetime(2014, 1, 21, 0, 0, 0, tzinfo=timezone.utc)


def test_groundtrack_returns_n_points():
    prof = OrbitalProfile(tle=ISS_TLE, t0=T0_NEAR_EPOCH)
    track = prof.groundtrack(t_start=0.0, t_end=600.0, n=10)
    assert len(track) == 10
    for lat, lon, alt in track:
        assert -90.0 <= lat <= 90.0
        assert -180.0 <= lon <= 180.0
        assert 200.0 < alt < 1500.0  # km, LEO sanity range


def test_at_returns_finite_vector_in_uT_range():
    prof = OrbitalProfile(tle=ISS_TLE, t0=T0_NEAR_EPOCH)
    v = prof.at(0.0)
    assert v.shape == (3,)
    assert np.all(np.isfinite(v))
    magnitude = float(np.linalg.norm(v))
    assert 10.0 < magnitude < 100.0  # µT, typical LEO


def test_time_scale_advances_subpoint():
    prof_fast = OrbitalProfile(tle=ISS_TLE, time_scale=600.0, t0=T0_NEAR_EPOCH)
    prof_real = OrbitalProfile(tle=ISS_TLE, time_scale=1.0, t0=T0_NEAR_EPOCH)
    lat_fast, _, _ = prof_fast.groundtrack(0.0, 10.0, 2)[1]
    lat_real, _, _ = prof_real.groundtrack(0.0, 10.0, 2)[1]
    assert abs(lat_fast - lat_real) > 0.5


def test_groundtrack_rejects_invalid_range():
    prof = OrbitalProfile(tle=ISS_TLE, t0=T0_NEAR_EPOCH)
    with pytest.raises(ValueError):
        prof.groundtrack(t_start=10.0, t_end=10.0, n=5)
    with pytest.raises(ValueError):
        prof.groundtrack(t_start=0.0, t_end=10.0, n=1)


def test_metadata_includes_satellite_name():
    prof = OrbitalProfile(tle=ISS_TLE, time_scale=2.5, t0=T0_NEAR_EPOCH)
    md = prof.metadata()
    assert md["type"] == "orbital"
    assert "ISS" in md["name"]
    assert md["time_scale"] == 2.5
