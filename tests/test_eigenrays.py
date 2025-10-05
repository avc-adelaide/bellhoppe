import pytest
import bellhop as bh



def test_rays_many_source():

    env = bh.create_env2d()
    env = bh.check_env2d(env)
    i1 =  5.0
    i2 = 10.0
    i3 = 15.0
    env['source_depth'] = [5, i2, i3]
    rays = bh.compute_rays(env,source_depth_ndx=0)
    assert rays.iloc[0]["ray"][0][1]==i1, "Ray should be leaving from first source."

    rays = bh.compute_eigenrays(env,source_depth_ndx=1)
    assert rays.iloc[0]["ray"][0][1]==i2, "Ray should be leaving from second source."

    rays = bh.compute_eigenrays(env,source_depth_ndx=2)
    assert rays.iloc[0]["ray"][0][1]==i3, "Ray should be leaving from third source."


def test_eigenrays_many_source():

    env = bh.create_env2d()
    env = bh.check_env2d(env)
    i1 =  5.0
    i2 = 10.0
    i3 = 15.0
    env['source_depth'] = [5, i2, i3]
    rays = bh.compute_eigenrays(env,source_depth_ndx=0)
    assert rays.iloc[0]["ray"][0][1]==i1, "Ray should be leaving from first source."

    rays = bh.compute_eigenrays(env,source_depth_ndx=1)
    assert rays.iloc[0]["ray"][0][1]==i2, "Ray should be leaving from second source."

    rays = bh.compute_eigenrays(env,source_depth_ndx=2)
    assert rays.iloc[0]["ray"][0][1]==i3, "Ray should be leaving from third source."


def test_eigenrays_many_receiver_depth():

    env = bh.create_env2d()
    env = bh.check_env2d(env)
    i1 =  5.0
    i2 = 10.0
    i3 = 15.0
    env['receiver_depth'] = [i1, i2, i3]

    tol = 2.0

    rays = bh.compute_eigenrays(env,receiver_depth_ndx=0)
    assert abs(rays.iloc[0]["ray"][-1][1] - i1) < tol, "Ray should be arriving at first receiver."

    rays = bh.compute_eigenrays(env,receiver_depth_ndx=1)
    assert abs(rays.iloc[0]["ray"][-1][1] - i2) < tol, "Ray should be arriving at second receiver."

    rays = bh.compute_eigenrays(env,receiver_depth_ndx=2)
    assert abs(rays.iloc[0]["ray"][-1][1] - i3) < tol, "Ray should be arriving at third receiver."


def test_eigenrays_many_receiver_ranges():

    env = bh.create_env2d()
    env = bh.check_env2d(env)
    i1 = 1000.0
    i2 = 900.0
    i3 = 800.0
    env['receiver_range'] = [i1, i2, i3]

    tol = 3.0

    rays = bh.compute_eigenrays(env,receiver_range_ndx=0)
    assert abs(rays.iloc[0]["ray"][-1][0] - i1) < tol, "Ray should be arriving at first receiver."

    rays = bh.compute_eigenrays(env,receiver_range_ndx=1)
    assert abs(rays.iloc[0]["ray"][-1][0] - i2) < tol, "Ray should be arriving at second receiver."

    rays = bh.compute_eigenrays(env,receiver_range_ndx=2)
    assert abs(rays.iloc[0]["ray"][-1][0] - i3) < tol, "Ray should be arriving at third receiver."

