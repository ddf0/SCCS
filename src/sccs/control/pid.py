"""Discrete PID controller with derivative-on-measurement and anti-windup.

Positional form. The derivative term acts on the measurement rather
than the error, which suppresses derivative kick when the setpoint
jumps. Anti-windup is implemented as conditional integration: the
integrator only accumulates if doing so will not push the output
further into saturation.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PIDController:
    """Single-axis PID — three instances make up the vector controller."""

    kp: float
    ki: float
    kd: float
    dt: float
    output_limits: tuple[float, float] = (-1.0, 1.0)

    _integral: float = field(default=0.0, init=False, repr=False)
    _measured_prev: float | None = field(default=None, init=False, repr=False)

    def reset(self) -> None:
        """Clear integrator and derivative history."""
        self._integral = 0.0
        self._measured_prev = None

    def compute(self, setpoint: float, measured: float) -> float:
        """Run one step. Returns the clipped output."""
        error = setpoint - measured

        if self._measured_prev is None:
            derivative = 0.0
        else:
            derivative = -(measured - self._measured_prev) / self.dt

        tentative_integral = self._integral + error * self.dt
        unbounded = self.kp * error + self.ki * tentative_integral + self.kd * derivative

        lo, hi = self.output_limits
        output = max(lo, min(hi, unbounded))

        # Conditional integration: only commit the new integral if it does
        # not push the output further into saturation.
        not_saturated = unbounded == output
        winding_down_from_high = unbounded > hi and error < 0
        winding_up_from_low = unbounded < lo and error > 0
        if not_saturated or winding_down_from_high or winding_up_from_low:
            self._integral = tentative_integral

        self._measured_prev = measured
        return output
