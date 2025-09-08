import pytest
import bellhop as bh



def test_local():
    """Test with default settings to calculate arrival times. Just check that there are no execution errors.
    """

    env = bh.read_env2d("tests/MunkB_geo_rot/MunkB_geo_rot")
    ssp = bh.read_ssp("tests/MunkB_geo_rot/MunkB_geo_rot")
    print(ssp)
    print(ssp.shape)
    print(ssp.shape[0])
    print(ssp.shape[1])
    assert ssp.ndim == 2, 'soundspeed must be an Nx2 array'
    assert ssp.shape[1] == 2, 'soundspeed must be an Nx2 array'

    env["soundspeed"] = ssp
    arr = bh.compute_arrivals(env,debug=True)
    print(arr)


