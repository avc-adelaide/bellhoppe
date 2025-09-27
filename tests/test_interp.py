import pytest
import bellhop as bh
import pandas as pd
import pandas.testing as pdt
import os

skip_if_coverage = pytest.mark.skipif(
    os.getenv("COVERAGE_RUN") == "true",
    reason="Skipped during coverage run"
)


# Define depth-dependent sound speed profile as specified in issue
ssp = [
    [ 0, 1540],  # 1540 m/s at the surface
    [10, 1530],  # 1530 m/s at 10 m depth
    [20, 1532],  # 1532 m/s at 20 m depth
    [25, 1533],  # 1533 m/s at 25 m depth
    [30, 1535]   # 1535 m/s at the seabed
]

# Create environment with variable sound speed profile
env = bh.create_env2d(soundspeed=ssp, depth=30, soundspeed_interp="linear", beam_angle_min=-80, beam_angle_max=80)

# Compute arrivals
arrivals = bh.compute_arrivals(env)
arrival_times = arrivals["time_of_arrival"]
print(arrival_times)
t_arr_exp = pd.Series([
    0.696581,
    0.692154,
    0.683810,
    0.680058,
    0.680058,
    0.673070,
    0.670030,
    0.664451,
    0.662158,
    0.658011,
    0.656496,
    0.653638,
    0.653623,
    0.653542,
    0.655967,
    0.657310,
    0.657310,
    0.661181,
    0.663332,
    0.668653,
    0.671564,
    0.678310,
    0.681941,
    0.690056,
    0.694371,
])


@skip_if_coverage
def test_interp_linear():
    """Test BELLHOP with depth-dependent sound speed profile and linear interpolation.

    This is exactly the same test as `test_variable_soundspeed()` in `test_simple.py` but
    with linear interpolation instead of spline. There are a different number of arrivals
    with slightly different arrival times.
    """
    pdt.assert_series_equal(
      arrival_times, t_arr_exp,
      check_index=False,
      check_names=False,
      atol=1e-4,  # absolute tolerance
      rtol=1e-4,  # relative tolerance
    )
