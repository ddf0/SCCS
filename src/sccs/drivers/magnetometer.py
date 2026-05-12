"""MMC5983MA driver — three-axis magnetometer over I²C.

Designed for the SET/RESET cycle that eliminates offset drift:
``B_true = (B_set - B_reset) / 2``. Calibration is an affine map
``M @ (raw - offset)`` applied to the output of every read; defaults
to identity until :meth:`MMC5983Driver.load_calibration` is called.
"""

from __future__ import annotations

import time

import numpy as np

from sccs.drivers.hccd import BusLike

MMC5983_ADDRESS = 0x30

# Register map (subset).
REG_OUT_BASE = 0x00  # Output bytes start here (XL, XH, YL, YH, ZL, ZH, XYZ2)
REG_STATUS = 0x08
REG_CTRL_0 = 0x09
REG_CTRL_1 = 0x0A
REG_CTRL_2 = 0x0B
REG_PRODUCT_ID = 0x2F

# CTRL_0 bits.
BIT_TM_M = 1 << 0  # Trigger one magnetic measurement.
BIT_SET = 1 << 3  # SET pulse.
BIT_RESET = 1 << 4  # RESET pulse.

# Sensitivity for the 18-bit output: 1 LSB = 0.0625 mG, span centred at 2**17.
COUNTS_TO_MILLIGAUSS = 0.0625
COUNTS_MID = 1 << 17
MILLIGAUSS_TO_MICROTESLA = 0.1  # 1 mG = 0.1 µT

# Measurement durations (see datasheet table for output bandwidth).
SET_RESET_PULSE_S = 0.001
MEASUREMENT_DELAY_S = 0.008  # 8 ms at BW = 100 Hz

# Bandwidth control bits (CTRL_1 lower two bits).
BW_BITS = {100: 0b00, 200: 0b01, 400: 0b10, 800: 0b11}


class MMC5983Driver:
    """Driver for the MEMSIC MMC5983MA over I²C.

    Parameters
    ----------
    bus
        smbus2-like bus object.
    address
        I²C address (default :data:`MMC5983_ADDRESS`).
    bandwidth_hz
        Output bandwidth: one of 100, 200, 400, 800 Hz.
    """

    def __init__(
        self,
        bus: BusLike,
        address: int = MMC5983_ADDRESS,
        bandwidth_hz: int = 100,
    ) -> None:
        if bandwidth_hz not in BW_BITS:
            raise ValueError(f"bandwidth_hz must be one of {sorted(BW_BITS)}")

        self._bus = bus
        self._addr = address
        self._calib_matrix = np.eye(3)
        self._calib_offset = np.zeros(3)

        self._bus.write_byte_data(self._addr, REG_CTRL_1, BW_BITS[bandwidth_hz])
        self._bus.write_byte_data(self._addr, REG_CTRL_2, 0x00)  # one-shot mode

    # -- public API --------------------------------------------------- #

    def load_calibration(self, matrix: np.ndarray, offset: np.ndarray) -> None:
        """Install an affine calibration: ``B = M @ (raw - offset)``."""
        matrix = np.asarray(matrix, dtype=float)
        offset = np.asarray(offset, dtype=float)
        if matrix.shape != (3, 3):
            raise ValueError("matrix must be (3, 3)")
        if offset.shape != (3,):
            raise ValueError("offset must be (3,)")
        self._calib_matrix = matrix
        self._calib_offset = offset

    def read_raw(self) -> np.ndarray:
        """Single measurement without SET/RESET (use for calibration sweeps)."""
        counts = self._trigger_and_read() - COUNTS_MID
        return counts * COUNTS_TO_MILLIGAUSS * MILLIGAUSS_TO_MICROTESLA

    def read_field_uT(self) -> np.ndarray:
        """Full SET/RESET-corrected measurement with calibration applied."""
        self._bus.write_byte_data(self._addr, REG_CTRL_0, BIT_SET)
        time.sleep(SET_RESET_PULSE_S)
        meas_set = self._trigger_and_read()

        self._bus.write_byte_data(self._addr, REG_CTRL_0, BIT_RESET)
        time.sleep(SET_RESET_PULSE_S)
        meas_reset = self._trigger_and_read()

        counts = (meas_set.astype(float) - meas_reset.astype(float)) / 2.0
        b_raw = counts * COUNTS_TO_MILLIGAUSS * MILLIGAUSS_TO_MICROTESLA
        return self._calib_matrix @ (b_raw - self._calib_offset)

    # -- internals ---------------------------------------------------- #

    def _trigger_and_read(self) -> np.ndarray:
        """Trigger a single measurement and return raw 18-bit counts (3,)."""
        self._bus.write_byte_data(self._addr, REG_CTRL_0, BIT_TM_M)
        time.sleep(MEASUREMENT_DELAY_S)

        block = self._bus.read_i2c_block_data(self._addr, REG_OUT_BASE, 7)
        # Bytes: XH XL YH YL ZH ZL XYZ2.
        # XYZ2 bits 7:6 -> X[1:0], 5:4 -> Y[1:0], 3:2 -> Z[1:0].
        xyz2 = block[6]
        x = (block[0] << 10) | (block[1] << 2) | ((xyz2 >> 6) & 0x03)
        y = (block[2] << 10) | (block[3] << 2) | ((xyz2 >> 4) & 0x03)
        z = (block[4] << 10) | (block[5] << 2) | ((xyz2 >> 2) & 0x03)
        return np.array([x, y, z], dtype=np.int64)
