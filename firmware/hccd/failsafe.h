// SCCS — failsafes: watchdog, communication timeout, over-temperature
// latch. None of the functions block; they are stateless or hold tiny
// amounts of `static` state inside the .cpp.

#pragma once

#include <stdint.h>

namespace sccs {

// Comm timeout: if no valid packet arrives within this window, the
// firmware drives all DAC channels to DAC_MID_CODE.
constexpr uint32_t COMM_TIMEOUT_MS = 1000;

// Set up the AVR watchdog timer (250 ms full-reset on missed kicks).
void failsafe_init();

// Pet the watchdog from the main loop.
void failsafe_kick();

// True if any of the three channel temperatures exceeds the
// configured limit. Values of INT16_MIN (sensor fault) are ignored.
bool failsafe_overtemp(const int16_t t_x100[3]);

// True if `now_ms - last_packet_ms` exceeds COMM_TIMEOUT_MS. Returns
// false until the first valid packet has been seen.
bool failsafe_comm_timeout(uint32_t now_ms, uint32_t last_packet_ms);

// Helper: forces all three setpoints to the zero-current mid-code.
void failsafe_force_zero(uint16_t setpoints[3]);

// Sticky emergency-stop latch. Cleared only by CMD_RESET_ESTOP.
void failsafe_set_estop(bool value);
bool failsafe_estop();

}  // namespace sccs
