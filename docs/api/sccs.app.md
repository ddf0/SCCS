# `sccs.app`

Defined in [`src/sccs/app.py`](../../src/sccs/app.py).

The daemon entry point. Wires together config, drivers, control loop,
logger, and Dash server.

## Command-line interface

```
python -m sccs.app [--config PATH] [--no-hw] [--validate]
```

| Flag | Effect |
| --- | --- |
| `--config` | YAML config path (default `config/default.yaml`). |
| `--no-hw` | Replace I²C drivers with `unittest.mock.MagicMock` for off-Pi development. Auto-enabled if `smbus2` cannot be imported. |
| `--validate` | Construct all components and exit zero. Used by CI and smoke tests. |

## Functions

### `build_application(cfg, no_hw) -> (app, state, queue, loop, logger)`

Pure wiring — returns the constructed (but **not started**) parts so
tests can inspect them. The control loop is not started until
`main()` calls `loop.start()`.

### `main(argv=None) -> int`

Standard entry point. Sets up signal handlers for SIGINT/SIGTERM that
stop the control loop, join the thread, and close the logger before
exiting.

### `_open_drivers(cfg, no_hw)`

Returns `(HCCDClient, MMC5983Driver)` against a real `smbus2.SMBus`,
or `(MagicMock, MagicMock)` when `no_hw=True` / smbus2 missing. The
mock magnetometer returns `np.zeros(3)`, the mock HCCD swallows
`set_currents` calls and raises `NotImplementedError` from
`read_temperatures` (matching the real driver until the firmware
`Wire.onRequest` handler lands).

### `_try_set_rt_priority()`

Best-effort `SCHED_FIFO` priority 50. Silently degrades to normal
scheduling when `CAP_SYS_NICE` is missing — typical on dev machines.

## Default profile

The daemon currently constructs a `FixedPointProfile` at Moscow
coordinates / 400 km / 2026-05-12 as the boot-time profile. The web
UI's `load_profile` command will be hooked up to swap the profile at
runtime in a follow-up change.
