// SCCS — MCP4922 SPI driver.
//
// Three single-channel MCP4922 DACs share MOSI/SCLK and have individual
// chip-select lines on PD5 (X), PD6 (Y), PD7 (Z). SPI runs at 4 MHz,
// SPI_MODE0, MSB-first. Each transaction writes a 16-bit configuration
// word containing 4 control bits + 12 data bits.

#pragma once

#include <stdint.h>

namespace sccs {

constexpr uint8_t CS_PIN_X = 5;
constexpr uint8_t CS_PIN_Y = 6;
constexpr uint8_t CS_PIN_Z = 7;

// Initialise CS pins and the SPI peripheral. Call once from setup().
void dac_init();

// Write a 12-bit code to channel 0..2. Values > DAC_MAX_CODE are clipped.
void dac_write(uint8_t channel, uint16_t value12);

// Convenience: write all three channels in one call.
void dac_write_all(const uint16_t values[3]);

}  // namespace sccs
