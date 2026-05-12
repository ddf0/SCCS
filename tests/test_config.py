"""Tests for the config loader."""

from __future__ import annotations

import pytest

from sccs.config import load_config


_GOOD_YAML = """
i2c:
  bus: 1
  hccd_address: 0x10
  magnetometer_address: 0x30
pid:
  kp: 0.05
  ki: 0.02
  kd: 0.001
  dt_ms: 10
  current_limit_a: 2.8
control:
  loop_period_ms: 10
  max_consecutive_errors: 5
web:
  host: "0.0.0.0"
  port: 8080
  update_interval_ms: 200
"""


def _write_config(tmp_path, content: str):
    path = tmp_path / "cfg.yaml"
    path.write_text(content)
    return path


def test_load_valid_config(tmp_path):
    cfg = load_config(_write_config(tmp_path, _GOOD_YAML))
    assert cfg.i2c.hccd_address == 0x10
    assert cfg.pid.kp == 0.05
    assert cfg.control.loop_period_ms == 10
    assert cfg.web.port == 8080


def test_loads_shipping_default():
    cfg = load_config("config/default.yaml")
    assert cfg.web.port == 8080


def test_rejects_invalid_address(tmp_path):
    bad = _GOOD_YAML.replace("hccd_address: 0x10", "hccd_address: 0x01")
    with pytest.raises(Exception):
        load_config(_write_config(tmp_path, bad))


def test_rejects_negative_gain(tmp_path):
    bad = _GOOD_YAML.replace("kp: 0.05", "kp: -0.1")
    with pytest.raises(Exception):
        load_config(_write_config(tmp_path, bad))


def test_rejects_zero_period(tmp_path):
    bad = _GOOD_YAML.replace("dt_ms: 10", "dt_ms: 0")
    with pytest.raises(Exception):
        load_config(_write_config(tmp_path, bad))
