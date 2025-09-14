import pytest
import bellhop as bh
import numpy as np
import pandas as pd
import pandas.testing as pdt

def test_MunkB_geo_rot_A():
    """Test using a Bellhop example that ENV file parameters are being picked up properly.
    Just check that there are no execution errors.
    """

    env = bh.read_env2d("tests/MunkB_geo_rot/MunkB_geo_rot.env")
    ssp = bh.read_ssp("tests/MunkB_geo_rot/MunkB_geo_rot.ssp")
    bty = bh.read_bty("tests/MunkB_geo_rot/MunkB_geo_rot.bty")

    assert ssp.shape[1] == 30, "Should be N=30 SSP data points"
    assert bty.shape[0] == 30, "Should be N=30 BTY data points"

    env["soundspeed"] = ssp
    env["depth"] = bty

    assert env['soundspeed_interp'] == 'quadrilateral', "SSPOPT = 'QVF' => Q == quadrilateral"
    assert env['top_boundary_condition'] == 'vacuum', "SSPOPT = 'QVF' => V == vacuum"
    assert env['attenuation_units'] == 'frequency dependent',  "SSPOPT = 'QVF' => F == frequency dependent"

    assert env['depth'].shape == (30,2), "BTY file should contain 30 data points"

    assert env['step_size'] == 0, "0.0  99500.0  5.0		! STEP (m), ZBOX (m), RBOX (km)"
    assert env['box_depth'] == 99500.0, "0.0  99500.0  5.0		! STEP (m), ZBOX (m), RBOX (km)"
    assert env['box_range'] == 5000.0, "0.0  99500.0  5.0		! STEP (m), ZBOX (m), RBOX (km)"

    bh.check_env2d(env)
    # bh.print_env(env)

    tl = bh.compute_transmission_loss(env,fname_base="tests/MunkB_geo_rot/MunkB_output",debug=True)
    assert tl is not None, "No results generated"

    tl_exp = bh.bellhop._Bellhop._load_shd(None,"tests/MunkB_geo_rot/MunkB_geo_rot") # implicit ".shd" suffix

    assert (tl.index == tl_exp.index).all(), "TL dataframe indexes not identical"
    assert (tl.columns - tl_exp.columns < 1e-6).all(), "Interpolation values not identical"
    assert (tl.shape == tl_exp.shape), "Incorrect/inconsistent number of TL values calculated"

    pdt.assert_frame_equal(
        tl, tl_exp,
        atol=1e-8,  # absolute tolerance
        rtol=0,     # relative tolerance (default 1e-5, but you can set 0)
    )
