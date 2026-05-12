# `sccs.control.pid`

Defined in [`src/sccs/control/pid.py`](../../src/sccs/control/pid.py).

Single-axis discrete PID controller. The vector controller in
`ControlLoop` instantiates three of these — one per magnetic axis.

## `class PIDController`

### Construction

```python
PIDController(
    kp: float,
    ki: float,
    kd: float,
    dt: float,
    output_limits: tuple[float, float] = (-1.0, 1.0),
)
```

### `compute(setpoint, measured) -> float`

Runs one step. The output is clipped to `output_limits`.

The integrator follows **positional form** (it stores the accumulated
integral of the error). The derivative term acts on the **measurement
itself**, not on the error — this suppresses the derivative kick that
would otherwise spike the output when the setpoint changes abruptly.

**Anti-windup** is conditional integration:

- If the unbounded output sits inside the limits, commit the
  tentative integral.
- If the output saturated high (`unbounded > hi`), commit only when
  the error is negative — that is, the integrator is about to walk
  back toward the centre.
- Symmetrically, if saturated low (`unbounded < lo`), commit only on
  positive error.

The integrator never accumulates further during persistent
saturation, so the system reacts immediately when the disturbance
clears.

### `reset()`

Clears the integrator and the derivative history. Call this on
emergency stop and on profile changes.
