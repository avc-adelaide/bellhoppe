##############################################################################
#
# Copyright (c) 2025-, Will Robertson
# Copyright (c) 2018-2025, Mandar Chitre
#
# This file was originally part of arlpy, released under Simplified BSD License.
# It has been relicensed in this repository to be compatible with the Bellhop licence (GPL).
#
##############################################################################

"""Plotting functions for the underwater acoustic propagation modeling toolbox.
"""

from typing import Any, Dict, Optional
from sys import float_info as _fi

import numpy as _np
import scipy.interpolate as _interp
import pandas as _pd

import matplotlib.pyplot as _pyplt
import matplotlib.colors as _mplc

from bellhop.constants import _Strings

def pyplot_env(env: Dict[str, Any], surface_color: str = 'dodgerblue', bottom_color: str = 'peru', source_color: str = 'orangered', receiver_color: str = 'midnightblue',
               receiver_plot: Optional[bool] = None, **kwargs: Any) -> None:
    """Plots a visual representation of the environment with matplotlib.

    :param env: environment description
    :param surface_color: color of the surface (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    :param bottom_color: color of the bottom (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    :param source_color: color of transmitters (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    :param receiver_color: color of receviers (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    :param receiver_plot: True to plot all receivers, False to not plot any receivers, None to automatically decide

    Other keyword arguments applicable for `bellhop.plot.plot()` are also supported.

    The surface, bottom, transmitters (marker: '*') and receivers (marker: 'o')
    are plotted in the environment. If `receiver_plot` is set to None and there are
    more than 2000 receivers, they are not plotted.

    >>> import bellhop as bh
    >>> env = bh.create_env2d(depth=[[0, 40], [100, 30], [500, 35], [700, 20], [1000,45]])
    >>> bh.plot_env(env)
    """

    if _np.array(env['receiver_range']).size > 1:
        min_x = _np.min(env['receiver_range'])
    else:
        min_x = 0
    max_x = _np.max(env['receiver_range'])
    if max_x - min_x > 10000:
        divisor = 1000
        min_x /= divisor
        max_x /= divisor
        xlabel = 'Range (km)'
    else:
        divisor = 1
        xlabel = 'Range (m)'
    if env['surface'] is None:
        min_y = 0
    else:
        min_y = _np.min(env['surface'][:, 1])
    if _np.size(env['depth']) > 1:
        max_y = _np.max(env['depth'][:, 1])
    else:
        max_y = env['depth']
    mgn_x = 0.01 * (max_x - min_x)
    mgn_y = 0.1 * (max_y - min_y)
    if env['surface'] is None:
        _pyplt.plot([min_x, max_x], [0, 0], color=surface_color, **kwargs)
        _pyplt.xlabel(xlabel)
        _pyplt.ylabel('Depth (m)')
        print(min_x, mgn_x, max_x, mgn_x)
        _pyplt.xlim([min_x - mgn_x, max_x + mgn_x])
        _pyplt.ylim([-max_y - mgn_y, -min_y + mgn_y])
    else:
        # linear and curvilinear options use the same altimetry, just with different normals
        s = env['surface']
        _pyplt.plot(s[:, 0] / divisor, -s[:, 1], color=surface_color, **kwargs)
        _pyplt.xlabel(xlabel)
        _pyplt.ylabel('Depth (m)')
        _pyplt.xlim([min_x - mgn_x, max_x + mgn_x])
        _pyplt.ylim([-max_y - mgn_y, -min_y + mgn_y])
    if _np.size(env['depth']) == 1:
        _pyplt.plot([min_x, max_x], [-env['depth'], -env['depth']], color=bottom_color, **kwargs)
    else:
        # linear and curvilinear options use the same bathymetry, just with different normals
        s = env['depth']
        _pyplt.plot(s[:, 0] / divisor, -s[:, 1], color=bottom_color, **kwargs)
    txd = env['source_depth']
    # print(txd, [0]*_np.size(txd))
    _pyplt.plot([0] * _np.size(txd), -txd, marker='*', markersize=6, color=source_color, **kwargs)
    if receiver_plot is None:
        receiver_plot = _np.size(env['receiver_depth']) * _np.size(env['receiver_range']) < 2000
    if receiver_plot:
        rxr = env['receiver_range']
        if _np.size(rxr) == 1:
            rxr = [rxr]
        for r in _np.array(rxr):
            rxd = env['receiver_depth']
            _pyplt.plot([r / divisor] * _np.size(rxd), -rxd, marker='o', color=receiver_color, **kwargs)

