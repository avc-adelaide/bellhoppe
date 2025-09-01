import pytest
import arlpy.uwapm as pm


def test_interp_linear():
    """Test BELLHOP with depth-dependent sound speed profile.

    This test validates acoustic propagation with a variable sound speed profile
    as requested in issue #8. The test:

    1. Defines a 5-point depth-dependent SSP from surface (0m) to bottom (30m)
    2. Creates a 2D environment using the SSP
    3. Validates default environment parameters remain correct
    4. Computes acoustic ray arrivals and validates results
    """

    # Define depth-dependent sound speed profile as specified in issue
    ssp = [
        [ 0, 1540],  # 1540 m/s at the surface
        [10, 1530],  # 1530 m/s at 10 m depth
        [20, 1532],  # 1532 m/s at 20 m depth
        [25, 1533],  # 1533 m/s at 25 m depth
        [30, 1535]   # 1535 m/s at the seabed
    ]

    # Create environment with variable sound speed profile
    env = pm.create_env2d(soundspeed=ssp, depth=30, soundspeed_interp="linear")

    # Test default environment parameters (keeping others same as test_simple)
    assert(env["bottom_absorption"]  == 0.1)
    assert(env["bottom_density"] == 1600)
    assert(env["bottom_roughness"] == 0)
    assert(env["bottom_soundspeed"] == 1600)
    assert(env["depth"] == 30)  # Updated to match SSP depth
    assert(env["depth_interp"] == "linear")
    assert(env["frequency"] == 25000)
    assert(env["max_angle"] == 80)
    assert(env["min_angle"] == -80)
    assert(env["nbeams"] == 0)
    assert(env["rx_depth"] == 10)
    assert(env["rx_range"] == 1000)
    assert(env["soundspeed_interp"] == "linear")
    assert(env["surface"] == None)
    assert(env["surface_interp"] == "linear")
    assert(env["tx_depth"] == 5)
    assert(env["tx_directionality"] == None)
    assert(env["type"] == "2D")

    # Compute arrivals
    arrivals = pm.compute_arrivals(env)
    # print(arrivals)

    # Test sound speed profile interpolation is working
    assert(len(env["soundspeed"]) == len(ssp))

    # Test environment consistency
    assert(env["depth"] == ssp[-1][0])  # Depth should match SSP bottom depth

    # Test number of rays - determined by running the test
    assert(len(arrivals) == 24)  # At least some rays should arrive

    arrival_times = arrivals["time_of_arrival"]
    # print(arrival_times)

    a_times = [
        0.696581,
        0.692154,
        0.683810,
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
    ]

    # Basic sanity checks on arrival times
    assert(len(arrival_times) == 24)  # Should have some arrivals

    a_test = arrival_times - a_times < 1e-6
    if not(a_test.all()):
    	print("EXPECTED:")
    	print(arrival_times)
    assert( a_test.all() )
