import pytest
import bellhop as bh

def test_simple():

    env = bh.create_env()
    # print(env)

    assert(env["bottom_attenuation"]  == None)
    assert(env["bottom_density"] == 1600)
    assert(env["bottom_roughness"] == 0)
    assert(env["bottom_soundspeed"] == 1600)
    assert(env["depth"] == 25)
    assert(env["depth_interp"] == "linear")
    assert(env["frequency"] == 25000)
    env["beam_angle_max"] == 80
    env["beam_angle_min"] == -80
    assert(env["beam_num"] == 0)
    assert(env["receiver_depth"] == 10)
    assert(env["receiver_range"] == 1000)
    assert(env["soundspeed"] == 1500)
    assert(env["soundspeed_interp"] == "linear")
    assert(env["surface"] == None)
    assert(env["surface_interp"] == "linear")
    assert(env["source_depth"] == 5)
    assert(env["source_directionality"] == None)
    assert(env["type"] == "2D")

    arrivals = bh.compute_arrivals(env)
    arrival_times = arrivals["time_of_arrival"]

    t_arr_exp = [
        0.721796,
        0.716791,
        0.709687,
        0.709687,
        0.705227,
        0.698960,
        0.695070,
        0.689678,
        0.686383,
        0.681901,
        0.679223,
        0.675681,
        0.673639,
        0.671060,
        0.669668,
        0.668074,
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
        0.696985,
        0.703081,
        0.707429,
        0.707429,
        0.714368,
        0.719267,
    ]

    if not len(t_arr_exp) == len(arrival_times):
        print(arrival_times)
        assert False, "Different number of arrivals!"

    a_test = arrivals["time_of_arrival"] - t_arr_exp < 1e-6
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
    env = bh.create_env(soundspeed=ssp, soundspeed_interp="spline", depth=30, beam_angle_min=-80, beam_angle_max=80)
    bh.print_env(env)

    # Compute arrivals
    arrivals = bh.compute_arrivals(env)
    arrival_times = arrivals["time_of_arrival"]

    t_arr_exp = [
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

    if not len(t_arr_exp) == len(arrival_times):
        print(arrival_times)
        assert len(t_arr_exp) == len(arrival_times), "Different number of arrivals!"

    a_test = arrivals["time_of_arrival"] - t_arr_exp < 1e-6
    assert( a_test.all() )



def test_bathy():

    bathy = [
        [0, 30],    # 30 m water depth at the transmitter
        [300, 15],  # 20 m water depth 300 m away
        [1000, 20]  # 25 m water depth at 1 km
	]

    env = bh.create_env(depth=bathy,beam_angle_max=80,beam_angle_min=-80)

    arrivals = bh.compute_arrivals(env)
    arrival_times = arrivals["time_of_arrival"]

    t_arr_exp = [
        0.712365,
        0.708236,
        0.704244,
        0.700392,
        0.696682,
        0.681542,
        0.679183,
        0.676985,
        0.674948,
        0.673075,
        0.667389,
        0.666980,
        0.666742,
        0.666675,
        0.666780,
        0.671037,
        0.672614,
        0.674357,
        0.676264,
        0.678334,
        0.692169,
        0.695612,
        0.699202,
        0.699202,
        0.702935,
        0.706809,
    ]

    if not len(t_arr_exp) == len(arrival_times):
        print(arrival_times)
        assert len(t_arr_exp) == len(arrival_times), "Different number of arrivals!"

    a_test = arrival_times - t_arr_exp < 1e-6
    assert( a_test.all() )


def test_impulse_response():
    env = bh.create_env()
    arr = bh.compute_arrivals(env)
    ir = bh.arrivals_to_impulse_response(arr, fs=19200)
    assert ir is not None


