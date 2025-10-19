import pytest
import bellhop as bh



def test_arrivals():
    """Test with default settings to calculate arrival times. Just check that there are no execution errors.
    """

    env = bh.create_env()
    arr = bh.compute_arrivals(env,debug=True,fname_base="tmp")
    #print(arr)



def test_eigenrays():
    """Test with default settings to calculate eigenrays. Just check that there are no execution errors.
    """

    env = bh.create_env()
    rays = bh.compute_eigenrays(env)
    #print(rays)



def test_rays():
    """Test with default settings to calculate rays. Just check that there are no execution errors.
    """

    env = bh.create_env()
    rays = bh.compute_rays(env)
    #print(rays)



def test_tl():
    """Test with default settings to calculate transmission loss. Just check that there are no execution errors.
    """

    env = bh.create_env()
    tl = bh.compute_transmission_loss(env)
    #print(tl)


