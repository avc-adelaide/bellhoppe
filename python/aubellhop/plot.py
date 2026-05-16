"""Plotting functions for aubellhop.
"""

from __future__ import annotations

from typing import Any
from sys import float_info as _fi

import numpy as np
import scipy.interpolate as _interp
import pandas as pd

import matplotlib.pyplot as _pyplt
import matplotlib.colors as _mplc

from .environment import Environment
from .constants import BHStrings
from .plotutils import figure as figure

import aubellhop.plotutils as _plt


def plot_env(env: Environment,
             surface_color: str = 'dodgerblue',
             bottom_color: str = 'peru',
             source_color: str = 'orangered',
             receiver_color: str = 'midnightblue',
             receiver_plot: bool | None = None,
             **kwargs: Any
            ) -> None:
    """Plots a visual representation of the environment.

    Parameters
    ----------
    env : dict
        Environment description
    surface_color : str, default='dodgerblue'
        Color of the surface (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    bottom_color : str, default='peru'
        Color of the bottom (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    source_color : str, default='orangered'
        Color of transmitters (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    receiver_color : str, default='midnightblue'
        Color of receivers (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    receiver_plot : bool, optional
        True to plot all receivers, False to not plot any receivers, None to automatically decide
    **kwargs
        Other keyword arguments applicable for `bellhop.plot.plot()` are also supported

    Notes
    -----
    The surface, bottom, transmitters (marker: '*') and receivers (marker: 'o')
    are plotted in the environment. If `receiver_plot` is set to None and there are
    more than 2000 receivers, they are not plotted.

    Examples
    --------
    >>> import aubellhop as bh
    >>> env = bh.Environment(bottom_depth=[[0, 40], [100, 30], [500, 35], [700, 20], [1000,45]])
    >>> bh.plot_env(env)
    """

    if env is not None:
        env.check()

    min_x = 0.0
    max_x = float(np.max(env['receiver_range']))
    if max_x-min_x > 10000:
        divisor = 1000.0
        min_x /= divisor
        max_x /= divisor
        xlabel = 'Range (km)'
    else:
        divisor = 1.0
        xlabel = 'Range (m)'
    if np.size(env['surface']) == 1:
        min_y = 0
    else:
        min_y = np.min(env['surface'][:,1])
    max_y = env['_depth_max']
    mgn_x = 0.01*(max_x-min_x)
    mgn_y = 0.1*(max_y-min_y)

    oh = _plt.hold()
    if np.size(env['surface']) == 1:
        xx = [min_x, max_x]
        yy = [0, 0]
    else:
        # linear and curvilinear options use the same altimetry, just with different normals
        s = env['surface']
        xx = s[:,0]/divisor
        yy = -s[:,1]
    _plt.plot(xx, yy, xlabel=xlabel, ylabel='Depth (m)', xlim=(min_x-mgn_x, max_x+mgn_x), ylim=(-max_y-mgn_y, -min_y+mgn_y), color=surface_color, **kwargs)

    if np.size(env['bottom_depth']) == 1:
        xx = [min_x, max_x]
        yy = [-env['bottom_depth'], -env['bottom_depth']]
    else:
        # linear and curvilinear options use the same bathymetry, just with different normals
        s = env['bottom_depth']
        xx = s[:,0]/divisor
        yy = -s[:,1]
    _plt.plot(xx, yy, color=bottom_color)

    txd = env['source_depth']
    _plt.plot([0]*np.size(txd), -txd, marker='*', style='solid', color=source_color)

    if receiver_plot is None:
        receiver_plot = np.size(env['receiver_depth'])*np.size(env['receiver_range']) < 2000
    if receiver_plot:
        rxr = env['receiver_range']
        if np.size(rxr) == 1:
            rxr = [rxr]
        for r in np.array(rxr):
            rxd = env['receiver_depth']
            _plt.plot([r/divisor]*np.size(rxd), -rxd, marker='o', style='solid', color=receiver_color)

    _plt.hold(oh if oh is not None else False)

def plot_ssp(env: Environment, **kwargs: Any) -> None:
    """Plots the sound speed profile.

    Parameters
    ----------
    env : dict
        Environment description
    **kwargs
        Other keyword arguments applicable for `bellhop.plot.plot()` are also supported

    Notes
    -----
    If the sound speed profile is range-dependent, this function only plots the first profile.

    Examples
    --------
    >>> import aubellhop as bh
    >>> env = bh.Environment(soundspeed=[[ 0, 1540], [10, 1530], [20, 1532], [25, 1533], [30, 1535]])
    >>> bh.plot_ssp(env)
    """

    if env is not None:
        env.check()

    oh = _plt.hold()
    svp = env['soundspeed']
    if isinstance(svp, pd.DataFrame):
        svp = np.hstack((np.array([svp.index]).T, np.asarray(svp)))
    if env['soundspeed_interp'] == BHStrings.spline:
        ynew = np.linspace(np.min(svp[:,0]), np.max(svp[:,0]), 100)
        tck = _interp.splrep(svp[:,0], svp[:,1], s=0)
        xnew = _interp.splev(ynew, tck, der=0)
        _plt.plot(xnew, -ynew, xlabel='Soundspeed (m/s)', ylabel='Depth (m)', hold=True, **kwargs)
        _plt.scatter(svp[:,1], -svp[:,0], **kwargs)
    else:
        for rr in range(1,svp.shape[1]):
            _plt.plot(svp[:,rr], -svp[:,0], xlabel='Soundspeed (m/s)', ylabel='Depth (m)', legend=f'Range {rr}', **kwargs)
    _plt.hold(oh if oh is not None else False)

