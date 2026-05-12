# `sccs.profile.fixed`

Defined in [`src/sccs/profile/fixed.py`](../../src/sccs/profile/fixed.py).

## `class FixedPointProfile`

Returns a **constant** magnetic-field vector representing the IGRF
field at a single geographic point.

### Constructor

```python
FixedPointProfile(
    latitude_deg: float,
    longitude_deg: float,
    altitude_km: float,
    date_str: str,        # ISO date "YYYY-MM-DD"
)
```

The IGRF model is evaluated once during construction. Subsequent calls
to `at(t)` return the cached vector.

### Methods

| Signature | Behaviour |
| --- | --- |
| `at(t) -> np.ndarray` | Returns the cached `(3,)` µT vector in NED frame. |
| `metadata() -> dict` | Returns `{"type": "fixed", "lat", "lon", "alt_km", "date"}`. |

### Frame convention

`ppigrf` returns East, North, Up components in nT. The driver remaps
to North-East-Down (NED) and converts to µT:

```
B_x = B_north
B_y = B_east
B_z = -B_up
```

This matches the bench-frame convention used by the rest of the SCCS
stack.
