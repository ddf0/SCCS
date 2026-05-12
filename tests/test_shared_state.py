"""Tests for the thread-safe SharedState."""

from __future__ import annotations

import threading

import numpy as np

from sccs.control.state import SharedState


def test_default_state_is_zeros_and_idle():
    s = SharedState()
    np.testing.assert_array_equal(s.b_target_uT, np.zeros(3))
    np.testing.assert_array_equal(s.b_measured_uT, np.zeros(3))
    assert s.status == "idle"


def test_rlock_can_be_reentered():
    s = SharedState()
    with s.lock:
        with s.lock:  # would deadlock with a plain Lock
            s.b_target_uT = np.array([1.0, 2.0, 3.0])
    with s.lock:
        np.testing.assert_array_equal(s.b_target_uT, [1.0, 2.0, 3.0])


def test_concurrent_writes_are_atomic_per_field():
    s = SharedState()
    iterations = 500

    def writer(value: float) -> None:
        for _ in range(iterations):
            with s.lock:
                s.b_target_uT = np.full(3, value)

    threads = [
        threading.Thread(target=writer, args=(1.0,)),
        threading.Thread(target=writer, args=(2.0,)),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    with s.lock:
        # Final array is uniformly 1.0 or 2.0 — never a mixed half-write.
        assert s.b_target_uT[0] == s.b_target_uT[1] == s.b_target_uT[2]
