// SCCS — wire-protocol constants shared with the Python side.
//
// Must stay byte-for-byte compatible with src/sccs/protocol.py.
// See docs/firmware/protocol.md for the full packet format.

#pragma once

#include <stdint.h>

namespace sccs {

constexpr uint8_t HCCD_I2C_ADDRESS = 0x10;
constexpr uint8_t PACKET_SIZE = 6;

// Command opcodes (byte 0 of every packet).
constexpr uint8_t CMD_WRITE_SETPOINT = 0x01;
constexpr uint8_t CMD_READ_TEMPERATURES = 0x02;
constexpr uint8_t CMD_RESET_ESTOP = 0x03;

// Bit mask for the status byte returned with CMD_READ_TEMPERATURES.
constexpr uint8_t STATUS_OK = 0x00;
constexpr uint8_t STATUS_OVERTEMP = 0x01;
constexpr uint8_t STATUS_COMM_TIMEOUT = 0x02;
constexpr uint8_t STATUS_ESTOP = 0x04;

// 12-bit DAC range. Mid-code corresponds to zero coil current.
constexpr uint16_t DAC_MAX_CODE = 4095;
constexpr uint16_t DAC_MID_CODE = 2048;

// Over-temperature threshold in centi-celsius (85.00 °C).
constexpr int16_t TEMP_LIMIT_C_X100 = 8500;

// CRC-8/SAE J1850. Polynomial 0x07, init 0xFF, no input/output reflection,
// no final XOR. Identical to the SAE J1850 OBD-II variant.
uint8_t crc8(const uint8_t* data, uint8_t length);

}  // namespace sccs
