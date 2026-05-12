"""PID controller tests."""

from __future__ import annotations

import pytest

from sccs.control.pid import PIDController


def test_proportional_only_step_response():
    pid = PIDController(kp=1.0, ki=0.0, kd=0.0, dt=0.01)
    assert pid.compute(setpoint=0.5, measured=0.0) == pytest.approx(0.5)


def test_integral_accumulates_linearly():
    pid = PIDController(kp=0.0, ki=1.0, kd=0.0, dt=0.1)
    pid.compute(1.0, 0.0)  # integral -> 0.1
    pid.compute(1.0, 0.0)  # integral -> 0.2
    third = pid.compute(1.0, 0.0)  # integral -> 0.3
    assert third == pytest.approx(0.3)


def test_derivative_on_measurement_suppresses_setpoint_kick():
    pid = PIDController(kp=0.0, ki=0.0, kd=1.0, dt=0.1)
    pid.compute(0.0, 0.0)  # seed measured_prev
    # Setpoint jumps but measurement does not — no derivative response.
    assert pid.compute(setpoint=100.0, measured=0.0) == pytest.approx(0.0)


def test_derivative_reacts_to_measurement_change():
    pid = PIDController(kp=0.0, ki=0.0, kd=1.0, dt=0.1)
    pid.compute(0.0, 0.0)
    # Measurement rises by 1 over dt=0.1 -> d_meas/dt = 10, derivative_term
    # = -kd * d_meas/dt = -10.
    assert pid.compute(0.0, 1.0) == pytest.approx(-1.0)  # clipped to -1.0


def test_output_clipped_to_limits():
    pid = PIDController(kp=10.0, ki=0.0, kd=0.0, dt=0.01, output_limits=(-1.0, 1.0))
    assert pid.compute(10.0, 0.0) == 1.0


def test_anti_windup_does_not_accumulate_in_saturation():
    pid = PIDController(kp=1.0, ki=10.0, kd=0.0, dt=0.1, output_limits=(-0.5, 0.5))
    for _ in range(50):
        pid.compute(1.0, 0.0)  # persistently saturated
    # Sign-flip: output must respond immediately, not wait for the
    # integrator to unwind.
    out = pid.compute(0.0, 1.0)
    assert out < 0  # corrective
    assert -0.5 <= out <= 0.5


def test_reset_clears_state():
    pid = PIDController(kp=0.0, ki=1.0, kd=0.0, dt=0.1)
    pid.compute(1.0, 0.0)
    pid.compute(1.0, 0.0)
    pid.reset()
    assert pid.compute(1.0, 0.0) == pytest.approx(0.1)


def test_zero_error_zero_output():
    pid = PIDController(kp=1.0, ki=1.0, kd=1.0, dt=0.01)
    pid.compute(0.0, 0.0)
    pid.compute(0.0, 0.0)
    assert pid.compute(0.0, 0.0) == 0.0
