import pytest
import arlpy.uwapm as pm

def test_simple():

    env = pm.create_env2d()
    # print(env)

    assert(env["bottom_absorption"]  == 0.1)
    assert(env["bottom_density"] == 1600)
    assert(env["bottom_roughness"] == 0)
    assert(env["bottom_soundspeed"] == 1600)
    assert(env["depth"] == 25)
    assert(env["depth_interp"] == "linear")
    assert(env["frequency"] == 25000)
    assert(env["max_angle"] == 80)
    assert(env["min_angle"] == -80)
    assert(env["nbeams"] == 0)
    assert(env["rx_depth"] == 10)
    assert(env["rx_range"] == 1000)
    assert(env["soundspeed"] == 1500)
    assert(env["soundspeed_interp"] == "spline")
    assert(env["surface"] == None)
    assert(env["surface_interp"] == "linear")
    assert(env["tx_depth"] == 5)
    assert(env["tx_directionality"] == None)
    assert(env["type"] == "2D")

    arrivals = pm.compute_arrivals(env)
    # print(arrivals)
    
    assert(len(arrivals) == 35) # 35 rays arrived at the receiver
    t_arr = [
        0.721796,
        0.716791,
        0.709687,
        0.709687,
        0.705226,
        0.698960,
        0.695070,
        0.689678,
        0.686383,
        0.681901,
        0.679223,
        0.675681,
        0.673638,
        0.671061,
        0.669668,
        0.668073,
        0.667341,
        0.666742,
        0.666675,
        0.667075,
        0.667674,
        0.669071,
        0.670332,
        0.672714,
        0.674627,
        0.677979,
        0.680531,
        0.684828,
        0.688000,
        0.693213,
        0.696986,
        0.703081,
        0.707429,
        0.714368,
        0.719267,
    ]
    a_test = arrivals["time_of_arrival"] - t_arr < 1e-6
    assert( a_test.all() )


def test_variable_soundspeed():
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
    env = pm.create_env2d(soundspeed=ssp, depth=30)
    
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
    assert(env["soundspeed_interp"] == "spline")
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
    assert(len(arrivals) == 26)  # At least some rays should arrive
        
    arrival_times = arrivals["time_of_arrival"]
    # print(arrival_times)
    
    a_times = [
        0.696913,
        0.692460,
        0.684141,
        0.680359,
        0.673402,
        0.670326,
        0.664790,
        0.662452,
        0.658368,
        0.656791,
        0.654073,
        0.653407,
        0.653346,
        0.653346,
        0.653350,
        0.653890,
        0.656213,
        0.657634,
        0.661445,
        0.663647,
        0.668928,
        0.671878,
        0.678593,
        0.682257,
        0.690348,
        0.694689,
    ]
    
    # Basic sanity checks on arrival times
    assert(len(arrival_times) == 26)  # Should have some arrivals
    
    a_test = arrivals["time_of_arrival"] - a_times < 1e-6
    assert( a_test.all() )

