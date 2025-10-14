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

env = bh.read_env2d("tests/VolAtt/free_FGB.env")

tl = bh.compute_transmission_loss(env,mode='coherent',fname_base="tests/VolAtt/FGB_output",debug=True)
tl_exp = bh.main.Bellhop._load_shd(None,"tests/VolAtt/free_FGB",".shd")


def test_simple():
    env2 = bh.create_env2d()
    env2["volume_attenuation"] = "francois-garrison"
    env2["fg_salinity"] = 19.3
    env2["fg_temperature"] = 33.5
    env2["fg_depth"] = 20
    env2["fg_pH"] = 7.5
    arr = bh.compute_arrivals(env2,fname_base="tests/VolAtt/debug_output",debug=True)

    assert arr is not None
    assert len(arr) == 36, "Should be N=36 arrivals"
    # don't check values here, might do that later

def test_FGB():
    """Test using a Bellhop example that ENV file parameters are being picked up properly.
    """

    assert env['soundspeed_interp'] == 'nlinear', "SSPOPT = 'NAWF' => N == nlinear"
    assert env['surface_boundary_condition'] == 'acousto-elastic', "SSPOPT = 'NAWF' => A == acousto-elastic"
    assert env['attenuation_units'] == 'dB per wavelength',  "SSPOPT = 'NAWF' => W == dB per wavelength"
    assert env['volume_attenuation'] == 'francois-garrison',  "SSPOPT = 'NAWF' => F == Francois-Garrison"

    assert env['step_size'] ==      0.0, "0.000000 10000.500000 10.050000"
    assert env['box_depth'] ==  10000.5, "0.000000 10000.500000 10.050000"
    assert env['box_range'] ==  10050.0, "0.000000 10000.500000 10.050000"

    assert env['task'] == 'TL-coherent'

    bh.print_env(env)

    assert tl is not None, "No results generated"
    assert (tl.shape == tl_exp.shape), "Incorrect/inconsistent number of TL values calculated"
    assert (tl.index == tl_exp.index).all(), "TL dataframe indexes not identical"


@skip_if_coverage
def test_table_output():
    pdt.assert_frame_equal(
        tl, tl_exp,
        check_names=False,
        atol=1e-4,  # absolute tolerance
        rtol=1e-6,  # relative tolerance
    )
