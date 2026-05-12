// SCCS — failsafes implementation.

#include "failsafe.h"

#include <Arduino.h>
#include <avr/wdt.h>

#include "protocol.h"

namespace sccs {

namespace {
bool g_estop = false;
}  // namespace

void failsafe_init() {
  wdt_enable(WDTO_250MS);
}

void failsafe_kick() {
  wdt_reset();
}

bool failsafe_overtemp(const int16_t t_x100[3]) {
  for (uint8_t i = 0; i < 3; ++i) {
    if (t_x100[i] != INT16_MIN && t_x100[i] > TEMP_LIMIT_C_X100) {
      return true;
    }
  }
  return false;
}

bool failsafe_comm_timeout(uint32_t now_ms, uint32_t last_packet_ms) {
  if (last_packet_ms == 0) return false;  // no comm seen yet — boot grace
  return (now_ms - last_packet_ms) > COMM_TIMEOUT_MS;
}

void failsafe_force_zero(uint16_t setpoints[3]) {
  for (uint8_t i = 0; i < 3; ++i) {
    setpoints[i] = DAC_MID_CODE;
  }
}

void failsafe_set_estop(bool value) { g_estop = value; }
bool failsafe_estop() { return g_estop; }

}  // namespace sccs
