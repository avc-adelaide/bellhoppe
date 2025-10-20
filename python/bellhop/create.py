
from typing import Any

import numpy as _np
import pandas as _pd

import bellhop.environment as _env
from bellhop.environment import EnvironmentConfig

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

