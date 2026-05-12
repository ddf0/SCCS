"""CSV telemetry logger.

The control thread calls :meth:`CSVLogger.append` once per tick (or
less frequently via the decimation parameter). The file is timestamped
at construction so multiple runs do not overwrite each other.
"""

from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sccs.control.state import SharedState


class CSVLogger:
    HEADER: tuple[str, ...] = (
        "timestamp",
        "bx_set",
        "by_set",
        "bz_set",
        "bx_meas",
        "by_meas",
        "bz_meas",
        "ix",
        "iy",
        "iz",
        "tx",
        "ty",
        "tz",
        "status",
    )

    def __init__(self, out_dir: str | Path, decimation: int = 5) -> None:
        if decimation < 1:
            raise ValueError("decimation must be >= 1")
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%d_%H%M%S")
        self._path = out_dir / f"sccs_{stamp}.csv"
        self._fh = self._path.open("w", newline="")
        self._writer = csv.writer(self._fh)
        self._writer.writerow(self.HEADER)
        self._decim = decimation
        self._tick = 0

    @property
    def path(self) -> Path:
        return self._path

    def append(self, state: "SharedState") -> None:
        """Write one row if the current tick is a multiple of `decimation`."""
        if self._tick % self._decim != 0:
            self._tick += 1
            return
        with state.lock:
            row = [
                state.timestamp,
                *state.b_target_uT.tolist(),
                *state.b_measured_uT.tolist(),
                *state.currents_A.tolist(),
                *state.temps_C.tolist(),
                state.status,
            ]
        self._writer.writerow(row)
        self._fh.flush()
        self._tick += 1

    def close(self) -> None:
        try:
            self._fh.close()
        except Exception:
            # Closing twice or in a bad state is non-fatal — the file is
            # already flushed on every append().
            pass
