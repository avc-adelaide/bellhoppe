import pytest
import bellhop.bellhop as pm



def test_arrivals():
    """Test with default settings to calculate arrival times. Just check that there are no execution errors.
    """

    env = pm.create_env2d()
    arr = pm.compute_arrivals(env)
    #print(arr)



def test_eigenrays():
    """Test with default settings to calculate eigenrays. Just check that there are no execution errors.
    """

    env = pm.create_env2d()
    rays = pm.compute_eigenrays(env)
    #print(rays)



def test_rays():
    """Test with default settings to calculate rays. Just check that there are no execution errors.
    """

    env = pm.create_env2d()
    rays = pm.compute_rays(env)
    #print(rays)



def test_tl():
    """Test with default settings to calculate transmission loss. Just check that there are no execution errors.
    """

    env = pm.create_env2d()
    tl = pm.compute_transmission_loss(env)
    #print(tl)


