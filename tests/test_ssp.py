import pytest
import bellhop as bh
import pandas as pd


def test_ssp_spline_points(): # not an error but anyway
    ssp = pd.DataFrame({ 'depth':[0,10,20,30], 'speed':[1540,1530,1520,1525]})
    env = bh.create_env2d(soundspeed=ssp,depth=30,soundspeed_interp="spline")
    env = bh.check_env2d(env)
    arr = bh.compute_arrivals(env,debug=True)
