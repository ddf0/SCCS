"""Tests for MMC5983Driver — structural checks against a mock bus."""

from __future__ import annotations

from unittest.mock import MagicMock

import numpy as np
import pytest

from sccs.drivers.magnetometer import (
    BIT_RESET,
    BIT_SET,
    BIT_TM_M,
    MMC5983_ADDRESS,
    MMC5983Driver,
    REG_CTRL_0,
    REG_CTRL_1,
    REG_CTRL_2,
)


@pytest.fixture
def mock_bus():
    bus = MagicMock()
    # 18-bit mid-code (2**17) is encoded as XH=0x80, XL=0x00, XYZ2 low bits 0.
    bus.read_i2c_block_data.return_value = [0x80, 0x00, 0x80, 0x00, 0x80, 0x00, 0x00]
    return bus


def test_init_sets_bandwidth_and_one_shot_mode(mock_bus):
    MMC5983Driver(bus=mock_bus, bandwidth_hz=100)

    writes = {call.args[1]: call.args[2] for call in mock_bus.write_byte_data.call_args_list}
    assert REG_CTRL_1 in writes
    assert (writes[REG_CTRL_1] & 0b11) == 0b00  # 100 Hz
    assert writes[REG_CTRL_2] == 0x00


def test_init_rejects_invalid_bandwidth(mock_bus):
    with pytest.raises(ValueError):
        MMC5983Driver(bus=mock_bus, bandwidth_hz=123)


def test_default_address(mock_bus):
    MMC5983Driver(bus=mock_bus)
    assert mock_bus.write_byte_data.call_args_list[0].args[0] == MMC5983_ADDRESS


def test_read_field_triggers_set_then_reset(mock_bus):
    drv = MMC5983Driver(bus=mock_bus)
    mock_bus.reset_mock()
    drv.read_field_uT()

    ctrl0_writes = [
        call.args[2]
        for call in mock_bus.write_byte_data.call_args_list
        if call.args[1] == REG_CTRL_0
    ]
    # We expect: SET, TM_M, RESET, TM_M (two trigger cycles bracketing SET/RESET).
    assert any(c & BIT_SET for c in ctrl0_writes), "SET bit never asserted"
    assert any(c & BIT_RESET for c in ctrl0_writes), "RESET bit never asserted"
    assert sum(1 for c in ctrl0_writes if c & BIT_TM_M) == 2


def test_read_field_returns_three_axis_array(mock_bus):
    drv = MMC5983Driver(bus=mock_bus)
    result = drv.read_field_uT()
    assert isinstance(result, np.ndarray)
    assert result.shape == (3,)


def test_read_field_at_mid_code_is_zero(mock_bus):
    drv = MMC5983Driver(bus=mock_bus)
    result = drv.read_field_uT()
    np.testing.assert_allclose(result, np.zeros(3), atol=1e-9)


def test_load_calibration_applied(mock_bus):
    drv = MMC5983Driver(bus=mock_bus)
    drv.load_calibration(np.diag([2.0, 2.0, 2.0]), np.array([10.0, 10.0, 10.0]))

    out = drv.read_field_uT()
    # raw at mid-code -> 0; calibrated = 2 * (0 - 10) = -20
    np.testing.assert_allclose(out, np.array([-20.0, -20.0, -20.0]), atol=1e-9)


def test_load_calibration_validates_shapes(mock_bus):
    drv = MMC5983Driver(bus=mock_bus)
    with pytest.raises(ValueError):
        drv.load_calibration(np.eye(4), np.zeros(3))
    with pytest.raises(ValueError):
        drv.load_calibration(np.eye(3), np.zeros(4))
