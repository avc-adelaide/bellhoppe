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

from typing import Any, List, Optional, Union, Tuple

import numpy as _np
import pandas as _pd

from bellhop.constants import _Strings, Defaults

# this format to explicitly mark the functions as public:
from bellhop.readers import read_env as read_env
from bellhop.readers import read_ssp as read_ssp
from bellhop.readers import read_ati as read_ati
from bellhop.readers import read_bty as read_bty
from bellhop.readers import read_sbp as read_sbp
from bellhop.readers import read_trc as read_trc
from bellhop.readers import read_brc as read_brc

from bellhop.environment import EnvironmentConfig
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
    ['bellhop']
    >>> bh.new_model(name="bellhop-at", exe="bellhop_at.exe")
    >>> bh.models()
    ['bellhop', 'bellhop-at']
    """
    for m in _models:
        if name == m.name:
            raise ValueError(f"Bellhop model with this name ('{name}') already exists.")
    model = Bellhop(name=name, **kwargs)
    _models.append(model)
    return model

new_model(name=Defaults.model_name)

def models(env: Optional[EnvironmentConfig] = None, task: Optional[str] = None) -> List[str]:
    """List available models.

    Parameters
    ----------
    env : dict, optional
        Environment to model
    task : str, optional
        Task type: arrivals/eigenrays/rays/coherent/incoherent/semicoherent

    Returns
    -------
    list of str
        List of models that can be used

    Examples
    --------
    >>> import bellhop as bh
    >>> bh.models()
    ['bellhop']
    >>> env = bh.create_env()
    >>> bh.models(env, task="coherent")
    ['bellhop']
    """
    if env is not None:
        env = check_env(env)
    if (env is None and task is not None) or (env is not None and task is None):
        raise ValueError('env and task should be both specified together')
    rv: List[str] = []
    for m in _models:
        if m.supports(env, task):
            rv.append(m.name)
    return rv

def create_env2d(**kv: Any) -> EnvironmentConfig:
    """Backwards compatibility for create_env"""
    return create_env(**kv)

def create_env(**kv: Any) -> EnvironmentConfig:
    """Create a new underwater environment.

    Parameters
    ----------
    **kv : dict
        Keyword arguments for environment configuration.

    Returns
    -------
    env : dict
        A new underwater environment dictionary.

    Raises
    ------
    ValueError
        If any parameter value is invalid according to BELLHOP constraints.

    Example
    -------

    To see all the parameters available and their default values:

    >>> import bellhop as bh
    >>> env = bh.create_env()
    >>> print(env)

    The environment parameters may be changed by passing keyword arguments
    or modified later using dictionary notation:

    >>> import bellhop as bh
    >>> env = bh.create_env(depth=40, soundspeed=1540)
    >>> print(env)
    >>> env['depth'] = 25
    >>> env['bottom_soundspeed'] = 1800
    >>> print(env)

    The default environment has a constant sound speed.
    A depth dependent sound speed profile be provided as a Nx2 array of (depth, sound speed):

    >>> import bellhop as bh
    >>> env = bh.create_env(depth=20,
    >>>.        soundspeed=[[0,1540], [5,1535], [10,1535], [20,1530]])

    A range-and-depth dependent sound speed profile can be provided as a Pandas frame:

    >>> import bellhop as bh
    >>> import pandas as pd
    >>> ssp2 = pd.DataFrame({
              0: [1540, 1530, 1532, 1533],     # profile at 0 m range
            100: [1540, 1535, 1530, 1533],     # profile at 100 m range
            200: [1530, 1520, 1522, 1525] },   # profile at 200 m range
            index=[0, 10, 20, 30])             # depths of the profile entries in m
    >>> env = bh.create_env(depth=20, soundspeed=ssp2)

    The default environment has a constant water depth. A range dependent bathymetry
    can be provided as a Nx2 array of (range, water depth):

    >>> import bellhop as bh
    >>> env = bh.create_env(depth=[[0,20], [300,10], [500,18], [1000,15]])
    """
    env = EnvironmentConfig()

    # Apply user-provided values to environment
    for k, v in kv.items():
        if k not in env.keys():
            raise KeyError('Unknown key: '+k)

        # Convert everything to ndarray except DataFrames and scalars
        if isinstance(v, _pd.DataFrame):
            env[k] = v
        elif _np.isscalar(v):
            env[k] = v
        else:
            env[k] = _np.asarray(v, dtype=_np.float64)

    return env



def check_env(env: EnvironmentConfig) -> EnvironmentConfig:
    """Check the validity of a underwater environment definition.

    This function is automatically executed before any of the compute_ functions,
    but must be called manually after setting environment parameters if you need to
    query against defaults that may be affected.

    Parameters
    ----------
    env : dict
        Environment definition

    Returns
    -------
    dict
        Updated environment definition

    Raises
    ------
    ValueError
        If the environment is invalid

    Examples
    --------
    >>> import bellhop as bh
    >>> env = bh.create_env()
    >>> env = check_env(env)
    """

    env._finalise()
    return env.check()


def check_env2d(env: EnvironmentConfig) -> EnvironmentConfig:
    """Backwards compatibility for check_env"""
    return check_env(env=env)

def compute(
            env: Union[EnvironmentConfig,List[EnvironmentConfig]],
            model: Optional[Any] = None,
            task: Optional[Any] = None,
            debug: bool = False,
            fname_base: Optional[str] = None
           ) -> Union[  Any,
                        EnvironmentConfig,
                        Tuple[List[EnvironmentConfig], _pd.DataFrame]
                     ]:
    """Compute Bellhop task(s) for given model(s) and environment(s).

    Parameters
    ----------
    env : dict or list of dict
        Environment definition (which includes the task specification)
    model : str, optional
        Propagation model to use (None to auto-select)
    task : str or list of str, optional
        Optional task or list of tasks ("arrivals", etc.)
    debug : bool, default=False
        Generate debug information for propagation model
    fname_base : str, optional
        Base file name for Bellhop working files, default (None), creates a temporary file

    Returns
    -------
    dict
        Single run result (and associated metadata) if only one computation is performed.
    tuple of (list of dict, pandas.DataFrame)
        List of results and an index DataFrame if multiple computations are performed.

    Notes
    -----
    If any of env, model, and/or task are lists then multiple runs are performed
    with a list of dictionary outputs returned. The ordering is based on loop iteration
    but might not be deterministic; use the index DataFrame to extract and filter the
    output logically.

    Examples
    --------
    Single task based on reading a complete `.env` file:
    >>> import bellhop as bh
    >>> env = bh.read_env("...")
    >>> output = bh.compute(env)
    >>> assert output['task'] == "arrivals"
    >>> bh.plot_arrivals(output['results'])

    Multiple tasks:
    >>> import bellhop as bh
    >>> env = bh.create_env()
    >>> output, ind_df = bh.compute(env,task=["arrivals", "eigenrays"])
    >>> bh.plot_arrivals(output[0]['results'])
    """
    envs = env if isinstance(env, list) else [env]
    models = model if isinstance(model, list) else [model]
    tasks = task if isinstance(task, list) else [task]
    results: List[Any] = []
    for this_env in envs:
        debug and print(f"Using environment: {this_env['name']}")
        for this_model in models:
            debug and print(f"Using model: {'[None] (default)' if this_model is None else this_model.get('name')}")
            for this_task in tasks:
                debug and print(f"Using task: {this_task}")
                env_chk = check_env(this_env)
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
    index_df = _pd.DataFrame([
        {
            "i": i,
            "name": r["name"],
            "model": getattr(r["model"], "name", str(r["model"])) if r["model"] is not None else None,
            "task": r["task"],
        }
        for i, r in enumerate(results)
    ])
    index_df.set_index("i", inplace=True)
    if len(results) > 1:
        return results, index_df
    else:
        return results[0]

def _select_model(env: EnvironmentConfig,
                  task: str,
                  model: Optional[str] = None,
                  debug: bool = False
                 ) -> Any:
    """Finds a model to use, or if a model is requested validate it.

    Parameters
    ----------
    env : dict
        The environment dictionary
    task : str
        The task to be computed
    model : str, optional
        Specified model to use
    debug : bool, default=False
        Whether to print diagnostics

    Returns
    -------
    Bellhop
        The model function to evaluate its `.run()` method

    Notes
    -----
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

    debug and print("Searching for propagation model:")
    for mm in _models:
        if mm.supports(env, task):
            debug and print(f'Model found: {mm.name}')
            return mm
    raise ValueError('No suitable propagation model available')

