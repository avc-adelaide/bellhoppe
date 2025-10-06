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

import warnings
from typing import Any, Dict, List, Optional

import numpy as _np
import pandas as _pd

from bellhop.constants import _Strings
import bellhop.environment as _env
from bellhop.environment import EnvironmentConfig, validate_transmission_loss_mode, validate_source_type

# this format to explicitly mark the functions as public:
from bellhop.readers import read_env2d as read_env2d
from bellhop.readers import read_ssp as read_ssp
from bellhop.readers import read_ati as read_ati
from bellhop.readers import read_bty as read_bty
from bellhop.readers import read_sbp as read_sbp
from bellhop.readers import read_refl_coeff as read_refl_coeff

from bellhop.bellhop import _Bellhop

# models (in order of preference)
_models: List[Any] = []
_models.append(('bellhop', _Bellhop))

def _debug_print(debug: bool, msg: str) -> None:
    if debug:
        print("[DEBUG]", msg)

def create_env2d(**kv: Any) -> Dict[str, Any]:
    """Create a new 2D underwater environment with automatic validation.

    Parameters
    ----------
    **kv : dict
        Keyword arguments for environment configuration.

    Returns
    -------
    env : dict
        A new 2D underwater environment dictionary.

    Raises
    ------
    ValueError
        If any parameter value is invalid according to BELLHOP constraints.

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
    env = _env.new()

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

    # Validate options using dataclass validation
    env = _validate_options_with_dataclass(env)

    return env



def _validate_options_with_dataclass(env: Dict[str, Any]) -> Dict[str, Any]:
    """Validate environment options using dataclass validation.

    This function validates all option fields using the dataclass,
    then returns the original dictionary.
    """
    try:
        # Validate options by creating dataclass instance (for side effects only)
        EnvironmentConfig.from_dict(env)
        return env  # Return original dict if validation passes
    except (ValueError, TypeError) as e:
        raise ValueError(str(e))


def check_env2d(env: Dict[str, Any]) -> Dict[str, Any]:
    """Check the validity of a 2D underwater environment definition.

    This function is automatically executed before any of the compute_ functions,
    but must be called manually after setting environment parameters if you need to
    query against defaults that may be affected.

    :param env: environment definition
    :returns: updated environment definition

    Exceptions are thrown with appropriate error messages if the environment is invalid.

    >>> import bellhop as bh
    >>> env = bh.create_env2d()
    >>> env = check_env2d(env)
    """
    env = _finalise_environment(env)

    # Use dataclass validation for option checking
    env = _validate_options_with_dataclass(env)

    try:
        assert env['type'] == '2D', 'Not a 2D environment'
        max_range = _np.max(env['receiver_range'])
        if env['surface'] is not None:
            assert _np.size(env['surface']) > 1, 'surface must be an Nx2 array'
            assert env['surface'].ndim == 2, 'surface must be a scalar or an Nx2 array'
            assert env['surface'].shape[1] == 2, 'surface must be a scalar or an Nx2 array'
            assert env['surface'][0,0] <= 0, 'First range in surface array must be 0 m'
            assert env['surface'][-1,0] >= max_range, 'Last range in surface array must be beyond maximum range: '+str(max_range)+' m'
            assert _np.all(_np.diff(env['surface'][:,0]) > 0), 'surface array must be strictly monotonic in range'
        if _np.size(env['depth']) > 1:
            assert env['depth'].ndim == 2, 'depth must be a scalar or an Nx2 array'
            assert env['depth'].shape[1] == 2, 'depth must be a scalar or an Nx2 array'
            assert env['depth'][0,0] <= 0, 'First range in depth array must be 0 m'
            assert env['depth'][-1,0] >= max_range, 'Last range in depth array must be beyond maximum range: '+str(max_range)+' m'
            assert _np.all(_np.diff(env['depth'][:,0]) > 0), 'Depth array must be strictly monotonic in range'
            assert env["_bathymetry"] == _Strings.from_file, 'len(depth)>1 requires BTY file'
        if isinstance(env['soundspeed'], _pd.DataFrame):
            if len(env['soundspeed'].columns) > 1:
                assert env['soundspeed_interp'] == _Strings.quadrilateral, "SVP DataFrame with multiple columns implies quadrilateral interpolation."
            # For DataFrames, apply the same minimum point requirements as numpy arrays
            if env['soundspeed_interp'] == _Strings.spline:
                assert len(env['soundspeed']) > 3, 'soundspeed profile must have at least 4 points for spline interpolation'
            else:
                assert len(env['soundspeed']) > 1, 'soundspeed profile must have at least 2 points'
            assert env['soundspeed'].index[0] <= 0, 'First depth in soundspeed array must be 0 m'
            assert env['soundspeed'].index[-1] >= env['depth_max'], 'Last depth in soundspeed array must be beyond water depth: '+str(env['depth_max'])+' m'
            assert _np.all(_np.diff(env['soundspeed'].index) > 0), 'Soundspeed array must be strictly monotonic in depth'
            # TODO: check soundspeed range limits
        elif _np.size(env['soundspeed']) > 1:
            assert env['soundspeed'].ndim == 2, 'soundspeed must be a scalar or an Nx2 array'
            assert env['soundspeed'].shape[1] == 2, 'soundspeed must be a scalar or an Nx2 array'
            # Minimum points depend on interpolation type
            if env['soundspeed_interp'] == _Strings.spline:
                assert env['soundspeed'].shape[0] > 3, 'soundspeed profile must have at least 4 points for spline interpolation'
            else:
                assert env['soundspeed'].shape[0] > 1, 'soundspeed profile must have at least 2 points'
            assert env['soundspeed'][0,0] <= 0, 'First depth in soundspeed array must be 0 m'
            assert env['soundspeed'][-1,0] >= env['depth_max'], 'Last depth in soundspeed array must be beyond water depth: '+str(env['depth_max'])+' m'
            assert _np.all(_np.diff(env['soundspeed'][:,0]) > 0), 'Soundspeed array must be strictly monotonic in depth'
            if env['depth_max'] not in env['soundspeed'][:,0]:
                indlarger = _np.argwhere(env['soundspeed'][:,0]>env['depth_max'])[0][0]
                insert_ss_val = _np.interp(env['depth_max'], env['soundspeed'][:,0], env['soundspeed'][:,1])
                env['soundspeed'] = _np.insert(env['soundspeed'],indlarger,[env['depth_max'],insert_ss_val],axis = 0)
                env['soundspeed'] = env['soundspeed'][:indlarger+1,:]
                warnings.warn("Bellhop.py has used linear interpolation to ensure the sound speed profile ends at the max depth. Ensure this is what you want.", UserWarning)

        assert _np.max(env['source_depth']) <= env['depth_max'], 'source_depth cannot exceed water depth: '+str(env['depth_max'])+' m'
        assert _np.max(env['receiver_depth']) <= env['depth_max'], 'receiver_depth cannot exceed water depth: '+str(env['depth_max'])+' m'
        assert env['beam_angle_min'] >= -180 and env['beam_angle_min'] <= 180, 'beam_angle_min must be in range (-180, 180]'
        assert env['beam_angle_max'] >= -180 and env['beam_angle_max'] <= 180, 'beam_angle_max must be in range (-180, 180]'
        if env["bottom_reflection_coefficient"] is not None:
            assert env["bottom_boundary_condition"] == _Strings.from_file, "BRC values need to be read from file"
        if env["surface_reflection_coefficient"] is not None:
            assert env["surface_boundary_condition"] == _Strings.from_file, "TRC values need to be read from file"
        if env['source_directionality'] is not None:
            assert _np.size(env['source_directionality']) > 1, 'source_directionality must be an Nx2 array'
            assert env['source_directionality'].ndim == 2, 'source_directionality must be an Nx2 array'
            assert env['source_directionality'].shape[1] == 2, 'source_directionality must be an Nx2 array'
            assert _np.all(env['source_directionality'][:,0] >= -180) and _np.all(env['source_directionality'][:,0] <= 180), 'source_directionality angles must be in (-180, 180]'

        validate_source_type(env['source_type'])
        if env['_single_beam'] == _Strings.single_beam:
            assert env['single_beam_index'] is not None, 'Single beam was requested with option I but no index was provided in NBeam line'

        return env
    except AssertionError as e:
        raise ValueError(str(e))

def _finalise_environment(env: Dict[str, Any]) -> Dict[str, Any]:
    """Reviews the data within an environment and updates settings for consistency.

    This function is run as the first step of check_env2d().
    """

    if _np.size(env['depth']) > 1:
        env["_bathymetry"] = _Strings.from_file
    if env["surface"] is not None:
        env["_altimetry"] = _Strings.from_file
    if env["bottom_reflection_coefficient"] is not None:
        env["bottom_boundary_condition"] = _Strings.from_file
    if env["surface_reflection_coefficient"] is not None:
        env["surface_boundary_condition"] = _Strings.from_file

    # this is a weird one, sometimes "depth_max" is defined as 0 in the env file and the simulation breaks if not
    # so we only set depth_max to be the maximum depth iff it hasn't been pre-set
    if env['depth_max'] is None:
        env['depth_max'] = _np.max(env['depth'])

    if isinstance(env["soundspeed"],_pd.DataFrame) and "depth" in env["soundspeed"].columns:
        env["soundspeed"] = env["soundspeed"].set_index("depth")

    # Beam angle ranges default to half-space if source is left-most, otherwise full-space:
    if env['beam_angle_min'] is None:
        if _np.min(env['receiver_range']) < 0:
            env['beam_angle_min'] = -_env.Defaults.beam_angle_fullspace
        else:
            env['beam_angle_min'] = -_env.Defaults.beam_angle_halfspace
    if env['beam_angle_max'] is None:
        if _np.min(env['receiver_range']) < 0:
            env['beam_angle_max'] = _env.Defaults.beam_angle_fullspace
        else:
            env['beam_angle_max'] = _env.Defaults.beam_angle_halfspace

    env['box_depth'] = env['box_depth'] or 1.01 * env['depth_max']
    env['box_range'] = env['box_range'] or 1.01 * (_np.max(env['receiver_range']) - min(0,_np.min(env['receiver_range'])))

    return env

def print_env(env: Dict[str, Any]) -> None:
    """Display the environment in a human readable form.

    :param env: environment definition

    >>> import bellhop as bh
    >>> env = bh.create_env2d(depth=40, soundspeed=1540)
    >>> bh.print_env(env)
    """
    env = check_env2d(env)
    keys_set = set(env.keys()) - {'name'}
    keys: List[str] = ['name'] + sorted(list(keys_set))
    for k in keys:
        v_str = str(env[k])
        if '\n' in v_str:
            v_list = v_str.split('\n')
            print('%20s : '%(k) + v_list[0])
            for v1 in v_list[1:]:
                print('%20s   '%('') + v1)
        else:
            print('%20s : '%(k) + v_str)

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

def compute_transmission_loss(env: Dict[str, Any], source_depth_ndx: int = 0, mode: str = _Strings.coherent, model: Optional[Any] = None, debug: bool = False, fname_base: Optional[str] = None) -> Any:
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
    env = check_env2d(env)
    # Use dataclass validation for option checking
    validate_transmission_loss_mode(mode)
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

def _select_model(env: Dict[str, Any], task: str, model: Optional[Any] = None, debug: bool = False) -> Any:
    print(f"{model = }")
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


__all__ = [
    name for name in globals() if not name.startswith("_")  # ignore private names
]
