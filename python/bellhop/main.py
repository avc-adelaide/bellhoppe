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
to work, the complete bellhop.py package must be built and installed
and `bellhop.exe` should be in your PATH.
"""

from typing import Any, Dict, List, Optional

import numpy as _np

from bellhop.constants import _Strings

# this format to explicitly mark the functions as public:
from bellhop.create import create_env2d as create_env2d
from bellhop.create import check_env2d as check_env2d
from bellhop.create import print_env as print_env

from bellhop.readers import read_env2d as read_env2d
from bellhop.readers import read_ssp as read_ssp
from bellhop.readers import read_ati as read_ati
from bellhop.readers import read_bty as read_bty
from bellhop.readers import read_sbp as read_sbp
from bellhop.readers import read_refl_coeff as read_refl_coeff

from bellhop.bellhop import Bellhop

# models (in order of preference)
_models: List[Any] = []
_models.append(('bellhop', Bellhop))

def _debug_print(debug: bool, msg: str) -> None:
    if debug:
        print("[DEBUG]", msg)

def compute_arrivals(env: Dict[str, Any], model: Optional[Any] = None, debug: bool = False, fname_base: Optional[str] = None) -> Any:
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
    model = _select_model(env, _Strings.arrivals, model, debug)
    return model.run(env, _Strings.arrivals, debug, fname_base)

def compute_eigenrays(env: Dict[str, Any], source_depth_ndx: int = 0, receiver_depth_ndx: int = 0, receiver_range_ndx: int = 0, model: Optional[Any] = None, debug: bool = False, fname_base: Optional[str] = None) -> Any:
    """Compute eigenrays between a given transmitter and receiver.

    :param env: environment definition
    :param source_depth_ndx: transmitter depth index
    :param receiver_depth_ndx: receiver depth index
    :param receiver_range_ndx: receiver range index
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
    if _np.size(env['source_depth']) > 1:
        env['source_depth'] = env['source_depth'][source_depth_ndx]
    if _np.size(env['receiver_depth']) > 1:
        env['receiver_depth'] = env['receiver_depth'][receiver_depth_ndx]
    if _np.size(env['receiver_range']) > 1:
        env['receiver_range'] = env['receiver_range'][receiver_range_ndx]
    model = _select_model(env, _Strings.eigenrays, model, debug)
    return model.run(env, _Strings.eigenrays, debug, fname_base)

def compute_rays(env: Dict[str, Any], source_depth_ndx: int = 0, model: Optional[Any] = None, debug: bool = False, fname_base: Optional[str] = None) -> Any:
    """Compute rays from a given transmitter.

    :param env: environment definition
    :param source_depth_ndx: transmitter depth index
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
    if _np.size(env['source_depth']) > 1:
        env = env.copy()
        env['source_depth'] = env['source_depth'][source_depth_ndx]
    model = _select_model(env, _Strings.rays, model, debug)
    return model.run(env, _Strings.rays, debug, fname_base)

def compute_transmission_loss(env: Dict[str, Any], source_depth_ndx: int = 0, mode: Optional[str] = None, model: Optional[Any] = None, debug: bool = False, fname_base: Optional[str] = None) -> Any:
    """Compute transmission loss from a given transmitter to all receviers.

    :param env: environment definition
    :param source_depth_ndx: transmitter depth index
    :param mode: coherent, incoherent or semicoherent
    :param model: propagation model to use (None to auto-select)
    :param debug: generate debug information for propagation model
    :param fname_base: base file name for Bellhop working files, default (None), creates a temporary file
    :returns: complex transmission loss at each receiver depth and range

    >>> import bellhop as bh
    >>> env = bh.create_env2d()
    >>> tloss = bh.compute_transmission_loss(env, mode=bh.incoherent)
    >>> bh.plot_transmission_loss(tloss, width=1000)
    """
    mode = env.interference_mode or _Strings.coherent
    env = check_env2d(env)
    if _np.size(env['source_depth']) > 1:
        env = env.copy()
        env['source_depth'] = env['source_depth'][source_depth_ndx]
    model = _select_model(env, mode, model, debug)
    return model.run(env, mode, debug, fname_base)

def arrivals_to_impulse_response(arrivals: Any, fs: float, abs_time: bool = False) -> Any:
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


def models(env: Optional[Dict[str, Any]] = None, task: Optional[str] = None) -> List[str]:
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
    rv: List[str] = []
    for m in _models:
        if m[1]().supports(env, task):
            rv.append(m[0])
    return rv

def _select_model(env: Dict[str, Any],
                  task: str,
                  model: Optional[Any] = None,
                  debug: bool = False
                 ) -> Any:
    """Finds a model to use, or if a model is requested validate it.

    :param env: the environment dictionary
    :param task: the task to be computed
    :param model: specified model to use
    :param debug: whether to print diagnostics

    :returns: the model function to evaluate its `.run()` method

    The intention of this function is to allow multiple models to be "loaded" and the
    first appropriate model found is used for the computation.

    This is likely to be more useful once we extend the code to handle things like 3D
    bellhop models, GPU bellhop models, and so on.
    """
    if model is not None:
        for m in _models:
            if m[0] == model:
                _debug_print(debug, 'Model: '+m[0])
                return m[1]()
        raise ValueError(f"Unknown model: '{model}'")
    _debug_print(debug, "Searching for propagation model:")
    for m in _models:
        mm = m[1]()
        if mm.supports(env, task):
            _debug_print(debug, 'Model found: '+m[0])
            return mm
    raise ValueError('No suitable propagation model available')


### Export module names for auto-importing in __init__.py

__all__ = [
    name for name in globals() if not name.startswith("_")  # ignore private names
]
