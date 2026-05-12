# `temp_sensor.h` / `temp_sensor.cpp`

Defined in [`firmware/hccd/temp_sensor.h`](../../firmware/hccd/temp_sensor.h)
and [`firmware/hccd/temp_sensor.cpp`](../../firmware/hccd/temp_sensor.cpp).

Reads three NTC 10 kΩ thermistors via ADC0..ADC2. Each thermistor is
wired in a voltage divider with a fixed 10 kΩ pull-up to 5 V. The
beta-equation form (B25/85 = 3950 K) is used because it costs less
flash than full Steinhart–Hart and is accurate to ±0.5 °C over the
0..85 °C window we care about.

## Constants

| Symbol | Value | Meaning |
| --- | --- | --- |
| `NTC_R0` | 10 000 Ω | Resistance at the reference temperature. |
| `NTC_BETA` | 3950 K | Material constant. |
| `NTC_T0_K` | 298.15 K | Reference temperature (25 °C). |
| `NTC_SERIES_R` | 10 000 Ω | Series resistor in the divider. |

## Functions

### `void temp_init()`

Sets `analogReference(DEFAULT)` (AVcc = 5 V) and configures pins.

### `int16_t temp_read_x100(uint8_t channel)`

Returns the temperature on `channel` (0..2) in centi-celsius
(e.g. `2350` = 23.50 °C). Returns `INT16_MIN` if the ADC reading is
saturated low or high — interpreted as «sensor open or shorted».
The over-temperature failsafe ignores `INT16_MIN` readings so a
disconnected sensor does not trigger a spurious shutdown.