def compute_arrivals(env: EnvironmentConfig, model: Optional[Any] = None, debug: bool = False, fname_base: Optional[str] = None) -> Any:
    """Compute arrivals between each transmitter and receiver.

    Parameters
    ----------
    env : dict
        Environment definition
    model : str, optional
        Propagation model to use (None to auto-select)
    debug : bool, default=False
        Generate debug information for propagation model
    fname_base : str, optional
        Base file name for Bellhop working files, default (None), creates a temporary file

    Returns
    -------
    pandas.DataFrame
        Arrival times and coefficients for all transmitter-receiver combinations

    Examples
    --------
    >>> import bellhop as bh
    >>> env = bh.create_env()
    >>> arrivals = bh.compute_arrivals(env)
    >>> bh.plot_arrivals(arrivals)
    """
    output = compute(env, model, _Strings.arrivals, debug, fname_base)
    assert isinstance(output, dict), "Single env should return single result"
    return output['results']

def compute_eigenrays(env: EnvironmentConfig, source_depth_ndx: int = 0, receiver_depth_ndx: int = 0, receiver_range_ndx: int = 0, model: Optional[Any] = None, debug: bool = False, fname_base: Optional[str] = None) -> Any:
    """Compute eigenrays between a given transmitter and receiver.

    Parameters
    ----------
    env : dict
        Environment definition
    source_depth_ndx : int, default=0
        Transmitter depth index
    receiver_depth_ndx : int, default=0
        Receiver depth index
    receiver_range_ndx : int, default=0
        Receiver range index
    model : str, optional
        Propagation model to use (None to auto-select)
    debug : bool, default=False
        Generate debug information for propagation model
    fname_base : str, optional
        Base file name for Bellhop working files, default (None), creates a temporary file

    Returns
    -------
    pandas.DataFrame
        Eigenrays paths

    Examples
    --------
    >>> import bellhop as bh
    >>> env = bh.create_env()
    >>> rays = bh.compute_eigenrays(env)
    >>> bh.plot_rays(rays, width=1000)
    """
    env = check_env(env)
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

