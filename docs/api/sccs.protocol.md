# `sccs.protocol`

Defined in [`src/sccs/protocol.py`](../../src/sccs/protocol.py).

Bit-exact mirror of [`firmware/hccd/protocol.h`](../firmware/protocol.md) —
any change here must be reflected on the firmware side and vice versa.

## Public constants

| Symbol | Value | Meaning |
| --- | --- | --- |
| `HCCD_I2C_ADDRESS` | `0x10` | I²C slave address of the HCCD controller. |
| `PACKET_SIZE` | `6` | All packets are 6 bytes (5 payload + 1 CRC). |
| `CMD_WRITE_SETPOINT` | `0x01` | Write a new 12-bit DAC code to one channel. |
| `CMD_READ_TEMPERATURES` | `0x02` | Request the three NTC temperatures. |
| `CMD_RESET_ESTOP` | `0x03` | Clear the firmware-side emergency stop latch. |
| `STATUS_OK` … `STATUS_ESTOP` | `0x00` … `0x04` | Bits of the status byte returned by reads. |
| `DAC_MAX_CODE`, `DAC_MID_CODE` | `4095`, `2048` | 12-bit DAC range; mid-code = zero current. |
| `TEMP_LIMIT_C_X100` | `8500` | Over-temperature threshold (85.00 °C, centi-celsius). |

## Public functions

### `crc8_sae_j1850(data: bytes) -> int`

CRC-8/SAE J1850. Polynomial `0x07`, init `0xFF`, no reflection, no
final XOR. Returns the 8-bit checksum.

### `pack_setpoint(channel: int, code: int) -> bytes`

Builds a 6-byte `CMD_WRITE_SETPOINT` packet:

```
[CMD=0x01] [CH=0..2] [DATA_LSB] [DATA_MSB nibble] [FLAGS=0] [CRC-8]
```

The 12-bit `code` is split LSB-first: byte 2 = bits 0..7,
byte 3 = bits 8..11 in the low nibble (high nibble is zero).

Raises `ValueError` if `channel` is not in `{0, 1, 2}` or `code` is
outside `[0, DAC_MAX_CODE]`.

### `pack_reset_estop() -> bytes`

Builds a 6-byte `CMD_RESET_ESTOP` packet. All payload bytes after the
opcode are zero.

## Usage

```python
from sccs.protocol import pack_setpoint

# Zero current on channel X
packet = pack_setpoint(channel=0, code=2048)
# Hand `packet[1:]` (5 bytes) to smbus2 as the "data block" after the
# command byte `packet[0]`.
```
