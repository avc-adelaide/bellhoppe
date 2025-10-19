import pytest
import bellhop as bh



def test_arrivals():
    """Test with default settings to calculate arrival times. Just check that there are no execution errors.
    """

    env = bh.create_env()
    arr = bh.compute_arrivals(env, model="bellhop")
    #print(arr)

def test_arrivals_bad_model():
    """Test with default settings to calculate arrival times. Catch error for unknown model.
    """

    with pytest.raises(ValueError, match=r"Unknown model"):
        env = bh.create_env()
        arr = bh.compute_arrivals(env, model="bellhop_not_found")


def test_arrivals_no_model():
    """Test with default settings to calculate arrival times. Catch error for no model found.
    """

    saved_models = bh.main._models.copy()  # snapshot
    try:
        bh.main._models.clear()
        with pytest.raises(ValueError, match=r"No suitable propagation model"):
            env = bh.create_env()
            arr = bh.compute_arrivals(env, debug=True)
    finally:
        bh.main._models[:] = saved_models  # restore contents in place



def test_eigenrays():
    """Test with default settings to calculate eigenrays. Just check that there are no execution errors.
    """

    env = bh.create_env()
    rays = bh.compute_eigenrays(env, model="bellhop")
    #print(rays)



def test_rays():
    """Test with default settings to calculate rays. Just check that there are no execution errors.
    """

    env = bh.create_env()
    rays = bh.compute_rays(env, model="bellhop")
    #print(rays)



def test_tl():
    """Test with default settings to calculate transmission loss. Just check that there are no execution errors.
    """

    env = bh.create_env()
    tl = bh.compute_transmission_loss(env, model="bellhop")
    #print(tl)


