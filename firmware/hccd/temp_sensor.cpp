// SCCS — NTC temperature reader implementation.

#include "temp_sensor.h"

#include <Arduino.h>
#include <math.h>

namespace sccs {

static const uint8_t kAdcPins[3] = {A0, A1, A2};

void temp_init() {
  analogReference(DEFAULT);
  for (uint8_t i = 0; i < 3; ++i) {
    pinMode(kAdcPins[i], INPUT);
  }
}

int16_t temp_read_x100(uint8_t channel) {
  if (channel > 2) return INT16_MIN;

  const uint16_t adc = analogRead(kAdcPins[channel]);
  if (adc == 0 || adc >= 1023) return INT16_MIN;  // open or short

  // Voltage divider:
  //   V_adc = V_cc * R_ntc / (R_ntc + R_series)
  //   R_ntc = R_series * adc / (1023 - adc)
  const float r_ntc = NTC_SERIES_R * static_cast<float>(adc) /
                      (1023.0f - static_cast<float>(adc));

  // Beta equation: 1/T = 1/T0 + (1/Beta) * ln(R/R0)
  const float ln_ratio = logf(r_ntc / NTC_R0);
  const float inv_t = (1.0f / NTC_T0_K) + (ln_ratio / NTC_BETA);
  const float t_c = (1.0f / inv_t) - 273.15f;

  return static_cast<int16_t>(t_c * 100.0f);
}

}  // namespace sccs
