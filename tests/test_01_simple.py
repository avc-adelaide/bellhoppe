import pytest
import arlpy.uwapm as pm



def test_arrivals():
    """Test with default settings to calculate arrival times. Just check that there are no execution errors.
    """

    env = pm.create_env2d()
    arr = pm.compute_arrivals(env)
    print(arr)



def test_eigenrays():
    """Test with default settings to calculate eigenrays. Just check that there are no execution errors.
    """

    env = pm.create_env2d()
    rays = pm.compute_eigenrays(env)
    print(rays)


