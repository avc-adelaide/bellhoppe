import pytest
import aubellhop as bh
import aubellhop.pyplot as bhp
import numpy as np

def test_pyplot_env2d():
    """Test pyplot_env2d function with default environment. Just check that there are no execution errors.
    """
    env = bh.Environment()
    bhp.pyplot_env2d(env)


def test_pyplot_env2d_complex():
    """Test pyplot_env2d function with complex environment. Just check that there are no execution errors.
    """
    env = bh.Environment(bottom_depth=[[0, 40], [100, 30], [500, 35], [700, 20], [1000, 45]])
    bhp.pyplot_env2d(env)


def test_pyplot_ssp():
    """Test pyplot_ssp function with default environment. Just check that there are no execution errors.
    """
    env = bh.Environment()
    bhp.pyplot_ssp(env)


def test_pyplot_ssp_complex():
    """Test pyplot_ssp function with complex sound speed profile. Just check that there are no execution errors.
    """
    env = bh.Environment(bottom_depth=30,soundspeed=[[0, 1540], [10, 1530], [20, 1532], [25, 1533], [30, 1535]])
    bhp.pyplot_ssp(env)


def test_pyplot_arrivals():
    """Test pyplot_arrivals function with computed arrivals. Just check that there are no execution errors.
    """
    env = bh.Environment()
    arrivals = bh.compute_arrivals(env)
    bhp.pyplot_arrivals(arrivals)


def test_pyplot_arrivals_db():
    """Test pyplot_arrivals function in dB scale. Just check that there are no execution errors.
    """
    env = bh.Environment()
    arrivals = bh.compute_arrivals(env)
    bhp.pyplot_arrivals(arrivals, dB=True)


def test_pyplot_rays():
    """Test pyplot_rays function with computed rays. Just check that there are no execution errors.
    """
    env = bh.Environment()
    rays = bh.compute_rays(env)
    bhp.pyplot_rays(rays)


def test_pyplot_rays_with_env():
    """Test pyplot_rays function with environment overlay. Just check that there are no execution errors.
    """
    env = bh.Environment()
    rays = bh.compute_eigenrays(env)
    bhp.pyplot_rays(rays, env=env)


def test_pyplot_rays_inverted():
    """Test pyplot_rays function with inverted colors. Just check that there are no execution errors.
    """
    env = bh.Environment()
    rays = bh.compute_eigenrays(env)
    bhp.pyplot_rays(rays, invert_colors=True)


def test_pyplot_transmission_loss():
    """Test pyplot_transmission_loss function with computed transmission loss. Just check that there are no execution errors.
    """
    env = bh.Environment(
        receiver_depth=np.arange(0, 25),
        receiver_range=np.arange(0, 1000),
        beam_angle_min=-45,
        beam_angle_max=45
    )
    tloss = bh.compute_transmission_loss(env)
    bhp.pyplot_transmission_loss(tloss)


def test_pyplot_transmission_loss_with_env():
    """Test pyplot_transmission_loss function with environment overlay. Just check that there are no execution errors.
    """
    env = bh.Environment(
        receiver_depth=np.arange(0, 25),
        receiver_range=np.arange(0, 1000),
        beam_angle_min=-45,
        beam_angle_max=45
    )
    tloss = bh.compute_transmission_loss(env)
    bhp.pyplot_transmission_loss(tloss, env=env)
