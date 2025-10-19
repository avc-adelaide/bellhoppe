import pytest
import bellhop as bh


def test_tl_many_source():

    env = bh.create_env()
    env = bh.check_env(env)
    i1 =  5.0
    i2 = 10.0
    i3 = 15.0
    env['source_depth'] = [5, i2, i3]
    tl0 = bh.compute_transmission_loss(env,source_depth_ndx=0)
    tl1 = bh.compute_transmission_loss(env,source_depth_ndx=1)
    tl2 = bh.compute_transmission_loss(env,source_depth_ndx=2)
    assert tl0.squeeze() != tl1.squeeze(), "TL from different sources should be different"
    assert tl0.squeeze() != tl2.squeeze(), "TL from different sources should be different"
