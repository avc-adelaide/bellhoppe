"""Computing wrappers for aubellhop.

These functions make use of the `Models` registry, selecting appropriate `BellhopSimulator` models (or loading explicitly request ones):

* `compute(env, ...)` — writes the environment to file and then executes an appropriate Bellhop model;

* `compute_from_file(model, filename)` uses specified model with pre-existing environment file.

The `compute()` function allows calculation with multiple environments, tasks, and models, and returns the results in a dictionary of metadata and results.

Simpler once-off wrapper functions are also provided for convenience (`compute_arrivals()` etc.).

"""

from __future__ import annotations

from typing import Any, cast
import numpy as np
import pandas as pd

from .constants import BHStrings, EnvDefaults, FileExt
from .environment import Environment
from .models import Models

def compute_from_file(
                      model: str,
                      fname: str,
                      debug: bool = False
                     ) -> dict[str, Any]:
    """Compute Bellhop model directly from existing .env file.

    Parameters
    ----------
    model: str
        Name of model to run that has been defined in the `Models` registry.
    fname: str
        Filename of environment file (with or w/o extension).
    debug : bool
        Whether to print diagnostics to the console.

    Returns
    -------
    results : dict
        Dictionary of metadata and results.

    Notes
    -----
    The environment file is parsed simply to read the specified task; the bellhop executable is run on the original file "in place" in the filesystem. A copy of the parsed environment file is stored in the metadata.
    """

    ext = FileExt.env
    if fname.endswith(ext):
        nchar = len(ext)
        fname_base = fname[:-nchar]
    else:
        fname_base = fname
        fname = fname + ext

    model_fn = Models.get(model)
    env_tmp = Environment.from_file(fname)
    task = env_tmp['task']

    return {
             "name": env_tmp["name"],
             "model": model,
             "task": task,
             "results": model_fn.run(task, fname_base, rm_files=False, debug=debug),
             "env": env_tmp.copy(),
           }


def compute(
            env: Environment | list[Environment],
            model: Any | None = None,
            task: Any | None = None,
            debug: bool = False,
            fname_base: str | None = None,
            overwrite: bool = False,
           ) -> dict[str, Any] | tuple[list[dict[str, Any]], pd.DataFrame]:
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
    overwrite : bool, default=False
        If True, remove any existing working/output files that share the same `fname_base`.

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
    >>> import aubellhop as bh
    >>> env = bh.Environment.from_file("...")
    >>> output = bh.compute(env)
    >>> assert output['task'] == "arrivals"
    >>> bh.plot_arrivals(output['results'])

    Multiple tasks:
    >>> import aubellhop as bh
    >>> env = bh.Environment()
    >>> output, ind_df = bh.compute(env,task=["arrivals", "eigenrays"])
    >>> bh.plot_arrivals(output[0]['results'])
    """
    if isinstance(env, list):
        envs = cast(list[Environment], env)
    else:
        envs = [env]
    models_ = model if isinstance(model, list) else [model]
    tasks = task if isinstance(task, list) else [task]
    results: list[dict[str, Any]] = []
    this_env: Environment
    for this_env in envs:
        for this_model in models_:
            for this_task in tasks:
                if debug:
                    print(f"Using environment: {this_env['name']}")
                    print(f"Using model: {'[None] (default)' if this_model is None else this_model.get('name')}")
                    print(f"Using task: {this_task}")
                this_env.check()
                this_task = this_task or this_env.get('task')
                if this_task is None:
                    raise ValueError("Task must be specified in env or as parameter")
                model_fn = Models.select(this_env, this_task, this_model, debug)
                fname_base = model_fn.write_env(this_env, this_task, fname_base, overwrite=overwrite)
                results.append({
                       "name": this_env["name"],
                       "model": this_model,
                       "task": this_task,
                       "results": model_fn.run(this_task, fname_base, debug=debug),
                       "env": this_env.copy(),
                      })
    assert len(results) > 0, "No results generated"
    index_df = pd.DataFrame([
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


def compute_arrivals(env: Environment, model: Any | None = None, debug: bool = False, fname_base: str | None = None, overwrite: bool = False) -> Any:
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
    overwrite : bool, default=False
        If True, remove any existing working/output files that share the same `fname_base`.

    Returns
    -------
    pandas.DataFrame
        Arrival times and coefficients for all transmitter-receiver combinations

    Examples
    --------
    >>> import aubellhop as bh
    >>> env = bh.Environment()
    >>> arrivals = bh.compute_arrivals(env)
    >>> bh.plot_arrivals(arrivals)
    """
    output = compute(env, model, BHStrings.arrivals, debug, fname_base, overwrite)
    assert isinstance(output, dict), "Single env should return single result"
    return output['results']

