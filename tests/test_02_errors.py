import pytest
import bellhop.bellhop as pm


def test_missing_key_error():
    """Test that KeyError is raised for unknown key 'missing_key'."""

    # Test that the specific KeyError is raised
    with pytest.raises(KeyError, match=r"Unknown key: missing_key"):
	    env = pm.create_env2d(missing_key=7)



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
    	env = pm.create_env2d(soundspeed=ssp, depth=30)

