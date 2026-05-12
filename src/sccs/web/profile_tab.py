"""Profile-tab layout and helpers."""

from __future__ import annotations

import plotly.graph_objects as go
from dash import dcc, html


def layout() -> html.Div:
    return html.Div(
        [
            html.H3("Profile source"),
            dcc.RadioItems(
                id="profile-type",
                options=[
                    {"label": "Fixed point (IGRF)", "value": "fixed"},
                    {"label": "Orbital (TLE + IGRF)", "value": "orbital"},
                    {"label": "CSV replay", "value": "csv"},
                ],
                value="fixed",
            ),
            html.Div(id="profile-form", style={"marginTop": "1em"}),
            html.Button("Load profile", id="btn-load-profile", n_clicks=0),
            html.Div(id="profile-load-feedback", style={"marginTop": "0.5em"}),
            dcc.Graph(id="map-groundtrack", figure=empty_map()),
        ]
    )


def empty_map() -> go.Figure:
    return go.Figure(
        data=[go.Scattergeo(lat=[], lon=[], mode="markers")],
        layout=go.Layout(
            geo=dict(
                projection_type="orthographic",
                showland=True,
                landcolor="#dfe8d0",
                showocean=True,
                oceancolor="#a8c2e2",
                showcountries=True,
                countrycolor="#888",
            ),
            height=500,
            margin=dict(l=0, r=0, t=10, b=0),
        ),
    )


def make_map(track: list[tuple[float, float, float]]) -> go.Figure:
    lats = [pt[0] for pt in track]
    lons = [pt[1] for pt in track]
    return go.Figure(
        data=[
            go.Scattergeo(
                lat=lats,
                lon=lons,
                mode="lines+markers",
                marker=dict(size=4, color="#1976d2"),
                line=dict(color="#1976d2", width=2),
                name="ground track",
            )
        ],
        layout=go.Layout(
            geo=dict(
                projection_type="orthographic",
                showland=True,
                landcolor="#dfe8d0",
                showocean=True,
                oceancolor="#a8c2e2",
                showcountries=True,
                countrycolor="#888",
            ),
            height=500,
            margin=dict(l=0, r=0, t=10, b=0),
        ),
    )
