"""Reusable Dash component builders.

These functions return component trees (`dcc`/`html`) and never touch
state directly — the controller wires them up in
:mod:`sccs.web.server` and :mod:`sccs.web.callbacks`.
"""

from __future__ import annotations

from dash import dcc, html


def telemetry_card() -> html.Div:
    return html.Div(
        [
            html.H3("Magnetic field (µT)"),
            dcc.Graph(id="graph-bx", config={"displayModeBar": False}),
            dcc.Graph(id="graph-by", config={"displayModeBar": False}),
            dcc.Graph(id="graph-bz", config={"displayModeBar": False}),
        ],
        style={"flex": "2", "minWidth": "0"},
    )


def control_panel() -> html.Div:
    return html.Div(
        [
            html.H3("Controller"),
            html.Label("Kp"),
            dcc.Slider(
                id="slider-kp",
                min=0.0,
                max=0.5,
                step=0.001,
                value=0.05,
                tooltip={"placement": "bottom", "always_visible": False},
            ),
            html.Label("Ki"),
            dcc.Slider(
                id="slider-ki",
                min=0.0,
                max=0.5,
                step=0.001,
                value=0.02,
            ),
            html.Label("Kd"),
            dcc.Slider(
                id="slider-kd",
                min=0.0,
                max=0.05,
                step=0.0001,
                value=0.001,
            ),
            html.Div(
                [
                    html.Button("Start", id="btn-start", n_clicks=0),
                    html.Button("Stop", id="btn-stop", n_clicks=0),
                    html.Button(
                        "Emergency Stop",
                        id="btn-estop",
                        n_clicks=0,
                        style={
                            "backgroundColor": "#d32f2f",
                            "color": "white",
                            "fontWeight": "bold",
                            "marginLeft": "1em",
                        },
                    ),
                ],
                style={"marginTop": "1em"},
            ),
            html.Div(id="status-indicator", style={"marginTop": "1em"}),
            html.Div(id="temperatures-indicator"),
        ],
        style={"flex": "1", "padding": "1em", "borderLeft": "1px solid #ccc"},
    )
