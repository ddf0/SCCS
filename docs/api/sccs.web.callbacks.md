# `sccs.web.callbacks`

Defined in [`src/sccs/web/callbacks.py`](../../src/sccs/web/callbacks.py).

## `register_callbacks(app: dash.Dash) -> None`

Attaches all callbacks to `app`. Must run once **after** the layout is
set, and **once** per app — calling twice will raise duplicate
callback errors.

## Callbacks registered

| Trigger | Outputs | Effect |
| --- | --- | --- |
| `telemetry-interval` (every 200 ms) | three graphs + status + temperatures text | Reads `SharedState` under its RLock, appends to a rolling deque, redraws. |
| `slider-kp/ki/kd` change | (queue side-effect) | Pushes `{"cmd": "set_gains", "values": (kp, ki, kd)}` into `command_queue`. |
| `btn-start`, `btn-stop`, `btn-estop` click | `status-indicator` text | Pushes `{"cmd": "<button-id>"}` into the queue and shows the last action. |
| `profile-type` change | `profile-form` children | Renders the form fields for the selected profile kind. |
| `btn-load-profile` click | `map-groundtrack` figure + load feedback | Pushes `{"cmd": "load_profile"}`; the map is updated by the control thread later via `SharedState`. |

## `class TelemetryBuffer`

Wraps six `collections.deque(maxlen=300)` time series (3 axes ×
target/measured) plus the time axis. The buffer is local to the
callback closure — one per `register_callbacks` call.
