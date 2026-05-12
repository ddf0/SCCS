# `sccs.profile.csv_replay`

Defined in [`src/sccs/profile/csv_replay.py`](../../src/sccs/profile/csv_replay.py).

## `class CSVProfile`

Replays a pre-computed `t, bx, by, bz` table. Linearly interpolates
between rows; outside the table the values are clamped to the first
or last row.

### CSV format

Required columns (exact names):

| Column | Unit | Notes |
| --- | --- | --- |
| `t` | seconds | Monotonic; unsorted rows are reordered automatically. |
| `bx`, `by`, `bz` | µT | NED frame to match the rest of SCCS. |

Example:

```csv
t,bx,by,bz
0.00,45.2,-2.1,-8.4
0.10,45.1,-2.2,-8.5
0.20,44.9,-2.4,-8.5
```

### Methods

| Signature | Behaviour |
| --- | --- |
| `at(t) -> np.ndarray` | Linearly interpolated field at simulation time `t`. |
| `metadata() -> dict` | `{"type": "csv", "path", "duration_s", "samples"}`. |

### Error cases

| Condition | Behaviour |
| --- | --- |
| Missing column | `ValueError` |
| Fewer than two rows | `ValueError` |
| Unsorted timestamps | Silently sorted on load |
| `t < t_min` or `t > t_max` | Clamped to first/last row |
