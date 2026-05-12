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

## Quick start (dev workstation)

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
python -m sccs.app --no-hw --validate
python -m sccs.app --no-hw                 # opens http://localhost:8080
```

## Firmware

Open `firmware/hccd/hccd.ino` in Arduino IDE 2, select **Arduino Uno**
(ATmega328P, 16 MHz), compile, upload to the HCCD board. All modules
in the same directory are picked up automatically.

## Deployment on Raspberry Pi 3B

See [`docs/deployment.md`](docs/deployment.md) for the full procedure.
Short version:

```bash
sudo git clone https://github.com/ddf0/SCCS /opt/sccs
cd /opt/sccs
sudo pip install -e . --break-system-packages
sudo cp deploy/sccs.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now sccs
```

Then open `http://sccs.local:8080` from any device on the LAN.

## Documentation

Start at [`docs/INDEX.md`](docs/INDEX.md). Every public module and
class has its own page under `docs/api/` (Python) or `docs/firmware/`
(C++). Per project convention, **a code change that touches a public
symbol is incomplete until its doc page is updated in the same commit**
— see [`docs/CONVENTIONS.md`](docs/CONVENTIONS.md).

Key reference documents:

- [`docs/architecture/overview.md`](docs/architecture/overview.md) — system overview and dataflow
- [`docs/firmware/overview.md`](docs/firmware/overview.md) — HCCD firmware modules
- [`docs/firmware/protocol.md`](docs/firmware/protocol.md) — wire protocol
- [`docs/api/sccs.web.md`](docs/api/sccs.web.md) — web UI structure
- [`docs/deployment.md`](docs/deployment.md) — production deploy

## Tests

```bash
pytest -v
```

The full suite covers the wire protocol, hardware drivers (mock-bus),
PID, shared state, control loop, calibration, profiles, config, the
CSV logger, the web app factory, and the application entry point.
The firmware modules are validated by manual upload via Arduino IDE
(hardware-in-the-loop bring-up).

## Licence

[AGPL-3.0-or-later](LICENSE).
