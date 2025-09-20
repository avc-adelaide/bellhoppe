import pytest
import bellhop as bh
import numpy as np

def test_sqrt_bug():

    env = bh.create_env2d(name="Test sqrt bug")

    dp = env["depth"]
    env["depth"] = np.array([[-2000,dp],[2000,dp]])
    env["rx_depth"] = 10
    env["rx_range"] = np.array([-1000, -500, -1, 1, 500, 1000])

    bh.check_env2d(env)
    bh.print_env(env)

    assert(env["depth"].ndim == 2)
    assert(env["depth"].size == 4)
    assert(env["rx_range"].ndim == 1)
    assert(env["rx_range"].size == 6)

    arrivals = bh.compute_arrivals(env,debug=True,fname_base="test_debug")

    print(arrivals.rx_range)
    print("Arrivals N=0")
    print(arrivals[arrivals.rx_range_ndx == 0])
    print("Arrivals N=1")
    print(arrivals[arrivals.rx_range_ndx == 1])
    print("Arrivals N=2")
    print(arrivals[arrivals.rx_range_ndx == 2])
    print(arrivals["arrival_amplitude"])

    # something is wrong, I can't figure out how to get rays into negative space
