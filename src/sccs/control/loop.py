"""100 Hz control loop running on its own thread.

Each tick:

1. Fetch the current setpoint vector from the active profile.
2. Read the magnetometer (SET/RESET-corrected µT vector).
3. Drive three :class:`~sccs.control.pid.PIDController` instances and
   send the resulting currents to the HCCD.
4. Every 100th tick (1 Hz) read back temperatures.
5. Update the shared state and append a row to the logger if present.

The thread is a normal :class:`threading.Thread` — the main thread
holds the Dash web server. The CPython GIL means there is one Python
bytecode interpreter at a time, but the I/O-heavy nature of this loop
(I²C and ``time.sleep``) leaves plenty of slack for Dash callbacks.
"""

from __future__ import annotations

import threading
import time
from typing import Protocol

import numpy as np

from sccs.control.pid import PIDController
from sccs.control.state import SharedState


class Profile(Protocol):
    """Anything that can produce a target ``B`` vector for a given time."""

    def at(self, t: float) -> np.ndarray: ...

    def metadata(self) -> dict: ...


class ControlLoop(threading.Thread):
    def __init__(
        self,
        hccd,
        magnetometer,
        profile: Profile,
        pids: list[PIDController],
        state: SharedState,
        period_s: float = 0.01,
        max_errors: int = 5,
        logger=None,
    ) -> None:
        super().__init__(daemon=True, name="ControlLoop")
        self._hccd = hccd
        self._mag = magnetometer
        self._profile = profile
        self._pids = pids
        self._state = state
        self._period = period_s
        self._max_errors = max_errors
        self._logger = logger
        self._stop_event = threading.Event()
        self._error_count = 0

    def stop(self) -> None:
        self._stop_event.set()

    def run(self) -> None:
        with self._state.lock:
            self._state.status = "running"

        next_tick = time.perf_counter()
        tick_index = 0
        t_start = time.monotonic()

        while not self._stop_event.is_set():
            try:
                target = self._profile.at(time.monotonic() - t_start)
                measured = self._mag.read_field_uT()
                currents = np.array(
                    [self._pids[i].compute(float(target[i]), float(measured[i])) for i in range(3)]
                )
                self._hccd.set_currents(*currents)
                self._error_count = 0

                temps = None
                if tick_index % 100 == 0:
                    try:
                        temps = self._hccd.read_temperatures()
                    except NotImplementedError:
                        # Firmware-side handler not wired yet; carry on.
                        temps = None

                with self._state.lock:
                    self._state.b_target_uT = np.asarray(target, dtype=float)
                    self._state.b_measured_uT = np.asarray(measured, dtype=float)
                    self._state.currents_A = currents
                    if temps is not None:
                        self._state.temps_C = np.asarray(temps, dtype=float)
                    self._state.timestamp = time.monotonic()

                if self._logger is not None:
                    self._logger.append(self._state)

            except OSError:
                self._error_count += 1
                if self._error_count >= self._max_errors:
                    with self._state.lock:
                        self._state.status = "error"
                    try:
                        self._hccd.set_currents(0.0, 0.0, 0.0)
                    except OSError:
                        pass
                    return

            tick_index += 1
            next_tick += self._period
            sleep_for = next_tick - time.perf_counter()
            if sleep_for > 0:
                time.sleep(sleep_for)
            else:
                # We fell behind; reset the schedule so we don't accumulate slip.
                next_tick = time.perf_counter()

        with self._state.lock:
            if self._state.status == "running":
                self._state.status = "idle"
