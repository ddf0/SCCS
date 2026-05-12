// SCCS — TWI/I²C slave implementation.

#include "i2c_slave.h"

#include <Arduino.h>
#include <Wire.h>

#include "protocol.h"

namespace sccs {

bool parse_packet(const uint8_t* buf, uint8_t length, ParsedPacket& out) {
  if (length != PACKET_SIZE) return false;
  if (crc8(buf, PACKET_SIZE - 1) != buf[PACKET_SIZE - 1]) return false;
  out.cmd = buf[0];
  out.channel = buf[1];
  out.code = static_cast<uint16_t>(buf[2]) |
             (static_cast<uint16_t>(buf[3] & 0x0F) << 8);
  out.flags = buf[4];
  return true;
}

namespace {

volatile bool g_packet_ready = false;
volatile uint8_t g_buffer[PACKET_SIZE] = {0};
volatile uint8_t g_length = 0;
volatile uint32_t g_last_packet_ms = 0;
volatile uint32_t g_crc_errors = 0;

void on_receive(int n) {
  // Drain spurious-length packets without touching the live buffer.
  if (n != PACKET_SIZE) {
    while (Wire.available()) (void)Wire.read();
    return;
  }
  for (uint8_t i = 0; i < PACKET_SIZE; ++i) {
    g_buffer[i] = static_cast<uint8_t>(Wire.read());
  }
  g_length = PACKET_SIZE;
  g_packet_ready = true;
}

}  // namespace

void i2c_slave_init() {
  Wire.begin(HCCD_I2C_ADDRESS);
  Wire.onReceive(on_receive);
}

bool i2c_slave_take_packet(ParsedPacket& out) {
  if (!g_packet_ready) return false;

  uint8_t local[PACKET_SIZE];
  noInterrupts();
  for (uint8_t i = 0; i < PACKET_SIZE; ++i) local[i] = g_buffer[i];
  g_packet_ready = false;
  interrupts();

  if (!parse_packet(local, PACKET_SIZE, out)) {
    g_crc_errors++;
    return false;
  }
  g_last_packet_ms = millis();
  return true;
}

uint32_t i2c_last_packet_millis() { return g_last_packet_ms; }
uint32_t i2c_crc_error_count() { return g_crc_errors; }

}  // namespace sccs
