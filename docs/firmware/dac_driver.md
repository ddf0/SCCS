# `dac_driver.h` / `dac_driver.cpp`

Defined in [`firmware/hccd/dac_driver.h`](../../firmware/hccd/dac_driver.h)
and [`firmware/hccd/dac_driver.cpp`](../../firmware/hccd/dac_driver.cpp).

Drives three MCP4922 dual-channel DACs (only channel A of each used)
that share MOSI/SCLK and have individual chip-select lines.

## Pinout

| Constant | Pin | Routed to |
| --- | --- | --- |
| `CS_PIN_X` | PD5 (Arduino `D5`) | MCP4922 #X `~CS` |
| `CS_PIN_Y` | PD6 (Arduino `D6`) | MCP4922 #Y `~CS` |
| `CS_PIN_Z` | PD7 (Arduino `D7`) | MCP4922 #Z `~CS` |

SPI: 4 MHz, `SPI_MODE0`, MSB-first. The configuration word sent on
each write is `0x7000 | (code & 0x0FFF)` — channel A, buffered, 1x
gain, output enabled.

## Functions

### `void dac_init()`

Initialises all three CS pins to OUTPUT/HIGH and starts the SPI bus.

### `void dac_write(uint8_t channel, uint16_t value12)`

Writes the 12-bit code to one channel (0 = X, 1 = Y, 2 = Z). Codes
larger than `DAC_MAX_CODE` are clipped. The function opens an
`SPI.beginTransaction` window per call so it is safe to mix with other
SPI peripherals later.

### `void dac_write_all(const uint16_t values[3])`

Convenience wrapper that calls `dac_write` three times. Takes < 50 µs
total at 4 MHz SPI.
