"""Tests for the CSV telemetry logger."""

from __future__ import annotations

import csv

import numpy as np

from sccs.control.state import SharedState
from sccs.logging_csv import CSVLogger


def _populate(state: SharedState) -> None:
    with state.lock:
        state.b_target_uT = np.array([1.0, 2.0, 3.0])
        state.b_measured_uT = np.array([0.9, 1.9, 2.9])
        state.currents_A = np.array([0.1, 0.2, 0.3])
        state.temps_C = np.array([25.0, 26.0, 27.0])
        state.status = "running"


def test_logger_writes_header_and_row(tmp_path):
    logger = CSVLogger(out_dir=tmp_path, decimation=1)
    state = SharedState()
    _populate(state)
    logger.append(state)
    logger.close()

    files = list(tmp_path.glob("sccs_*.csv"))
    assert len(files) == 1
    with files[0].open() as fh:
        rows = list(csv.reader(fh))
    assert rows[0] == list(CSVLogger.HEADER)
    assert len(rows) == 2  # header + one row
    assert rows[1][-1] == "running"


def test_decimation_drops_intermediate_rows(tmp_path):
    logger = CSVLogger(out_dir=tmp_path, decimation=3)
    state = SharedState()
    _populate(state)
    for _ in range(7):  # ticks 0, 3, 6 should write -> 3 rows + header
        logger.append(state)
    logger.close()

    files = list(tmp_path.glob("sccs_*.csv"))
    with files[0].open() as fh:
        rows = list(csv.reader(fh))
    assert len(rows) == 1 + 3  # header + 3 data rows


def test_rejects_zero_decimation(tmp_path):
    import pytest

    with pytest.raises(ValueError):
        CSVLogger(out_dir=tmp_path, decimation=0)


def test_path_property(tmp_path):
    logger = CSVLogger(out_dir=tmp_path)
    assert str(logger.path).startswith(str(tmp_path))
    assert logger.path.name.startswith("sccs_")
    logger.close()
