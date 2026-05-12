"""Calibration-tab layout and helpers."""

from __future__ import annotations

import plotly.graph_objects as go
from dash import dcc, html


def layout() -> html.Div:
    return html.Div(
        [
            html.H3("Magnetometer calibration"),
            html.P(
                "Rotate the sensor through as many orientations as possible "
                "in a stable external field, then click Fit. Aim for "
                "≥ 500 samples for a stable result."
            ),
            html.Button("Start sampling", id="btn-calib-start", n_clicks=0),
            html.Button(
                "Stop sampling",
                id="btn-calib-stop",
                n_clicks=0,
                style={"marginLeft": "0.5em"},
            ),
            html.Button(
                "Fit ellipsoid",
                id="btn-calib-fit",
                n_clicks=0,
                style={"marginLeft": "0.5em"},
            ),
            html.Button(
                "Save to calibration.yaml",
                id="btn-calib-save",
                n_clicks=0,
                style={"marginLeft": "0.5em"},
            ),
            html.Div(id="calib-status", style={"marginTop": "1em"}),
            dcc.Graph(id="calib-cloud", figure=empty_scatter()),
            html.Pre(
                id="calib-result",
                style={"backgroundColor": "#f5f5f5", "padding": "0.5em"},
            ),
        ]
    )


def empty_scatter() -> go.Figure:
    return go.Figure(
        data=[go.Scatter3d(x=[], y=[], z=[], mode="markers")],
        layout=go.Layout(height=500, margin=dict(l=0, r=0, t=10, b=0)),
    )


def make_scatter(samples) -> go.Figure:
    return go.Figure(
        data=[
            go.Scatter3d(
                x=samples[:, 0],
                y=samples[:, 1],
                z=samples[:, 2],
                mode="markers",
                marker=dict(size=2, color="#1976d2"),
            )
        ],
        layout=go.Layout(height=500, margin=dict(l=0, r=0, t=10, b=0)),
    )