def compute_eigenrays(env: Environment, source_depth_ndx: int = 0, receiver_depth_ndx: int = 0, receiver_range_ndx: int = 0, model: Any | None = None, debug: bool = False, fname_base: str | None = None, overwrite: bool = False) -> Any:
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
    overwrite : bool, default=False
        If True, remove any existing working/output files that share the same `fname_base`.

    Returns
    -------
    pandas.DataFrame
        Eigenrays paths

    Examples
    --------
    >>> import aubellhop as bh
    >>> env = bh.Environment()
    >>> rays = bh.compute_eigenrays(env)
    >>> bh.plot_rays(rays, width=1000)
    """
    env = env.copy()
    env.check()
    if np.size(env['source_depth']) > 1:
        env['source_depth'] = env['source_depth'][source_depth_ndx]
        env['source_ndepth'] = None  # count is recomputed on the next check()
    if np.size(env['receiver_depth']) > 1:
        env['receiver_depth'] = env['receiver_depth'][receiver_depth_ndx]
        env['receiver_ndepth'] = None
    if np.size(env['receiver_range']) > 1:
        env['receiver_range'] = env['receiver_range'][receiver_range_ndx]
        env['receiver_nrange'] = None
    output = compute(env, model, BHStrings.eigenrays, debug, fname_base, overwrite)
    assert isinstance(output, dict), "Single env should return single result"
    return output['results']

def compute_rays(env: Environment, source_depth_ndx: int = 0, model: Any | None = None, debug: bool = False, fname_base: str | None = None, overwrite: bool = False) -> Any:
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
    overwrite : bool, default=False
        If True, remove any existing working/output files that share the same `fname_base`.

    Returns
    -------
    pandas.DataFrame
        Ray paths

    Examples
    --------
    >>> import aubellhop as bh
    >>> env = bh.Environment()
    >>> rays = bh.compute_rays(env)
    >>> bh.plot_rays(rays, width=1000)
    """
    env = env.copy()
    env.check()
    if np.size(env['source_depth']) > 1:
        env['source_depth'] = env['source_depth'][source_depth_ndx]
        env['source_ndepth'] = None  # count is recomputed on the next check()
    output = compute(env, model, BHStrings.rays, debug, fname_base, overwrite)
    assert isinstance(output, dict), "Single env should return single result"
    return output['results']

def compute_transmission_loss(env: Environment, source_depth_ndx: int = 0, mode: str | None = None, model: Any | None = None, debug: bool = False, fname_base: str | None = None, overwrite: bool = False) -> Any:
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
    overwrite : bool, default=False
        If True, remove any existing working/output files that share the same `fname_base`.

    Returns
    -------
    numpy.ndarray
        Complex transmission loss at each receiver depth and range

    Examples
    --------
    >>> import aubellhop as bh
    >>> env = bh.Environment()
    >>> tloss = bh.compute_transmission_loss(env, mode="incoherent")
    >>> bh.plot_transmission_loss(tloss, width=1000)
    """
    env = env.copy()
    task = mode or env.get("interference_mode") or EnvDefaults.interference_mode
    env['interference_mode'] = task
    env.check()
    if np.size(env['source_depth']) > 1:
        env['source_depth'] = env['source_depth'][source_depth_ndx]
        env['source_ndepth'] = None  # count is recomputed on the next check()
    output = compute(env, model, task, debug, fname_base, overwrite)
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
    >>> import aubellhop as bh
    >>> env = bh.Environment()
    >>> arrivals = bh.compute_arrivals(env)
    >>> ir = bh.arrivals_to_impulse_response(arrivals, fs=192000)
    """
    t0 = 0 if abs_time else min(arrivals.time_of_arrival)
    irlen = int(np.ceil((max(arrivals.time_of_arrival)-t0)*fs))+1
    ir = np.zeros(irlen, dtype=np.complex128)
    for _, row in arrivals.iterrows():
        ndx = int(np.round((row.time_of_arrival.real-t0)*fs))
        ir[ndx] = row.arrival_amplitude
    return ir
