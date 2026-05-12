# `sccs.web.server`

Defined in [`src/sccs/web/server.py`](../../src/sccs/web/server.py).

## `create_app(state: SharedState, command_queue: queue.Queue) -> dash.Dash`

Builds the Dash application:

- Three tabs: **Control**, **Profile**, **Calibration**.
- `dcc.Interval(id="telemetry-interval", interval=200)` drives the
  telemetry callback.
- Attaches `app.shared_state = state` and `app.command_queue =
  command_queue` so callbacks can reach them without globals.
- Calls `register_callbacks(app)`.

The factory does **not** start the server. The caller (`sccs.app`)
runs `app.run(host=..., port=...)`.

`suppress_callback_exceptions=True` is enabled because some component
IDs only appear under specific profile choices (the dynamic
`profile-form`).
