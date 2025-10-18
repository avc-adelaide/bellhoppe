import pytest
import bellhop as bh
import os

def test_malformed_ati_count_mismatch():
    """Test ATI file where count doesn't match number of lines"""
    with pytest.raises(ValueError, match="Expected 5 altimetry/bathymetry points, but found 3"):
        bh.read_ati("tests/malformed_files/bad_count_ati.ati")

def test_malformed_ati_insufficient_data():
    """Test ATI file where a line has too few data points"""
    with pytest.raises((ValueError, IndexError)):
        bh.read_ati("tests/malformed_files/insufficient_data_ati.ati")

def test_malformed_bty_count_mismatch():
    """Test BTY file where count doesn't match number of lines"""
    with pytest.raises(ValueError, match="Expected 4 altimetry/bathymetry points, but found 2"):
        bh.read_bty("tests/malformed_files/bad_count_bty.bty")

def test_malformed_bty_insufficient_data():
    """Test BTY file where a line has too few data points"""
    with pytest.raises((ValueError, IndexError)):
        bh.read_bty("tests/malformed_files/insufficient_data_bty.bty")

def test_malformed_ssp_count_mismatch():
    """Test SSP file where count doesn't match number of ranges"""
    with pytest.raises(ValueError, match="Expected 5 ranges, but found 3"):
        bh.read_ssp("tests/malformed_files/bad_count_ssp.ssp")

def test_malformed_ssp_insufficient_data():
    """Test SSP file where a line has too few data points"""
    with pytest.raises((ValueError, IndexError)):
        bh.read_ssp("tests/malformed_files/insufficient_data_ssp.ssp")

def test_malformed_sbp_count_mismatch():
    """Test SBP file where count doesn't match number of lines"""
    with pytest.raises(ValueError, match="Expected 5 points, but found 3"):
        bh.read_sbp("tests/malformed_files/bad_count_sbp.sbp")

def test_malformed_sbp_insufficient_data():
    """Test SBP file where a line has too few data points"""
    with pytest.raises((ValueError, IndexError)):
        bh.read_sbp("tests/malformed_files/insufficient_data_sbp.sbp")

def test_empty_ati_file():
    """Test ATI file with 0 points declared - should return empty array"""
    result, interp = bh.read_ati("tests/malformed_files/empty_ati.ati")
    assert result.shape == (0, 2)

def test_missing_ssp_data():
    """Test SSP file with no sound speed data"""
    with pytest.raises(ValueError, match="Wrong number of depths found in sound speed data file"):
        bh.read_ssp("tests/malformed_files/missing_data_ssp.ssp")

def test_extra_data_sbp():
    """Test SBP file where a line has too many data points (should still work)"""
    # This should work because we only read the first 2 values
    result = bh.read_sbp("tests/malformed_files/extra_data_sbp.sbp")
    assert result.shape == (2, 2)

def test_malformed_brc_count_mismatch():
    """Test BRC file where count doesn't match number of lines"""
    with pytest.raises(ValueError, match="Expected 4 reflection coefficient points, but found 2"):
        bh.read_brc("tests/malformed_files/bad_count_brc.brc")

def test_malformed_brc_insufficient_data():
    """Test BRC file where a line has too few data points"""
    with pytest.raises(ValueError, match="Expected 3 reflection coefficient points, but found 2"):
        bh.read_brc("tests/malformed_files/insufficient_data_brc.brc")
