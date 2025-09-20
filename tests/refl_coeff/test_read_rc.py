import pytest
import bellhop as bh
import numpy as np
import pandas as pd
import os

def test_read_rc():
    """Test reading .brc file"""
    brc_file = "tests/refl_coeff/example.brc"

    if not os.path.exists(brc_file):
        pytest.skip(f"Test file not found: {brc_file}")

    brc = bh.read_refl_coeff(brc_file)

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

def test_write_rc():
    """Test round-tripping .brc file"""

    env = bh.create_env2d()
    brc1 = bh.read_refl_coeff("tests/refl_coeff/example.brc")
    env["bottom_reflection_coefficient"] = brc1

    arr = bh.compute_arrivals(env,debug=True,fname_base="tests/refl_coeff/test_debug")

    brc2 = bh.read_refl_coeff("tests/refl_coeff/test_debug.brc")

    np.testing.assert_array_equal(brc1, brc2)
