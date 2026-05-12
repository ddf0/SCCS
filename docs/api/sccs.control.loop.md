# `sccs.control.loop`

Defined in [`src/sccs/control/loop.py`](../../src/sccs/control/loop.py).

## `Profile` (Protocol)

```python
class Profile(Protocol):
    def at(self, t: float) -> np.ndarray: ...   # target B in µT (shape (3,))
    def metadata(self) -> dict: ...
```

Any object with these two methods is acceptable as the active profile
(`FixedPointProfile`, `OrbitalProfile`, `CSVProfile`, …).

## `class ControlLoop` (subclass of `threading.Thread`)

### Construction

```python
ControlLoop(
    hccd,
    magnetometer,
    profile: Profile,
    pids: list[PIDController],   # length 3
    state: SharedState,
    period_s: float = 0.01,      # 100 Hz default
    max_errors: int = 5,
    logger=None,
)
```

### Behaviour

Per tick:

1. Read the target vector from `profile.at(t)` where `t` is
   monotonic time since `start()`.
2. Read the measured field via `magnetometer.read_field_uT()`.
3. Drive three independent `PIDController.compute(target_i,
   measured_i)` and assemble the result as a current vector.
4. `hccd.set_currents(*currents)`.
5. Every 100th tick (1 Hz) read temperatures via `hccd.read_temperatures()`.
   `NotImplementedError` (stub firmware) is swallowed.
6. Update `SharedState` under its `RLock`.
7. Append a row to the logger if one was supplied.

### Error handling

If `hccd.set_currents` raises `OSError` (typical for an I²C wedge),
an internal counter increments. After `max_errors` consecutive
failures the loop:

- Sets `state.status = "error"`.
- Attempts a final `set_currents(0, 0, 0)` to drive coils to zero.
- Exits the thread.

A single successful tick resets the counter.

### Scheduling

The loop uses absolute `next_tick` timestamps (`time.perf_counter`)
and `time.sleep(next_tick - now)` to compensate for measurement
duration. If the loop falls behind, the schedule is reset rather than
catching up with back-to-back ticks — this avoids burst behaviour on
the I²C bus.

### Stop semantics

`stop()` sets an event; the next loop iteration returns. The caller
should `join()` the thread.
