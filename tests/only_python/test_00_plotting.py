import pytest
import bellhop as bh
import bellhop.plot as bhp
import numpy as np

import bokeh.plotting

# Avoid the tests opening up the images, thanks ChatGPT:
@pytest.fixture(autouse=True)
def no_bokeh_show(monkeypatch):
    """Disable bokeh.plotting.show() during tests."""
    monkeypatch.setattr(bokeh.plotting, "show", lambda *a, **k: None)


def test_plot_env():
    """Test plot_env function with default environment. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    bhp.plot_env(env)


def test_plot_env_complex():
    """Test plot_env function with complex environment. Just check that there are no execution errors.
    """
    env = bh.create_env2d(depth=[[0, 40], [100, 30], [500, 35], [700, 20], [1000, 45]])
    bhp.plot_env(env)


def test_plot_ssp():
    """Test plot_ssp function with default environment. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    bhp.plot_ssp(env)


def test_plot_ssp_complex():
    """Test plot_ssp function with complex sound speed profile. Just check that there are no execution errors.
    """
    env = bh.create_env2d(soundspeed=[[0, 1540], [10, 1530], [20, 1532], [25, 1533], [30, 1535]])
    bhp.plot_ssp(env)


def test_plot_arrivals():
    """Test plot_arrivals function with computed arrivals. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    arrivals = bh.compute_arrivals(env)
    bhp.plot_arrivals(arrivals)


def test_plot_arrivals_db():
    """Test plot_arrivals function in dB scale. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    arrivals = bh.compute_arrivals(env)
    bhp.plot_arrivals(arrivals, dB=True)


def test_plot_rays():
    """Test plot_rays function with computed rays. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    rays = bh.compute_rays(env)
    bhp.plot_rays(rays)


def test_plot_rays_with_env():
    """Test plot_rays function with environment overlay. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    rays = bh.compute_eigenrays(env)
    bhp.plot_rays(rays, env=env)


def test_plot_rays_inverted():
    """Test plot_rays function with inverted colors. Just check that there are no execution errors.
    """
    env = bh.create_env2d()
    rays = bh.compute_eigenrays(env)
    bhp.plot_rays(rays, invert_colors=True)


def test_plot_transmission_loss():
    """Test plot_transmission_loss function with computed transmission loss. Just check that there are no execution errors.
    """
    env = bh.create_env2d(
        receiver_depth=np.arange(0, 25),
        receiver_range=np.arange(0, 1000),
        beam_angle_min=-45,
        beam_angle_max=45
    )
    tloss = bh.compute_transmission_loss(env)
    bhp.plot_transmission_loss(tloss)


def test_plot_transmission_loss_with_env():
    """Test plot_transmission_loss function with environment overlay. Just check that there are no execution errors.
    """
    env = bh.create_env2d(
        receiver_depth=np.arange(0, 25),
        receiver_range=np.arange(0, 1000),
        beam_angle_min=-45,
        beam_angle_max=45
    )
    tloss = bh.compute_transmission_loss(env)
    bhp.plot_transmission_loss(tloss, env=env)


