"""SCCS daemon entry point.

Wires together the config, drivers, control loop, logger, and Dash web
server. On Raspberry Pi this runs as the `sccs.service` systemd unit.

Use ``--no-hw`` for off-Pi development — drivers are replaced with
``unittest.mock.MagicMock`` so the rest of the pipeline still runs.
``--validate`` exits after construction without starting Dash; useful
for smoke tests and CI.
"""

from __future__ import annotations

import argparse
import os
import queue
import signal
import sys
from pathlib import Path
from typing import Any

import numpy as np

from sccs.config import SCCSConfig, load_config
from sccs.control.loop import ControlLoop
from sccs.control.pid import PIDController
from sccs.control.state import SharedState
from sccs.logging_csv import CSVLogger
from sccs.profile.fixed import FixedPointProfile
from sccs.web.server import create_app

try:
    import smbus2  # noqa: F401

    HAS_SMBUS = True
except ImportError:  # pragma: no cover - depends on host
    HAS_SMBUS = False


def _open_drivers(cfg: SCCSConfig, no_hw: bool):
    """Return ``(hccd, magnetometer)``, choosing real bus or mocks."""
    if no_hw or not HAS_SMBUS:
        from unittest.mock import MagicMock

        hccd = MagicMock()
        hccd.read_temperatures.side_effect = NotImplementedError
        mag = MagicMock()
        mag.read_field_uT.return_value = np.zeros(3)
        return hccd, mag

    import smbus2 as sm

    from sccs.drivers.hccd import HCCDClient
    from sccs.drivers.magnetometer import MMC5983Driver

    bus = sm.SMBus(cfg.i2c.bus)
    hccd = HCCDClient(bus=bus, address=cfg.i2c.hccd_address)
    mag = MMC5983Driver(bus=bus, address=cfg.i2c.magnetometer_address)
    return hccd, mag


def _try_set_rt_priority() -> None:
    """Best-effort SCHED_FIFO. Silently fall back to normal scheduling."""
    try:
        os.sched_setscheduler(0, os.SCHED_FIFO, os.sched_param(50))  # type: ignore[attr-defined]
    except (PermissionError, OSError, AttributeError):
        pass


def build_application(
    cfg: SCCSConfig, no_hw: bool
) -> tuple[Any, SharedState, "queue.Queue[Any]", ControlLoop, CSVLogger]:
    """Construct every component but do not start servers/threads.

    Returns the Dash app, the shared state, the command queue, the
    (unstarted) control loop, and the open CSV logger.
    """
    state = SharedState()
    cmd_queue: queue.Queue = queue.Queue()

    hccd, mag = _open_drivers(cfg, no_hw)
    profile = FixedPointProfile(
        latitude_deg=55.75,
        longitude_deg=37.62,
        altitude_km=400.0,
        date_str="2026-05-12",
    )

    dt = cfg.pid.dt_ms / 1000.0
    pids = [
        PIDController(
            kp=cfg.pid.kp,
            ki=cfg.pid.ki,
            kd=cfg.pid.kd,
            dt=dt,
            output_limits=(-cfg.pid.current_limit_a, cfg.pid.current_limit_a),
        )
        for _ in range(3)
    ]
    logger = CSVLogger(out_dir=Path("logs"), decimation=5)
    loop = ControlLoop(
        hccd=hccd,
        magnetometer=mag,
        profile=profile,
        pids=pids,
        state=state,
        period_s=dt,
        logger=logger,
        max_errors=cfg.control.max_consecutive_errors,
    )

    app = create_app(state, cmd_queue)
    return app, state, cmd_queue, loop, logger


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SCCS control daemon")
    parser.add_argument(
        "--config", type=Path, default=Path("config/default.yaml"), help="YAML config path"
    )
    parser.add_argument("--no-hw", action="store_true", help="run with mock drivers")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="construct everything and exit (no server, no control thread)",
    )
    args = parser.parse_args(argv)

    cfg = load_config(args.config)

    if args.validate:
        app, state, cmd_queue, loop, logger = build_application(cfg, no_hw=True)
        logger.close()
        print("OK — configuration valid, components constructed")
        return 0

    app, state, cmd_queue, loop, logger = build_application(cfg, no_hw=args.no_hw)
    _try_set_rt_priority()
    loop.start()

    def _shutdown(_signum, _frame):
        loop.stop()
        loop.join(timeout=2.0)
        logger.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    try:
        app.run(host=cfg.web.host, port=cfg.web.port, debug=False)
    finally:
        loop.stop()
        loop.join(timeout=2.0)
        logger.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
