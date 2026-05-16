import pytest
import aubellhop as bh
from aubellhop.constants import EnvDefaults
import numpy as np
import pandas as pd
import pandas.testing as pdt
import tempfile
import os


def test_defaults():
    env = bh.Environment()
    env.reset()
    assert env.frequency is None, "Reset should set everything to None"
    env.defaults()
    assert env.frequency == EnvDefaults.frequency, "Defaults should now be set"
    env.reset()
    assert env.frequency is None, "Reset should set everything to None"
    env.frequency = 200
    env.defaults()
    assert env.frequency == 200, "Defaults should not override explicit settings"

def test_env_dict_round_trip():
    """Test creating an environment, exporting to DICT, then reading it back."""
    # Create a test environment
    env_orig = bh.Environment(
        name="Dict round trip test",
        frequency=100.0,
        bottom_depth=30.0,
        soundspeed=1520.0,
        bottom_soundspeed=1700.0,
        bottom_density=1800.0,
        bottom_attenuation=0.2,
        source_depth=5.0,
        receiver_depth=np.array([2.0, 10.0, 25.0]),
        receiver_range=np.array([100.0, 500.0, 1000.0]),
        beam_angle_min=-30.0,
        beam_angle_max=30.0,
        beam_num=31
    )
    env_orig.check()

    env_dict = env_orig.to_dict()
    assert env_dict['name'] == env_orig['name']
    assert env_dict['frequency'] == env_orig['frequency']
    assert env_dict['bottom_depth'] == env_orig['bottom_depth']
    assert env_dict['bottom_soundspeed'] == env_orig['bottom_soundspeed']
    assert env_dict['beam_angle_min'] == env_orig['beam_angle_min']
    assert env_dict['beam_angle_max'] == env_orig['beam_angle_max']
    assert env_dict['beam_num'] == env_orig['beam_num']

    # Read it back
    env_read = bh.Environment.from_dict(env_dict)

    # Compare key values (allowing for expected transformations)
    assert env_read['name'] == env_orig['name']
    assert env_read['frequency'] == env_orig['frequency']
    assert env_read['bottom_depth'] == env_orig['bottom_depth']
    assert env_read['bottom_soundspeed'] == env_orig['bottom_soundspeed']
    assert env_read['beam_angle_min'] == env_orig['beam_angle_min']
    assert env_read['beam_angle_max'] == env_orig['beam_angle_max']
    assert env_read['beam_num'] == env_orig['beam_num']

    # Sound speed gets converted to profile format
    pdt.assert_frame_equal(env_read['soundspeed'], env_orig['soundspeed'])

    # Arrays should match
    np.testing.assert_array_equal(env_read['source_depth'], env_orig['source_depth'])
    np.testing.assert_array_equal(env_read['receiver_depth'], env_orig['receiver_depth'])
    np.testing.assert_array_equal(env_read['receiver_range'], env_orig['receiver_range'])

