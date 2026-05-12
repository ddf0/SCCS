"""Smoke test for the daemon entry point."""

from __future__ import annotations

from sccs.app import main


def test_validate_mode_returns_zero():
    rc = main(["--config", "config/default.yaml", "--validate"])
    assert rc == 0
