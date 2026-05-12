# `sccs.logging_csv`

Defined in [`src/sccs/logging_csv.py`](../../src/sccs/logging_csv.py).

## `class CSVLogger`

Append-only CSV writer for control-loop telemetry. The file is named
`sccs_YYYYMMDD_HHMMSS.csv` so multiple runs do not overwrite each
other.

### Constructor

```python
CSVLogger(out_dir: str | Path, decimation: int = 5)
```

- `out_dir` is created if it does not exist.
- `decimation` = 1 writes every tick. `decimation` = 5 (default) keeps
  20 Hz output at a 100 Hz control loop.

Raises `ValueError` for `decimation < 1`.

### Methods

| Signature | Behaviour |
| --- | --- |
| `append(state: SharedState)` | Acquires `state.lock`, copies the row, writes if the tick counter is a multiple of `decimation`. |
| `close()` | Closes the file. Idempotent and exception-safe. |
| `path` (property) | Absolute path of the open log file. |

### Schema

| Column | Unit | Source |
| --- | --- | --- |
| `timestamp` | `time.monotonic` seconds | `state.timestamp` |
| `bx_set, by_set, bz_set` | µT | `state.b_target_uT` |
| `bx_meas, by_meas, bz_meas` | µT | `state.b_measured_uT` |
| `ix, iy, iz` | A | `state.currents_A` |
| `tx, ty, tz` | °C | `state.temps_C` |
| `status` | enum | `state.status` |
