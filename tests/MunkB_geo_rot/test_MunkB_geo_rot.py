import pytest
import bellhop as bh
import numpy as np



def test_MunkB_geo_rot_A():
    """Test from Bellhop examples to calculate arrival times. Just check that there are no execution errors.
    """

    env = bh.read_env2d("tests/MunkB_geo_rot/MunkB_geo_rot")
    ssp = bh.read_ssp("tests/MunkB_geo_rot/MunkB_geo_rot")

    env["soundspeed"] = ssp
    assert ssp.shape[1] == 30, "Should be N=30 SSP data points."
    assert env['soundspeed_interp'] == 'quadrilateral', "SSPOPT = 'QVF' => Q == quadrilateral"
    assert env['top_boundary_condition'] == 'vacuum', "SSPOPT = 'QVF' => V == vacuum"
    assert env['attenuation_units'] == 'frequency dependent',  "SSPOPT = 'QVF' => F == frequency dependent"

    print(env)
    bh.check_env2d(env)
    bh.print_env(env)

    arr = bh.compute_arrivals(env,debug=True)
    assert arr is not None, "No arrival results generated."
