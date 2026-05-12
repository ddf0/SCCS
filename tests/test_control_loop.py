"""Integration smoke tests for ControlLoop with mocked drivers."""

from __future__ import annotations

import time
from unittest.mock import MagicMock

import numpy as np

from sccs.control.loop import ControlLoop
from sccs.control.pid import PIDController
from sccs.control.state import SharedState


class _ConstProfile:
    def at(self, t: float) -> np.ndarray:
        return np.array([50.0, 0.0, 0.0])

    def metadata(self) -> dict:
        return {"type": "const"}


def _make_loop(period_ms: int = 10) -> tuple[ControlLoop, MagicMock, MagicMock, SharedState]:
    hccd = MagicMock()
    hccd.read_temperatures.side_effect = NotImplementedError
    mag = MagicMock()
    mag.read_field_uT.return_value = np.zeros(3)
    state = SharedState()
    pids = [
        PIDController(
            kp=0.01,
            ki=0.0,
            kd=0.0,
            dt=period_ms / 1000.0,
            output_limits=(-3.0, 3.0),
        )
        for _ in range(3)
    ]
    loop = ControlLoop(
        hccd=hccd,
        magnetometer=mag,
        profile=_ConstProfile(),
        pids=pids,
        state=state,
        period_s=period_ms / 1000.0,
    )
    return loop, hccd, mag, state


def test_loop_runs_many_iterations():
    loop, hccd, mag, _ = _make_loop(period_ms=10)
    loop.start()
    time.sleep(0.2)
    loop.stop()
    loop.join(timeout=1.0)
    # ~20 cycles at 100 Hz; tolerate jitter.
    assert mag.read_field_uT.call_count >= 15
    assert hccd.set_currents.call_count >= 15


def test_loop_populates_shared_state():
    loop, _, _, state = _make_loop()
    loop.start()
    time.sleep(0.1)
    loop.stop()
    loop.join(timeout=1.0)
    with state.lock:
        np.testing.assert_array_equal(state.b_target_uT, [50.0, 0.0, 0.0])
        assert state.timestamp > 0
        assert state.status == "idle"


def test_loop_transitions_to_error_on_repeated_failures():
    hccd = MagicMock()
    hccd.set_currents.side_effect = OSError("bus")
    mag = MagicMock()
    mag.read_field_uT.return_value = np.zeros(3)
    state = SharedState()
    pids = [PIDController(kp=0.0, ki=0.0, kd=0.0, dt=0.01, output_limits=(-1, 1)) for _ in range(3)]
    loop = ControlLoop(
        hccd=hccd,
        magnetometer=mag,
        profile=_ConstProfile(),
        pids=pids,
        state=state,
        period_s=0.01,
        max_errors=3,
    )
    loop.start()
    loop.join(timeout=1.0)
    with state.lock:
        assert state.status == "error"
