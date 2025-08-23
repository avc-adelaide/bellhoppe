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

