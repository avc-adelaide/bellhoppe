
import warnings
from typing import Any, Dict, List

import numpy as _np
import pandas as _pd

from bellhop.constants import Defaults, _Strings
import bellhop.environment as _env
from bellhop.environment import EnvironmentConfig, _validate_source_type

def create_env2d(**kv: Any) -> Dict[str, Any]:
    """Backwards compatibility for create_env"""
    return create_env(**kv)

def create_env(**kv: Any) -> Dict[str, Any]:
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
    >>> bh.print_env(env)

    The environment parameters may be changed by passing keyword arguments
    or modified later using dictionary notation:

    >>> import bellhop as bh
    >>> env = bh.create_env(depth=40, soundspeed=1540)
    >>> bh.print_env(env)
    >>> env['depth'] = 25
    >>> env['bottom_soundspeed'] = 1800
    >>> bh.print_env(env)

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

def check_env(env: Dict[str, Any]) -> Dict[str, Any]:
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
    env = _finalise_environment(env)

    # Use dataclass validation for option checking
    env = _validate_options_with_dataclass(env)

    try:
        assert env['type'] == '2D', 'Not a 2D environment'
        assert env["_num_media"] == 1, f"BELLHOP only supports 1 medium, found {env['_num_media']}"
        _check_env_surface(env)
        _check_env_depth(env)
        _check_env_ssp(env)
        _check_env_sbp(env)
        assert _np.max(env['source_depth']) <= env['depth_max'], 'source_depth cannot exceed water depth: '+str(env['depth_max'])+' m'
        assert _np.max(env['receiver_depth']) <= env['depth_max'], 'receiver_depth cannot exceed water depth: '+str(env['depth_max'])+' m'
        assert env['beam_angle_min'] >= -180 and env['beam_angle_min'] <= 180, 'beam_angle_min must be in range (-180, 180]'
        assert env['beam_angle_max'] >= -180 and env['beam_angle_max'] <= 180, 'beam_angle_max must be in range (-180, 180]'
        if env["bottom_reflection_coefficient"] is not None:
            assert env["bottom_boundary_condition"] == _Strings.from_file, "BRC values need to be read from file"
        if env["surface_reflection_coefficient"] is not None:
            assert env["surface_boundary_condition"] == _Strings.from_file, "TRC values need to be read from file"
        _validate_source_type(env['source_type'])
        if env['_single_beam'] == _Strings.single_beam:
            assert env['single_beam_index'] is not None, 'Single beam was requested with option I but no index was provided in NBeam line'
        return env
    except AssertionError as e:
        raise ValueError(str(e))


def check_env2d(env: Dict[str, Any]) -> Dict[str, Any]:
    """Backwards compatibility for check_env"""
    return check_env(env=env)

def _check_env_surface(env: dict):
    max_range = _np.max(env['receiver_range'])
    if env['surface'] is not None:
        assert _np.size(env['surface']) > 1, 'surface must be an Nx2 array'
        assert env['surface'].ndim == 2, 'surface must be a scalar or an Nx2 array'
        assert env['surface'].shape[1] == 2, 'surface must be a scalar or an Nx2 array'
        assert env['surface'][0,0] <= 0, 'First range in surface array must be 0 m'
        assert env['surface'][-1,0] >= max_range, 'Last range in surface array must be beyond maximum range: '+str(max_range)+' m'
        assert _np.all(_np.diff(env['surface'][:,0]) > 0), 'surface array must be strictly monotonic in range'

def _check_env_depth(env: dict):
    max_range = _np.max(env['receiver_range'])
    if _np.size(env['depth']) > 1:
        assert env['depth'].ndim == 2, 'depth must be a scalar or an Nx2 array'
        assert env['depth'].shape[1] == 2, 'depth must be a scalar or an Nx2 array'
        assert env['depth'][0,0] <= 0, 'First range in depth array must be 0 m'
        assert env['depth'][-1,0] >= max_range, 'Last range in depth array must be beyond maximum range: '+str(max_range)+' m'
        assert _np.all(_np.diff(env['depth'][:,0]) > 0), 'Depth array must be strictly monotonic in range'
        assert env["_bathymetry"] == _Strings.from_file, 'len(depth)>1 requires BTY file'

