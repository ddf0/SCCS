# `failsafe.h` / `failsafe.cpp`

Defined in [`firmware/hccd/failsafe.h`](../../firmware/hccd/failsafe.h)
and [`firmware/hccd/failsafe.cpp`](../../firmware/hccd/failsafe.cpp).

Four independent failsafes:

1. **Watchdog** — `wdt_enable(WDTO_250MS)`. Any code path that
   forgets to call `failsafe_kick()` within 250 ms causes a full
   reset. After reset, `setup()` re-writes the mid-code (zero current)
   to all three DACs before any other action.
2. **Communication timeout** — if no valid packet arrives within
   `COMM_TIMEOUT_MS` (1 second), the loop drives all three channels
   to mid-code. Boot grace: returns false until the first packet has
   ever been seen.
3. **Over-temperature** — checks the three latest temperatures
   against `TEMP_LIMIT_C_X100` (85.00 °C). Sensor faults
   (`INT16_MIN`) are ignored.
4. **Emergency-stop latch** — sticky boolean cleared only by the
   `CMD_RESET_ESTOP` packet. Set automatically by the over-temp path.

## Functions

### `void failsafe_init()`

Enables the watchdog. Must be called once from `setup()` after all
other peripheral init (otherwise a slow peripheral init could itself
trigger a reset).

### `void failsafe_kick()`

`wdt_reset()`. Call near the bottom of every `loop()` iteration.

### `bool failsafe_overtemp(const int16_t t_x100[3])`

True if any non-fault temperature exceeds the threshold.

### `bool failsafe_comm_timeout(uint32_t now_ms, uint32_t last_packet_ms)`

Pure function over the two timestamps. Returns false during boot
grace.

### `void failsafe_force_zero(uint16_t setpoints[3])`

Helper used by both the over-temp and comm-timeout branches. Sets
every entry to `DAC_MID_CODE` — the caller must follow up with
`dac_write_all`.

### `void failsafe_set_estop(bool value)` / `bool failsafe_estop()`

Get/set the sticky E-stop latch. When set, `CMD_WRITE_SETPOINT`
packets are ignored.
