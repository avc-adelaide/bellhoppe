import pytest
import bellhop as bh
import bellhop.plot as bhp
import numpy as np
import pandas as pd
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


def test_plot_ssp_linear():
    """Test plot_ssp function with complex sound speed profile. Just check that there are no execution errors."""
    env = bh.create_env2d(soundspeed_interp="linear",depth=30,soundspeed=[[0, 1540], [10, 1530], [20, 1532], [25, 1533], [30, 1535]])

    with bhp.figure() as f:
        bhp.plot_ssp(env)
        bokeh.plotting.output_file(output_dir+"ssp_linear.html")
        bokeh.plotting.save(f)

def test_plot_ssp_spline():
    """Test plot_ssp function with complex sound speed profile. Just check that there are no execution errors."""
    env = bh.create_env2d(soundspeed_interp="spline",depth=30,soundspeed=[[0, 1540], [10, 1530], [20, 1532], [25, 1533], [30, 1535]])

    with bhp.figure() as f:
        bhp.plot_ssp(env)
        bokeh.plotting.output_file(output_dir+"ssp_spline.html")
        bokeh.plotting.save(f)

def test_plot_ssp_dataframe():
    """Test plot_ssp function with complex sound speed profile. Just check that there are no execution errors."""
    ssp = pd.DataFrame({ 'depth':[0,10,20,30], 'speed':[1540,1530,1532,1535]})
    env = bh.create_env2d(soundspeed=ssp,depth=30,soundspeed_interp="spline")
    env = bh.check_env2d(env)

    with bhp.figure() as f:
        bhp.plot_ssp(env)
        bokeh.plotting.output_file(output_dir+"ssp_spline_dataframe.html")
        bokeh.plotting.save(f)

def test_plot_ssp_const():
    """Test plot_ssp function with complex sound speed profile. Just check that there are no execution errors."""
    env = bh.create_env2d(soundspeed=1500,depth=30)
    env = bh.check_env2d(env)

    with bhp.figure() as f:
        bhp.plot_ssp(env)
        bokeh.plotting.output_file(output_dir+"ssp_const.html")
        bokeh.plotting.save(f)

def test_plot_ssp_quad():
    """Test plot_ssp function with complex sound speed profile. Just check that there are no execution errors."""
    ssp = pd.DataFrame({
        'ssp1':[1540,1530,1532,1535],
        'ssp2':[1545,1535,1535,1555],
        'ssp3':[1545,1550,1552,1545],
    }, index=[0,10,20,30])
    env = bh.create_env2d(soundspeed=ssp,depth=30,soundspeed_interp="quadrilateral")
    env = bh.check_env2d(env)

    with bhp.figure() as f:
        bhp.plot_ssp(env)
        bokeh.plotting.output_file(output_dir+"ssp_spline_quad.html")
        bokeh.plotting.save(f)
