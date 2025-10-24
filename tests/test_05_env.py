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


def test_unwrap():

    env1 = bh.create_env()
    env1.frequency = [100, 200]
    env2 = env1.unwrap('frequency')
    assert len(env2) == 2, "Two frequencies"
    assert env2[0].frequency == 100, "f1 = 100"
    assert env2[1].frequency == 200, "f2 = 200"
    print(env2[0].name)
    print(env2[1].name)

def test_unwrap_twice():

    env1 = bh.create_env()
    env1.frequency = [100, 200]
    env1.source_depth = [5, 10]
    env2 = env1.unwrap('frequency','source_depth')
    assert len(env2) == 4, "Four combinations"
    print(env2[0].name)
    print(env2[1].name)
    print(env2[2].name)
    print(env2[3].name)

    assert env2[0].frequency == 100
    assert env2[1].frequency == 100
    assert env2[2].frequency == 200
    assert env2[3].frequency == 200

    assert env2[0].source_depth == 5
    assert env2[1].source_depth == 10
    assert env2[2].source_depth == 5
    assert env2[3].source_depth == 10

def test_unwrap_once():

    env1 = bh.create_env()
    env1.frequency = [100, 200]
    env2 = env1.unwrap('frequency','source_depth')
    assert len(env2) == 2, "Two frequencies"
    assert env2[0].frequency == 100, "f1 = 100"
    assert env2[1].frequency == 200, "f2 = 200"
    print(env2[0].name)
    print(env2[1].name)
