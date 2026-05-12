"""Sanity check that the package imports."""

import sccs


def test_package_version():
    assert sccs.__version__ == "0.1.0"
