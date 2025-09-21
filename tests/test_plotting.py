import pytest
import bellhop as bh
import numpy as np


def test_plot_env():
    """Test plot_env function with default environment. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    bh.plot_env(env)


def test_plot_env_complex():
    """Test plot_env function with complex environment. Just check that there are no execution errors.
    """
    env = bh.create_env2d(depth=[[0, 40], [100, 30], [500, 35], [700, 20], [1000, 45]])
    bh.plot_env(env)


def test_plot_ssp():
    """Test plot_ssp function with default environment. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    bh.plot_ssp(env)


def test_plot_ssp_complex():
    """Test plot_ssp function with complex sound speed profile. Just check that there are no execution errors.
    """
    env = bh.create_env2d(soundspeed=[[0, 1540], [10, 1530], [20, 1532], [25, 1533], [30, 1535]])
    bh.plot_ssp(env)


def test_plot_arrivals():
    """Test plot_arrivals function with computed arrivals. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    arrivals = bh.compute_arrivals(env)
    bh.plot_arrivals(arrivals)


def test_plot_arrivals_db():
    """Test plot_arrivals function in dB scale. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    arrivals = bh.compute_arrivals(env)
    bh.plot_arrivals(arrivals, dB=True)


def test_plot_rays():
    """Test plot_rays function with computed rays. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    rays = bh.compute_rays(env)
    bh.plot_rays(rays)


def test_plot_rays_with_env():
    """Test plot_rays function with environment overlay. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    rays = bh.compute_eigenrays(env)
    bh.plot_rays(rays, env=env)


def test_plot_rays_inverted():
    """Test plot_rays function with inverted colors. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    rays = bh.compute_eigenrays(env)
    bh.plot_rays(rays, invert_colors=True)


def test_plot_transmission_loss():
    """Test plot_transmission_loss function with computed transmission loss. Just check that there are no execution errors.
    """
    env = bh.create_env2d(
        rx_depth=np.arange(0, 25),
        rx_range=np.arange(0, 1000),
        min_angle=-45,
        max_angle=45
    )
    tloss = bh.compute_transmission_loss(env)
    bh.plot_transmission_loss(tloss)


def test_plot_transmission_loss_with_env():
    """Test plot_transmission_loss function with environment overlay. Just check that there are no execution errors.
    """
    env = bh.create_env2d(
        rx_depth=np.arange(0, 25),
        rx_range=np.arange(0, 1000),
        min_angle=-45,
        max_angle=45
    )
    tloss = bh.compute_transmission_loss(env)
    bh.plot_transmission_loss(tloss, env=env)


def test_pyplot_env():
    """Test pyplot_env function with default environment. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    bh.pyplot_env(env)


def test_pyplot_env_complex():
    """Test pyplot_env function with complex environment. Just check that there are no execution errors.
    """
    env = bh.create_env2d(depth=[[0, 40], [100, 30], [500, 35], [700, 20], [1000, 45]])
    bh.pyplot_env(env)


def test_pyplot_ssp():
    """Test pyplot_ssp function with default environment. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    bh.pyplot_ssp(env)


def test_pyplot_ssp_complex():
    """Test pyplot_ssp function with complex sound speed profile. Just check that there are no execution errors.
    """
    env = bh.create_env2d(soundspeed=[[0, 1540], [10, 1530], [20, 1532], [25, 1533], [30, 1535]])
    bh.pyplot_ssp(env)


def test_pyplot_arrivals():
    """Test pyplot_arrivals function with computed arrivals. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    arrivals = bh.compute_arrivals(env)
    bh.pyplot_arrivals(arrivals)


def test_pyplot_arrivals_db():
    """Test pyplot_arrivals function in dB scale. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    arrivals = bh.compute_arrivals(env)
    bh.pyplot_arrivals(arrivals, dB=True)


def test_pyplot_rays():
    """Test pyplot_rays function with computed rays. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    rays = bh.compute_rays(env)
    bh.pyplot_rays(rays)


def test_pyplot_rays_with_env():
    """Test pyplot_rays function with environment overlay. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    rays = bh.compute_eigenrays(env)
    bh.pyplot_rays(rays, env=env)


def test_pyplot_rays_inverted():
    """Test pyplot_rays function with inverted colors. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    rays = bh.compute_eigenrays(env)
    bh.pyplot_rays(rays, invert_colors=True)


def test_pyplot_transmission_loss():
    """Test pyplot_transmission_loss function with computed transmission loss. Just check that there are no execution errors.
    """
    env = bh.create_env2d(
        rx_depth=np.arange(0, 25),
        rx_range=np.arange(0, 1000),
        min_angle=-45,
        max_angle=45
    )
    tloss = bh.compute_transmission_loss(env)
    bh.pyplot_transmission_loss(tloss)


def test_pyplot_transmission_loss_with_env():
    """Test pyplot_transmission_loss function with environment overlay. Just check that there are no execution errors.
    """
    env = bh.create_env2d(
        rx_depth=np.arange(0, 25),
        rx_range=np.arange(0, 1000),
        min_angle=-45,
        max_angle=45
    )
    tloss = bh.compute_transmission_loss(env)
    bh.pyplot_transmission_loss(tloss, env=env)