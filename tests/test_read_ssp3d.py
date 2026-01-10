import pytest
import aubellhop.readers as bhr
import numpy as np
import pandas as pd
import os

def test_read_ssp3d():
    """Test reading 3D SSP file"""
    ssp3d = bhr.read_ssp3d("examples/Bellhop3DTests/KoreanSeas/KoreanSea.ssp")
    assert ssp3d["ssp"].shape == (151, 169, 33)
    assert ssp3d["ranges"].shape[0] == 151
    assert ssp3d["crossranges"].shape[0] == 169
    assert ssp3d["depths"].shape[0] == 33