def pyplot_ssp(env: Dict[str, Any], **kwargs: Any) -> None:
    """Plots the sound speed profile with matplotlib.

    :param env: environment description

    Other keyword arguments applicable for `bellhop.plot.plot()` are also supported.

    If the sound speed profile is range-dependent, this function only plots the first profile.

    >>> import bellhop as bh
    >>> env = bh.create_env2d(soundspeed=[[ 0, 1540], [10, 1530], [20, 1532], [25, 1533], [30, 1535]])
    >>> bh.plot_ssp(env)
    """

    svp = env['soundspeed']
    if isinstance(svp, _pd.DataFrame):
        svp = _np.hstack((_np.array([svp.index]).T, _np.asarray(svp)))
    if _np.size(svp) == 1:
        if _np.size(env['depth']) > 1:
            max_y = _np.max(env['depth'][:, 1])
        else:
            max_y = env['depth']
        _pyplt.plot([svp, svp], [0, -max_y], **kwargs)
        _pyplt.xlabel('Soundspeed (m/s)')
        _pyplt.ylabel('Depth (m)')
    elif env['soundspeed_interp'] == _Strings.spline:
        ynew = _np.linspace(_np.min(svp[:, 0]), _np.max(svp[:, 0]), 100)
        tck = _interp.splrep(svp[:, 0], svp[:, 1], s=0)
        xnew = _interp.splev(ynew, tck, der=0)
        _pyplt.plot(xnew, -ynew, **kwargs)
        _pyplt.xlabel('Soundspeed (m/s)')
        _pyplt.ylabel('Depth (m)')
        _pyplt.plot(svp[:, 1], -svp[:, 0], marker='.', **kwargs)
    else:
        _pyplt.plot(svp[:, 1], -svp[:, 0], **kwargs)
        _pyplt.xlabel('Soundspeed (m/s)')
        _pyplt.ylabel('Depth (m)')

def pyplot_arrivals(arrivals: Any, dB: bool = False, color: str = 'blue', **kwargs: Any) -> None:
    """Plots the arrival times and amplitudes with matplotlib.

    :param arrivals: arrivals times (s) and coefficients
    :param dB: True to plot in dB, False for linear scale
    :param color: line color (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)

    Other keyword arguments applicable for `bellhop.plot.plot()` are also supported.

    >>> import bellhop as bh
    >>> env = bh.create_env2d()
    >>> arrivals = bh.compute_arrivals(env)
    >>> bh.plot_arrivals(arrivals)
    """
    t0 = min(arrivals.time_of_arrival)
    t1 = max(arrivals.time_of_arrival)
    if dB:
        min_y = 20 * _np.log10(_np.max(_np.abs(arrivals.arrival_amplitude))) - 60
        ylabel = 'Amplitude (dB)'
    else:
        ylabel = 'Amplitude'
        _pyplt.plot([t0, t1], [0, 0], color=color, **kwargs)
        _pyplt.xlabel('Arrival time (s)')
        _pyplt.ylabel(ylabel)
        min_y = 0
    for _, row in arrivals.iterrows():
        t = row.time_of_arrival.real
        y = _np.abs(row.arrival_amplitude)
        if dB:
            y = max(20 * _np.log10(_fi.epsilon + y), min_y)
        _pyplt.plot([t, t], [min_y, y], color=color, **kwargs)
        _pyplt.xlabel('Arrival time (s)')
        _pyplt.ylabel(ylabel)

