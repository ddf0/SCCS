# `protocol.h` / `protocol.cpp`

Defined in [`firmware/hccd/protocol.h`](../../firmware/hccd/protocol.h)
and [`firmware/hccd/protocol.cpp`](../../firmware/hccd/protocol.cpp).

Bit-exact mirror of [`src/sccs/protocol.py`](../api/sccs.protocol.md) —
any change must be reflected on both sides.

## Constants

Listed in `namespace sccs`:

| Symbol | Value | Meaning |
| --- | --- | --- |
| `HCCD_I2C_ADDRESS` | `0x10` | TWI slave address of this controller. |
| `PACKET_SIZE` | `6` | Always 6 bytes. |
| `CMD_WRITE_SETPOINT` | `0x01` | One-axis DAC setpoint write. |
| `CMD_READ_TEMPERATURES` | `0x02` | Three NTC temperature read-back. |
| `CMD_RESET_ESTOP` | `0x03` | Clear the over-temperature/E-stop latch. |
| `STATUS_OK` / `STATUS_OVERTEMP` / `STATUS_COMM_TIMEOUT` / `STATUS_ESTOP` | `0x00` / `0x01` / `0x02` / `0x04` | Status-byte bits. |
| `DAC_MAX_CODE`, `DAC_MID_CODE` | `4095`, `2048` | 12-bit range; mid = zero current. |
| `TEMP_LIMIT_C_X100` | `8500` | 85.00 °C in centi-celsius. |

## Function

### `uint8_t crc8(const uint8_t* data, uint8_t length)`

CRC-8/SAE J1850 over `length` bytes starting at `data`. Polynomial
`0x07`, init `0xFF`, no reflection, no final XOR. Returns the 8-bit
checksum. Compute over the **first 5 bytes** of the packet to obtain
the CRC byte that goes into the 6th position.

## Packet formats

`CMD_WRITE_SETPOINT`:

```
[0x01] [channel 0..2] [DAC_LSB] [DAC_MSB nibble] [FLAGS=0] [CRC-8]
```

`CMD_READ_TEMPERATURES` request (payload bytes 1..4 are zero):

```
[0x02] [0] [0] [0] [0] [CRC-8]
```

`CMD_READ_TEMPERATURES` response (driven back to the master by the
firmware Wire callback):

```
[status byte] [T_x LSB] [T_x MSB] [T_y LSB] [T_y MSB] [T_z LSB] [T_z MSB] [CRC-8]
```

Temperatures are signed 16-bit centi-celsius (e.g. `2350` = 23.50 °C).

## CRC reference vectors

Both sides must produce these values. The Python mirror in
`tests/test_protocol_crc.py` is parametrised over the same vectors.

| Input bytes | CRC-8 |
| --- | --- |
| (empty) | `0xFF` |
| `0x00` | `0xF3` |
| `0xFF` | `0x00` |
| `"123456789"` (ASCII) | `0xFB` |
| `0x01 0x00 0x00 0x08 0x00` (write_setpoint mid, channel 0) | `0xF3` |
| `0x01 0x02 0xFF 0x0F 0x00` (write_setpoint max, channel 2) | `0x9F` |
| `0x03 0x00 0x00 0x00 0x00` (reset E-stop) | `0x9F` |
