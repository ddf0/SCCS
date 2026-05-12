// SCCS — NTC temperature reader.
//
// Three NTC 10 kΩ thermistors are wired to ADC0..ADC2 each with a fixed
// 10 kΩ pull-up to VCC (5 V). Beta-equation conversion (B25/85 = 3950 K).

#pragma once

#include <stdint.h>

namespace sccs {

// NTC parameters — adjust if the hardware changes.
constexpr float NTC_R0 = 10000.0f;        // resistance at T0 (Ω)
constexpr float NTC_BETA = 3950.0f;       // material constant (K)
constexpr float NTC_T0_K = 298.15f;       // reference temperature (K) = 25 °C
constexpr float NTC_SERIES_R = 10000.0f;  // series resistor (Ω)

void temp_init();

// Returns the temperature on `channel` (0..2) in centi-celsius
// (e.g. 2350 = 23.50 °C). Returns INT16_MIN if the ADC reading is
// outside the usable range (open or shorted sensor).
int16_t temp_read_x100(uint8_t channel);

}  // namespace sccs