def pyplot_rays(rays: Any, env: Optional[Dict[str, Any]] = None, invert_colors: bool = False, **kwargs: Any) -> None:
    """Plots ray paths with matplotlib

    :param rays: ray paths
    :param env: environment definition
    :param invert_colors: False to use black for high intensity rays, True to use white

    If environment definition is provided, it is overlayed over this plot using default
    parameters for `bellhop.plot_env()`.

    Other keyword arguments applicable for `bellhop.plot.plot()` are also supported.

    >>> import bellhop as bh
    >>> env = bh.create_env2d()
    >>> rays = bh.compute_eigenrays(env)
    >>> bh.plot_rays(rays, width=1000)
    """
    rays = rays.sort_values('bottom_bounces', ascending=False)
    max_amp = _np.max(_np.abs(rays.bottom_bounces)) if len(rays.bottom_bounces) > 0 else 0
    if max_amp <= 0:
        max_amp = 1
    divisor = 1
    xlabel = 'Range (m)'
    r = []
    for _, row in rays.iterrows():
        r += list(row.ray[:, 0])
    if max(r) - min(r) > 10000:
        divisor = 1000
        xlabel = 'Range (km)'
    for _, row in rays.iterrows():
        c = float(_np.abs(row.bottom_bounces) / max_amp)
        if invert_colors:
            c = 1.0 - c
        cmap = _pyplt.get_cmap("gray")
        col_str = _mplc.to_hex(cmap(c))
        if "color" in kwargs.keys():
            _pyplt.plot(row.ray[:, 0] / divisor, -row.ray[:, 1], **kwargs)
        else:
            _pyplt.plot(row.ray[:, 0] / divisor, -row.ray[:, 1], color=col_str, **kwargs)
        _pyplt.xlabel(xlabel)
        _pyplt.ylabel('Depth (m)')
    if env is not None:
        pyplot_env(env)

def pyplot_transmission_loss(tloss: Any, env: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
    """Plots transmission loss with matplotlib.

    :param tloss: complex transmission loss
    :param env: environment definition

    If environment definition is provided, it is overlayed over this plot using default
    parameters for `bellhop.plot_env()`.

    Other keyword arguments applicable for `bellhop.plot.image()` are also supported.

    >>> import bellhop as bh
    >>> import numpy as np
    >>> env = bh.create_env2d(
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
    if xr[1] - xr[0] > 10000:
        xr = (min(tloss.columns) / 1000, max(tloss.columns) / 1000)
        xlabel = 'Range (km)'
    trans_loss = 20 * _np.log10(_fi.epsilon + _np.abs(_np.flipud(_np.array(tloss))))
    x_mesh, ymesh = _np.meshgrid(_np.linspace(xr[0], xr[1], trans_loss.shape[1]),
                                 _np.linspace(yr[0], yr[1], trans_loss.shape[0]))
    trans_loss = trans_loss.reshape(-1)
    # print(trans_loss.shape)
    if "vmin" in kwargs.keys():
        trans_loss[trans_loss < kwargs["vmin"]] = kwargs["vmin"]
    if "vmax" in kwargs.keys():
        trans_loss[trans_loss > kwargs["vmax"]] = kwargs["vmax"]
    trans_loss = trans_loss.reshape((x_mesh.shape[0], -1))
    _pyplt.contourf(x_mesh, ymesh, trans_loss, cmap="jet", **kwargs)
    _pyplt.xlabel(xlabel)
    _pyplt.ylabel('Depth (m)')
    _pyplt.colorbar(label="Transmission Loss(dB)")
    if env is not None:
        pyplot_env(env, receiver_plot=False)



__all__ = [
    name
    for name in globals()
    if not name.startswith("_")  # ignore private names
]
