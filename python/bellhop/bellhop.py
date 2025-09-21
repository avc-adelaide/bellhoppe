##############################################################################
#
# Copyright (c) 2025-, Will Robertson
# Copyright (c) 2018-2025, Mandar Chitre
#
# This file was originally part of arlpy, released under Simplified BSD License.
# It has been relicensed in this repository to be compatible with the Bellhop licence (GPL).
#
##############################################################################

"""Underwater acoustic propagation modeling toolbox.

This toolbox uses the Bellhop acoustic propagation model. For this model
to work, the conplete bellhop-hub package must be built and installed
and `bellhop.exe` should be in your PATH.
"""

import os as _os
import re as _re
import subprocess as _proc

from tempfile import mkstemp as _mkstemp
from struct import unpack as _unpack
from sys import float_info as _fi

import numpy as _np
from scipy import interpolate as _interp
import pandas as _pd

import matplotlib.pyplot as _pyplt
import matplotlib.cm as _cm
import bokeh as _bokeh

from bellhop.constants import _Strings, _Maps
from bellhop.readers import *
import bellhop.environment
import bellhop.plotutils as _plt

# models (in order of preference)
_models = []

def create_env2d(**kv):
    """Create a new 2D underwater environment.

    Parameters
    ----------
    **kv : dict
        Keyword arguments for environment configuration.

    Returns
    -------
    env : dict
        A new 2D underwater environment dictionary.

    Example
    -------

    To see all the parameters available and their default values:

    >>> import bellhop as bh
    >>> env = bh.create_env2d()
    >>> bh.print_env(env)

    The environment parameters may be changed by passing keyword arguments
    or modified later using dictionary notation:

    >>> import bellhop as bh
    >>> env = bh.create_env2d(depth=40, soundspeed=1540)
    >>> bh.print_env(env)
    >>> env['depth'] = 25
    >>> env['bottom_soundspeed'] = 1800
    >>> bh.print_env(env)

    The default environment has a constant sound speed.
    A depth dependent sound speed profile be provided as a Nx2 array of (depth, sound speed):

    >>> import bellhop as bh
    >>> env = bh.create_env2d(depth=20,
    >>>.        soundspeed=[[0,1540], [5,1535], [10,1535], [20,1530]])

    A range-and-depth dependent sound speed profile can be provided as a Pandas frame:

    >>> import bellhop as bh
    >>> import pandas as pd
    >>> ssp2 = pd.DataFrame({
              0: [1540, 1530, 1532, 1533],     # profile at 0 m range
            100: [1540, 1535, 1530, 1533],     # profile at 100 m range
            200: [1530, 1520, 1522, 1525] },   # profile at 200 m range
            index=[0, 10, 20, 30])             # depths of the profile entries in m
    >>> env = bh.create_env2d(depth=20, soundspeed=ssp2)

    The default environment has a constant water depth. A range dependent bathymetry
    can be provided as a Nx2 array of (range, water depth):

    >>> import bellhop as bh
    >>> env = bh.create_env2d(depth=[[0,20], [300,10], [500,18], [1000,15]])
    """
    env = bellhop.environment.new()
    for k, v in kv.items():
        if k not in env.keys():
            raise KeyError('Unknown key: '+k)
        env[k] = _np.asarray(v, dtype=_np.float64) if not isinstance(v, _pd.DataFrame) and _np.size(v) > 1 else v
    env['depth_max'] = env['depth_max'] or _np.max(env['depth'])
    env = check_env2d(env)
    return env



