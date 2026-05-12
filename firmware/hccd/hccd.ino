// SCCS — HCCD firmware entry point.
//
// Helmholtz Coil Control Driver: receives 6-byte I²C packets from the
// Raspberry Pi over TWI (slave at 0x10), writes 12-bit codes to three
// MCP4922 DACs over SPI, periodically samples three NTC temperatures,
// and enforces watchdog / comm-timeout / over-temperature failsafes.
//
// See docs/firmware/overview.md for the high-level design.

#include <Arduino.h>

void setup() {
  Serial.begin(115200);
  Serial.println(F("HCCD boot — placeholder, firmware modules pending"));
}

void loop() {
  // To be replaced by the event-driven loop once modules land.
}
