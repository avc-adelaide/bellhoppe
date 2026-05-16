import pytest
import aubellhop as bh
import numpy as np
import pandas as pd
import pandas.testing as pdt


def test_ssp_spline_points(): # not an error but anyway
    ssp = pd.DataFrame({ 'depth':[0,10,20,30], 'speed':[1540,1530,1520,1525]})
    env = bh.Environment(soundspeed=ssp,bottom_depth=30,soundspeed_interp="spline")
    env.check()
    arr = bh.compute_arrivals(env,debug=True)



def test_ssp_one_speed():
    """Test singleton SSP entries. All of these should be equivalent."""

    ssp1 = 1540
    env1 = bh.Environment(soundspeed=ssp1, bottom_depth=30, soundspeed_interp="pchip").check()

    ssp2 = [
        [ 0, 1540],  # equivalent to "constant"
    ]
    env2 = bh.Environment(soundspeed=ssp2, bottom_depth=30, soundspeed_interp="pchip").check()

    ssp3 = [
        [ 30, 1540],  # equivalent to "constant"
    ]
    env3 = bh.Environment(soundspeed=ssp3, bottom_depth=30, soundspeed_interp="pchip").check()

    pdt.assert_frame_equal(env1['soundspeed'],env2['soundspeed'])
    pdt.assert_frame_equal(env1['soundspeed'],env3['soundspeed'])


def test_ssp_neg():
    env = bh.Environment.from_file("tests/simple/simple_neg_ssp")
    with pytest.raises(RuntimeError):
        tl = bh.compute_transmission_loss(env)



def test_ssp_error(): # too many columns
    ssp = np.column_stack((
                [0,10,20,30],
                [1540,1530,1520,1525],
                [1540,1530,1520,1525],
                [1540,1530,1520,1525],
        ))
    env = bh.Environment(soundspeed=ssp,bottom_depth=30,soundspeed_interp="spline")
    with pytest.raises(TypeError, match='For an NDArray, soundspeed must be defined as a Nx2 array'):
        env.check()
