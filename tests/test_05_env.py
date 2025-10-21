import pytest
import bellhop as bh
import numpy as np


def test_env():
    """Just check that there are no execution errors.
    """

    env = bh.create_env()
    print(env)


def test_copy():

    env1 = bh.create_env()
    range_vec = np.linspace(0,5000) # 5km simulation
    depth_vec = np.linspace(1000,2000) # ramp seabed
    env1.depth = np.column_stack([range_vec,depth_vec])
    assert env1.depth_max == None
    env1.check()
    assert env1.depth_max == 2000
    env2 = env1.copy()
    assert env2.depth_max == 2000
