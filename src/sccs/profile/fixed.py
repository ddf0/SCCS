"""Static-position IGRF profile.

Computes the IGRF-13 geomagnetic vector at a single geographic point
and returns it for every time. Useful as the default profile and for
acceptance tests.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import ppigrf


class FixedPointProfile:
    """Returns a constant magnetic-field vector for a single (lat, lon, alt, date).

    ``ppigrf.igrf`` returns East, North, Up components in nT. We convert
    to µT and remap to a North-East-Down (NED) frame, which is the
    convention used by the rest of the SCCS stack:

        ``B = [Bx, By, Bz] = [Bn, Be, -Bu]``.
    """

    def __init__(
        self,
        latitude_deg: float,
        longitude_deg: float,
        altitude_km: float,
        date_str: str,
    ) -> None:
        self._lat = latitude_deg
        self._lon = longitude_deg
        self._alt = altitude_km
        self._date = pd.Timestamp(date_str)

        Be, Bn, Bu = ppigrf.igrf(longitude_deg, latitude_deg, altitude_km, self._date)
        # ppigrf returns ndarrays even for scalar inputs — flatten to scalar.
        bn = float(np.asarray(Bn).flatten()[0])
        be = float(np.asarray(Be).flatten()[0])
        bu = float(np.asarray(Bu).flatten()[0])
        b_ned_nT = np.array([bn, be, -bu])
        self._b_uT = b_ned_nT / 1000.0

    def at(self, t: float) -> np.ndarray:
        return self._b_uT.copy()

    def metadata(self) -> dict:
        return {
            "type": "fixed",
            "lat": self._lat,
            "lon": self._lon,
            "alt_km": self._alt,
            "date": self._date.date().isoformat(),
        }
