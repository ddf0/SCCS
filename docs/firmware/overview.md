# HCCD firmware — overview

Sketch root: [`firmware/hccd/`](../../firmware/hccd/).
Open `hccd.ino` in Arduino IDE 2 (or `arduino-cli`), select board
**Arduino Uno (ATmega328P, 16 MHz)**, compile and upload.

## Module layout

| File | Responsibility |
| --- | --- |
| `hccd.ino` | Sketch entry point — `setup()`, `loop()` |
| `protocol.h` / `protocol.cpp` | Wire protocol constants, CRC-8/SAE J1850 |
| `dac_driver.h` / `dac_driver.cpp` | MCP4922 SPI driver (three channels) |
| `i2c_slave.h` / `i2c_slave.cpp` | TWI slave + 6-byte packet parser |
| `temp_sensor.h` / `temp_sensor.cpp` | NTC ADC + Steinhart–Hart conversion |
| `failsafe.h` / `failsafe.cpp` | Watchdog, comm timeout, over-temp lockout |

Modules are added as Phase 1–2 of the implementation plan proceeds.

## Wiring (planned)

| Signal | ATmega328P pin | Destination |
| --- | --- | --- |
| `SCK`, `MOSI` | PB5, PB3 | MCP4922 ×3 (shared) |
| `CS_X`, `CS_Y`, `CS_Z` | PD5, PD6, PD7 | MCP4922 channel selects |
| `SDA`, `SCL` | PC4, PC5 | I²C bus to Raspberry Pi |
| `ADC0`, `ADC1`, `ADC2` | PC0, PC1, PC2 | NTC dividers on CS boards |
