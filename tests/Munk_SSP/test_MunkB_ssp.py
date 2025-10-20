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


def test_MunkB_ray_rot():
    """Test using a Bellhop example that ENV file parameters are being picked up properly.
    Just check that there are no execution errors.
    """

    env = bh.read_env("tests/Munk_SSP/MunkB_ray_rot.env")
    ssp0 = env['soundspeed']
    ssp1 = bh.read_ssp("tests/Munk_SSP/MunkB_ray_rot.ssp")
    ssp2 = bh.read_ssp("tests/Munk_SSP/MunkB_ray_rot_empties.ssp")

    assert env["soundspeed"].shape == (2,30) # Q interpolation, so this is MxN

    assert isinstance(ssp0,pd.DataFrame), "Q interp => 2D array of SSP points => expect DataFrame"
    assert isinstance(ssp1,pd.DataFrame), "Q interp => 2D array of SSP points => expect DataFrame"
    assert isinstance(ssp2,pd.DataFrame), "Q interp => 2D array of SSP points => expect DataFrame"

    assert ssp0.shape == (2,30), "Should be N=30 SSP data points"
    assert ssp1.shape == (2,30), "Should be N=30 SSP data points"
    assert ssp2.shape == (2,30), "Should be N=30 SSP data points"

    pdt.assert_frame_equal(
        ssp0.reset_index(drop=True),
        ssp2.reset_index(drop=True)
    ) # check .ssp file automatically read
    pdt.assert_frame_equal(ssp1, ssp2) # check that blank lines in the SSP file are skipped

    rays = bh.compute_rays(env,fname_base="tests/Munk_SSP/MunkB_output",debug=True)
    assert rays is not None, "No results generated"

    #print(rays)
