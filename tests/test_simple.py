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
    
    The SSP represents a typical oceanic sound channel with:
    - Surface speed: 1540 m/s (typical for warm surface water)
    - Minimum at 10m: 1530 m/s (sound channel axis)
    - Recovery toward bottom: 1535 m/s at 30m depth
    
    When arlpy dependencies are available, this test should:
    1. Run successfully and generate actual arrival times
    2. Have the expected_arrival_times list populated with real values
    3. Include exact ray count assertions
    
    To update after first successful run:
    - Replace len(arrivals) > 0 with exact count: assert(len(arrivals) == N)
    - Fill expected_arrival_times list with actual values
    - Uncomment the final exact time comparison section
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
    assert(env["depth"] == 30)  # Updated to match our SSP depth
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
    
    # Verify that soundspeed is now the SSP list instead of a single value
    assert(env["soundspeed"] == ssp)
    
    # Compute arrivals
    arrivals = pm.compute_arrivals(env)
    
    # Test number of rays - this will need to be determined by running the test
    # For now, using a placeholder that should be updated after first successful run
    assert(len(arrivals) > 0)  # At least some rays should arrive
    
    # Expected arrival times - these would need to be determined by running
    # the test once to get the actual values, then hard-coded here
    # Following the same pattern as test_simple.py
    # TODO: Run test to get actual arrival times and update this list
    expected_arrival_times = [
        # Placeholder - to be filled with actual values after first test run
        # Format: arrival times in seconds, sorted
    ]
    
    # For now, just test that we have reasonable arrival times
    arrival_times = arrivals["time_of_arrival"]
    
    # Basic sanity checks on arrival times
    assert(len(arrival_times) > 0)  # Should have some arrivals
    assert((arrival_times > 0).all())  # All times should be positive
    assert((arrival_times < 10).all())  # Should be reasonable times (< 10 seconds)
    
    # Check that times are in reasonable range for 1000m range
    # With speeds around 1530-1540 m/s, expect times around 0.65-0.66 seconds
    assert((arrival_times > 0.6).all())  # Lower bound
    assert((arrival_times < 1.0).all())  # Upper bound
    
    # Additional recommended assertions for comprehensive testing:
    
    # Test that the variable SSP actually affects the results vs constant SSP
    # (This would require running both and comparing - useful for validation)
    
    # Test sound speed profile interpolation is working
    # Verify the environment actually contains our SSP data
    assert(isinstance(env["soundspeed"], list))
    assert(len(env["soundspeed"]) == 5)
    
    # Test that different ray angles produce different arrival times
    # (The variable SSP should cause ray bending and time variations)
    if len(arrival_times) > 1:
        # Should have some variation in arrival times due to ray bending
        time_variation = arrival_times.max() - arrival_times.min()
        assert(time_variation > 1e-6)  # Should have some spread
    
    # Test that ray paths exist and are reasonable
    # This would require additional output from BELLHOP ray files if available
    
    # Test environment consistency
    assert(env["depth"] == ssp[-1][0])  # Depth should match SSP bottom depth
    
    # Verify frequency-dependent behavior could be tested
    # (Though this test uses single frequency like the original)
    
    # TODO: Once actual arrival times are determined, add specific comparison:
    # Steps to complete this test:
    # 1. Run: export PATH="$PWD/bin:$PATH" && hatch run test -v -k test_variable_soundspeed
    # 2. Print arrivals["time_of_arrival"] to get actual values
    # 3. Replace expected_arrival_times = [] with the printed values
    # 4. Update assert(len(arrivals) > 0) with exact count
    # 5. Uncomment and adapt the final comparison section below:
    # 
    # if len(expected_arrival_times) > 0:
    #     assert(len(arrivals) == len(expected_arrival_times))
    #     a_test = arrivals["time_of_arrival"] - expected_arrival_times < 1e-6
    #     assert(a_test.all())

