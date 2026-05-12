"""Tests for HCCDClient — verifies that the right bytes leave the bus."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from sccs.drivers.hccd import (
    HCCDClient,
    I_MAX,
    amps_to_code,
    code_to_amps,
)
from sccs.protocol import (
    CMD_RESET_ESTOP,
    CMD_WRITE_SETPOINT,
    DAC_MAX_CODE,
    DAC_MID_CODE,
    HCCD_I2C_ADDRESS,
    crc8_sae_j1850,
)


@pytest.fixture
def mock_bus():
    return MagicMock()


# -- amps_to_code / code_to_amps ------------------------------------- #


def test_amps_to_code_zero_is_mid():
    assert amps_to_code(0.0) == DAC_MID_CODE


def test_amps_to_code_max_positive():
    assert amps_to_code(I_MAX) == DAC_MAX_CODE


def test_amps_to_code_max_negative():
    assert amps_to_code(-I_MAX) == 0


def test_amps_to_code_clips_overshoot():
    assert amps_to_code(I_MAX * 5) == DAC_MAX_CODE
    assert amps_to_code(-I_MAX * 5) == 0


def test_code_to_amps_round_trip_at_zero():
    assert code_to_amps(DAC_MID_CODE) == pytest.approx(0.0)


def test_code_to_amps_at_extremes_within_half_lsb():
    # The bipolar mapping has 4095 = DAC_MAX_CODE -> 3.0 A, but
    # CURRENT_TO_DAC = 4095 / (2 * 3) = 682.5 leaves a half-LSB
    # asymmetry at the extremes (the negative side has 2048 codes,
    # the positive only 2047). Half an LSB is ~7 mA — well below
    # the noise floor of the analogue chain.
    half_lsb_A = 1.0 / (2 * 682.5)
    assert code_to_amps(DAC_MAX_CODE) == pytest.approx(I_MAX, abs=half_lsb_A)
    assert code_to_amps(0) == pytest.approx(-I_MAX, abs=half_lsb_A)


# -- set_currents ---------------------------------------------------- #


def test_set_currents_sends_three_packets(mock_bus):
    client = HCCDClient(bus=mock_bus)
    client.set_currents(0.0, 0.0, 0.0)
    assert mock_bus.write_i2c_block_data.call_count == 3


def test_set_currents_uses_correct_address(mock_bus):
    client = HCCDClient(bus=mock_bus)
    client.set_currents(0.0, 0.0, 0.0)
    for call in mock_bus.write_i2c_block_data.call_args_list:
        assert call.args[0] == HCCD_I2C_ADDRESS


def test_set_currents_layout_and_crc(mock_bus):
    client = HCCDClient(bus=mock_bus)
    client.set_currents(0.0, 0.0, 0.0)
    for ch_idx, call in enumerate(mock_bus.write_i2c_block_data.call_args_list):
        _addr, register, data = call.args
        assert register == CMD_WRITE_SETPOINT
        assert len(data) == 5
        assert data[0] == ch_idx
        payload = bytes([register, *data[:4]])
        assert crc8_sae_j1850(payload) == data[4]


def test_set_currents_zero_maps_to_mid_code(mock_bus):
    client = HCCDClient(bus=mock_bus)
    client.set_currents(0.0, 0.0, 0.0)
    first_data = mock_bus.write_i2c_block_data.call_args_list[0].args[2]
    code = first_data[1] | ((first_data[2] & 0x0F) << 8)
    assert code == DAC_MID_CODE


def test_set_currents_clips_to_imax(mock_bus):
    client = HCCDClient(bus=mock_bus)
    client.set_currents(100.0, -100.0, 0.0)
    calls = mock_bus.write_i2c_block_data.call_args_list

    code_x = calls[0].args[2][1] | ((calls[0].args[2][2] & 0x0F) << 8)
    code_y = calls[1].args[2][1] | ((calls[1].args[2][2] & 0x0F) << 8)
    assert code_x == DAC_MAX_CODE
    assert code_y == 0


# -- reset_estop ----------------------------------------------------- #


def test_reset_estop_sends_correct_packet(mock_bus):
    client = HCCDClient(bus=mock_bus)
    client.reset_estop()

    mock_bus.write_i2c_block_data.assert_called_once()
    addr, register, data = mock_bus.write_i2c_block_data.call_args.args
    assert addr == HCCD_I2C_ADDRESS
    assert register == CMD_RESET_ESTOP
    assert data[:4] == [0, 0, 0, 0]
    payload = bytes([register, *data[:4]])
    assert crc8_sae_j1850(payload) == data[4]


# -- read_temperatures (deferred) ------------------------------------ #


def test_read_temperatures_raises_until_firmware_ready(mock_bus):
    client = HCCDClient(bus=mock_bus)
    with pytest.raises(NotImplementedError):
        client.read_temperatures()
