import pytest
import bellhop as bh
import numpy as np
import pandas as pd
import pandas.testing as pdt
import os

skip_if_coverage = pytest.mark.skipif(
    os.getenv("COVERAGE_RUN") == "true",
    reason="Skipped during coverage run"
)

env = bh.read_env2d("tests/MunkB_geo_rot/MunkB_geo_rot.env")
ssp = bh.read_ssp("tests/MunkB_geo_rot/MunkB_geo_rot.ssp")
bty,interp_bty = bh.read_bty("tests/MunkB_geo_rot/MunkB_geo_rot.bty")

env["soundspeed"] = ssp
env["depth"] = bty

tl = bh.compute_transmission_loss(env,fname_base="tests/MunkB_geo_rot/MunkB_output",debug=True)
tl_exp = bh.load_shd("tests/MunkB_geo_rot/MunkB_geo_rot") # implicit ".shd" suffix

def test_MunkB_geo_rot_A():
    """Test using a Bellhop example that ENV file parameters are being picked up properly.
    Just check that there are no execution errors.
    """

    assert ssp.shape[1] == 30, "Should be N=30 SSP data points"
    assert bty.shape[0] == 30, "Should be N=30 BTY data points"

    assert env['soundspeed_interp'] == 'quadrilateral', "SSPOPT = 'QVF' => Q == quadrilateral"
    assert env['top_boundary_condition'] == 'vacuum', "SSPOPT = 'QVF' => V == vacuum"
    assert env['attenuation_units'] == 'frequency dependent',  "SSPOPT = 'QVF' => F == frequency dependent"

    assert env['depth'].shape == (30,2), "BTY file should contain 30 data points"

    assert env['step_size'] == 0, "0.0  99500.0  5.0		! STEP (m), ZBOX (m), RBOX (km)"
    assert env['box_depth'] == 99500.0, "0.0  99500.0  5.0		! STEP (m), ZBOX (m), RBOX (km)"
    assert env['box_range'] == 5000.0, "0.0  99500.0  5.0		! STEP (m), ZBOX (m), RBOX (km)"

    bh.check_env2d(env)

    assert tl is not None, "No results generated"
    assert (tl.shape == tl_exp.shape), "Incorrect/inconsistent number of TL values calculated"
    assert (tl.index == tl_exp.index).all(), "TL dataframe indexes not identical"


@skip_if_coverage
def test_table_output():
    pdt.assert_frame_equal(
        tl, tl_exp,
        check_names=False,
        atol=1e-8,  # absolute tolerance
        rtol=1e-5,  # relative tolerance
    )
