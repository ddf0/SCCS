"""Dash app factory.

The factory takes the shared state object and the command queue that
connect the web UI to the control thread. The factory does **not**
start the server; that is the caller's responsibility (typically
``app.run(...)`` from :mod:`sccs.app`).
"""

from __future__ import annotations

import queue
from typing import Any

import dash
from dash import dcc, html

from sccs.control.state import SharedState
from sccs.web.calibration_tab import layout as calibration_layout
from sccs.web.callbacks import register_callbacks
from sccs.web.components import control_panel, telemetry_card
from sccs.web.profile_tab import layout as profile_layout


def create_app(state: SharedState, command_queue: "queue.Queue[Any]") -> dash.Dash:
    """Build the Dash application and wire it to ``state`` / ``command_queue``."""
    app = dash.Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div(
        [
            html.H1("SCCS — Helmholtz Coil Control"),
            dcc.Tabs(
                id="tabs",
                value="tab-control",
                children=[
                    dcc.Tab(
                        label="Control",
                        value="tab-control",
                        children=html.Div(
                            [telemetry_card(), control_panel()],
                            style={"display": "flex", "gap": "2em"},
                        ),
                    ),
                    dcc.Tab(label="Profile", value="tab-profile", children=profile_layout()),
                    dcc.Tab(
                        label="Calibration",
                        value="tab-calibration",
                        children=calibration_layout(),
                    ),
                ],
            ),
            dcc.Interval(id="telemetry-interval", interval=200),  # ms
            dcc.Store(id="store-state"),
        ]
    )
    # Stash dependencies on the app so callbacks can reach them.
    app.shared_state = state
    app.command_queue = command_queue
    register_callbacks(app)
    return app
