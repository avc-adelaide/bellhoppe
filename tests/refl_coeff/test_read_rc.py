import pytest
import bellhop as bh
import numpy as np
import pandas as pd
import os

def test_read_brc():
    """Test reading .brc file"""
    brc_file = "tests/refl_coeff/example.brc"

    if not os.path.exists(brc_file):
        pytest.skip(f"Test file not found: {brc_file}")

    brc = bh.read_brc(brc_file)

    # Should return [theta, rmag, rphase] triplets
    assert isinstance(brc, np.ndarray), "Should return numpy array"
    assert brc.ndim == 2, "Should be 2D array"
    assert brc.shape[1] == 3, "Should have 3 columns"
    assert brc.shape[0] == 3, "Should have 3 rows, as per file"

    # Check values
    assert brc[0, 0] == 00.0
    assert brc[1, 0] == 45.0
    assert brc[2, 0] == 90.0
    assert brc[0, 1] == 1.00
    assert brc[1, 1] == 0.95
    assert brc[2, 1] == 0.90
    assert brc[0, 2] == 180.0
    assert brc[1, 2] == 175.0
    assert brc[2, 2] == 170.0

def test_read_trc():
    """Test reading .trc file"""
    trc_file = "tests/refl_coeff/example.trc"

    if not os.path.exists(trc_file):
        pytest.skip(f"Test file not found: {trc_file}")

    trc = bh.read_trc(trc_file)

    # Should return [theta, rmag, rphase] triplets
    assert isinstance(trc, np.ndarray), "Should return numpy array"
    assert trc.ndim == 2, "Should be 2D array"
    assert trc.shape[1] == 3, "Should have 3 columns"
    assert trc.shape[0] == 3, "Should have 3 rows, as per file"

    # Check values
    assert trc[0, 0] == 00.0
    assert trc[1, 0] == 45.0
    assert trc[2, 0] == 90.0
    assert trc[0, 1] == 1.00
    assert trc[1, 1] == 0.95
    assert trc[2, 1] == 0.90
    assert trc[0, 2] == 180.0
    assert trc[1, 2] == 175.0
    assert trc[2, 2] == 170.0

def test_write_brc():
    """Test round-tripping .brc file"""

    env = bh.create_env()
    brc1 = bh.read_brc("tests/refl_coeff/example.brc")
    env["bottom_reflection_coefficient"] = brc1

    arr = bh.compute_arrivals(env,debug=True,fname_base="tests/refl_coeff/brc_debug")
    brc2 = bh.read_brc("tests/refl_coeff/brc_debug.brc")

    np.testing.assert_array_equal(brc1, brc2)


def test_write_trc():
    """Test round-tripping .trc file"""

    env = bh.create_env()
    trc1 = bh.read_trc("tests/refl_coeff/example.trc")
    env["surface_reflection_coefficient"] = trc1

    arr = bh.compute_arrivals(env,debug=True,fname_base="tests/refl_coeff/trc_debug")
    trc2 = bh.read_trc("tests/refl_coeff/trc_debug.trc")

    np.testing.assert_array_equal(trc1, trc2)
