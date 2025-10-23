import pytest
import bellhop as bh
import numpy as np


def test_model_new():
    """Just check that there are no execution errors.
    """

    bh.new_model(exe="bellhop3d.exe",dim=3,name="bellhop3d")
    assert "bellhop3d" in bh.models(), "Bellhop3D model not created"
    assert bh.models(dim=2) == ["bellhop"], "Model of dim 2 not found"
    assert bh.models(dim=3) == ["bellhop3d"], "Model of dim 3 not found"
