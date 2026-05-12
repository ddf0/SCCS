// SCCS — TWI/I²C slave with 6-byte packet parser.
//
// Receives 6-byte packets from the Raspberry Pi at HCCD_I2C_ADDRESS,
// validates CRC-8, and exposes parsed packets to the main loop via a
// double-buffered non-blocking handoff.

#pragma once

#include <stdint.h>

namespace sccs {

struct ParsedPacket {
  uint8_t cmd;
  uint8_t channel;
  uint16_t code;   // 12-bit DAC code
  uint8_t flags;
};

// Parse a raw 6-byte buffer. Returns true if length and CRC are valid.
// Safe to call from non-ISR context (used by tests when implemented).
bool parse_packet(const uint8_t* buf, uint8_t length, ParsedPacket& out);

// Initialise Wire as slave at HCCD_I2C_ADDRESS, register onReceive ISR.
void i2c_slave_init();

// Non-blocking poll. If a valid packet is pending, fills `out` and
// returns true. The caller drives all side effects (DAC writes etc.).
bool i2c_slave_take_packet(ParsedPacket& out);

// millis() timestamp of the last successfully validated packet, or 0 if
// none has been received since boot. Used by the comm-timeout failsafe.
uint32_t i2c_last_packet_millis();

// Number of packets dropped due to CRC mismatch (cumulative). Useful for
// surfacing bus quality issues over the diagnostic Serial channel.
uint32_t i2c_crc_error_count();

}  // namespace sccs