def check_env2d(env):
    """Check the validity of a 2D underwater environment definition.

    :param env: environment definition

    Exceptions are thrown with appropriate error messages if the environment is invalid.

    >>> import bellhop as bh
    >>> env = bh.create_env2d()
    >>> check_env2d(env)
    """
    try:
        assert env['type'] == '2D', 'Not a 2D environment'
        max_range = _np.max(env['rx_range'])
        if env['surface'] is not None:
            assert _np.size(env['surface']) > 1, 'surface must be an Nx2 array'
            assert env['surface'].ndim == 2, 'surface must be a scalar or an Nx2 array'
            assert env['surface'].shape[1] == 2, 'surface must be a scalar or an Nx2 array'
            assert env['surface'][0,0] <= 0, 'First range in surface array must be 0 m'
            assert env['surface'][-1,0] >= max_range, 'Last range in surface array must be beyond maximum range: '+str(max_range)+' m'
            assert _np.all(_np.diff(env['surface'][:,0]) > 0), 'surface array must be strictly monotonic in range'
            assert env['surface_interp'] == _Strings.curvilinear or env['surface_interp'] == _Strings.linear, 'Invalid interpolation type: '+str(env['surface_interp'])
        if _np.size(env['depth']) > 1:
            assert env['depth'].ndim == 2, 'depth must be a scalar or an Nx2 array'
            assert env['depth'].shape[1] == 2, 'depth must be a scalar or an Nx2 array'
            assert env['depth'][0,0] <= 0, 'First range in depth array must be 0 m'
            assert env['depth'][-1,0] >= max_range, 'Last range in depth array must be beyond maximum range: '+str(max_range)+' m'
            assert _np.all(_np.diff(env['depth'][:,0]) > 0), 'Depth array must be strictly monotonic in range'
            assert env['depth_interp'] == _Strings.curvilinear or env['depth_interp'] == _Strings.linear, 'Invalid interpolation type: '+str(env['depth_interp'])
            max_depth = _np.max(env['depth'][:,1])
            env["_bottom_bathymetry"] = "from-file"
        else:
            max_depth = env['depth']
        if isinstance(env['soundspeed'], _pd.DataFrame):
            # For DataFrames, apply the same minimum point requirements as numpy arrays
            if env['soundspeed_interp'] == 'spline':
                assert env['soundspeed'].shape[0] > 3, 'soundspeed profile must have at least 4 points for spline interpolation'
            else:
                assert env['soundspeed'].shape[0] > 1, 'soundspeed profile must have at least 2 points'
            assert env['soundspeed'].index[0] <= 0, 'First depth in soundspeed array must be 0 m'
            assert env['soundspeed'].index[-1] >= max_depth, 'Last depth in soundspeed array must be beyond water depth: '+str(max_depth)+' m'
            assert _np.all(_np.diff(env['soundspeed'].index) > 0), 'Soundspeed array must be strictly monotonic in depth'
        elif _np.size(env['soundspeed']) > 1:
            assert env['soundspeed'].ndim == 2, 'soundspeed must be a scalar or an Nx2 array'
            assert env['soundspeed'].shape[1] == 2, 'soundspeed must be a scalar or an Nx2 array'
            # Minimum points depend on interpolation type
            if env['soundspeed_interp'] == 'spline':
                assert env['soundspeed'].shape[0] > 3, 'soundspeed profile must have at least 4 points for spline interpolation'
            else:
                assert env['soundspeed'].shape[0] > 1, 'soundspeed profile must have at least 2 points'
            assert env['soundspeed'][0,0] <= 0, 'First depth in soundspeed array must be 0 m'
            assert env['soundspeed'][-1,0] >= max_depth, 'Last depth in soundspeed array must be beyond water depth: '+str(max_depth)+' m'
            assert _np.all(_np.diff(env['soundspeed'][:,0]) > 0), 'Soundspeed array must be strictly monotonic in depth'
            assert env['soundspeed_interp'] in _Maps.interp_rev, 'Invalid interpolation type: '+str(env['soundspeed_interp'])
            if max_depth not in env['soundspeed'][:,0]:
                indlarger = _np.argwhere(env['soundspeed'][:,0]>max_depth)[0][0]
                if env['soundspeed_interp'] == _Strings.spline:
                    tck = _interp.splrep(env['soundspeed'][:,0], env['soundspeed'][:,1], s=0)
                    insert_ss_val = _interp.splev(max_depth, tck, der=0)
                else:
                    insert_ss_val = _np.interp(max_depth, env['soundspeed'][:,0], env['soundspeed'][:,1])
                env['soundspeed'] = _np.insert(env['soundspeed'],indlarger,[max_depth,insert_ss_val],axis = 0)
                env['soundspeed'] = env['soundspeed'][:indlarger+1,:]
        assert _np.max(env['tx_depth']) <= max_depth, 'tx_depth cannot exceed water depth: '+str(max_depth)+' m'
        assert _np.max(env['rx_depth']) <= max_depth, 'rx_depth cannot exceed water depth: '+str(max_depth)+' m'
        assert env['min_angle'] > -180 and env['min_angle'] < 180, 'min_angle must be in range (-180, 180)'
        assert env['max_angle'] > -180 and env['max_angle'] < 180, 'max_angle must be in range (-180, 180)'
        if env["bottom_reflection_coefficient"] is not None:
            env["bottom_boundary_condition"] = "from-file"
        if env['tx_directionality'] is not None:
            assert _np.size(env['tx_directionality']) > 1, 'tx_directionality must be an Nx2 array'
            assert env['tx_directionality'].ndim == 2, 'tx_directionality must be an Nx2 array'
            assert env['tx_directionality'].shape[1] == 2, 'tx_directionality must be an Nx2 array'
            assert _np.all(env['tx_directionality'][:,0] >= -180) and _np.all(env['tx_directionality'][:,0] <= 180), 'tx_directionality angles must be in [-90, 90]'
        return env
    except AssertionError as e:
        raise ValueError(e.args)

def print_env(env):
    """Display the environment in a human readable form.

    :param env: environment definition

    >>> import bellhop as bh
    >>> env = bh.create_env2d(depth=40, soundspeed=1540)
    >>> bh.print_env(env)
    """
    env = check_env2d(env)
    keys = ['name'] + sorted(list(env.keys()-['name']))
    for k in keys:
        v = str(env[k])
        if '\n' in v:
            v = v.split('\n')
            print('%20s : '%(k) + v[0])
            for v1 in v[1:]:
                print('%20s   '%('') + v1)
        else:
            print('%20s : '%(k) + v)