def _check_env_ssp(env: dict):
    assert isinstance(env['soundspeed'], _pd.DataFrame), 'Soundspeed should always be a DataFrame by this point'
    assert env['soundspeed'].size > 1, "Soundspeed DataFrame should have been constructed internally to be two elements"
    if env['soundspeed'].size > 1:
        if len(env['soundspeed'].columns) > 1:
            assert env['soundspeed_interp'] == _Strings.quadrilateral, "SVP DataFrame with multiple columns implies quadrilateral interpolation."
        if env['soundspeed_interp'] == _Strings.spline:
            assert env['soundspeed'].shape[0] > 3, 'soundspeed profile must have at least 4 points for spline interpolation'
        else:
            assert env['soundspeed'].shape[0] > 1, 'soundspeed profile must have at least 2 points'
        assert env['soundspeed'].index[0] <= 0.0, 'First depth in soundspeed array must be 0 m'
        assert _np.all(_np.diff(env['soundspeed'].index) > 0), 'Soundspeed array must be strictly monotonic in depth'
        if env['depth_max'] != env['soundspeed'].index[-1]:
            if env['soundspeed'].shape[1] > 1:
                # TODO: generalise interpolation trimming from np approach below
                assert env['soundspeed'].index[-1] == env['depth_max'], '2D SSP: Final entry in soundspeed array must be at the maximum water depth: '+str(env['depth_max'])+' m'
            else:
                indlarger = _np.argwhere(env['soundspeed'].index > env['depth_max'])[0][0]
                prev_ind = env['soundspeed'].index[:indlarger].tolist()
                insert_ss_val = _np.interp(env['depth_max'], env['soundspeed'].index, env['soundspeed'].iloc[:,0])
                new_row = _pd.DataFrame([env['depth_max'], insert_ss_val], columns=env['soundspeed'].columns)
                env['soundspeed'] = _pd.concat([
                        env['soundspeed'].iloc[:(indlarger-1)],  # rows before insertion
                        new_row,                             # new row
                    ], ignore_index=True)
                env['soundspeed'].index = prev_ind + [env['depth_max']]
                warnings.warn("Bellhop.py has used linear interpolation to ensure the sound speed profile ends at the max depth. Ensure this is what you want.", UserWarning)
                print("ATTEMPTING TO FIX")
        # TODO: check soundspeed range limits

def _check_env_sbp(env: dict):
    if env['source_directionality'] is not None:
        assert _np.size(env['source_directionality']) > 1, 'source_directionality must be an Nx2 array'
        assert env['source_directionality'].ndim == 2, 'source_directionality must be an Nx2 array'
        assert env['source_directionality'].shape[1] == 2, 'source_directionality must be an Nx2 array'
        assert _np.all(env['source_directionality'][:,0] >= -180) and _np.all(env['source_directionality'][:,0] <= 180), 'source_directionality angles must be in (-180, 180]'

def _finalise_environment(env: Dict[str, Any]) -> Dict[str, Any]:
    """Reviews the data within an environment and updates settings for consistency.

    This function is run as the first step of check_env().
    """

    if _np.size(env['depth']) > 1:
        env["_bathymetry"] = _Strings.from_file
    if env["surface"] is not None:
        env["_altimetry"] = _Strings.from_file
    if env["bottom_reflection_coefficient"] is not None:
        env["bottom_boundary_condition"] = _Strings.from_file
    if env["surface_reflection_coefficient"] is not None:
        env["surface_boundary_condition"] = _Strings.from_file

    if env['depth_max'] is None:
        env['depth_max'] = _np.max(env['depth'])

    if not isinstance(env['soundspeed'], _pd.DataFrame):
        if _np.size(env['soundspeed']) == 1:
            speed = [float(env["soundspeed"]), float(env["soundspeed"])]
            depth = [0, float(env['depth_max'])]
            env["soundspeed"] = _pd.DataFrame(speed, columns=["speed"], index=depth)
            env["soundspeed"].index.name = "depth"
        elif env['soundspeed'].shape[0] == 1 and env['soundspeed'].shape[1] == 2:
            speed = [float(env["soundspeed"][0,1]), float(env["soundspeed"][0,1])]
            d1 = float(min([0.0, env["soundspeed"][0,0]]))
            d2 = float(max([env["soundspeed"][0,0], env['depth_max']]))
            env["soundspeed"] = _pd.DataFrame(speed, columns=["speed"], index=[d1, d2])
            env["soundspeed"].index.name = "depth"
        elif env['soundspeed'].ndim == 2 and env['soundspeed'].shape[1] == 2:
            depth = env['soundspeed'][:,0]
            speed = env['soundspeed'][:,1]
            env["soundspeed"] = _pd.DataFrame(speed, columns=["speed"], index=depth)
            env["soundspeed"].index.name = "depth"
        else:
            raise ValueError("Soundspeed array must be a 2xN array (better to use a DataFrame)")

    if "depth" in env["soundspeed"].columns:
        env["soundspeed"] = env["soundspeed"].set_index("depth")

    if len(env['soundspeed'].columns) > 1:
        env['soundspeed_interp'] == _Strings.quadrilateral

    # Beam angle ranges default to half-space if source is left-most, otherwise full-space:
    if env['beam_angle_min'] is None:
        if _np.min(env['receiver_range']) < 0:
            env['beam_angle_min'] = - Defaults.beam_angle_fullspace
        else:
            env['beam_angle_min'] = - Defaults.beam_angle_halfspace
    if env['beam_angle_max'] is None:
        if _np.min(env['receiver_range']) < 0:
            env['beam_angle_max'] =  Defaults.beam_angle_fullspace
        else:
            env['beam_angle_max'] = Defaults.beam_angle_halfspace

    env['box_depth'] = env['box_depth'] or 1.01 * env['depth_max']
    env['box_range'] = env['box_range'] or 1.01 * (_np.max(env['receiver_range']) - min(0,_np.min(env['receiver_range'])))

    return env

def print_env(env: Dict[str, Any]) -> None:
    """Display the environment in a human readable form.

    Parameters
    ----------
    env : dict
        Environment definition

    Examples
    --------
    >>> import bellhop as bh
    >>> env = bh.create_env(depth=40, soundspeed=1540)
    >>> bh.print_env(env)
    """
    env = check_env(env)
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
