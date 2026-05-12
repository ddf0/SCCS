# `sccs.config`

Defined in [`src/sccs/config.py`](../../src/sccs/config.py).

## Pydantic v2 schemas

| Class | Fields |
| --- | --- |
| `I2CConfig` | `bus`, `hccd_address`, `magnetometer_address` (all validated address range 0x08..0x77). |
| `PIDConfig` | `kp`, `ki`, `kd` ≥ 0; `dt_ms` > 0; `current_limit_a` > 0. |
| `ControlConfig` | `loop_period_ms` > 0; `max_consecutive_errors` > 0. |
| `WebConfig` | `host`, `port` 1..65535, `update_interval_ms` > 0. |
| `SCCSConfig` | Aggregates the four above. |

## `load_config(path: str | Path) -> SCCSConfig`

Reads the YAML at `path`, runs pydantic validation, and returns a
fully typed `SCCSConfig`. Invalid values raise `pydantic.ValidationError`
with a JSON-pointer to the offending key.

## Default file

[`config/default.yaml`](../../config/default.yaml) ships sensible
defaults for the SCCS-1 hardware. Override per-host values
(calibration, IP) using a second YAML file passed on the command
line.

## Notes on hex literals

PyYAML 1.1-style hex (`0x10`) is parsed as an integer. Stick to that
form in the I²C section to keep the file readable.