def plot_env(env, surface_color='dodgerblue', bottom_color='peru', tx_color='orangered', rx_color='midnightblue', rx_plot=None, **kwargs):
    """Plots a visual representation of the environment.

    :param env: environment description
    :param surface_color: color of the surface (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    :param bottom_color: color of the bottom (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    :param tx_color: color of transmitters (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    :param rx_color: color of receviers (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    :param rx_plot: True to plot all receivers, False to not plot any receivers, None to automatically decide

    Other keyword arguments applicable for `bellhop.plot.plot()` are also supported.

    The surface, bottom, transmitters (marker: '*') and receivers (marker: 'o')
    are plotted in the environment. If `rx_plot` is set to None and there are
    more than 2000 receivers, they are not plotted.

    >>> import bellhop as bh
    >>> env = bh.create_env2d(depth=[[0, 40], [100, 30], [500, 35], [700, 20], [1000,45]])
    >>> bh.plot_env(env)
    """

    min_x = 0
    max_x = _np.max(env['rx_range'])
    if max_x-min_x > 10000:
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
        min_y = _np.min(env['surface'][:,1])
    if _np.size(env['depth']) > 1:
        max_y = _np.max(env['depth'][:,1])
    else:
        max_y = env['depth']
    mgn_x = 0.01*(max_x-min_x)
    mgn_y = 0.1*(max_y-min_y)
    oh = _plt.hold()
    if env['surface'] is None:
        _plt.plot([min_x, max_x], [0, 0], xlabel=xlabel, ylabel='Depth (m)', xlim=(min_x-mgn_x, max_x+mgn_x), ylim=(-max_y-mgn_y, -min_y+mgn_y), color=surface_color, **kwargs)
    else:
        # linear and curvilinear options use the same altimetry, just with different normals
        s = env['surface']
        _plt.plot(s[:,0]/divisor, -s[:,1], xlabel=xlabel, ylabel='Depth (m)', xlim=(min_x-mgn_x, max_x+mgn_x), ylim=(-max_y-mgn_y, -min_y+mgn_y), color=surface_color, **kwargs)
    if _np.size(env['depth']) == 1:
        _plt.plot([min_x, max_x], [-env['depth'], -env['depth']], color=bottom_color)
    else:
        # linear and curvilinear options use the same bathymetry, just with different normals
        s = env['depth']
        _plt.plot(s[:,0]/divisor, -s[:,1], color=bottom_color)
    txd = env['tx_depth']
    _plt.plot([0]*_np.size(txd), -txd, marker='*', style=None, color=tx_color)
    if rx_plot is None:
        rx_plot = _np.size(env['rx_depth'])*_np.size(env['rx_range']) < 2000
    if rx_plot:
        rxr = env['rx_range']
        if _np.size(rxr) == 1:
            rxr = [rxr]
        for r in _np.array(rxr):
            rxd = env['rx_depth']
            _plt.plot([r/divisor]*_np.size(rxd), -rxd, marker='o', style=None, color=rx_color)
    _plt.hold(oh)

