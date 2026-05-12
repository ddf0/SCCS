"""Smoke tests for the Dash web app.

The server is never actually started — we only verify the factory
constructs a valid layout and registers callbacks without errors.
"""

from __future__ import annotations

import queue

from sccs.control.state import SharedState
from sccs.web.server import create_app


def test_create_app_returns_dash_instance():
    state = SharedState()
    cmd_q: queue.Queue = queue.Queue()
    app = create_app(state, cmd_q)
    assert app is not None
    assert app.layout is not None
    # Dependencies wired correctly.
    assert app.shared_state is state
    assert app.command_queue is cmd_q


def test_layout_contains_expected_tabs():
    app = create_app(SharedState(), queue.Queue())
    layout_str = str(app.layout)
    for label in ("Control", "Profile", "Calibration"):
        assert label in layout_str


def test_layout_has_required_callback_targets():
    app = create_app(SharedState(), queue.Queue())
    layout_str = str(app.layout)
    for target_id in (
        "graph-bx",
        "graph-by",
        "graph-bz",
        "slider-kp",
        "slider-ki",
        "slider-kd",
        "btn-start",
        "btn-stop",
        "btn-estop",
        "telemetry-interval",
        "profile-type",
        "map-groundtrack",
    ):
        assert target_id in layout_str, f"missing id={target_id!r}"
