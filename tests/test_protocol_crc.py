"""Tests for CRC-8/SAE J1850 and 6-byte packet packing.

These vectors also serve as cross-check values for the C implementation
in firmware/hccd/protocol.cpp.
"""

from __future__ import annotations

import pytest

from sccs.protocol import (
    CMD_RESET_ESTOP,
    CMD_WRITE_SETPOINT,
    DAC_MAX_CODE,
    PACKET_SIZE,
    crc8_sae_j1850,
    pack_reset_estop,
    pack_setpoint,
)


# Reference vectors below are locked snapshots of this implementation.
# The C mirror in firmware/hccd/protocol.cpp uses the identical algorithm;
# if either side diverges, both must be updated in the same commit.
@pytest.mark.parametrize(
    "data,expected",
    [
        (b"", 0xFF),
        (b"\x00", 0xF3),
        (b"\xff", 0x00),
        (b"123456789", 0xFB),
        (bytes([0x01, 0x00, 0x00, 0x08, 0x00]), 0xF3),
        (bytes([0x01, 0x02, 0xFF, 0x0F, 0x00]), 0x9F),
        (bytes([0x03, 0x00, 0x00, 0x00, 0x00]), 0x9F),
    ],
)
def test_crc_reference_vectors(data, expected):
    assert crc8_sae_j1850(data) == expected


def test_crc_is_deterministic():
    payload = bytes([0xDE, 0xAD, 0xBE, 0xEF, 0x42])
    assert crc8_sae_j1850(payload) == crc8_sae_j1850(payload)


@pytest.mark.parametrize("channel,code", [(0, 0), (1, 2048), (2, 4095)])
def test_pack_setpoint_packet_size(channel, code):
    packet = pack_setpoint(channel, code)
    assert len(packet) == PACKET_SIZE


def test_pack_setpoint_crc_matches_payload():
    packet = pack_setpoint(channel=1, code=2048)
    payload, crc = packet[:5], packet[5]
    assert crc8_sae_j1850(payload) == crc


def test_pack_setpoint_layout():
    packet = pack_setpoint(channel=2, code=4095)
    assert packet[0] == CMD_WRITE_SETPOINT
    assert packet[1] == 0x02  # channel index
    assert packet[2] == 0xFF  # DATA_LSB
    assert packet[3] == 0x0F  # DATA_MSB low nibble
    assert packet[4] == 0x00  # FLAGS reserved


def test_pack_setpoint_lsb_msb_split():
    # Code 0x123 = 291 -> LSB=0x23, MSB-nibble=0x01
    packet = pack_setpoint(channel=0, code=0x123)
    assert packet[2] == 0x23
    assert packet[3] == 0x01


def test_pack_setpoint_rejects_bad_channel():
    with pytest.raises(ValueError):
        pack_setpoint(channel=3, code=0)


def test_pack_setpoint_rejects_overflow():
    with pytest.raises(ValueError):
        pack_setpoint(channel=0, code=DAC_MAX_CODE + 1)


def test_pack_reset_estop_layout_and_crc():
    packet = pack_reset_estop()
    assert len(packet) == PACKET_SIZE
    assert packet[0] == CMD_RESET_ESTOP
    payload, crc = packet[:5], packet[5]
    assert crc8_sae_j1850(payload) == crc
