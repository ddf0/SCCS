# `sccs.profile.orbital`

Defined in [`src/sccs/profile/orbital.py`](../../src/sccs/profile/orbital.py).

## `class OrbitalProfile`

Propagates a Two-Line-Element (TLE) set with SGP4 (via :mod:`skyfield`)
and evaluates the IGRF field (:mod:`ppigrf`) at the satellite's
sub-point each step.

### Constructor

```python
OrbitalProfile(
    tle: tuple[str, str, str],   # (name, line1, line2) — valid checksums required
    time_scale: float = 1.0,     # >1 to accelerate, e.g. 600 = 10 min/s
    t0: datetime | None = None,  # UTC reference for simulation t=0 (defaults to now)
)
```

SGP4 propagation accuracy degrades quickly beyond ~30 days from the
TLE epoch. Tests pin `t0` near the TLE epoch to stay inside the sweet
spot; in production, supply a fresh TLE before starting.

### Methods

| Signature | Behaviour |
| --- | --- |
| `at(t) -> np.ndarray` | NED µT vector at simulation time `t` seconds. |
| `groundtrack(t_start, t_end, n) -> list[(lat, lon, alt_km)]` | `n ≥ 2` evenly spaced subpoints for the map widget. |
| `metadata() -> dict` | `{"type": "orbital", "name", "epoch", "time_scale"}`. |

### Time scale

`time_scale = 1.0` runs in real time. `time_scale = 600` advances the
simulation 600 seconds per wall-clock second — one orbit (~5400 s)
plays in nine seconds. This is the lever the web UI exposes for fast
HIL playback.

### IGRF date handling

ppigrf's coefficient table is indexed by a tz-naive `DatetimeIndex`,
so the profile stores the date as a tz-naive `pd.Timestamp` to keep
the comparison happy. For unit tests we use the TLE-epoch date; in
production the date corresponds to wall-clock at construction time.
