# `sccs.drivers.magnetometer`

Defined in [`src/sccs/drivers/magnetometer.py`](../../src/sccs/drivers/magnetometer.py).

Driver for the MEMSIC MMC5983MA three-axis magnetometer over I²C.
Returns calibrated field vectors in µT.

## Constants

| Symbol | Value | Meaning |
| --- | --- | --- |
| `MMC5983_ADDRESS` | `0x30` | Default I²C address. |
| `REG_CTRL_0`, `REG_CTRL_1`, `REG_CTRL_2` | `0x09`, `0x0A`, `0x0B` | Control registers. |
| `REG_OUT_BASE` | `0x00` | Start of 7-byte output block (XH XL YH YL ZH ZL XYZ2). |
| `BIT_TM_M`, `BIT_SET`, `BIT_RESET` | `0x01`, `0x08`, `0x10` | CTRL_0 trigger bits. |
| `COUNTS_TO_MILLIGAUSS` | `0.0625` | LSB-to-mG scaling for the 18-bit output. |
| `COUNTS_MID` | `2**17` | Zero-field code. |
| `MILLIGAUSS_TO_MICROTESLA` | `0.1` | Unit conversion. |
| `BW_BITS` | `{100: 0b00, 200: 0b01, 400: 0b10, 800: 0b11}` | Output bandwidth selection. |

## `class MMC5983Driver`

### Constructor

```python
MMC5983Driver(bus, address=MMC5983_ADDRESS, bandwidth_hz=100)
```

Configures CTRL_1 (bandwidth) and CTRL_2 (one-shot mode) immediately.
Raises `ValueError` on unsupported bandwidth.

### Methods

| Signature | Behaviour |
| --- | --- |
| `load_calibration(matrix, offset)` | Install affine calibration `B = M @ (raw - offset)`. Shapes are validated. |
| `read_raw() -> np.ndarray` | One-shot measurement without SET/RESET. Use for calibration sweeps. |
| `read_field_uT() -> np.ndarray` | Full SET/RESET cycle with calibration applied. Returns a `(3,)` array in µT. |

## SET/RESET cycle

`read_field_uT` performs four bus transactions:

1. Write CTRL_0 = `BIT_SET`, wait 1 ms.
2. Trigger and read (call `_trigger_and_read`).
3. Write CTRL_0 = `BIT_RESET`, wait 1 ms.
4. Trigger and read again.

The final value is `(B_set − B_reset) / 2`, which removes offset drift
that single-shot measurements would carry.
