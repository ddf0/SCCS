// SCCS — HCCD firmware entry point.
//
// Helmholtz Coil Control Driver: receives 6-byte I²C packets from the
// Raspberry Pi over TWI (slave at 0x10), writes 12-bit codes to three
// MCP4922 DACs over SPI, periodically samples three NTC temperatures,
// and enforces watchdog / comm-timeout / over-temperature failsafes.
//
// Event-driven loop — heavy work happens here; the TWI ISR only copies
// bytes into a volatile buffer and raises a ready flag.

#include <Arduino.h>

#include "dac_driver.h"
#include "failsafe.h"
#include "i2c_slave.h"
#include "protocol.h"
#include "temp_sensor.h"

namespace {

// Current setpoints (12-bit DAC codes), one per axis.
uint16_t g_setpoints[3] = {sccs::DAC_MID_CODE, sccs::DAC_MID_CODE,
                           sccs::DAC_MID_CODE};

// Latest temperatures, in centi-celsius. INT16_MIN means «no reading».
int16_t g_temps_x100[3] = {0, 0, 0};

uint32_t g_last_temp_ms = 0;
constexpr uint32_t TEMP_POLL_INTERVAL_MS = 100;

}  // namespace

void setup() {
  Serial.begin(115200);

  sccs::dac_init();
  sccs::dac_write_all(g_setpoints);  // ensure zero current at boot

  sccs::temp_init();
  sccs::i2c_slave_init();
  sccs::failsafe_init();

  Serial.println(F("HCCD ready"));
}

void loop() {
  // 1. Drain any pending packet.
  sccs::ParsedPacket pkt;
  if (sccs::i2c_slave_take_packet(pkt)) {
    switch (pkt.cmd) {
      case sccs::CMD_WRITE_SETPOINT:
        if (pkt.channel < 3 && !sccs::failsafe_estop()) {
          g_setpoints[pkt.channel] = pkt.code;
          sccs::dac_write(pkt.channel, pkt.code);
        }
        break;
      case sccs::CMD_RESET_ESTOP:
        sccs::failsafe_set_estop(false);
        break;
      default:
        // CMD_READ_TEMPERATURES is handled via Wire.onRequest when added.
        break;
    }
  }

  // 2. Periodic temperature sampling.
  const uint32_t now = millis();
  if (now - g_last_temp_ms >= TEMP_POLL_INTERVAL_MS) {
    g_last_temp_ms = now;
    for (uint8_t i = 0; i < 3; ++i) {
      g_temps_x100[i] = sccs::temp_read_x100(i);
    }
    if (sccs::failsafe_overtemp(g_temps_x100)) {
      sccs::failsafe_set_estop(true);
      sccs::failsafe_force_zero(g_setpoints);
      sccs::dac_write_all(g_setpoints);
    }
  }

  // 3. Communication timeout check.
  if (sccs::failsafe_comm_timeout(now, sccs::i2c_last_packet_millis())) {
    sccs::failsafe_force_zero(g_setpoints);
    sccs::dac_write_all(g_setpoints);
  }

  // 4. Kick watchdog.
  sccs::failsafe_kick();
}
