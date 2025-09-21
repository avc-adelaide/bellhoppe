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

env = bh.read_env2d("tests/Dickins/DickinsB.env")
bty,interp_bty = bh.read_bty("tests/Dickins/DickinsB.bty")

print(interp_bty)

env["depth"] = bty
env["depth_interp"] = interp_bty

tl = bh.compute_transmission_loss(env,fname_base="tests/Dickins/DickinsB_output",debug=True)
tl_exp = bh.bellhop._Bellhop._load_shd(None,"tests/Dickins/DickinsB") # implicit ".shd" suffix

def test_MunkB_geo_rot_A():
    """Test using a Bellhop example that ENV file parameters are being picked up properly.
    Just check that there are no execution errors.
    """

    assert bty.shape[0] == 5,  "Should be N= 5 BTY data points"

    assert env['soundspeed_interp'] == 'linear', "SSPOPT = 'CVW' => C == linear"
    assert env['top_boundary_condition'] == 'vacuum', "SSPOPT = 'CVW' => V == vacuum"
    assert env['attenuation_units'] == 'dB per wavelength',  "SSPOPT = 'CVW' => W == dB per wavelength"

    assert env['depth'].shape == (5,2), "BTY file should contain 30 data points"

    assert env['step_size'] ==      0.0, "0.0  3100.0  101.0		! STEP (m), ZBOX (m), RBOX (km)"
    assert env['box_depth'] ==   3100.0, "0.0  3100.0  101.0		! STEP (m), ZBOX (m), RBOX (km)"
    assert env['box_range'] == 101000.0, "0.0  3100.0  101.0		! STEP (m), ZBOX (m), RBOX (km)"

    bh.check_env2d(env)
    # bh.print_env(env)

    assert tl is not None, "No results generated"
    assert (tl.shape == tl_exp.shape), "Incorrect/inconsistent number of TL values calculated"
    assert (tl.index == tl_exp.index).all(), "TL dataframe indexes not identical"


@skip_if_coverage
def test_table_output():
    pdt.assert_frame_equal(
        tl, tl_exp,
        atol=1e-8,  # absolute tolerance
        rtol=1e-5,  # relative tolerance
    )
