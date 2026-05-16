import pytest
import aubellhop as bh
from aubellhop.readers import read_shd
import numpy as np
import pandas as pd
import pandas.testing as pdt
import os

skip_if_coverage = pytest.mark.skipif(
    os.getenv("COVERAGE_RUN") == "true",
    reason="Skipped during coverage run"
)

env = bh.Environment.from_file("tests/MunkB_geo_rot/MunkB_geo_rot.env")

tl = bh.compute_transmission_loss(env,fname_base="tests/MunkB_geo_rot/MunkB_output",debug=True)
tl_exp = read_shd("tests/MunkB_geo_rot/MunkB_geo_rot.shd")

def test_MunkB_geo_rot_A():
    """Test using a Bellhop example that ENV file parameters are being picked up properly.
    Just check that there are no execution errors.
    """

    assert env["soundspeed"].shape[1] == 30, "Should be N=30 SSP data points"
    assert env['bottom_depth'].shape == (30,2), "BTY file should contain 30 data points"

    assert env['soundspeed_interp'] == 'quadrilateral', "SSPOPT = 'QVF' => Q == quadrilateral"
    assert env['surface_boundary_condition'] == 'vacuum', "SSPOPT = 'QVF' => V == vacuum"
    assert env['attenuation_units'] == 'frequency dependent',  "SSPOPT = 'QVF' => F == frequency dependent"

    assert env['step_size'] == 0, "0.0  99500.0  5.0		! STEP (m), ZBOX (m), RBOX (km)"
    assert env['simulation_depth'] == 99500.0, "0.0  99500.0  5.0		! STEP (m), ZBOX (m), RBOX (km)"
    assert env['simulation_range'] == 5000.0, "0.0  99500.0  5.0		! STEP (m), ZBOX (m), RBOX (km)"

    env.check()

    assert tl is not None, "No results generated"
    assert (tl.shape == tl_exp.shape), "Incorrect/inconsistent number of TL values calculated"
    assert (tl.index == tl_exp.index).all(), "TL dataframe indexes not identical"
    assert (np.abs(tl.columns - tl_exp.columns) < 1e-2 ).all(), "TL dataframe columns not identical"


def assert_mostly_allclose(a, b, rtol=1e-4, atol=1e-2, threshold=0.99):
    diff = np.abs(a - b)
    ok = diff <= (atol + rtol * np.abs(b))
    frac_ok = ok.mean()

    if frac_ok < threshold:
        raise AssertionError(
            f"Only {frac_ok:.4f} of elements match; "
            f"required {threshold:.4f}"
        )

@skip_if_coverage
def test_table_output():
    assert_mostly_allclose(tl.to_numpy(), tl_exp.to_numpy())


def test_MunkB_extra_bot_param():
    env2 = bh.Environment.from_file("tests/MunkB_geo_rot/MunkB_geo_rot_botx.env")
    assert env2['bottom_beta'] == 3.3, "Bottom beta value not read correctly"
    assert env2['bottom_transition_freq'] == 4.4, "Bottom trans freq value not read correctly"
    assert env2['bottom_attenuation'] == 7.7, "Bottom abs value not read correctly"
    assert env2['_bottom_attenuation_shear'] == 8.8, "Bottom abs shear value not read correctly"
