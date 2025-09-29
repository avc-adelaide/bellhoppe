import pytest
import bellhop as bh
import os

def test_malformed_env_interp():
    """Test ENV file where interp doesn't match allowed option"""
    with pytest.raises(ValueError, match="Interpolation option 'Z' not available"):
        bh.read_env2d("tests/malformed_env/bad_interp.env")


def test_malformed_env_media():
    """Test ENV file where nmedia > 1"""
    with pytest.raises(ValueError, match="BELLHOP only supports 1 medium, found 2"):
        bh.read_env2d("tests/malformed_env/bad_media.env")


def test_malformed_env_top():
    """Test ENV file where top bc doesn't match allowed option'"""
    with pytest.raises(ValueError, match="Top boundary condition option 'Z' not available"):
        bh.read_env2d("tests/malformed_env/bad_top.env")


def test_malformed_env_att():
    """Test ENV file where attentuation units doesn't match allowed option'"""
    with pytest.raises(ValueError, match="Attenuation units option 'Z' not available"):
        bh.read_env2d("tests/malformed_env/bad_att.env")


def test_malformed_env_vol():
    """Test ENV file where volume attenuation doesn't match allowed option'"""
    with pytest.raises(ValueError, match="Volume attenuation option 'Z' not available"):
        bh.read_env2d("tests/malformed_env/bad_vol.env")


def test_malformed_env_ati():
    """Test ENV file where altimetry doesn't match allowed option'"""
    with pytest.raises(ValueError, match="Altimetry option 'Z' not available"):
        bh.read_env2d("tests/malformed_env/bad_ati.env")


def test_malformed_env_sb():
    """Test ENV file where single beam doesn't match allowed option'"""
    with pytest.raises(ValueError, match="Single beam option 'Z' not available"):
        bh.read_env2d("tests/malformed_env/bad_sb.env")


def test_malformed_env_bot():
    """Test ENV file where bottom bc doesn't match allowed option'"""
    with pytest.raises(ValueError, match="Bottom boundary condition option 'Z' not available"):
        bh.read_env2d("tests/malformed_env/bad_bot.env")


def test_malformed_env_bty():
    """Test ENV file where bathymetry doesn't match allowed option'"""
    with pytest.raises(ValueError, match="Bathymetry option 'Z' not available"):
        bh.read_env2d("tests/malformed_env/bad_bty.env")