def plot_ssp(env, **kwargs):
    """Plots the sound speed profile.

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
            max_y = _np.max(env['depth'][:,1])
        else:
            max_y = env['depth']
        _plt.plot([svp, svp], [0, -max_y], xlabel='Soundspeed (m/s)', ylabel='Depth (m)', **kwargs)
    elif env['soundspeed_interp'] == _Strings.spline:
        ynew = _np.linspace(_np.min(svp[:,0]), _np.max(svp[:,0]), 100)
        tck = _interp.splrep(svp[:,0], svp[:,1], s=0)
        xnew = _interp.splev(ynew, tck, der=0)
        _plt.plot(xnew, -ynew, xlabel='Soundspeed (m/s)', ylabel='Depth (m)', hold=True, **kwargs)
        _plt.plot(svp[:,1], -svp[:,0], marker='.', style=None, **kwargs)
    else:
        _plt.plot(svp[:,1], -svp[:,0], xlabel='Soundspeed (m/s)', ylabel='Depth (m)', **kwargs)

def compute_arrivals(env, model=None, debug=False, fname_base=None):
    """Compute arrivals between each transmitter and receiver.

    :param env: environment definition
    :param model: propagation model to use (None to auto-select)
    :param debug: generate debug information for propagation model
    :param fname_base: base file name for Bellhop working files, default (None), creates a temporary file
    :returns: arrival times and coefficients for all transmitter-receiver combinations

    >>> import bellhop as bh
    >>> env = bh.create_env2d()
    >>> arrivals = bh.compute_arrivals(env)
    >>> bh.plot_arrivals(arrivals)
    """
    env = check_env2d(env)
    (model_name, model) = _select_model(env, _Strings.arrivals, model)
    if debug:
        print('[DEBUG] Model: '+model_name)
    return model.run(env, _Strings.arrivals, debug, fname_base)

def compute_eigenrays(env, tx_depth_ndx=0, rx_depth_ndx=0, rx_range_ndx=0, model=None, debug=False, fname_base=None):
    """Compute eigenrays between a given transmitter and receiver.

    :param env: environment definition
    :param tx_depth_ndx: transmitter depth index
    :param rx_depth_ndx: receiver depth index
    :param rx_range_ndx: receiver range index
    :param model: propagation model to use (None to auto-select)
    :param debug: generate debug information for propagation model
    :param fname_base: base file name for Bellhop working files, default (None), creates a temporary file
    :returns: eigenrays paths

    >>> import bellhop as bh
    >>> env = bh.create_env2d()
    >>> rays = bh.compute_eigenrays(env)
    >>> bh.plot_rays(rays, width=1000)
    """
    env = check_env2d(env)
    env = env.copy()
    if _np.size(env['tx_depth']) > 1:
        env['tx_depth'] = env['tx_depth'][tx_depth_ndx]
    if _np.size(env['rx_depth']) > 1:
        env['rx_depth'] = env['rx_depth'][rx_depth_ndx]
    if _np.size(env['rx_range']) > 1:
        env['rx_range'] = env['rx_range'][rx_range_ndx]
    (model_name, model) = _select_model(env, _Strings.eigenrays, model)
    if debug:
        print('[DEBUG] Model: '+model_name)
    return model.run(env, _Strings.eigenrays, debug, fname_base)

def compute_rays(env, tx_depth_ndx=0, model=None, debug=False, fname_base=None):
    """Compute rays from a given transmitter.

    :param env: environment definition
    :param tx_depth_ndx: transmitter depth index
    :param model: propagation model to use (None to auto-select)
    :param debug: generate debug information for propagation model
    :param fname_base: base file name for Bellhop working files, default (None), creates a temporary file
    :returns: ray paths

    >>> import bellhop as bh
    >>> env = bh.create_env2d()
    >>> rays = bh.compute_rays(env)
    >>> bh.plot_rays(rays, width=1000)
    """
    env = check_env2d(env)
    if _np.size(env['tx_depth']) > 1:
        env = env.copy()
        env['tx_depth'] = env['tx_depth'][tx_depth_ndx]
    (model_name, model) = _select_model(env, _Strings.rays, model)
    if debug:
        print('[DEBUG] Model: '+model_name)
    return model.run(env, _Strings.rays, debug, fname_base)

def compute_transmission_loss(env, tx_depth_ndx=0, mode=_Strings.coherent, model=None, tx_type="default", debug=False, fname_base=None):
    """Compute transmission loss from a given transmitter to all receviers.

    :param env: environment definition
    :param tx_depth_ndx: transmitter depth index
    :param mode: coherent, incoherent or semicoherent
    :param model: propagation model to use (None to auto-select)
    :param tx_type: point or line
    :param debug: generate debug information for propagation model
    :param fname_base: base file name for Bellhop working files, default (None), creates a temporary file
    :returns: complex transmission loss at each receiver depth and range

    >>> import bellhop as bh
    >>> env = bh.create_env2d()
    >>> tloss = bh.compute_transmission_loss(env, mode=bh.incoherent)
    >>> bh.plot_transmission_loss(tloss, width=1000)
    """
    env = check_env2d(env)
    if mode not in [_Strings.coherent, _Strings.incoherent, _Strings.semicoherent]:
        raise ValueError('Unknown transmission loss mode: '+mode)
    if tx_type not in _Maps.source_rev:
        raise ValueError(f'Unknown source type: {tx_type!r}')
    if env['tx_type'] == 'default':
        env['tx_type'] = tx_type
    else:
        if not(tx_type == 'default') and not(env['tx_type'] == tx_type):
            raise ValueError('ENV file defines source type "'+env['tx_type']+'" inconsistent with Python argument tx_type="'+tx_type+'"')
    if _np.size(env['tx_depth']) > 1:
        env = env.copy()
        env['tx_depth'] = env['tx_depth'][tx_depth_ndx]
    (model_name, model) = _select_model(env, mode, model)
    if debug:
        print('[DEBUG] Model: '+model_name)
    return model.run(env, mode, debug, fname_base)

def arrivals_to_impulse_response(arrivals, fs, abs_time=False):
    """Convert arrival times and coefficients to an impulse response.

    :param arrivals: arrivals times (s) and coefficients
    :param fs: sampling rate (Hz)
    :param abs_time: absolute time (True) or relative time (False)
    :returns: impulse response

    If `abs_time` is set to True, the impulse response is placed such that
    the zero time corresponds to the time of transmission of signal.

    >>> import bellhop as bh
    >>> env = bh.create_env2d()
    >>> arrivals = bh.compute_arrivals(env)
    >>> ir = bh.arrivals_to_impulse_response(arrivals, fs=192000)
    """
    t0 = 0 if abs_time else min(arrivals.time_of_arrival)
    irlen = int(_np.ceil((max(arrivals.time_of_arrival)-t0)*fs))+1
    ir = _np.zeros(irlen, dtype=_np.complex128)
    for _, row in arrivals.iterrows():
        ndx = int(_np.round((row.time_of_arrival.real-t0)*fs))
        ir[ndx] = row.arrival_amplitude
    return ir

def plot_arrivals(arrivals, dB=False, color='blue', **kwargs):
    """Plots the arrival times and amplitudes.

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
    oh = _plt.hold()
    if dB:
        min_y = 20*_np.log10(_np.max(_np.abs(arrivals.arrival_amplitude)))-60
        ylabel = 'Amplitude (dB)'
    else:
        ylabel = 'Amplitude'
        _plt.plot([t0, t1], [0, 0], xlabel='Arrival time (s)', ylabel=ylabel, color=color, **kwargs)
        min_y = 0
    for _, row in arrivals.iterrows():
        t = row.time_of_arrival.real
        y = _np.abs(row.arrival_amplitude)
        if dB:
            y = max(20*_np.log10(_fi.epsilon+y), min_y)
        _plt.plot([t, t], [min_y, y], xlabel='Arrival time (s)', ylabel=ylabel, ylim=[min_y, min_y+70], color=color, **kwargs)
    _plt.hold(oh)

