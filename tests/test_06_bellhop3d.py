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

def test_model_env():
    """Check we can switch between bellhop 2d & 3d easily.
    """

    if "bellhop3d" not in bh.models():
      bh.new_model(exe="bellhop3d.exe",dim=3,name="bellhop3d")

    env2d = bh.create_env(dimension="2D")
    env3d = bh.create_env(dimension="3D")

#    assert env2d._dimension == 2
#    assert env3d._dimension == 3

#    assert bh.models(env=env2d) == ["bellhop"], "Model 2D not found"
#    assert bh.models(env=env3d) == ["bellhop3d"], "Model 3D not found"
