import pytest
import bellhop as bh
import pandas as pd
from unittest.mock import patch


def test_missing_key_error():
    """Test that KeyError is raised for unknown key 'missing_key'."""

    # Test that the specific KeyError is raised
    with pytest.raises(KeyError, match=r"Unknown key: missing_key"):
	    env = bh.create_env2d(missing_key=7)



def test_variable_soundspeed_error():
    """Test BELLHOP with mis-ordered depth-dependent sound speed profile.
    """

    # Define depth-dependent sound speed profile as specified in issue
    ssp = [
        [ 0, 1540],
        [10, 1530],
        [25, 1533], # <- out of order
        [20, 1532],
        [30, 1535],
    ]

    # Create environment with variable sound speed profile
    with pytest.raises(ValueError, match=r"Soundspeed array must be strictly monotonic in depth"):
        env = bh.create_env2d(soundspeed=ssp, depth=30)
        env = bh.check_env2d(env)



def test_error_type():
    """Test that an error is raised for unknown model type."""

    with pytest.raises(ValueError, match=r"Not a 2D environment"):
        env = bh.create_env2d(type="4D")
        bh.check_env2d(env)


def test_ssp_spline_points():
    ssp = pd.DataFrame({'speed': [1540,1530,1535]},index=[0,15,30])
    env = bh.create_env2d(soundspeed=ssp,depth=30,soundspeed_interp="spline")

    with pytest.raises(ValueError, match=r"soundspeed profile must have at least 4 points for spline interpolation"):
        bh.check_env2d(env)


def test_missing_output_triggers_warning(capsys):
    bellhop = bh.bellhop.Bellhop()
    env = bh.create_env2d()
    env = bh.check_env2d(env)
    task = bh.bellhop._Strings.arrivals

    with pytest.raises(RuntimeError, match="Bellhop did not generate expected output file"):
        # Patch the Enum member temporarily to a bogus extension
        with patch.object(bh.bellhop._File_Ext, "arr", new=".bogus"):
            bellhop.run(env, task)
