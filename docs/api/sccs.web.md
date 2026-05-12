# `sccs.web` (Dash UI)

Defined in [`src/sccs/web/`](../../src/sccs/web/).

The web UI is a single Plotly Dash app served on port 8080. It runs in
the **main thread**; the control loop runs in its own daemon thread
and writes the `SharedState` object the UI reads.

## Module layout

| Module | Purpose |
| --- | --- |
| [`sccs.web.server`](sccs.web.server.md) | `create_app(state, command_queue)` — Dash factory. |
| [`sccs.web.components`](sccs.web.components.md) | Reusable layout pieces (`telemetry_card`, `control_panel`). |
| [`sccs.web.profile_tab`](sccs.web.profile_tab.md) | Profile-selection layout + Plotly `Scattergeo` map. |
| [`sccs.web.calibration_tab`](sccs.web.calibration_tab.md) | Calibration wizard layout. |
| [`sccs.web.callbacks`](sccs.web.callbacks.md) | All Dash callbacks. |

## Data-flow boundaries

The UI never imports drivers or the control loop directly. Instead:

- **Telemetry** flows UI ← `SharedState` (read-only, under `RLock`).
- **Commands** flow UI → `queue.Queue` → control thread.

This keeps the UI deterministic — callbacks never block on hardware
I/O — and the control loop never depends on Dash being healthy.
