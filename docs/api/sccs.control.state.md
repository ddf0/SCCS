# `sccs.control.state`

Defined in [`src/sccs/control/state.py`](../../src/sccs/control/state.py).

## `class SharedState`

Lock-protected snapshot of the system. The control thread is the sole
writer of every field; the Dash web UI treats it as read-only and
submits user commands separately through a `queue.Queue`.

### Fields

| Field | Type | Meaning |
| --- | --- | --- |
| `b_target_uT` | `np.ndarray (3,)` | Current magnetic-field target. |
| `b_measured_uT` | `np.ndarray (3,)` | Latest measurement from the magnetometer. |
| `currents_A` | `np.ndarray (3,)` | Currents the loop last commanded. |
| `temps_C` | `np.ndarray (3,)` | Last temperatures read from the HCCD. |
| `pid_gains` | `tuple[float, float, float]` | Active `kp, ki, kd`. |
| `status` | `Literal["idle", "running", "estop", "error"]` | Loop state. |
| `timestamp` | `float` | `time.monotonic()` of the last update. |
| `lock` | `threading.RLock` | Use `with state.lock: ...` for every access. |

### Locking discipline

The lock is **reentrant** (`RLock`) so callers may nest acquisitions
safely. All writers must take the lock; readers must take it before
copying out fields. Never expose `np.ndarray` objects to callers
without copying them first — they are mutable and shared.

### Status transitions

```
idle ──start──> running ──stop──> idle
                  │
                  ├── overtemp / estop ──> estop
                  └── repeated I/O fail ──> error
```

`estop` and `error` are sticky and require an explicit reset command.
