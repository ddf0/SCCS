# `sccs.web.profile_tab`

Defined in [`src/sccs/web/profile_tab.py`](../../src/sccs/web/profile_tab.py).

## `layout() -> html.Div`

Profile-tab content: a radio group choosing one of *fixed*,
*orbital*, *csv*; a dynamic form rendered by the
`_profile_form` callback; a Load button; and a `dcc.Graph` for the
ground-track map.

## `empty_map() -> go.Figure`

A blank `Scattergeo` figure with the orthographic projection turned
on. Used as the initial value of `map-groundtrack` so the tab is
populated immediately on load.

## `make_map(track: list[(lat, lon, alt_km)]) -> go.Figure`

Renders a ground track as a polyline of subpoints. The plot uses the
orthographic projection (looks like a 3-D globe) — no external map
tiles, no API token needed.
