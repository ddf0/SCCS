// SCCS — CRC-8/SAE J1850 implementation.
//
// Bit-exact mirror of crc8_sae_j1850() in src/sccs/protocol.py.

#include "protocol.h"

namespace sccs {

uint8_t crc8(const uint8_t* data, uint8_t length) {
  uint8_t crc = 0xFF;
  for (uint8_t i = 0; i < length; ++i) {
    crc ^= data[i];
    for (uint8_t b = 0; b < 8; ++b) {
      if (crc & 0x80) {
        crc = static_cast<uint8_t>((crc << 1) ^ 0x07);
      } else {
        crc = static_cast<uint8_t>(crc << 1);
      }
    }
  }
  return crc;
}

}  // namespace sccs
