import pytest
import bellhop as bh
import bellhop.pyplot as bhp
import numpy as np

def test_pyplot_env():
    """Test pyplot_env function with default environment. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    bhp.pyplot_env(env)


def test_pyplot_env_complex():
    """Test pyplot_env function with complex environment. Just check that there are no execution errors.
    """
    env = bh.create_env2d(depth=[[0, 40], [100, 30], [500, 35], [700, 20], [1000, 45]])
    bhp.pyplot_env(env)


def test_pyplot_ssp():
    """Test pyplot_ssp function with default environment. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    bhp.pyplot_ssp(env)


def test_pyplot_ssp_complex():
    """Test pyplot_ssp function with complex sound speed profile. Just check that there are no execution errors.
    """
    env = bh.create_env2d(soundspeed=[[0, 1540], [10, 1530], [20, 1532], [25, 1533], [30, 1535]])
    bhp.pyplot_ssp(env)


def test_pyplot_arrivals():
    """Test pyplot_arrivals function with computed arrivals. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    arrivals = bh.compute_arrivals(env)
    bhp.pyplot_arrivals(arrivals)


def test_pyplot_arrivals_db():
    """Test pyplot_arrivals function in dB scale. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    arrivals = bh.compute_arrivals(env)
    bhp.pyplot_arrivals(arrivals, dB=True)


def test_pyplot_rays():
    """Test pyplot_rays function with computed rays. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    rays = bh.compute_rays(env)
    bhp.pyplot_rays(rays)


def test_pyplot_rays_with_env():
    """Test pyplot_rays function with environment overlay. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    rays = bh.compute_eigenrays(env)
    bhp.pyplot_rays(rays, env=env)


def test_pyplot_rays_inverted():
    """Test pyplot_rays function with inverted colors. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    rays = bh.compute_eigenrays(env)
    bhp.pyplot_rays(rays, invert_colors=True)


def test_pyplot_transmission_loss():
    """Test pyplot_transmission_loss function with computed transmission loss. Just check that there are no execution errors.
    """
    env = bh.create_env2d(
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
    env = bh.create_env2d(
        receiver_depth=np.arange(0, 25),
        receiver_range=np.arange(0, 1000),
        beam_angle_min=-45,
        beam_angle_max=45
    )
    tloss = bh.compute_transmission_loss(env)
    bhp.pyplot_transmission_loss(tloss, env=env)
