import pytest
import bellhop as bh
import numpy as np
import tempfile
import os


def test_read_env2d_basic():
    """Test reading a basic ENV file."""
    # Test with Munk profile
    env_file = 'examples/Munk/MunkB_ray.env'
    env = bh.read_env2d(env_file)

    # Verify basic properties
    assert env['name'] == 'Munk profile'
    assert env['frequency'] == 50.0
    assert env['depth'] == 5000.0
    assert env['bottom_soundspeed'] == 1600.0
    assert env['min_angle'] == -20.0
    assert env['max_angle'] == 20.0
    assert env['nbeams'] == 41

    # Verify the environment is valid
    checked_env = bh.check_env2d(env)
    assert checked_env is not None


def test_read_env2d_free_space():
    """Test reading a free space ENV file with different format."""
    env_file = 'examples/free/freePointB.env'
    env = bh.read_env2d(env_file)

    # Verify basic properties
    assert env['name'] == 'Free space, point source, Hat beam'
    assert env['frequency'] == 5.0
    assert env['depth'] == 10000.0
    assert env['min_angle'] == -89.0
    assert env['max_angle'] == 89.0
    assert env['nbeams'] == 500

    # Note: This environment may not pass check_env2d due to minimal SSP profile
    # but the parsing itself should work


def test_read_env2d_round_trip():
    """Test creating an environment, writing it to ENV file, then reading it back."""
    # Create a test environment
    env_orig = bh.create_env2d(
        name="Round trip test",
        frequency=100.0,
        depth=30.0,
        soundspeed=1520.0,
        bottom_soundspeed=1700.0,
        bottom_density=1800.0,
        bottom_absorption=0.2,
        tx_depth=5.0,
        rx_depth=np.array([2.0, 10.0, 25.0]),
        rx_range=np.array([100.0, 500.0, 1000.0]),
        min_angle=-30.0,
        max_angle=30.0,
        nbeams=31
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        fname_base = os.path.join(temp_dir, "test_env")

        # Create the Bellhop model and generate the env file
        from bellhop.bellhop import _Bellhop
        model = _Bellhop()
        fname_base = model._create_env_file(env_orig, 'R', fname_base)
        env_file = fname_base + '.env'

        # Read it back
        env_read = bh.read_env2d(env_file)

        # Compare key values (allowing for expected transformations)
        assert env_read['name'] == env_orig['name']
        assert env_read['frequency'] == env_orig['frequency']
        assert env_read['depth'] == env_orig['depth']
        assert env_read['bottom_soundspeed'] == env_orig['bottom_soundspeed']
        assert env_read['min_angle'] == env_orig['min_angle']
        assert env_read['max_angle'] == env_orig['max_angle']
        assert env_read['nbeams'] == env_orig['nbeams']

        # Sound speed gets converted to profile format
        if isinstance(env_read['soundspeed'], np.ndarray):
            assert env_read['soundspeed'][0, 1] == env_orig['soundspeed']

        # Arrays should match
        np.testing.assert_array_equal(env_read['tx_depth'], env_orig['tx_depth'])
        np.testing.assert_array_equal(env_read['rx_depth'], env_orig['rx_depth'])
        np.testing.assert_array_equal(env_read['rx_range'], env_orig['rx_range'])


def test_read_env2d_missing_file():
    """Test that missing file raises appropriate error."""
    with pytest.raises(FileNotFoundError):
        bh.read_env2d('nonexistent_file.env')


def test_read_env2d_add_extension():
    """Test that .env extension is added automatically."""
    # Test without extension
    env1 = bh.read_env2d('examples/Munk/MunkB_ray')
    # Test with extension
    env2 = bh.read_env2d('examples/Munk/MunkB_ray.env')

    # Should be the same
    assert env1['name'] == env2['name']
    assert env1['frequency'] == env2['frequency']


def test_read_env2d_vector_parsing():
    """Test various vector formats are parsed correctly."""
    env_file = 'examples/Munk/MunkB_ray.env'
    env = bh.read_env2d(env_file)

    # Check that compressed vector notation works (should have generated linearly spaced values)
    assert len(env['rx_depth']) == 2  # From "51" and "0.0 5000.0 /"
    assert env['rx_ndepth'] == 51  # From "51" and "0.0 5000.0 /"
    assert env['rx_depth'][0] == 0.0
    assert env['rx_depth'][-1] == 5000.0

    assert len(env['rx_range']) == 2  # From "1001" and "0.0 100.0 /"
    assert env['rx_nrange'] == 1001  # From "1001" and "0.0 100.0 /"
    assert env['rx_range'][0] == 0.0
    assert env['rx_range'][-1] == 100000.0  # Converted from km to m


def test_read_env2d_vector_parsing():
    """Test various vector formats are parsed correctly."""
    env_file = 'examples/Munk/MunkB_ray.env'
    env = bh.read_env2d(env_file)

    # Check that compressed vector notation works (should have generated linearly spaced values)
    assert len(env['rx_depth']) == 2  # From "51" and "0.0 5000.0 /"
    assert env['rx_ndepth'] == 51  # From "51" and "0.0 5000.0 /"
    assert env['rx_depth'][0] == 0.0
    assert env['rx_depth'][-1] == 5000.0

    assert len(env['rx_range']) == 2  # From "1001" and "0.0 100.0 /"
    assert env['rx_nrange'] == 1001  # From "1001" and "0.0 100.0 /"
    assert env['rx_range'][0] == 0.0
    assert env['rx_range'][-1] == 100000.0  # Converted from km to m
