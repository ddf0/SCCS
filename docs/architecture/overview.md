# Architecture Overview

## Two-tier model

```
[ Operator browser ] <-- HTTP/JSON --> [ Dash web server (Pi, thread A) ]
                                                 |
                                                 |  threading.RLock shared state
                                                 |  + queue.Queue (UI commands)
                                                 v
                                       [ Control loop (Pi, thread B, 100 Hz) ]
                                                 |
                                                 |  smbus2: I2C bus 1
                                                 v
                          +----------+-----------+---------+
                          v                                v
                  [ MMC5983MA       ]            [ HCCD controller     ]
                  [ 0x30, I²C       ]            [ 0x10, I²C slave     ]
                                                          |
                                                          | SPI master, 4 MHz
                                                          v
                                                 [ MCP4922 x3 (X/Y/Z) ]
                                                          |
                                                          v
                                                 [ Current source CS  ]
                                                          |
                                                          v
                                                 [ Helmholtz coils    ]
```

## Tiers

- **Upper tier** — Python 3.11 application on a Raspberry Pi 3B. Runs a
  100 Hz PID control loop in a dedicated thread, serves a Plotly Dash
  web UI on port 8080.
- **Lower tier** — ATmega328P firmware on the HCCD board. Accepts a
  6-byte CRC-protected I²C packet per axis update, drives three MCP4922
  DACs over SPI, periodically reads NTC temperatures, and enforces
  watchdog / comm-timeout / over-temperature failsafes.

## Information flow per 10 ms cycle

1. The active profile (fixed point / orbital / CSV) yields the target
   field vector `b_target` at the current simulation time.
2. The MMC5983MA driver returns the calibrated measured vector
   `b_measured`.
3. Three independent `PIDController` instances produce three current
   setpoints in amperes.
4. `HCCDClient.set_currents` sends three I²C packets to the HCCD
   firmware (one per axis), each containing the 12-bit DAC code.
5. The HCCD firmware writes the new codes to the MCP4922 DACs.
6. Every 100th tick (1 Hz) temperatures are read back via I²C.
7. Shared state is updated under `RLock`; the Dash web UI reads it
   every 200 ms via `dcc.Interval`.

For full details see the design spec
(`docs/superpowers/specs/2026-05-12-sccs-software-design.md` in the
parent VKR repository).
