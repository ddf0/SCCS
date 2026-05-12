"""Orbital IGRF profile — TLE → subpoint → IGRF in NED.

Uses :mod:`skyfield` to propagate a Two-Line-Element set through SGP4
and convert geocentric positions to (lat, lon, altitude). The IGRF
field at each subpoint is then computed with :mod:`ppigrf` and remapped
into the bench-frame NED convention used elsewhere in SCCS.

The ``groundtrack`` method exists primarily to feed the Plotly Dash
map widget in :mod:`sccs.web`.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import ppigrf
from skyfield.api import EarthSatellite, load, wgs84


class OrbitalProfile:
    """Propagate a satellite TLE and return the IGRF field at its subpoint.

    Parameters
    ----------
    tle
        ``(name, line1, line2)`` — the TLE checksum must be valid; the
        skyfield/sgp4 parser rejects bad ones.
    time_scale
        Wall-clock to simulation-time multiplier. ``1.0`` means real
        time; e.g. ``60.0`` runs an orbit in one minute of wall time.
    t0
        Reference UTC time at simulation ``t = 0``. Defaults to "now".
    """

    def __init__(
        self,
        tle: tuple[str, str, str],
        time_scale: float = 1.0,
        t0: datetime | None = None,
    ) -> None:
        name, line1, line2 = tle
        self._ts = load.timescale()
        self._sat = EarthSatellite(line1, line2, name, self._ts)
        self._scale = float(time_scale)
        self._t0 = t0 if t0 is not None else datetime.now(tz=timezone.utc)
        # ppigrf compares against a tz-naive DatetimeIndex; strip the tz to
        # avoid pandas raising on naive-vs-aware comparisons.
        self._date = pd.Timestamp(self._t0.year, self._t0.month, self._t0.day)

    # ---------------------------------------------------------------- #

    def _subpoint(self, t_sim: float) -> tuple[float, float, float]:
        when = self._t0 + timedelta(seconds=t_sim * self._scale)
        epoch = self._ts.from_datetime(when)
        geocentric = self._sat.at(epoch)
        sub = wgs84.geographic_position_of(geocentric)
        return (
            float(sub.latitude.degrees),
            float(sub.longitude.degrees),
            float(sub.elevation.km),
        )

    def at(self, t: float) -> np.ndarray:
        lat, lon, alt = self._subpoint(t)
        Be, Bn, Bu = ppigrf.igrf(lon, lat, alt, self._date)
        bn = float(np.asarray(Bn).flatten()[0])
        be = float(np.asarray(Be).flatten()[0])
        bu = float(np.asarray(Bu).flatten()[0])
        return np.array([bn, be, -bu]) / 1000.0

    def groundtrack(
        self, t_start: float, t_end: float, n: int = 300
    ) -> list[tuple[float, float, float]]:
        """Return ``n`` evenly spaced (lat, lon, alt_km) tuples."""
        if n < 2:
            raise ValueError("n must be >= 2")
        if t_end <= t_start:
            raise ValueError("t_end must be greater than t_start")
        ts = np.linspace(t_start, t_end, n)
        return [self._subpoint(float(t)) for t in ts]

    def metadata(self) -> dict:
        return {
            "type": "orbital",
            "name": self._sat.name,
            "epoch": self._sat.epoch.utc_iso(),
            "time_scale": self._scale,
        }
