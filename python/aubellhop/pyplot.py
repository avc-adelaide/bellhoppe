"""Plotting functions using Matplotlib for aubellhop.
"""

from __future__ import annotations

from typing import Any
from sys import float_info as _fi

import numpy as np
import scipy.interpolate as _interp
import pandas as pd

import matplotlib.pyplot as _pyplt
import matplotlib.colors as _mplc
from matplotlib.axes import Axes

from .constants import BHStrings
from .environment import Environment


def pyplot_env2d(
                 env: Environment,
                 surface_color: str = 'dodgerblue',
                 bottom_color: str = 'peru',
                 source_color: str = 'orangered',
                 receiver_color: str = 'midnightblue',
                 receiver_plot: bool | None = None,
                 fill: bool | None = None,
                 ax: Any | None = None,
                 **kwargs: Any
                ) -> None:
    """Plots a visual representation of the environment with matplotlib.

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

    env.check()

    if ax is None:
        fig = _pyplt.figure()
        ax = fig.add_subplot()

    if np.array(env['receiver_range']).size > 1:
        min_x = np.min(env['receiver_range'])
    else:
        min_x = 0
    max_x = np.max(env['receiver_range'])
    if max_x - min_x > 10000:
        divisor = 1000
        min_x /= divisor
        max_x /= divisor
        range_unit = ' (km)'
    else:
        divisor = 1
        range_unit = ' (m)'
    if np.size(env['surface_depth']) == 1:
        min_y = 0
    else:
        min_y = np.min(env['surface_depth'][:, 1])
    max_y = env['_depth_max']
    mgn_x = 0.01 * (max_x - min_x)
    mgn_y = 0.1 * (max_y - min_y)

    if np.size(env['surface_depth']) == 1:
        surface_x = [min_x, max_x]
        surface_y = [0, 0]
    else:
        surface_x = env['surface_depth'][:, 0] / divisor
        surface_y = env['surface_depth'][:, 1]
    _pyplt.plot(surface_x, surface_y, color=surface_color, **kwargs)

    if np.size(env['bottom_depth']) == 1:
        _pyplt.plot([min_x, max_x], [env['bottom_depth'], env['bottom_depth']], color=bottom_color, **kwargs)
    else:
        _pyplt.plot(env['bottom_depth'][:, 0] / divisor, env['bottom_depth'][:, 1], color=bottom_color, **kwargs)

    txd = env['source_depth']
    _pyplt.plot([0] * np.size(txd), txd, marker='*', markersize=6, color=source_color, **kwargs)

    if receiver_plot is None:
        receiver_plot = np.size(env['receiver_depth']) * np.size(env['receiver_range']) < 2000
    if receiver_plot:
        rxr = env['receiver_range']
        if np.size(rxr) == 1:
            rxr = [rxr]
        for r in np.array(rxr):
            rxd = env['receiver_depth']
            _pyplt.plot([r / divisor] * np.size(rxd), rxd, marker='o', color=receiver_color, **kwargs)

    if fill:
        y0 = 0.0
        _pyplt.axhline(y0, color="w", linestyle="-")
        _pyplt.fill_between(surface_x, surface_y, y0, color="w")

    _pyplt.xlabel('Range'+range_unit)
    _pyplt.ylabel('Depth (m)')
    ax.yaxis.set_inverted(True)
    _pyplt.xlim((min_x - mgn_x, max_x + mgn_x))
    _pyplt.ylim((max_y + mgn_y, min_y - mgn_y))

def pyplot_env3d(env: Environment, surface_color: str = 'dodgerblue', bottom_color: str = 'peru', source_color: str = 'orangered', receiver_color: str = 'midnightblue',
               receiver_plot: bool | None = None, ax: Any | None = None, **kwargs: Any) -> None:
    """Plots a visual representation of the environment with matplotlib.
    """

    env.check()

    if ax is None:
        fig = _pyplt.figure()
        ax = fig.add_subplot(projection='3d')

    if np.array(env['receiver_range']).size > 1:
        min_x = np.min(env['receiver_range'])
    else:
        min_x = 0
    max_x = env['simulation_range']
    min_y = -env['simulation_cross_range']
    max_y = +env['simulation_cross_range']
    xdivisor = 1
    ydivisor = 1
    xrange_unit = ' (m)'
    yrange_unit = ' (m)'
    if max_x - min_x > 10000:
        xdivisor = 1000
        min_x /= xdivisor
        max_x /= xdivisor
        xrange_unit = ' (km)'
    if max_y - min_y > 10000:
        ydivisor = 1000
        min_y /= ydivisor
        max_y /= ydivisor
        yrange_unit = ' (km)'
    if np.size(env['surface_depth']) == 1:
        min_z = 0
    else:
        min_z = np.min(env['surface_depth'][:, 1])
    max_z = env['simulation_depth']
    mgn_x = 0.01 * (max_x - min_x)
    mgn_z = 0.1 * (max_z - min_z)

    if np.size(env['surface_depth']) == 1:
        z = float(env['surface_depth'])
        X, Y = np.meshgrid([min_x, max_x], [min_y, max_y])
        Z = np.full_like(X, z)
        ax.plot_surface(X, Y, Z, color=surface_color, alpha=0.3, **kwargs)
    else:
        _pyplt.plot(env['surface_depth'][:, 0] / xdivisor, env['surface_depth'][:, 1], color=surface_color, **kwargs)

    if np.size(env['bottom_depth']) == 1:
        z = float(env['bottom_depth'])
        X, Y = np.meshgrid([min_x, max_x], [min_y, max_y])
        Z = np.full_like(X, z)
        ax.plot_surface(X, Y, Z, color=bottom_color, alpha=0.3, **kwargs)
    else:
        _pyplt.plot(env['bottom_depth'][:, 0] / xdivisor, env['bottom_depth'][:, 1], color=bottom_color, **kwargs)

    if env._source_num == 1:
        _pyplt.plot(
            env['source_range'] / xdivisor,
            env['source_cross_range'] / ydivisor,
            env['source_depth'],
            marker='*',
            markersize=6,
            color=source_color,
            **kwargs,
        )
    else:
        print("MULTIPLE SOURCES NOT IMPLEMENTED YET")

    if env._source_num == 1:
        _pyplt.plot(
            env['receiver_range'] * np.cos(env['receiver_bearing']) / xdivisor,
            env['receiver_range'] * np.sin(env['receiver_bearing']) / ydivisor,
            env['receiver_depth'],
            marker='o',
            markersize=6,
            color=receiver_color,
            **kwargs,
        )
    else:
        print("MULTIPLE RECEIVERS NOT IMPLEMENTED YET")

    ax.set_xlabel('Range'+xrange_unit)
    ax.set_ylabel('Cross range'+yrange_unit)
    ax.set_zlabel('Depth (m)')
    ax.yaxis.set_inverted(True)
    ax.set_xlim([min_x - mgn_x, max_x + mgn_x])
    ax.set_ylim([min_y, max_y])
    ax.set_zlim([max_z + mgn_z, min_z - mgn_z])

def pyplot_ssp(env: Environment, ax: Any | None = None, **kwargs: Any) -> None:
    """Plots the sound speed profile with matplotlib.

    Parameters
    ----------
    env : Environment
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

    if ax is None:
        fig = _pyplt.figure()
        ax = fig.add_subplot()

    assert(isinstance(ax, Axes))

    env.check()
    svp = env['soundspeed']
    if isinstance(svp, pd.DataFrame):
        svp = np.hstack((np.array([svp.index]).T, np.asarray(svp)))
    if np.size(svp) == 1:
        if np.size(env['bottom_depth']) > 1:
            max_y = np.max(env['bottom_depth'][:, 1])
        else:
            max_y = env['bottom_depth']
        _pyplt.plot([svp, svp], [0, -max_y], **kwargs)
        _pyplt.xlabel('Soundspeed (m/s)')
        _pyplt.ylabel('Depth (m)')
    elif env['soundspeed_interp'] == BHStrings.spline:
        ynew = np.linspace(np.min(svp[:, 0]), np.max(svp[:, 0]), 100)
        tck = _interp.splrep(svp[:, 0], svp[:, 1], s=0)
        xnew = _interp.splev(ynew, tck, der=0)
        _pyplt.plot(xnew, -ynew, **kwargs)
        _pyplt.xlabel('Soundspeed (m/s)')
        _pyplt.ylabel('Depth (m)')
        _pyplt.plot(svp[:, 1], -svp[:, 0], marker='.', **kwargs)
    else:
        for i in range(svp.shape[1]-1):
            _pyplt.plot(svp[:, i+1], -svp[:, 0], **kwargs)
        _pyplt.xlabel('Soundspeed (m/s)')
        _pyplt.ylabel('Depth (m)')

