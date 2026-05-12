# SCCS — Source Current Control System

Control software for a three-axis Helmholtz coil system used in
hardware-in-the-loop testing of small satellite ADCS algorithms.
Part of a bachelor thesis at HSE MIEM.

## Repository layout

| Path | Purpose |
| --- | --- |
| `firmware/hccd/` | ATmega328P sketch (Arduino IDE), runs on the HCCD controller board |
| `src/sccs/` | Python application for Raspberry Pi 3B (Dash web UI + PID loop) |
| `tests/` | pytest unit tests |
| `config/` | YAML configuration (defaults + per-host calibration) |
| `docs/` | API and architecture documentation (see `docs/INDEX.md`) |
| `deploy/` | systemd unit and deployment scripts |

## Python development

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
```

## Firmware

Open `firmware/hccd/hccd.ino` in Arduino IDE, select board "Arduino Uno"
(ATmega328P, 16 MHz), compile, upload to the HCCD board.

## Documentation

Start from [`docs/INDEX.md`](docs/INDEX.md). Every module and class has a
corresponding page under `docs/api/`. Pages are kept in sync with the
code — if a public symbol changes, the matching doc page must be updated
in the same commit.

## Licence

AGPL-3.0 — see [`LICENSE`](LICENSE).
