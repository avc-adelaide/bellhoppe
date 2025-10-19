import pytest
import bellhop as bh
import pandas as pd
import pandas.testing as pdt


def test_ssp_spline_points(): # not an error but anyway
    ssp = pd.DataFrame({ 'depth':[0,10,20,30], 'speed':[1540,1530,1520,1525]})
    env = bh.create_env(soundspeed=ssp,depth=30,soundspeed_interp="spline")
    env = bh.check_env(env)
    arr = bh.compute_arrivals(env,debug=True)



def test_ssp_one_speed():
    """Test singleton SSP entries. All of these should be equivalent."""

    ssp1 = 1540
    env1 = bh.create_env(soundspeed=ssp1, depth=30, soundspeed_interp="pchip")
    bh.check_env(env1)

    ssp2 = [
        [ 0, 1540],  # equivalent to "constant"
    ]
    env2 = bh.create_env(soundspeed=ssp2, depth=30, soundspeed_interp="pchip")
    bh.check_env(env2)

    ssp3 = [
        [ 30, 1540],  # equivalent to "constant"
    ]
    env3 = bh.create_env(soundspeed=ssp3, depth=30, soundspeed_interp="pchip")
    bh.check_env(env3)

    pdt.assert_frame_equal(env1['soundspeed'],env2['soundspeed'])
    pdt.assert_frame_equal(env1['soundspeed'],env3['soundspeed'])


def test_ssp_neg():
    env = bh.read_env2d("tests/simple/simple_neg_ssp")
    with pytest.raises(RuntimeError):
        tl = bh.compute_transmission_loss(env)
