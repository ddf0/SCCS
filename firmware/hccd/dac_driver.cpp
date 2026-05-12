// SCCS — MCP4922 SPI driver.

#include "dac_driver.h"

#include <Arduino.h>
#include <SPI.h>

#include "protocol.h"

namespace sccs {

static const uint8_t kCSPins[3] = {CS_PIN_X, CS_PIN_Y, CS_PIN_Z};

void dac_init() {
  for (uint8_t i = 0; i < 3; ++i) {
    pinMode(kCSPins[i], OUTPUT);
    digitalWrite(kCSPins[i], HIGH);
  }
  SPI.begin();
}

void dac_write(uint8_t channel, uint16_t value12) {
  if (channel > 2) return;
  if (value12 > DAC_MAX_CODE) value12 = DAC_MAX_CODE;

  // MCP4922 config bits:
  //   bit 15: DAC select (0 = channel A — the only one we use)
  //   bit 14: buffer enable (1)
  //   bit 13: gain select (1 = 1x)
  //   bit 12: output active (1 = ON)
  //   bits 11..0: 12-bit data
  const uint16_t word = static_cast<uint16_t>(0x7000) | (value12 & 0x0FFF);

  SPI.beginTransaction(SPISettings(4000000UL, MSBFIRST, SPI_MODE0));
  digitalWrite(kCSPins[channel], LOW);
  SPI.transfer(static_cast<uint8_t>(word >> 8));
  SPI.transfer(static_cast<uint8_t>(word & 0xFF));
  digitalWrite(kCSPins[channel], HIGH);
  SPI.endTransaction();
}

void dac_write_all(const uint16_t values[3]) {
  for (uint8_t i = 0; i < 3; ++i) {
    dac_write(i, values[i]);
  }
}

}  // namespace sccs
