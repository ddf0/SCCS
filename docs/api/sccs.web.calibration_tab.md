# `sccs.web.calibration_tab`

Defined in [`src/sccs/web/calibration_tab.py`](../../src/sccs/web/calibration_tab.py).

## `layout() -> html.Div`

Calibration-tab content: instruction paragraph, four buttons (Start
sampling, Stop sampling, Fit ellipsoid, Save to `calibration.yaml`),
a `Scatter3d` plot of the collected raw samples, and a `<pre>` block
that displays the fit result.

## `empty_scatter() -> go.Figure` / `make_scatter(samples) -> go.Figure`

Builders for the 3-D cloud plot. `empty_scatter()` shows axes but no
data; `make_scatter(samples)` accepts an `(N, 3)` array.

## Wiring (deferred)

The buttons are present in the layout, but the data-collection logic
is **deferred to hardware bring-up**. The control thread will gain a
calibration mode that drops raw magnetometer readings into a shared
buffer; for now, clicking the buttons fires no-op callbacks. Tests
verify only that the layout constructs cleanly.
