import pytest
import bellhop as bh
import numpy as np
import pandas as pd
import os

def test_read_ssp_multi_range():
    """Test reading .ssp file with multiple ranges"""
    ssp_file = "tests/MunkB_geo_rot/MunkB_geo_rot.ssp"

    if not os.path.exists(ssp_file):
        pytest.skip(f"Test file not found: {ssp_file}")

    ssp = bh.read_ssp(ssp_file)

    # Multi-range file should return a pandas DataFrame for range-dependent modeling
    assert isinstance(ssp, pd.DataFrame), "Should return pandas DataFrame for multi-range SSP"
    assert ssp.shape[0] == 2, "Should have 2 depth points as per file"
    assert ssp.shape[1] == 30, "Should have 30 range profiles as per file"

    # Check that depths are sequential starting from 0
    expected_depths = np.array([0., 1.])
    np.testing.assert_array_equal(ssp.index.values, expected_depths)

    # Ranges should be in meters (converted from km in file)
    # Check that we have reasonable range values
    assert np.min(ssp.columns) >= -60000, "Minimum range should be reasonable"
    assert np.max(ssp.columns) <= 15000, "Maximum range should be reasonable"
    assert 0.0 in ssp.columns, "Should include range 0.0 m"

    # All sound speed values should be reasonable (around 1500-1600 m/s)
    assert np.all(ssp.values >= 1400), "Sound speeds should be >= 1400 m/s"
    assert np.all(ssp.values <= 1700), "Sound speeds should be <= 1700 m/s"

    # Should work with create_env2d for range-dependent modeling
    env = bh.create_env2d()
    env['soundspeed'] = ssp
    assert isinstance(env['soundspeed'], pd.DataFrame), "Should be compatible with create_env2d"

def test_read_ssp_single_range():
    """Test reading .ssp file with single range"""
    # Create a test file with single range
    test_file = "test_single_range.ssp"
    with open(test_file, 'w') as f:
        f.write("1\n")
        f.write("0.0\n")
        f.write("1500\n")
        f.write("1520\n")
        f.write("1540\n")

    try:
        ssp = bh.read_ssp(test_file)

        # Single-range file should return [depth, soundspeed] pairs
        assert isinstance(ssp, pd.DataFrame), "Should return Pandas DataFrame"
        assert ssp.ndim == 2, "Should be 2D array"
        assert ssp.shape[0] == 3, "Should have 3 depth points"
        assert ssp.shape[1] == 1, "Should have 1 column of data (depth is the index)"

        # Check depth values are sequential
        expected_depths = np.array([0., 1., 2.])
        np.testing.assert_array_equal(ssp.index.values, expected_depths)

        # Check sound speed values
        expected_speeds = np.array([[1500.], [1520.], [1540.]])
        np.testing.assert_array_equal(ssp.values, expected_speeds)

    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

def test_read_bty():
    """Test reading .bty file"""
    bty_file = "tests/MunkB_geo_rot/MunkB_geo_rot.bty"

    if not os.path.exists(bty_file):
        pytest.skip(f"Test file not found: {bty_file}")

    bty,interp_bty = bh.read_bty(bty_file)

    # Should return [range, depth] pairs
    assert isinstance(bty, np.ndarray), "Should return numpy array"
    assert bty.ndim == 2, "Should be 2D array"
    assert bty.shape[1] == 2, "Should have 2 columns: [range, depth]"
    assert bty.shape[0] == 30, "Should have 30 bathymetry points as per file"

    # Range should start at negative values and end positive (converted from km to m)
    assert bty[0, 0] == -50000, "First range should be -50 km = -50000 m"
    assert bty[-1, 0] == 10000, "Last range should be 10 km = 10000 m"

    # All depths should be 0 for this flat bathymetry file
    np.testing.assert_array_equal(bty[:, 1], np.zeros(30))

def test_read_bty_complex():
    """Test reading .bty file with varying depths"""
    bty_file = "examples/Dickins/DickinsB.bty"

    if not os.path.exists(bty_file):
        pytest.skip(f"Test file not found: {bty_file}")

    bty,interp_bty = bh.read_bty(bty_file)

    # Should return [range, depth] pairs
    assert isinstance(bty, np.ndarray), "Should return numpy array"
    assert bty.shape == (5, 2), "Should have 5 points with [range, depth]"

    # Range values should be converted from km to m
    assert bty[0, 0] == 0, "First range should be 0"
    assert bty[1, 0] == 10000, "Second range should be 10 km = 10000 m"
    assert bty[-1, 0] == 100000, "Last range should be 100 km = 100000 m"

    # Depths should include the shallow section at 20 km
    assert bty[2, 1] == 500, "Depth at 20 km should be 500 m"

def test_integration_with_env():
    """Test that read functions work with environment creation"""
    ssp_file = "tests/MunkB_geo_rot/MunkB_geo_rot.ssp"
    bty_file = "tests/MunkB_geo_rot/MunkB_geo_rot.bty"

    if not (os.path.exists(ssp_file) and os.path.exists(bty_file)):
        pytest.skip("Test files not found")

    # Read files
    ssp = bh.read_ssp(ssp_file)
    bty,interp_bty = bh.read_bty(bty_file)

    # Create environment
    env = bh.create_env2d()

    # Assign loaded data (this should not raise errors)
    env["soundspeed"] = ssp
    env["depth"] = bty

    # Verify the data is stored correctly
    # For multi-profile SSP files, read_ssp returns pandas DataFrame, for single-profile, numpy array
    if hasattr(ssp, 'columns'):  # pandas DataFrame (multi-profile)
        # Environment should store the DataFrame as-is for range-dependent modeling
        assert hasattr(env["soundspeed"], 'columns'), "Multi-profile SSP should remain as DataFrame in environment"
        assert env["soundspeed"].shape == ssp.shape
    else:  # numpy array (single-profile)
        assert isinstance(env["soundspeed"], np.ndarray)
        assert env["soundspeed"].shape == ssp.shape

    assert isinstance(env["depth"], np.ndarray)
    assert env["depth"].shape == bty.shape

def test_file_extensions():
    """Test that functions handle missing extensions correctly"""
    # Test without extension
    ssp_file = "tests/MunkB_geo_rot/MunkB_geo_rot"  # No .ssp extension
    bty_file = "tests/MunkB_geo_rot/MunkB_geo_rot"  # No .bty extension

    if not (os.path.exists(ssp_file + ".ssp") and os.path.exists(bty_file + ".bty")):
        pytest.skip("Test files not found")

    # Should work without extensions
    ssp = bh.read_ssp(ssp_file)
    bty,interp_bty = bh.read_bty(bty_file)

    # Check data types - read_ssp can return DataFrame (multi-profile) or numpy array (single-profile)
    if hasattr(ssp, 'columns'):  # pandas DataFrame (multi-profile)
        assert hasattr(ssp, 'shape'), "SSP DataFrame should have shape attribute"
        assert len(ssp.columns) > 0, "SSP DataFrame should have range columns"
    else:  # numpy array (single-profile)
        assert isinstance(ssp, np.ndarray)

    assert isinstance(bty, np.ndarray)

def test_file_not_found():
    """Test error handling for missing files"""
    with pytest.raises(FileNotFoundError):
        bh.read_ssp("nonexistent.ssp")

    with pytest.raises(FileNotFoundError):
        bh.read_bty("nonexistent.bty")

    with pytest.raises(FileNotFoundError):
        bh.read_brc("nonexistent.brc")

    with pytest.raises(FileNotFoundError):
        bh.read_sbp("nonexistent.sbp")
