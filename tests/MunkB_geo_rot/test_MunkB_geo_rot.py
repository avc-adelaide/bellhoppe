import pytest
import bellhop as bh
import numpy as np



def test_MunkB_geo_rot_A():
    """Test from Bellhop examples to calculate arrival times. Just check that there are no execution errors.
    """

    env = bh.read_env2d("tests/MunkB_geo_rot/MunkB_geo_rot.env")
    ssp = bh.read_ssp("tests/MunkB_geo_rot/MunkB_geo_rot.ssp")
    bty = bh.read_bty("tests/MunkB_geo_rot/MunkB_geo_rot.bty")

    env["soundspeed"] = ssp
    env["depth"] = bty

    assert ssp.shape[1] == 30, "Should be N=30 SSP data points."
    assert env['soundspeed_interp'] == 'quadrilateral', "SSPOPT = 'QVF' => Q == quadrilateral"
    assert env['top_boundary_condition'] == 'vacuum', "SSPOPT = 'QVF' => V == vacuum"
    assert env['attenuation_units'] == 'frequency dependent',  "SSPOPT = 'QVF' => F == frequency dependent"

    assert env['depth'].shape == (30,2), "BTY file should contain 30 data points"

    assert env['step_size'] == 0, "0.0  99500.0  5.0		! STEP (m), ZBOX (m), RBOX (km)"
    assert env['box_depth'] == 99500.0, "0.0  99500.0  5.0		! STEP (m), ZBOX (m), RBOX (km)"
    assert env['box_range'] == 5000.0, "0.0  99500.0  5.0		! STEP (m), ZBOX (m), RBOX (km)"

    print(env)
    bh.check_env2d(env)
    bh.print_env(env)

    tl = bh.compute_transmission_loss(env,debug=True)
    assert tl is not None, "No results generated."

    print(tl)
