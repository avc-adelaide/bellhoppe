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

