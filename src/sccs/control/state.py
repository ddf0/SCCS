"""Thread-safe state object shared between the control loop and the web UI.

Access **must** be guarded by ``with state.lock: ...`` blocks. The
control thread is the sole writer of every field; web callbacks treat
the state as read-only and submit user commands via a separate
``queue.Queue``.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Literal

import numpy as np

Status = Literal["idle", "running", "estop", "error"]


@dataclass
class SharedState:
    b_target_uT: np.ndarray = field(default_factory=lambda: np.zeros(3))
    b_measured_uT: np.ndarray = field(default_factory=lambda: np.zeros(3))
    currents_A: np.ndarray = field(default_factory=lambda: np.zeros(3))
    temps_C: np.ndarray = field(default_factory=lambda: np.zeros(3))
    pid_gains: tuple[float, float, float] = (0.05, 0.02, 0.001)
    status: Status = "idle"
    timestamp: float = field(default_factory=time.monotonic)
    lock: threading.RLock = field(default_factory=threading.RLock)
