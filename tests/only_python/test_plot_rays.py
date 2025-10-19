import pytest
import bellhop as bh
import bellhop.plot as bhp
import numpy as np
import bokeh.plotting
import os

output_dir = "tests/only_python/_tmp/"

# Create the directory and all intermediate directories if needed
os.makedirs(output_dir, exist_ok=True)
# Avoid the tests opening up the images, thanks ChatGPT:
@pytest.fixture(autouse=True)
def no_bokeh_show(monkeypatch):
    """Disable bokeh.plotting.show() during tests."""
    monkeypatch.setattr(bokeh.plotting, "show", lambda *a, **k: None)


def test_plot_rays():
    """Test plot_env function with complex environment. Just check that there are no execution errors.
    """
    dp = [[0, 40], [100, 30], [500, 35], [700, 20], [1000, 45]]
    rr = np.linspace(0,1000,1001)
    sf = np.array([[r, 0.5+0.5*np.sin(2*np.pi*0.005*r)] for r in rr]) # must be 0 at highest point

    env = bh.create_env(
            depth=dp,
            surface=sf,
            beam_num=100,
            receiver_range=1000,
          )
    rays = bh.compute_rays(env)

    with bhp.figure() as f:
        bhp.plot_rays(rays)
        bhp.plot_env(env)
        bokeh.plotting.output_file(output_dir+"env_rays.html")
        bokeh.plotting.save(f)

def test_plot_rays_long():
    """Test plot_env function with complex environment. Just check that there are no execution errors.
    """
    dp = 50
    env = bh.create_env(
            depth=dp,
            beam_num=100,
            receiver_range=20000,
          )
    rays = bh.compute_rays(env)

    with bhp.figure() as f:
        bhp.plot_rays(rays)
        bhp.plot_env(env)
        bokeh.plotting.output_file(output_dir+"env_rays_long.html")
        bokeh.plotting.save(f)