def compute_rays(env: EnvironmentConfig, source_depth_ndx: int = 0, model: Optional[Any] = None, debug: bool = False, fname_base: Optional[str] = None) -> Any:
    """Compute rays from a given transmitter.

    Parameters
    ----------
    env : dict
        Environment definition
    source_depth_ndx : int, default=0
        Transmitter depth index
    model : str, optional
        Propagation model to use (None to auto-select)
    debug : bool, default=False
        Generate debug information for propagation model
    fname_base : str, optional
        Base file name for Bellhop working files, default (None), creates a temporary file

    Returns
    -------
    pandas.DataFrame
        Ray paths

    Examples
    --------
    >>> import bellhop as bh
    >>> env = bh.create_env()
    >>> rays = bh.compute_rays(env)
    >>> bh.plot_rays(rays, width=1000)
    """
    env = check_env(env)
    if _np.size(env['source_depth']) > 1:
        env = env.copy()
        env['source_depth'] = env['source_depth'][source_depth_ndx]
    output = compute(env, model, _Strings.rays, debug, fname_base)
    assert isinstance(output, dict), "Single env should return single result"
    return output['results']

def compute_transmission_loss(env: EnvironmentConfig, source_depth_ndx: int = 0, mode: Optional[str] = None, model: Optional[Any] = None, debug: bool = False, fname_base: Optional[str] = None) -> Any:
    """Compute transmission loss from a given transmitter to all receviers.

    Parameters
    ----------
    env : dict
        Environment definition
    source_depth_ndx : int, default=0
        Transmitter depth index
    mode : str, optional
        Coherent, incoherent or semicoherent
    model : str, optional
        Propagation model to use (None to auto-select)
    debug : bool, default=False
        Generate debug information for propagation model
    fname_base : str, optional
        Base file name for Bellhop working files, default (None), creates a temporary file

    Returns
    -------
    numpy.ndarray
        Complex transmission loss at each receiver depth and range

    Examples
    --------
    >>> import bellhop as bh
    >>> env = bh.create_env()
    >>> tloss = bh.compute_transmission_loss(env, mode=bh.incoherent)
    >>> bh.plot_transmission_loss(tloss, width=1000)
    """
    env = env.copy()
    task = mode or env.get("interference_mode") or Defaults.interference_mode
    env['interference_mode'] = task
    debug and print(f"  {task=}")
    env = check_env(env)
    if _np.size(env['source_depth']) > 1:
        env['source_depth'] = env['source_depth'][source_depth_ndx]
    output = compute(env, model, task, debug, fname_base)
    assert isinstance(output, dict), "Single env should return single result"
    return output['results']

def arrivals_to_impulse_response(arrivals: Any, fs: float, abs_time: bool = False) -> Any:
    """Convert arrival times and coefficients to an impulse response.

    Parameters
    ----------
    arrivals : pandas.DataFrame
        Arrivals times (s) and coefficients
    fs : float
        Sampling rate (Hz)
    abs_time : bool, default=False
        Absolute time (True) or relative time (False)

    Returns
    -------
    numpy.ndarray
        Impulse response

    Notes
    -----
    If `abs_time` is set to True, the impulse response is placed such that
    the zero time corresponds to the time of transmission of signal.

    Examples
    --------
    >>> import bellhop as bh
    >>> env = bh.create_env()
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
