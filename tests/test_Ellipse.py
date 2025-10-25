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

env = bh.read_env("tests/Ellipse/Ellipse.env")

print(env["soundspeed"])
print(env["depth"])
print(env["depth_interp"])
print(env["surface"])
print(env["surface_interp"])

def test_Ellipse_read_data():
    """Test using a Bellhop example that ENV file parameters are being picked up properly.
    Just check that the ATI/BTY files are read first.
    """

    assert env['soundspeed_interp'] == 'linear', "SSPOPT = 'CVF *' => C == linear"
    assert env['surface_boundary_condition'] == 'vacuum', "SSPOPT = 'CVF *' => V == vacuum"
    assert env['attenuation_units'] == 'frequency dependent',  "SSPOPT = 'CVF *' => F == frequency dependent"

    assert env['depth'].shape == (1000,2), "BTY file contains 1000 data points"
    assert env['surface'].shape == (1000,2), "ATI file contains 1000 data points"

    assert env['task'] == "rays", "Task description is 'RB RR'"
    assert env['beam_type'] == "gaussian-cartesian", "Task description is 'RB RR'"
    assert env['_sbp_file'] == "default", "Task description is 'RB RR' => ' ' = none"
    assert env['source_type'] == "point", "Task description is 'RB RR'"
    assert env['grid_type'] == "rectilinear", "Task description is 'RB RR'"

    print(env)
    env.check()

    rays = bh.compute_rays(env, debug=True, fname_base="tests/Ellipse/ellipse_debug")
    assert rays is not None
