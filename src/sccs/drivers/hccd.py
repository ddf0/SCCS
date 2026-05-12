"""High-level I²C client for the HCCD firmware.

Converts amperes to 12-bit DAC codes, packs the wire protocol from
:mod:`sccs.protocol`, and pushes them to the bus through a smbus2-like
interface. The bus dependency is duck-typed (see :class:`BusLike`) so
the driver can be exercised with :class:`unittest.mock.Mock` in tests.
"""

from __future__ import annotations

from typing import Protocol

from sccs.protocol import (
    CMD_RESET_ESTOP,
    CMD_WRITE_SETPOINT,
    DAC_MAX_CODE,
    DAC_MID_CODE,
    HCCD_I2C_ADDRESS,
    crc8_sae_j1850,
)

# Maximum nominal current per axis. Outputs are clipped to ±I_MAX.
I_MAX: float = 3.0

# DAC counts per ampere.
CURRENT_TO_DAC: float = DAC_MAX_CODE / (2 * I_MAX)


class BusLike(Protocol):
    """Minimal subset of ``smbus2.SMBus`` we depend on."""

    def write_i2c_block_data(
        self, addr: int, cmd: int, data: list[int]
    ) -> None:  # pragma: no cover - protocol
        ...

    def read_i2c_block_data(
        self, addr: int, cmd: int, length: int
    ) -> list[int]:  # pragma: no cover - protocol
        ...


def amps_to_code(amps: float) -> int:
    """Convert a signed current in amperes to a 12-bit DAC code.

    Zero amperes -> ``DAC_MID_CODE`` (2048). Out-of-range values are
    clipped to ``[0, DAC_MAX_CODE]``.
    """
    code = int(round(DAC_MID_CODE + amps * CURRENT_TO_DAC))
    return max(0, min(DAC_MAX_CODE, code))


def code_to_amps(code: int) -> float:
    """Inverse of :func:`amps_to_code`."""
    return (code - DAC_MID_CODE) / CURRENT_TO_DAC


class HCCDClient:
    """Send commands to the HCCD controller over I²C.

    Parameters
    ----------
    bus
        A smbus2-like bus object. The class never owns the bus; the
        caller is responsible for opening and closing it.
    address
        7-bit I²C slave address of the HCCD board (default
        :data:`HCCD_I2C_ADDRESS`).
    """

    def __init__(self, bus: BusLike, address: int = HCCD_I2C_ADDRESS) -> None:
        self._bus = bus
        self._address = address

    # -- public API --------------------------------------------------- #

    def set_currents(self, ix: float, iy: float, iz: float) -> None:
        """Send three :data:`CMD_WRITE_SETPOINT` packets, one per axis."""
        for channel, current in enumerate((ix, iy, iz)):
            self._send_setpoint(channel, current)

    def reset_estop(self) -> None:
        """Send :data:`CMD_RESET_ESTOP` to clear the firmware E-stop latch."""
        payload = bytes([CMD_RESET_ESTOP, 0, 0, 0, 0])
        data = [0, 0, 0, 0, crc8_sae_j1850(payload)]
        self._bus.write_i2c_block_data(self._address, CMD_RESET_ESTOP, data)

    def read_temperatures(self) -> tuple[float, float, float]:
        """Read three NTC temperatures from the controller (°C).

        Returns ``INT16_MIN``-derived NaN-like values if a sensor is
        flagged as faulty by the firmware. Not yet wired up on the
        firmware side — calling this raises until the firmware
        ``Wire.onRequest`` handler is added.
        """
        # The firmware response layout is defined in
        # docs/firmware/protocol.md; activation deferred to hardware
        # bring-up so we don't ship code that silently returns garbage.
        raise NotImplementedError(
            "CMD_READ_TEMPERATURES response handler not yet implemented on the firmware side"
        )

    # -- internal helpers --------------------------------------------- #

    def _send_setpoint(self, channel: int, current_A: float) -> None:
        code = amps_to_code(current_A)
        data = [
            channel,
            code & 0xFF,
            (code >> 8) & 0x0F,
            0x00,  # FLAGS reserved
        ]
        payload = bytes([CMD_WRITE_SETPOINT, *data])
        data.append(crc8_sae_j1850(payload))
        self._bus.write_i2c_block_data(self._address, CMD_WRITE_SETPOINT, data)
