import pytest
import aubellhop as bh
import pandas as pd
from unittest.mock import patch


def test_missing_key_error():
    """Test that KeyError is raised for unknown key 'missing_key'."""

    # Test that the specific KeyError is raised
    with pytest.raises(TypeError, match=r"unexpected keyword argument .*missing_key"):
	    env = bh.Environment(missing_key=7)



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
        env = bh.Environment(soundspeed=ssp, bottom_depth=30)
        env.check()



def test_ssp_spline_points():
    ssp = pd.DataFrame({'speed': [1540,1530,1535]},index=[0,15,30])

    with pytest.raises(ValueError, match=r"soundspeed profile must have at least 4 points for spline interpolation"):
        env = bh.Environment(soundspeed=ssp,bottom_depth=30,soundspeed_interp="spline")
        env.check()


def test_missing_output_triggers_warning(capsys):
    bellhop = bh.bellhop.BellhopSimulator()
    env = bh.Environment()
    env.check()
    task = bh.bellhop.BHStrings.arrivals

    with pytest.raises(RuntimeError, match="Bellhop did not generate expected output file"):
        # Patch the Enum member temporarily to a bogus extension
        with patch.object(bh.bellhop.FileExt, "arr", new=".bogus"):
            fname = bellhop.write_env(env, task)
            bellhop.run(task, fname)