def plot_rays(rays, env=None, invert_colors=False, **kwargs):
    """Plots ray paths.

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
        r += list(row.ray[:,0])
    if max(r)-min(r) > 10000:
        divisor = 1000
        xlabel = 'Range (km)'
    oh = _plt.hold()
    for _, row in rays.iterrows():
        c = int(255*_np.abs(row.bottom_bounces)/max_amp)
        if invert_colors:
            c = 255-c
        c = _bokeh.colors.RGB(c, c, c)
        _plt.plot(row.ray[:,0]/divisor, -row.ray[:,1], color=c, xlabel=xlabel, ylabel='Depth (m)', **kwargs)
    if env is not None:
        plot_env(env)
    _plt.hold(oh)

def plot_transmission_loss(tloss, env=None, **kwargs):
    """Plots transmission loss.

    :param tloss: complex transmission loss
    :param env: environment definition

    If environment definition is provided, it is overlayed over this plot using default
    parameters for `bellhop.plot_env()`.

    Other keyword arguments applicable for `bellhop.plot.image()` are also supported.

    >>> import bellhop as bh
    >>> import numpy as np
    >>> env = bh.create_env2d(
            rx_depth=np.arange(0, 25),
            rx_range=np.arange(0, 1000),
            min_angle=-45,
            max_angle=45
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
    _plt.image(20*_np.log10(_fi.epsilon+_np.abs(_np.flipud(_np.array(tloss)))), x=xr, y=yr, xlabel=xlabel, ylabel='Depth (m)', xlim=xr, ylim=yr, **kwargs)
    if env is not None:
        plot_env(env, rx_plot=False)
    _plt.hold(oh)

def pyplot_env(env, surface_color='dodgerblue', bottom_color='peru', tx_color='orangered', rx_color='midnightblue',
               rx_plot=None, **kwargs):
    """Plots a visual representation of the environment with matplotlib.

    :param env: environment description
    :param surface_color: color of the surface (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    :param bottom_color: color of the bottom (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    :param tx_color: color of transmitters (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    :param rx_color: color of receviers (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    :param rx_plot: True to plot all receivers, False to not plot any receivers, None to automatically decide

    Other keyword arguments applicable for `bellhop.plot.plot()` are also supported.

    The surface, bottom, transmitters (marker: '*') and receivers (marker: 'o')
    are plotted in the environment. If `rx_plot` is set to None and there are
    more than 2000 receivers, they are not plotted.

    >>> import bellhop as bh
    >>> env = bh.create_env2d(depth=[[0, 40], [100, 30], [500, 35], [700, 20], [1000,45]])
    >>> bh.plot_env(env)
    """

    if _np.array(env['rx_range']).size > 1:
        min_x = _np.min(env['rx_range'])
    else:
        min_x = 0
    max_x = _np.max(env['rx_range'])
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
    txd = env['tx_depth']
    # print(txd, [0]*_np.size(txd))
    _pyplt.plot([0] * _np.size(txd), -txd, marker='*', markersize=6, color=tx_color, **kwargs)
    if rx_plot is None:
        rx_plot = _np.size(env['rx_depth']) * _np.size(env['rx_range']) < 2000
    if rx_plot:
        rxr = env['rx_range']
        if _np.size(rxr) == 1:
            rxr = [rxr]
        for r in _np.array(rxr):
            rxd = env['rx_depth']
            _pyplt.plot([r / divisor] * _np.size(rxd), -rxd, marker='o', color=rx_color, **kwargs)

def pyplot_ssp(env, **kwargs):
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

def pyplot_arrivals(arrivals, dB=False, color='blue', **kwargs):
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

def pyplot_rays(rays, env=None, invert_colors=False, **kwargs):
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
        c = _np.abs(row.bottom_bounces) / max_amp
        if invert_colors:
            c = 1.0 - c
        c = _cm.gray(c)
        if "color" in kwargs.keys():
            _pyplt.plot(row.ray[:, 0] / divisor, -row.ray[:, 1], **kwargs)
        else:
            _pyplt.plot(row.ray[:, 0] / divisor, -row.ray[:, 1], color=c, **kwargs)
        _pyplt.xlabel(xlabel)
        _pyplt.ylabel('Depth (m)')
    if env is not None:
        pyplot_env(env)

def pyplot_transmission_loss(tloss, env=None, **kwargs):
    """Plots transmission loss with matplotlib.

    :param tloss: complex transmission loss
    :param env: environment definition

    If environment definition is provided, it is overlayed over this plot using default
    parameters for `bellhop.plot_env()`.

    Other keyword arguments applicable for `bellhop.plot.image()` are also supported.

    >>> import bellhop as bh
    >>> import numpy as np
    >>> env = bh.create_env2d(
            rx_depth=np.arange(0, 25),
            rx_range=np.arange(0, 1000),
            min_angle=-45,
            max_angle=45
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
        pyplot_env(env, rx_plot=False)


def _quoted_opt(*args: str) -> str:
    """Concatenate N input _Strings. strip whitespace, surround with single quotes
    """
    combined = "".join(args).strip()
    return f"'{combined}'"


def models(env=None, task=None):
    """List available models.

    :param env: environment to model
    :param task: arrivals/eigenrays/rays/coherent/incoherent/semicoherent
    :returns: list of models that can be used

    >>> import bellhop as bh
    >>> bh.models()
    ['bellhop']
    >>> env = bh.create_env2d()
    >>> bh.models(env, task=coherent)
    ['bellhop']
    """
    if env is not None:
        env = check_env2d(env)
    if (env is None and task is not None) or (env is not None and task is None):
        raise ValueError('env and task should be both specified together')
    rv = []
    for m in _models:
        if m[1]().supports(env, task):
            rv.append(m[0])
    return rv

def _select_model(env, task, model):
    if model is not None:
        for m in _models:
            if m[0] == model:
                return (m[0], m[1]())
        raise ValueError('Unknown model: '+model)
    for m in _models:
        mm = m[1]()
        if mm.supports(env, task):
            return (m[0], mm)
    raise ValueError('No suitable propagation model available')

def load_shd(fname_base):
    with open(fname_base+'.shd', 'rb') as f:
        recl, = _unpack('i', f.read(4))
        # _title = str(f.read(80))
        f.seek(4*recl, 0)
        ptype = f.read(10).decode('utf8').strip()
        assert ptype == 'rectilin', 'Invalid file format (expecting ptype == "rectilin")'
        f.seek(8*recl, 0)
        nfreq, ntheta, nsx, nsy, nsd, nrd, nrr, atten = _unpack('iiiiiiif', f.read(32))
        assert nfreq == 1, 'Invalid file format (expecting nfreq == 1)'
        assert ntheta == 1, 'Invalid file format (expecting ntheta == 1)'
        assert nsd == 1, 'Invalid file format (expecting nsd == 1)'
        f.seek(32*recl, 0)
        pos_r_depth = _unpack('f'*nrd, f.read(4*nrd))
        f.seek(36*recl, 0)
        pos_r_range = _unpack('f'*nrr, f.read(4*nrr))
        pressure = _np.zeros((nrd, nrr), dtype=_np.complex128)
        for ird in range(nrd):
            recnum = 10 + ird
            f.seek(recnum*4*recl, 0)
            temp = _np.array(_unpack('f'*2*nrr, f.read(2*nrr*4)))
            pressure[ird,:] = temp[::2] + 1j*temp[1::2]
    return _pd.DataFrame(pressure, index=pos_r_depth, columns=pos_r_range)

### Bellhop propagation model ###

class _Bellhop:

    def __init__(self):
        pass

    def supports(self, env=None, task=None):
        if env is not None and env['type'] != '2D':
            return False
        fh, fname = _mkstemp(suffix='.env')
        _os.close(fh)
        fname_base = fname[:-4]
        self._unlink(fname_base+'.env')
        rv = self._bellhop(fname_base)
        self._unlink(fname_base+'.prt')
        self._unlink(fname_base+'.log')
        return rv

    def run(self, env, task, debug=False, fname_base=None):
        taskmap = {
            _Strings.arrivals:     ['A', self._load_arrivals],
            _Strings.eigenrays:    ['E', self._load_rays],
            _Strings.rays:         ['R', self._load_rays],
            _Strings.coherent:     ['C', self._load_shd],
            _Strings.incoherent:   ['I', self._load_shd],
            _Strings.semicoherent: ['S', self._load_shd]
        }
        fname_flag=False
        if fname_base is not None:
            fname_flag = True

        fname_base = self._create_env_file(env, taskmap[task][0], fname_base)

        results = None
        if self._bellhop(fname_base):
            err = self._check_error(fname_base)
            if err is not None:
                print(err)
            else:
                try:
                    results = taskmap[task][1](fname_base)
                except FileNotFoundError:
                    print('[WARN] Bellhop did not generate expected output file')
        if debug:
            print('[DEBUG] Bellhop working files: '+fname_base+'.*')
        elif fname_flag:
            print('[CUSTOM FILES] Bellhop working files: '+fname_base+'.*')
        else:
            self._unlink(fname_base+'.env')
            self._unlink(fname_base+'.bty')
            self._unlink(fname_base+'.ssp')
            self._unlink(fname_base+'.ati')
            self._unlink(fname_base+'.sbp')
            self._unlink(fname_base+'.prt')
            self._unlink(fname_base+'.log')
            self._unlink(fname_base+'.arr')
            self._unlink(fname_base+'.ray')
            self._unlink(fname_base+'.shd')
        return results

    def _bellhop(self,*args):
        try:
            runcmd = f'bellhop.exe {" ".join(list(args))}'
            #print(f"RUNNING {runcmd}")
            result = _proc.run(runcmd,
                        stderr=_proc.STDOUT, stdout=_proc.PIPE,
                        shell=True)
            #print(f"RETURN CODE: {result.returncode}")
            if result.returncode == 127:
                return False
        except OSError:
            return False
        return True

    def _unlink(self, f: str) -> None:
        try:
            _os.unlink(f)
        except FileNotFoundError:
            pass

    def _print(self, fh, s, newline=True):
        _os.write(fh, (s+'\n' if newline else s).encode())

    def _print_array(self, fh, a, label="", nn=None):
        if nn is None:
            nn = _np.size(a)
        if nn == 1:
            self._print(fh, "1")
            self._print(fh, f"{a} /  ! {label} (single value)")
        else:
            self._print(fh, f"{nn}")
            for j in a:
                self._print(fh, f"{j} ", newline=False)
            self._print(fh, f"/   ! {label} ({nn} values)")

    def _create_env_file(self, env, taskcode, fname_base=None):

        # get env file name
        if fname_base is not None:
            fname = fname_base+'.env'
            fh = _os.open(_os.path.abspath(fname), _os.O_WRONLY | _os.O_CREAT | _os.O_TRUNC)
        else:
            fh, fname = _mkstemp(suffix='.env')
            fname_base = fname[:-4]

        self._print(fh, "'"+env['name']+"'")
        self._print(fh, f"{env['frequency']}    ! FREQ (Hz)")
        self._print(fh, "1    ! NMedia=1 always for Bellhop")

        svp = env['soundspeed']
        svp_depth = 0.0
        svp_interp = _Maps.interp_rev[env['soundspeed_interp']]
        svp_boundcond = _Maps.boundcond_rev[env['top_boundary_condition']]
        svp_attunits = _Maps.attunits_rev[env['attenuation_units']]
        svp_volatt = _Maps.volatt_rev[env['volume_attenuation']]
        if isinstance(svp, _pd.DataFrame):
            svp_depth = svp.index[-1]
            if len(svp.columns) > 1:
                assert svp_interp == 'Q', "SVP DataFrame with multiple columns implies quadrilateral interpolation."
            else:
                svp = _np.hstack((_np.array([svp.index]).T, _np.asarray(svp)))
        if env['surface'] is None:
            comment = "SSP parameters: Interp / Top Boundary Cond / Attenuation Units / Volume Attenuation)"
            self._print(fh, f"'{svp_interp}{svp_boundcond}{svp_attunits}{svp_volatt}'    ! {comment}")
        else:
            comment = "SSP parameters: Interp / Top Boundary Cond / Attenuation Units / Volume Attenuation)"
            self._print(fh, f"'{svp_interp}VWT*'    ! {comment}")
            self._create_bty_ati_file(fname_base+'.ati', env['surface'], env['surface_interp'])

        max_depth = env["depth_max"] if env["depth_max"] else env['depth'] if _np.size(env['depth']) == 1 else max(_np.max(env['depth'][:,1]), svp_depth)

        if env['volume_attenuation'] == _Strings.francois_garrison:
            comment = "Francois-Garrison volume attenuation parameters (sal, temp, pH, depth)"
            self._print(fh,f"{env['fg_salinity']} {env['fg_temperature']} {env['fg_pH']} {env['fg_depth']}    ! {comment}")
            if _np.size(svp) > 1: # why is this necessary? Included to match bellhop examples but seems erroneous/misplaced/redundant
                self._print(fh, f"{svp[0,0]} {svp[0,1]} /    ! MAXDEPTH SSP")

        # max depth should be the depth of the acoustic domain, which can be deeper than the max depth bathymetry
        comment = "DEPTH_Npts  DEPTH_SigmaZ  DEPTH_Max"
        self._print(fh, f"{env['depth_npts']} {env['depth_sigmaz']} {env['depth_max']}    ! {comment}")

        if _np.size(svp) == 1:
            self._print(fh, f"0.0 {svp} /    ! '0.0' SSP_Const")
            self._print(fh, f"{max_depth} {svp} /    ! MAXDEPTH SSP_Const")
        elif svp_interp == 'Q':
            sspenv = env['ssp_env']
            # if the SSP data was provided in the ENV file, use that:
            if sspenv is not None:
                for j in range(sspenv.shape[0]):
                    self._print(fh, f"{sspenv[j,0]} {sspenv[j,1]} /  ! ssp_{j}")
            # otherwise use the SSP data specified in the dataframe:
            else:
                for j in range(svp.shape[0]):
                    self._print(fh, f"{svp.index[j]} {svp.iloc[j,0]} /  ! ssp_{j}")
            self._create_ssp_file(fname_base+'.ssp', svp)
        else:
            for j in range(svp.shape[0]):
                self._print(fh, f"{svp[j,0]} {svp[j,1]} /  ! ssp_{j}")

        depth = env['depth']
        bot_bc = _Maps.boundcond_rev[env['bottom_boundary_condition']]
        dp_flag = _Maps.bottom_rev[env['_bottom_bathymetry']]
        comment = "BOT_Boundary_cond / BOT_Roughness"
        self._print(fh, f"{_quoted_opt(bot_bc,dp_flag)} {env['bottom_roughness']}    ! {comment}")

        comment = "DEPTH_Max  BOT_SoundSpeed  BOT_SoundSpeed_Shear BOT_Density [ BOT_Absorp [ BOT_Absorp_Shear ] ]"
        if _np.size(depth) > 1:
            self._create_bty_ati_file(fname_base+'.bty', depth, env['depth_interp'])

        if env['bottom_boundary_condition'] == "acousto-elastic":
            if env['bottom_absorption'] is None:
                self._print(fh, f"{env['depth_max']} {env['bottom_soundspeed']} {env['bottom_soundspeed_shear']} {env['bottom_density']/1000} /  ! {comment}")
            elif env['bottom_absorption_shear'] is None:
                self._print(fh, "%0.6f %0.6f %0.6f %0.6f %0.6f /" % (env['depth_max'], env['bottom_soundspeed'], env['bottom_soundspeed_shear'], env['bottom_density']/1000, env['bottom_absorption']))
            else:
                self._print(fh, "%0.6f %0.6f %0.6f %0.6f %0.6f %0.6f /" % (env['depth_max'], env['bottom_soundspeed'], env['bottom_soundspeed_shear'], env['bottom_density']/1000, env['bottom_absorption'], env['bottom_absorption_shear']))

        if env['bottom_boundary_condition'] == "from-file":
            self._create_refl_coeff_file(fname_base+".brc", env['bottom_reflection_coefficient'])

        self._print_array(fh, env['tx_depth'], nn=env['tx_ndepth'], label="TX_DEPTH")
        self._print_array(fh, env['rx_depth'], nn=env['rx_ndepth'], label="RX_DEPTH")
        self._print_array(fh, env['rx_range']/1000, nn=env['rx_nrange'], label="RX_RANGE")

        beamtype = _Maps.beam_rev[env['beam_type']]
        beampattern = " "
        txtype = _Maps.source_rev[env['tx_type']]
        gridtype = _Maps.grid_rev[env['grid']]
        if env['tx_directionality'] is not None:
            beampattern = "*"
            self._create_sbp_file(fname_base+'.sbp', env['tx_directionality'])
        runtype_str = taskcode + beamtype + beampattern + txtype + gridtype
        self._print(fh, f"'{runtype_str.rstrip()}'  ! RUN TYPE")
        self._print(fh, f"{env['nbeams']} ! NBeams")
        self._print(fh, "%0.6f %0.6f /   ! ALPHA1,2 (degrees)" % (env['min_angle'], env['max_angle']))
        step_size = env["step_size"] or 0.0
        box_depth = env["box_depth"] or 1.01*max_depth
        box_range = env["box_range"] or 1.01*_np.max(env['rx_range'])
        self._print(fh, f"{step_size} {box_depth} {box_range/1000} ! STEP (m), ZBOX (m), RBOX (km)")
        _os.close(fh)
        return fname_base

    def _create_bty_ati_file(self, filename, depth, interp):
        with open(filename, 'wt') as f:
            f.write("'%c'\n" % ('C' if interp == _Strings.curvilinear else 'L'))
            f.write(str(depth.shape[0])+"\n")
            for j in range(depth.shape[0]):
                f.write("%0.6f %0.6f\n" % (depth[j,0]/1000, depth[j,1]))

    def _create_sbp_file(self, filename, dir):
        with open(filename, 'wt') as f:
            f.write(str(dir.shape[0])+"\n")
            for j in range(dir.shape[0]):
                f.write("%0.6f %0.6f\n" % (dir[j,0], dir[j,1]))

    def _create_refl_coeff_file(self, filename, rc):
        with open(filename, 'wt') as f:
            f.write(str(rc.shape[0])+"\n")
            for j in range(rc.shape[0]):
                f.write(f"{rc[j,0]} {rc[j,1]} {rc[j,2]}\n")

    def _create_ssp_file(self, filename, svp):
        with open(filename, 'wt') as f:
            f.write(str(svp.shape[1])+"\n")
            for j in range(svp.shape[1]):
                f.write("%0.6f%c" % (svp.columns[j]/1000, '\n' if j == svp.shape[1]-1 else ' '))
            for k in range(svp.shape[0]):
                for j in range(svp.shape[1]):
                    f.write("%0.6f%c" % (svp.iloc[k,j], '\n' if j == svp.shape[1]-1 else ' '))

    def _readf(self, f, types, dtype=str):
        if type(f) is str:
            p = _re.split(r' +', f.strip())
        else:
            p = _re.split(r' +', f.readline().strip())
        for j in range(len(p)):
            if len(types) > j:
                p[j] = types[j](p[j])
            else:
                p[j] = dtype(p[j])
        return tuple(p)

    def _check_error(self, fname_base: str):
        err = None
        try:
            with open(fname_base+'.prt', 'rt') as f:
                for lno, s in enumerate(f):
                    if err is not None:
                        err += '[BELLHOP] ' + s
                    elif '*** FATAL ERROR ***' in s:
                        err = '\n[BELLHOP] ' + s
        except FileNotFoundError:
            pass
        return err

    def _load_arrivals(self, fname_base):
        with open(fname_base+'.arr', 'rt') as f:
            hdr = f.readline()
            if hdr.find('2D') >= 0:
                freq = self._readf(f, (float,))
                tx_depth_info = self._readf(f, (int,), float)
                tx_depth_count = tx_depth_info[0]
                tx_depth = tx_depth_info[1:]
                assert tx_depth_count == len(tx_depth)
                rx_depth_info = self._readf(f, (int,), float)
                rx_depth_count = rx_depth_info[0]
                rx_depth = rx_depth_info[1:]
                assert rx_depth_count == len(rx_depth)
                rx_range_info = self._readf(f, (int,), float)
                rx_range_count = rx_range_info[0]
                rx_range = rx_range_info[1:]
                assert rx_range_count == len(rx_range)
            else:
                freq, tx_depth_count, rx_depth_count, rx_range_count = self._readf(hdr, (float, int, int, int))
                tx_depth = self._readf(f, (float,)*tx_depth_count)
                rx_depth = self._readf(f, (float,)*rx_depth_count)
                rx_range = self._readf(f, (float,)*rx_range_count)
            arrivals = []
            for j in range(tx_depth_count):
                f.readline()
                for k in range(rx_depth_count):
                    for m in range(rx_range_count):
                        count = int(f.readline())
                        for n in range(count):
                            data = self._readf(f, (float, float, float, float, float, float, int, int))
                            arrivals.append(_pd.DataFrame({
                                'tx_depth_ndx': [j],
                                'rx_depth_ndx': [k],
                                'rx_range_ndx': [m],
                                'tx_depth': [tx_depth[j]],
                                'rx_depth': [rx_depth[k]],
                                'rx_range': [rx_range[m]],
                                'arrival_number': [n],
                                # 'arrival_amplitude': [data[0]*_np.exp(1j * data[1]* _np.pi/180)],
                                'arrival_amplitude': [data[0] * _np.exp( -1j * (_np.deg2rad(data[1]) + freq[0] * 2 * _np.pi * (data[3] * 1j +  data[2])))],
                                'time_of_arrival': [data[2]],
                                'complex_time_of_arrival': [data[2] + 1j*data[3]],
                                'angle_of_departure': [data[4]],
                                'angle_of_arrival': [data[5]],
                                'surface_bounces': [data[6]],
                                'bottom_bounces': [data[7]]
                            }, index=[len(arrivals)+1]))
        return _pd.concat(arrivals)

    def _load_shd(self, fname_base):
        return load_shd(fname_base)

    def _load_rays(self, fname_base):
        with open(fname_base+'.ray', 'rt') as f:
            f.readline()
            f.readline()
            f.readline()
            f.readline()
            f.readline()
            f.readline()
            f.readline()
            rays = []
            while True:
                s = f.readline()
                if s is None or len(s.strip()) == 0:
                    break
                a = float(s)
                pts, sb, bb = self._readf(f, (int, int, int))
                ray = _np.empty((pts, 2))
                for k in range(pts):
                    ray[k,:] = self._readf(f, (float, float))
                rays.append(_pd.DataFrame({
                    'angle_of_departure': [a],
                    'surface_bounces': [sb],
                    'bottom_bounces': [bb],
                    'ray': [ray]
                }))
        return _pd.concat(rays)



_models.append(('bellhop', _Bellhop))

__all__ = [
    name
    for name in globals()
    if not name.startswith("_")  # ignore private names
]
