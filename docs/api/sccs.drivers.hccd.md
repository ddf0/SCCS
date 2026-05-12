# `sccs.drivers.hccd`

Defined in [`src/sccs/drivers/hccd.py`](../../src/sccs/drivers/hccd.py).

High-level I²C client for the HCCD controller. Converts amperes to
12-bit DAC codes, packs the wire protocol from
[`sccs.protocol`](sccs.protocol.md), and pushes the bytes to a
smbus2-like bus.

## Constants

| Symbol | Value | Meaning |
| --- | --- | --- |
| `I_MAX` | `3.0` | Nominal current limit per axis (A). Inputs are clipped to `±I_MAX`. |
| `CURRENT_TO_DAC` | `DAC_MAX_CODE / (2 * I_MAX) = 682.5` | DAC counts per ampere. |

## Public functions

### `amps_to_code(amps: float) -> int`

Maps a signed current (A) to a 12-bit DAC code. Zero amperes maps to
`DAC_MID_CODE` (2048). Values outside `±I_MAX` are clipped. Rounds to
the nearest integer.

### `code_to_amps(code: int) -> float`

Inverse of `amps_to_code`. There is an unavoidable half-LSB asymmetry
at the extremes (the negative side has 2048 codes, the positive 2047)
— `code_to_amps(DAC_MAX_CODE)` returns ≈ 2.9993 A. ~7 mA error at
the rail is well below the analogue noise floor.

## `class HCCDClient`

### Constructor

```python
HCCDClient(bus: BusLike, address: int = HCCD_I2C_ADDRESS)
```

`bus` must implement the smbus2 `write_i2c_block_data` /
`read_i2c_block_data` methods. The client does not own the bus.

### Methods

| Signature | Behaviour |
| --- | --- |
| `set_currents(ix, iy, iz)` | Send three `CMD_WRITE_SETPOINT` packets, one per axis. Currents are clipped to `±I_MAX`. |
| `reset_estop()` | Send `CMD_RESET_ESTOP` to clear the firmware E-stop latch. |
| `read_temperatures()` | Raises `NotImplementedError` until the firmware-side `Wire.onRequest` handler is wired up. |

## `class BusLike` (Protocol)

Structural type that captures the subset of `smbus2.SMBus` we depend
on. Lets us substitute `unittest.mock.Mock` in tests without
importing `smbus2`.
