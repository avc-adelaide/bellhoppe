import pytest
import bellhop as bh
import numpy as np
import pandas as pd
import pandas.testing as pdt
import tempfile
import os


def test_read_env_basic():
    """Test reading a basic ENV file."""
    # Test with Munk profile
    env_file = 'examples/Munk/MunkB_ray.env'
    env = bh.read_env(env_file)

    # Verify basic properties
    assert env['name'] == 'Munk profile'
    assert env['frequency'] == 50.0
    assert env['depth'] == 5000.0
    assert env['bottom_soundspeed'] == 1600.0
    assert env['beam_angle_min'] == -20.0
    assert env['beam_angle_max'] == 20.0
    assert env['beam_num'] == 41

    # Verify the environment is valid
    checked_env = env.check()
    assert checked_env is not None


def test_read_env_free_space():
    """Test reading a free space ENV file with different format."""
    env_file = 'examples/free/freePointB.env'
    env = bh.read_env(env_file)

    # Verify basic properties
    assert env['name'] == 'Free space, point source, Hat beam'
    assert env['frequency'] == 5.0
    assert env['depth'] == 10000.0
    assert env['beam_angle_min'] == -89.0
    assert env['beam_angle_max'] == 89.0
    assert env['beam_num'] == 500

    # Note: This environment may not pass check_env due to minimal SSP profile
    # but the parsing itself should work


def test_read_env_round_trip():
    """Test creating an environment, writing it to ENV file, then reading it back."""
    # Create a test environment
    env_orig = bh.create_env(
        name="Round trip test",
        frequency=100.0,
        depth=30.0,
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

    with tempfile.TemporaryDirectory() as temp_dir:
        fname_base = os.path.join(temp_dir, "test_env")

        # Create the Bellhop model and generate the env file
        from bellhop.main import BellhopSimulator
        model = BellhopSimulator()
        fh_fd, fname_base = model._prepare_env_file(fname_base)
        with os.fdopen(fh_fd, "w") as fh:
            model._create_env_file(env_orig, 'R', fh, fname_base)
        env_file = fname_base + '.env'

        # Read it back
        env_read = bh.read_env(env_file)

        # Compare key values (allowing for expected transformations)
        assert env_read['name'] == env_orig['name']
        assert env_read['frequency'] == env_orig['frequency']
        assert env_read['depth'] == env_orig['depth']
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


def test_read_env_missing_file():
    """Test that missing file raises appropriate error."""
    with pytest.raises(FileNotFoundError):
        bh.read_env('nonexistent_file.env')


def test_read_env_add_extension():
    """Test that .env extension is added automatically."""
    # Test without extension
    env1 = bh.read_env('examples/Munk/MunkB_ray')
    # Test with extension
    env2 = bh.read_env('examples/Munk/MunkB_ray.env')

    # Should be the same
    assert env1['name'] == env2['name']
    assert env1['frequency'] == env2['frequency']


def test_read_env_vector_parsing():
    """Test various vector formats are parsed correctly."""
    env_file = 'examples/Munk/MunkB_ray.env'
    env = bh.read_env(env_file)

    # Check that compressed vector notation works (should have generated linearly spaced values)
    assert len(env['receiver_depth']) == 2  # From "51" and "0.0 5000.0 /"
    assert env['receiver_ndepth'] == 51  # From "51" and "0.0 5000.0 /"
    assert env['receiver_depth'][0] == 0.0
    assert env['receiver_depth'][-1] == 5000.0

    assert len(env['receiver_range']) == 2  # From "1001" and "0.0 100.0 /"
    assert env['receiver_nrange'] == 1001  # From "1001" and "0.0 100.0 /"
    assert env['receiver_range'][0] == 0.0
    assert env['receiver_range'][-1] == 100000.0  # Converted from km to m


def test_read_env_vector_parsing():
    """Test various vector formats are parsed correctly."""
    env_file = 'examples/Munk/MunkB_ray.env'
    env = bh.read_env(env_file)

    # Check that compressed vector notation works (should have generated linearly spaced values)
    assert len(env['receiver_depth']) == 2  # From "51" and "0.0 5000.0 /"
    assert env['receiver_ndepth'] == 51  # From "51" and "0.0 5000.0 /"
    assert env['receiver_depth'][0] == 0.0
    assert env['receiver_depth'][-1] == 5000.0

    assert len(env['receiver_range']) == 2  # From "1001" and "0.0 100.0 /"
    assert env['receiver_nrange'] == 1001  # From "1001" and "0.0 100.0 /"
    assert env['receiver_range'][0] == 0.0
    assert env['receiver_range'][-1] == 100000.0  # Converted from km to m


def test_read_env2e_dataframe():

    env1 = bh.create_env(soundspeed=[[0,1540], [5,1535], [10,1535], [20,1530]])

    ssp2 = bh.read_ssp("tests/MunkB_geo_rot/MunkB_geo_rot.ssp")  # Returns DataFrame
    env2 = bh.create_env(soundspeed=ssp2)

    assert isinstance(env1['soundspeed'],np.ndarray), "Expect plain array => Numpy array"
    assert isinstance(env2['soundspeed'],pd.DataFrame), "Expect DataFrame => preserved"

