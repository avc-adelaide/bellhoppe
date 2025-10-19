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

from typing import Any, Dict, List, Optional, Union

import numpy as _np

from bellhop.constants import _Strings, Defaults

# this format to explicitly mark the functions as public:
from bellhop.create import create_env2d as create_env2d
from bellhop.create import check_env2d as check_env2d
from bellhop.create import print_env as print_env

from bellhop.readers import read_env2d as read_env2d
from bellhop.readers import read_ssp as read_ssp
from bellhop.readers import read_ati as read_ati
from bellhop.readers import read_bty as read_bty
from bellhop.readers import read_sbp as read_sbp
from bellhop.readers import read_trc as read_trc
from bellhop.readers import read_brc as read_brc

from bellhop.bellhop import Bellhop
_models: List[Bellhop] = []

def new_model(name: str, **kwargs: Any) -> Bellhop:
    """Instantiate a new Bellhop model and add it to the list of models.

    Creates a Bellhop instance with the specified parameters and
    adds it to the internal registry of models for later access.
    
    Parameters
    ----------
    name : str
        Descriptive name for this model instance, must be unique
    
    **kwargs
        Keyword arguments passed directly to the Bellhop constructor.
        Common parameters include:
        - exe : str
            Filename of the Bellhop executable
    
    Returns
    -------
    Bellhop
        The newly created Bellhop model instance.
    
    Examples
    --------
    >>> bh.models() # there is always a default model
    ['Bellhop']
    >>> bh.new_model(name="Bellhop AT", exe="bellhop_at.exe")
    >>> bh.models()
    ['Bellhop', 'Bellhop AT']
    """
    for m in _models:
        if name == m.name:
            raise ValueError(f"Bellhop model with this name ('{name}') already exists.")
    model = Bellhop(name=name, **kwargs)
    _models.append(model)
    return model

new_model(name=Defaults.model_name)

def models(env: Optional[Dict[str, Any]] = None, task: Optional[str] = None) -> List[str]:
    """List available models.

    :param env: environment to model
    :param task: arrivals/eigenrays/rays/coherent/incoherent/semicoherent
    :returns: list of models that can be used

    >>> import bellhop as bh
    >>> bh.models()
    ['bellhop']
    >>> env = bh.create_env2d()
    >>> bh.models(env, task="coherent")
    ['bellhop']
    """
    if env is not None:
        env = check_env2d(env)
    if (env is None and task is not None) or (env is not None and task is None):
        raise ValueError('env and task should be both specified together')
    rv: List[str] = []
    for m in _models:
        if m.supports(env, task):
            rv.append(m.name)
    return rv

def compute(env: Union[Dict[str, Any],List[Dict[str, Any]]],
            model: Optional[Any] = None,
            task: Optional[Any] = None,
            debug: bool = False,
            fname_base: Optional[str] = None
           ) -> Union[Dict[str, Any],List[Dict[str, Any]]]:
    """Compute Bellhop task(s) for given model(s) and environment(s).

    :param env: environment definition (which includes the task specification)
    :param model: propagation model to use (None to auto-select)
    :param task: optional task or list of tasks ("arrivals", etc.)
    :param debug: generate debug information for propagation model
    :param fname_base: base file name for Bellhop working files, default (None), creates a temporary file
    :returns: dictionary of results and metadata (model used, task executed, etc)

    If any of env, model, and/or task are lists then multiple runs are performed
    with a list of dictionary outputs returned.

    >>> import bellhop as bh
    >>> env = bh.read_env2d("...")
    >>> output = bh.compute(env)
    >>> assert output['task'] == "arrivals"
    >>> bh.plot_arrivals(output['results'])
    """
    envs = env if isinstance(env, list) else [env]
    models = model if isinstance(model, list) else [model]
    tasks = task if isinstance(task, list) else [task]
    results: List[Any] = []
    for this_env in envs:
        for this_model in models:
            for this_task in tasks:
                env_chk = check_env2d(this_env)
                this_task = this_task or env_chk.get('task')
                if this_task is None:
                    raise ValueError("Task must be specified in env or as parameter")
                model_fn = _select_model(env_chk, this_task, this_model, debug)
                results.append({
                       "name": env_chk["name"],
                       "model": this_model,
                       "task": this_task,
                       "results": model_fn.run(env_chk, this_task, debug, fname_base),
                      })
    assert len(results) > 0, "No results generated"
    return results if len(results) > 1 else results[0]

def _select_model(env: Dict[str, Any],
                  task: str,
                  model: Optional[str] = None,
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
            if m.name == model:
                debug and print(f'Model selected: {m.name}')
                return m
        raise ValueError(f"Unknown model: '{model}'")

    debug and print(debug, "Searching for propagation model:")
    for mm in _models:
        if mm.supports(env, task):
            debug and print(f'Model found: {mm.name}')
            return mm
    raise ValueError('No suitable propagation model available')

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
    output = compute(env, model, _Strings.arrivals, debug, fname_base)
    assert isinstance(output, dict), "Single env should return single result"
    return output['results']

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
    output = compute(env, model, _Strings.eigenrays, debug, fname_base)
    assert isinstance(output, dict), "Single env should return single result"
    return output['results']

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
    output = compute(env, model, _Strings.rays, debug, fname_base)
    assert isinstance(output, dict), "Single env should return single result"
    return output['results']

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
    task = mode or env.get("interference_mode") or Defaults.interference_mode
    debug and print(f"  {mode=}")
    env = check_env2d(env)
    if _np.size(env['source_depth']) > 1:
        env = env.copy()
        env['source_depth'] = env['source_depth'][source_depth_ndx]
    output = compute(env, model, task, debug, fname_base)
    assert isinstance(output, dict), "Single env should return single result"
    return output['results']

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

### Export module names for auto-importing in __init__.py

__all__ = [
    name for name in globals() if not name.startswith("_")  # ignore private names
]
