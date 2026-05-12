"""CSV-replay profile.

Loads a pre-computed ``t, bx, by, bz`` table and linearly interpolates
between the rows. Useful for offline simulator integration: any tool
that can emit a CSV (Matlab, GMAT, custom skyfield script) becomes an
SCCS profile.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np


class CSVProfile:
    def __init__(self, path: str | Path) -> None:
        path = Path(path)
        times: list[float] = []
        values: list[list[float]] = []
        with path.open() as fh:
            reader = csv.DictReader(fh)
            required = {"t", "bx", "by", "bz"}
            if reader.fieldnames is None or not required.issubset(reader.fieldnames):
                raise ValueError(
                    f"CSV must have columns {sorted(required)}; got {reader.fieldnames}"
                )
            for row in reader:
                times.append(float(row["t"]))
                values.append([float(row["bx"]), float(row["by"]), float(row["bz"])])
        if len(times) < 2:
            raise ValueError("CSV must contain at least two rows")
        order = np.argsort(times)
        self._t = np.asarray(times)[order]
        self._b = np.asarray(values)[order]
        self._path = path

    def at(self, t: float) -> np.ndarray:
        # Clamp at the table edges to avoid extrapolating into nonsense.
        if t <= self._t[0]:
            return self._b[0].copy()
        if t >= self._t[-1]:
            return self._b[-1].copy()
        idx = int(np.searchsorted(self._t, t))
        t0, t1 = self._t[idx - 1], self._t[idx]
        frac = (t - t0) / (t1 - t0)
        return (1.0 - frac) * self._b[idx - 1] + frac * self._b[idx]

    def metadata(self) -> dict:
        return {
            "type": "csv",
            "path": str(self._path),
            "duration_s": float(self._t[-1] - self._t[0]),
            "samples": int(len(self._t)),
        }
