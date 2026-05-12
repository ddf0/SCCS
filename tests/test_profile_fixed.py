"""Tests for FixedPointProfile."""

from __future__ import annotations

import numpy as np

from sccs.profile.fixed import FixedPointProfile


def test_returns_constant_vector():
    prof = FixedPointProfile(
        latitude_deg=55.75, longitude_deg=37.62, altitude_km=400.0, date_str="2026-05-12"
    )
    v1 = prof.at(0.0)
    v2 = prof.at(123.456)
    np.testing.assert_array_equal(v1, v2)


def test_magnitude_in_expected_earth_range():
    prof = FixedPointProfile(
        latitude_deg=0.0, longitude_deg=0.0, altitude_km=400.0, date_str="2026-05-12"
    )
    magnitude = float(np.linalg.norm(prof.at(0.0)))
    assert 20.0 < magnitude < 70.0  # µT — typical LEO range


def test_metadata_contains_inputs():
    prof = FixedPointProfile(
        latitude_deg=10.0, longitude_deg=20.0, altitude_km=500.0, date_str="2026-05-12"
    )
    md = prof.metadata()
    assert md["type"] == "fixed"
    assert md["lat"] == 10.0
    assert md["lon"] == 20.0
    assert md["alt_km"] == 500.0
    assert md["date"] == "2026-05-12"


def test_returns_shape_three():
    prof = FixedPointProfile(
        latitude_deg=0.0, longitude_deg=0.0, altitude_km=400.0, date_str="2026-05-12"
    )
    assert prof.at(0.0).shape == (3,)
