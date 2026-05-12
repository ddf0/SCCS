# Documentation Index

Top-level map of all classes and modules in the SCCS codebase. Update
this index whenever you add, rename, or delete a public symbol.

## Convention

- Every public Python module has a matching page under `docs/api/<module>.md`.
- Every public class has its own H2 section inside its module page.
- Firmware modules (`.h`/`.cpp` pairs) are documented under `docs/firmware/`.
- Architecture overviews live under `docs/architecture/`.

## Python — `src/sccs/`

| Module | Page | Public symbols |
| --- | --- | --- |
| `sccs` | [`api/sccs.md`](api/sccs.md) | `__version__` |
| `sccs.protocol` | [`api/sccs.protocol.md`](api/sccs.protocol.md) | `crc8_sae_j1850`, `pack_setpoint`, `pack_reset_estop`, protocol constants |
| `sccs.drivers.hccd` | [`api/sccs.drivers.hccd.md`](api/sccs.drivers.hccd.md) | `HCCDClient`, `amps_to_code`, `code_to_amps`, `BusLike` |
| `sccs.drivers.magnetometer` | [`api/sccs.drivers.magnetometer.md`](api/sccs.drivers.magnetometer.md) | `MMC5983Driver`, register & sensitivity constants |

(Modules are added as they are implemented.)

## Firmware — `firmware/hccd/`

| File | Page |
| --- | --- |
| `hccd.ino` (entry sketch) | [`firmware/overview.md`](firmware/overview.md) |
| `protocol.h` / `protocol.cpp` | [`firmware/protocol.md`](firmware/protocol.md) |
| `dac_driver.h` / `dac_driver.cpp` | [`firmware/dac_driver.md`](firmware/dac_driver.md) |
| `i2c_slave.h` / `i2c_slave.cpp` | [`firmware/i2c_slave.md`](firmware/i2c_slave.md) |
| `temp_sensor.h` / `temp_sensor.cpp` | [`firmware/temp_sensor.md`](firmware/temp_sensor.md) |
| `failsafe.h` / `failsafe.cpp` | [`firmware/failsafe.md`](firmware/failsafe.md) |

## Architecture

| Document | Topic |
| --- | --- |
| [`architecture/overview.md`](architecture/overview.md) | System architecture and dataflow |

## See also

- Repository [`README.md`](../README.md)
- Software design spec (in the parent VKR repository): `docs/superpowers/specs/2026-05-12-sccs-software-design.md`
- Implementation plan: `docs/superpowers/plans/2026-05-12-sccs-implementation.md`
