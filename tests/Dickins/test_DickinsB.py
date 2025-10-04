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
tl_exp = bh.load_shd("tests/Dickins/DickinsB") # implicit ".shd" suffix

def test_DickensB():
    """Test using a Bellhop example that ENV file parameters are being picked up properly.
    Just check that there are no execution errors.
    """

    assert bty.shape[0] == 5,  "Should be N= 5 BTY data points"

    assert env['soundspeed_interp'] == 'linear', "SSPOPT = 'CVW' => C == linear"
    assert env['surface_boundary_condition'] == 'vacuum', "SSPOPT = 'CVW' => V == vacuum"
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
        atol=1e-7,  # absolute tolerance
        rtol=1e-4,  # relative tolerance
    )

def test_DickensB_one_ssp():
    """Artificial scenario to test if just one point in the SSP profile"""
    with pytest.raises(ValueError, match="Only one SSP point found"):
        env2 = bh.read_env2d("tests/Dickins/DickinsB_one_ssp.env")

def test_DickensB_one_beam():
    """Artificial scenario to test if one beam"""
    env3 = bh.read_env2d("tests/Dickins/DickinsB_one_beam.env")
    ray3 = bh.compute_rays(env3,fname_base="tests/Dickins/DickinsB_output3",debug=True)
    assert ray3 is not None, "No results generated"
    assert len(ray3) == 1, "One beam should result in one row of results only"


def test_DickensB_one_beam_wrong():
    """Artificial scenario to test if one beam with malformed env file"""
    with pytest.raises(ValueError, match="Single beam was requested with option I but"):
        env3 = bh.read_env2d("tests/Dickins/DickinsB_one_beam_wrong.env")
        ray3 = bh.compute_rays(env3,fname_base="tests/Dickins/DickinsB_output3",debug=True)
        assert ray3 is not None, "No results generated"


def xtest_DickensB_empty_lines():
    """Test if empty lines are okay"""
    env5 = bh.read_env2d("tests/Dickins/DickinsB_simpl.env")
    env6 = bh.read_env2d("tests/Dickins/DickinsB_simpl_empty_lines.env")
    pdt.assert_frame_equal(env5['soundspeed'],env6['soundspeed'])
    tl5 = bh.compute_transmission_loss(env5)
    tl6 = bh.compute_transmission_loss(env6)
    assert tl5 is not None, "No results generated"
    assert tl6 is not None, "No results generated"
    assert tl5 == tl6, "Results should be identical"
