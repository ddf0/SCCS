"""Tests for CSVProfile."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest

from sccs.profile.csv_replay import CSVProfile


def _make_csv(rows: list[tuple[float, float, float, float]], tmp_path: Path) -> Path:
    path = tmp_path / "profile.csv"
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["t", "bx", "by", "bz"])
        writer.writerows(rows)
    return path


def test_linear_interpolation_midpoint(tmp_path):
    path = _make_csv([(0.0, 0.0, 0.0, 0.0), (1.0, 10.0, 20.0, 30.0)], tmp_path)
    prof = CSVProfile(path)
    np.testing.assert_allclose(prof.at(0.5), [5.0, 10.0, 15.0])


def test_clamps_outside_range(tmp_path):
    path = _make_csv([(0.0, 0.0, 0.0, 0.0), (1.0, 10.0, 10.0, 10.0)], tmp_path)
    prof = CSVProfile(path)
    np.testing.assert_allclose(prof.at(-1.0), [0.0, 0.0, 0.0])
    np.testing.assert_allclose(prof.at(2.0), [10.0, 10.0, 10.0])


def test_unsorted_rows_are_reordered(tmp_path):
    path = _make_csv([(2.0, 20.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (1.0, 10.0, 0.0, 0.0)], tmp_path)
    prof = CSVProfile(path)
    np.testing.assert_allclose(prof.at(0.5), [5.0, 0.0, 0.0])


def test_metadata_reports_duration_and_samples(tmp_path):
    path = _make_csv([(0.0, 0.0, 0.0, 0.0), (5.0, 0.0, 0.0, 0.0), (10.0, 0.0, 0.0, 0.0)], tmp_path)
    md = CSVProfile(path).metadata()
    assert md["type"] == "csv"
    assert md["duration_s"] == pytest.approx(10.0)
    assert md["samples"] == 3


def test_rejects_too_few_rows(tmp_path):
    path = _make_csv([(0.0, 0.0, 0.0, 0.0)], tmp_path)
    with pytest.raises(ValueError):
        CSVProfile(path)


def test_rejects_missing_columns(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("t,bx\n0,0\n1,1\n")
    with pytest.raises(ValueError):
        CSVProfile(path)