def pyplot_arrivals(arrivals: Any, dB: bool = False, color: str = 'blue', **kwargs: Any) -> None:
    """Plots the arrival times and amplitudes with matplotlib.

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
    if dB:
        min_y = 20 * np.log10(np.max(np.abs(arrivals.arrival_amplitude))) - 60
        ylabel = 'Amplitude (dB)'
    else:
        ylabel = 'Amplitude'
        _pyplt.plot([t0, t1], [0, 0], color=color, **kwargs)
        _pyplt.xlabel('Arrival time (s)')
        _pyplt.ylabel(ylabel)
        min_y = 0
    for _, row in arrivals.iterrows():
        t = row.time_of_arrival.real
        y = np.abs(row.arrival_amplitude)
        if dB:
            y = max(20 * np.log10(_fi.epsilon + y), min_y)
        _pyplt.plot([t, t], [min_y, y], color=color, **kwargs)
        _pyplt.xlabel('Arrival time (s)')
        _pyplt.ylabel(ylabel)

def pyplot_rays(
                rays: Any,
                env: Environment | None = None,
                invert_colors: bool = False,
                ax: Any | None = None,
                **kwargs: Any
               ) -> Axes:
    """Plots ray paths with matplotlib

    Parameters
    ----------
    rays : pandas.DataFrame
        Ray paths
    env : Environment, optional
        Environment definition
    invert_colors : bool, default=False
        False to use black for high intensity rays, True to use white
    **kwargs
        Other keyword arguments applicable for `bellhop.plot.plot()` are also supported

    Notes
    -----
    If environment definition is provided, it is overlayed over this plot using default
    parameters for `bellhop.plot_env()`. Without an environment file, no axis labels etc
    are provided, you are in charge of that.

    Examples
    --------
    >>> import aubellhop as bh
    >>> env = bh.Environment()
    >>> rays = bh.compute_eigenrays(env)
    >>> bh.plot_rays(rays, width=1000)
    """
    if env is not None:
        env.check()

    rays = rays.sort_values('bottom_bounces', ascending=False)
    dim = rays["ray"].iloc[0][0].shape[0]

    if ax is None:
        fig = _pyplt.figure()
        if dim == 2:
            ax = fig.add_subplot()
        elif dim == 3:
            ax = fig.add_subplot(projection='3d')
    assert(isinstance(ax, Axes))

    max_amp = np.max(np.abs(rays.bottom_bounces)) if len(rays.bottom_bounces) > 0 else 0
    if max_amp <= 0:
        max_amp = 1
    divisor = 1
    r = []
    for _, row in rays.iterrows():
        r += list(row.ray[:, 0])
    if max(r) - min(r) > 10000:
        divisor = 1000
    for _, row in rays.iterrows():
        rr = float( row.bottom_bounces / (max_amp + 1) ) # avoid rr = 1 == 100% white
        c = 1.0 - rr if invert_colors else rr
        cmap = _pyplt.get_cmap("gray")
        col_str = _mplc.to_hex(cmap(c))
        if dim == 2:
            if "color" in kwargs.keys():
                ax.plot(row.ray[:, 0] / divisor, row.ray[:, 1], **kwargs)
            else:
                ax.plot(row.ray[:, 0] / divisor, row.ray[:, 1], color=col_str, **kwargs)
        if dim == 3:
            if "color" in kwargs.keys():
                ax.plot(row.ray[:, 0] / divisor, row.ray[:, 1], row.ray[:, 2], **kwargs)
            else:
                ax.plot(row.ray[:, 0] / divisor, row.ray[:, 1], row.ray[:, 2], color=col_str, **kwargs)
    if env is not None:
        if dim == 2:
            pyplot_env2d(env,ax=ax,receiver_plot=False)
        elif dim == 3:
            pyplot_env3d(env,ax=ax)

    return ax

def pyplot_transmission_loss(
                             tloss: Any,
                             env: Environment | None = None,
                             ax: Any | None = None,
                             vmin: float | None = None,
                             vmax: float | None = None,
                             **kwargs: Any
                            ) -> Axes:
    """Plots transmission loss with matplotlib.

    Parameters
    ----------
    tloss : pandas.DataFrame
        Complex transmission loss
    env : Environment, optional
        Environment definition
    vmin, vmax : float, optional
        Colour limits in dB (equivalent to Matlab's `clim`). Values outside the
        range saturate at the end colours. Ignored if `levels` is passed explicitly.
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
    if env is not None:
        env.check()

    if ax is None:
        fig = _pyplt.figure()
        ax = fig.add_subplot()
    assert(isinstance(ax, Axes))

    xr = (min(tloss.columns), max(tloss.columns))
    yr = (max(tloss.index), min(tloss.index))
    xlabel = 'Range (m)'
    if xr[1] - xr[0] > 10000:
        xr = (min(tloss.columns) / 1000, max(tloss.columns) / 1000)
        xlabel = 'Range (km)'

    trans_loss = 20 * np.log10(_fi.epsilon + np.abs(np.flipud(np.array(tloss))))
    x_mesh, y_mesh = np.meshgrid(np.linspace(xr[0], xr[1], trans_loss.shape[1]),
                                np.linspace(yr[0], yr[1], trans_loss.shape[0]))

    if vmin is not None or vmax is not None:
        lo = vmin if vmin is not None else trans_loss.min()
        hi = vmax if vmax is not None else trans_loss.max()
        kwargs.setdefault("levels", np.linspace(lo, hi, 21))
        kwargs.setdefault("extend", "both")

    _pyplt.contourf(x_mesh, y_mesh, trans_loss, cmap="jet", **kwargs)
    _pyplt.xlabel(xlabel)
    _pyplt.ylabel('Depth (m)')
    _pyplt.colorbar(label="Transmission loss (dB)")
    if env is not None:
        pyplot_env2d(env, ax=ax, receiver_plot=False, fill=True)

    return ax


### Export module names for auto-importing in __init__.py

__all__ = [
    name for name in globals() if not name.startswith("_")  # ignore private names
]
