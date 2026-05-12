# `sccs.web.components`

Defined in [`src/sccs/web/components.py`](../../src/sccs/web/components.py).

Reusable component builders for the Control tab.

| Function | Returns | Component IDs |
| --- | --- | --- |
| `telemetry_card()` | `html.Div` | `graph-bx`, `graph-by`, `graph-bz` |
| `control_panel()` | `html.Div` | `slider-kp`, `slider-ki`, `slider-kd`, `btn-start`, `btn-stop`, `btn-estop`, `status-indicator`, `temperatures-indicator` |

The functions return inert layouts only — all behaviour is in
[`sccs.web.callbacks`](sccs.web.callbacks.md).
