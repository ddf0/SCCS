"""CRC-8/SAE J1850 and 6-byte HCCD packet format.

Must stay byte-for-byte compatible with firmware/hccd/protocol.{h,cpp}.
"""

from __future__ import annotations

HCCD_I2C_ADDRESS = 0x10
PACKET_SIZE = 6

CMD_WRITE_SETPOINT = 0x01
CMD_READ_TEMPERATURES = 0x02
CMD_RESET_ESTOP = 0x03

STATUS_OK = 0x00
STATUS_OVERTEMP = 0x01
STATUS_COMM_TIMEOUT = 0x02
STATUS_ESTOP = 0x04

DAC_MAX_CODE = 4095
DAC_MID_CODE = 2048

TEMP_LIMIT_C_X100 = 8500


def crc8_sae_j1850(data: bytes) -> int:
    """CRC-8/SAE J1850 — poly=0x07, init=0xFF, no reflection, no XOR-out."""
    crc = 0xFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0x07) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc


def pack_setpoint(channel: int, code: int) -> bytes:
    """Build a 6-byte CMD_WRITE_SETPOINT packet.

    Layout: CMD | CH | DATA_LSB | DATA_MSB | FLAGS | CRC-8.
    The 12-bit `code` is split LSB-first: byte 2 = bits 0..7,
    byte 3 = bits 8..11 in the low nibble (high nibble of byte 3 is zero).
    """
    if channel not in (0, 1, 2):
        raise ValueError(f"channel must be 0..2, got {channel}")
    if not 0 <= code <= DAC_MAX_CODE:
        raise ValueError(f"code out of range: {code}")
    payload = bytes(
        [
            CMD_WRITE_SETPOINT,
            channel,
            code & 0xFF,
            (code >> 8) & 0x0F,
            0x00,
        ]
    )
    return payload + bytes([crc8_sae_j1850(payload)])


def pack_reset_estop() -> bytes:
    """Build a 6-byte CMD_RESET_ESTOP packet."""
    payload = bytes([CMD_RESET_ESTOP, 0, 0, 0, 0])
    return payload + bytes([crc8_sae_j1850(payload)])
