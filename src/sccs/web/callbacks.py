"""Dash callbacks.

Telemetry callbacks read the lock-protected ``SharedState`` directly.
User-driven callbacks (buttons, sliders) push command dicts into a
``queue.Queue`` that the control thread (or the main loop) drains.
"""

from __future__ import annotations

import collections
import time
from dataclasses import dataclass, field
from typing import Any

import plotly.graph_objects as go
from dash import Input, Output, callback_context, dcc, no_update

from sccs.web.profile_tab import empty_map


@dataclass
class TelemetryBuffer:
    maxlen: int = 300
    t: collections.deque = field(init=False)
    bx_set: collections.deque = field(init=False)
    bx_meas: collections.deque = field(init=False)
    by_set: collections.deque = field(init=False)
    by_meas: collections.deque = field(init=False)
    bz_set: collections.deque = field(init=False)
    bz_meas: collections.deque = field(init=False)

    def __post_init__(self) -> None:
        for name in ("t", "bx_set", "bx_meas", "by_set", "by_meas", "bz_set", "bz_meas"):
            setattr(self, name, collections.deque(maxlen=self.maxlen))


def _line_figure(t, set_arr, meas_arr, axis_name: str) -> go.Figure:
    return go.Figure(
        data=[
            go.Scatter(x=list(t), y=list(set_arr), name="target", mode="lines"),
            go.Scatter(x=list(t), y=list(meas_arr), name="measured", mode="lines"),
        ],
        layout=go.Layout(
            title=f"B_{axis_name} (µT)",
            height=220,
            margin=dict(l=40, r=10, t=30, b=30),
            xaxis=dict(title="t, s"),
        ),
    )


def register_callbacks(app: Any) -> None:
    """Attach all callbacks to ``app``. Must be called once after the layout is set."""
    buffer = TelemetryBuffer()
    t_start = time.monotonic()

    @app.callback(
        Output("graph-bx", "figure"),
        Output("graph-by", "figure"),
        Output("graph-bz", "figure"),
        Output("status-indicator", "children"),
        Output("temperatures-indicator", "children"),
        Input("telemetry-interval", "n_intervals"),
    )
    def _update_telemetry(_n_intervals):
        state = app.shared_state
        with state.lock:
            target = state.b_target_uT.copy()
            measured = state.b_measured_uT.copy()
            temps = state.temps_C.copy()
            status = state.status

        ts = time.monotonic() - t_start
        buffer.t.append(ts)
        buffer.bx_set.append(float(target[0]))
        buffer.bx_meas.append(float(measured[0]))
        buffer.by_set.append(float(target[1]))
        buffer.by_meas.append(float(measured[1]))
        buffer.bz_set.append(float(target[2]))
        buffer.bz_meas.append(float(measured[2]))

        temp_txt = f"Temps °C: X={temps[0]:.1f}  Y={temps[1]:.1f}  Z={temps[2]:.1f}"
        return (
            _line_figure(buffer.t, buffer.bx_set, buffer.bx_meas, "x"),
            _line_figure(buffer.t, buffer.by_set, buffer.by_meas, "y"),
            _line_figure(buffer.t, buffer.bz_set, buffer.bz_meas, "z"),
            f"Status: {status}",
            temp_txt,
        )

    @app.callback(
        Output("slider-kp", "value", allow_duplicate=True),
        Input("slider-kp", "value"),
        Input("slider-ki", "value"),
        Input("slider-kd", "value"),
        prevent_initial_call=True,
    )
    def _push_gains(kp, ki, kd):
        app.command_queue.put({"cmd": "set_gains", "values": (kp, ki, kd)})
        return no_update

    @app.callback(
        Output("status-indicator", "children", allow_duplicate=True),
        Input("btn-start", "n_clicks"),
        Input("btn-stop", "n_clicks"),
        Input("btn-estop", "n_clicks"),
        prevent_initial_call=True,
    )
    def _buttons(_n_start, _n_stop, _n_estop):
        triggered = callback_context.triggered_id
        if triggered is None:
            return no_update
        app.command_queue.put({"cmd": triggered})
        return f"Last action: {triggered}"

    @app.callback(
        Output("profile-form", "children"),
        Input("profile-type", "value"),
    )
    def _profile_form(kind):
        if kind == "fixed":
            return [
                dcc.Input(id="lat", type="number", placeholder="latitude", value=55.75),
                dcc.Input(id="lon", type="number", placeholder="longitude", value=37.62),
                dcc.Input(id="alt", type="number", placeholder="altitude km", value=400.0),
            ]
        if kind == "orbital":
            return [
                dcc.Textarea(
                    id="tle",
                    placeholder="Three-line TLE (name + line1 + line2)",
                    style={"width": "100%", "height": "5em"},
                ),
                dcc.Input(id="time-scale", type="number", value=1.0, min=0.1),
            ]
        return [dcc.Upload(id="csv-upload", children=html.Div("Drop CSV here"))]

    @app.callback(
        Output("map-groundtrack", "figure"),
        Output("profile-load-feedback", "children"),
        Input("btn-load-profile", "n_clicks"),
        prevent_initial_call=True,
    )
    def _load_profile(_n):
        # Loading is handled by the control thread; here we only render
        # the visualisation if the queued profile metadata says it has a
        # groundtrack to show. For now we just send the command and let
        # the control thread answer back via SharedState.
        app.command_queue.put({"cmd": "load_profile"})
        return empty_map(), "Load command queued."


# Local import to avoid circulars in the module-level namespace.
from dash import html  # noqa: E402