def plot_arrivals(arrivals: Any, dB: bool = False, color: str = 'blue', **kwargs: Any) -> None:
    """Plots the arrival times and amplitudes.

    Parameters
    ----------
    arrivals : pandas.DataFrame
        Arrivals times (s) and coefficients
    dB : bool, default=False
        True to plot in dB, False for linear scale
    color : str, default='blue'
        Line color (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    **kwargs
        Other keyword arguments applicable for `bellhop.plot.plot()` are also supported

    Examples
    --------
    >>> import aubellhop as bh
    >>> env = bh.Environment()
    >>> arrivals = bh.compute_arrivals(env)
    >>> bh.plot_arrivals(arrivals)
    """

    t0 = min(arrivals.time_of_arrival)
    t1 = max(arrivals.time_of_arrival)
    oh = _plt.hold()
    if dB:
        min_y = 20*np.log10(np.max(np.abs(arrivals.arrival_amplitude)))-60
        ylabel = 'Amplitude (dB)'
    else:
        ylabel = 'Amplitude'
        min_y = 0
    _plt.plot([t0, t1], [min_y, min_y], xlabel='Arrival time (s)', ylabel=ylabel, color=color, **kwargs)
    for _, row in arrivals.iterrows():
        t = row.time_of_arrival.real
        y = np.abs(row.arrival_amplitude)
        if dB:
            y = max(20*np.log10(_fi.epsilon+y), min_y)
        _plt.plot([t, t], [min_y, y], color=color, **kwargs)
    _plt.hold(oh if oh is not None else False)

def plot_rays(rays: pd.DataFrame, env: Environment | None = None, invert_colors: bool = False, **kwargs: Any) -> None:
    """Plots ray paths.

    Parameters
    ----------
    rays : pandas.DataFrame
        Ray paths
    env : dict, optional
        Environment definition
    invert_colors : bool, default=False
        False to use black for high intensity rays, True to use white
    **kwargs
        Other keyword arguments applicable for `bellhop.plot.plot()` are also supported

    Notes
    -----
    If environment definition is provided, it is overlayed over this plot using default
    parameters for `bellhop.plot_env()`.

    Examples
    --------
    >>> import aubellhop as bh
    >>> env = bh.Environment()
    >>> rays = bh.compute_eigenrays(env)
    >>> bh.plot_rays(rays, width=1000)
    """
    rays = rays.sort_values('bottom_bounces', ascending=False)
    dim = rays["ray"].iloc[0][0].shape[0]

    # some edge cases to worry about here: rays.bottom_bounces could be all zeros?
    max_amp = np.max(np.abs(rays.bottom_bounces)) if len(rays.bottom_bounces) > 0 else 0
    max_amp = max_amp or 1

    divisor = 1
    xunits = '(m)'
    r = []
    for _, row in rays.iterrows():
        r += list(row.ray[:,0])
    if max(r)-min(r) > 10000:
        divisor = 1000
        xunits = '(km)'

    oh = _plt.hold()
    for _, row in rays.iterrows():
        rr = float( row.bottom_bounces / (max_amp + 1) ) # avoid rr = 1 == 100% white
        c = 1.0 - rr if invert_colors else rr
        cmap = _pyplt.get_cmap("gray")
        col_str = _mplc.to_hex(cmap(c))
        ax_ind = dim - 1
        _plt.plot(row.ray[:,0]/divisor, -row.ray[:,ax_ind], color=col_str, xlabel='Range '+xunits, ylabel='Depth (m)', **kwargs)
    if env is not None:
        plot_env(env,title=None)
    _plt.hold(oh if oh is not None else False)

def plot_transmission_loss(tloss: Any, env: Environment | None = None, **kwargs: Any) -> None:
    """Plots transmission loss.

    Parameters
    ----------
    tloss : pandas.DataFrame
        Complex transmission loss
    env : dict, optional
        Environment definition
    **kwargs
        Other keyword arguments applicable for `bellhop.plot.image()` are also supported

    Notes
    -----
    If environment definition is provided, it is overlayed over this plot using default
    parameters for `bellhop.plot_env()`.

    Examples
    --------
    >>> import aubellhop as bh
    >>> import numpy as np
    >>> env = bh.Environment(
            receiver_depth=np.arange(0, 25),
            receiver_range=np.arange(0, 1000),
            beam_angle_min=-45,
            beam_angle_max=45
        )
    >>> tloss = bh.compute_transmission_loss(env)
    >>> bh.plot_transmission_loss(tloss, width=1000)
    """

    xr = (min(tloss.columns), max(tloss.columns))
    yr = (-max(tloss.index), -min(tloss.index))
    xlabel = 'Range (m)'
    if xr[1]-xr[0] > 10000:
        xr = (min(tloss.columns)/1000, max(tloss.columns)/1000)
        xlabel = 'Range (km)'
    oh = _plt.hold()
    _plt.image(20*np.log10(_fi.epsilon+np.abs(np.flipud(np.array(tloss)))), x=xr, y=yr, xlabel=xlabel, ylabel='Depth (m)', xlim=xr, ylim=yr, **kwargs)
    if env is not None:
        plot_env(env, receiver_plot=False, title=None)
    _plt.hold(oh if oh is not None else False)


### Export module names for auto-importing in __init__.py

__all__ = [
    name for name in globals() if not name.startswith("_")  # ignore private names
]
