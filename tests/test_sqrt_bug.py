import pytest
import bellhop as bh
import numpy as np

def test_sqrt_bug():

    env = bh.create_env2d(name="Test sqrt bug")

    dp = env["depth"]
    env["depth"] = np.array([[-2000,dp],[2000,dp]])
    env["receiver_depth"] = 10
    env["receiver_range"] = np.array([-1000, -500, -1, 1, 500, 1000])
    env["beam_num"] = 9999

    nn = len(env["receiver_range"])

    bh.check_env2d(env)

    assert(env["depth"].ndim == 2)
    assert(env["depth"].size == 4)
    assert(env["receiver_range"].ndim == 1)
    assert(env["receiver_range"].size == nn)

    arrivals = bh.compute_arrivals(env,debug=True,fname_base="tests/_test_sqrt")

    for i in range(len(env["receiver_range"])):
        arr_subset = arrivals[arrivals.receiver_range_ndx == i]
        print(f"{len(arr_subset)} arrivals for receiver range {env['receiver_range'][i]}")
        assert len(arr_subset) > 0, f"No arrivals found for receiver range {env['receiver_range'][i]}"

    for i in range(int(nn/2)):
        arr_subset1 = arrivals[arrivals.receiver_range_ndx == i]
        arr_subset2 = arrivals[arrivals.receiver_range_ndx == nn-i-1]
        assert len(arr_subset1) == len(arr_subset2), f"Should have equal number of arrivals for range: ±{env['receiver_range'][i]}"

        arr_amp1 = np.sort(np.abs(np.array(arr_subset1["arrival_amplitude"])))
        arr_amp2 = np.sort(np.abs(np.array(arr_subset2["arrival_amplitude"])))

        np.testing.assert_allclose(arr_amp1, arr_amp2, rtol=1e-4, atol=1e-4)
