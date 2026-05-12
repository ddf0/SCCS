# `i2c_slave.h` / `i2c_slave.cpp`

Defined in [`firmware/hccd/i2c_slave.h`](../../firmware/hccd/i2c_slave.h)
and [`firmware/hccd/i2c_slave.cpp`](../../firmware/hccd/i2c_slave.cpp).

Sets up the AVR TWI peripheral as an I²C slave at `HCCD_I2C_ADDRESS`
(`0x10`) and exposes a non-blocking double-buffered handoff between
the `Wire.onReceive` ISR and the main `loop()`.

## Types

### `struct ParsedPacket`

| Field | Type | Meaning |
| --- | --- | --- |
| `cmd` | `uint8_t` | One of `CMD_*` from `protocol.h` |
| `channel` | `uint8_t` | Axis index 0..2 (only valid for `CMD_WRITE_SETPOINT`) |
| `code` | `uint16_t` | 12-bit DAC code reconstructed from bytes 2–3 |
| `flags` | `uint8_t` | Reserved (currently always 0) |

## Functions

### `bool parse_packet(const uint8_t* buf, uint8_t length, ParsedPacket& out)`

Pure parsing — no Wire dependencies. Returns true only if `length` is
`PACKET_SIZE` and the CRC byte matches. Fills `out` on success.

### `void i2c_slave_init()`

Starts `Wire` as slave and registers the receive ISR.

### `bool i2c_slave_take_packet(ParsedPacket& out)`

Non-blocking. Returns true once per validated packet. Spurious-length
packets are silently drained inside the ISR; CRC mismatches are
counted (see `i2c_crc_error_count`).

### `uint32_t i2c_last_packet_millis()`

`millis()` timestamp of the last successfully validated packet, or
`0` before any packet has been received. The comm-timeout failsafe
uses this value.

### `uint32_t i2c_crc_error_count()`

Monotonic counter of packets dropped due to CRC mismatch. Surface over
`Serial` when diagnosing flaky cables.
