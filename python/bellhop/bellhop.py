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

import numpy as _np
from scipy import interpolate as _interp
import pandas as _pd

from bellhop.constants import _Strings, _Maps
import bellhop.environment as _env
from bellhop.environment import EnvironmentConfig, validate_transmission_loss_mode, validate_source_type

# this format to explicitly mark the functions as public:
from bellhop.readers import read_env2d as read_env2d
from bellhop.readers import read_ssp as read_ssp
from bellhop.readers import read_ati as read_ati
from bellhop.readers import read_bty as read_bty
from bellhop.readers import read_sbp as read_sbp
from bellhop.readers import read_refl_coeff as read_refl_coeff

# models (in order of preference)
_models = []

def create_env2d(**kv):
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



def _validate_options_with_dataclass(env):
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


def check_env2d(env):
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
            # For DataFrames, apply the same minimum point requirements as numpy arrays
            if env['soundspeed_interp'] == _Strings.spline:
                assert env['soundspeed'].shape[0] > 3, 'soundspeed profile must have at least 4 points for spline interpolation'
            else:
                assert env['soundspeed'].shape[0] > 1, 'soundspeed profile must have at least 2 points'
            assert env['soundspeed'].index[0] <= 0, 'First depth in soundspeed array must be 0 m'
            assert env['soundspeed'].index[-1] >= env['depth_max'], 'Last depth in soundspeed array must be beyond water depth: '+str(env['depth_max'])+' m'
            assert _np.all(_np.diff(env['soundspeed'].index) > 0), 'Soundspeed array must be strictly monotonic in depth'
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
                if env['soundspeed_interp'] == _Strings.spline:
                    tck = _interp.splrep(env['soundspeed'][:,0], env['soundspeed'][:,1], s=0)
                    insert_ss_val = _interp.splev(env['depth_max'], tck, der=0)
                else:
                    insert_ss_val = _np.interp(env['depth_max'], env['soundspeed'][:,0], env['soundspeed'][:,1])
                env['soundspeed'] = _np.insert(env['soundspeed'],indlarger,[env['depth_max'],insert_ss_val],axis = 0)
                env['soundspeed'] = env['soundspeed'][:indlarger+1,:]
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

        if env['_single_beam'] == _Strings.single_beam:
            assert env['single_beam_index'] is not None, 'Single beam was requested with option I but no index was provided in NBeam line'

        return env
    except AssertionError as e:
        raise ValueError(str(e))

def _finalise_environment(env):
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

    return env

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
    model = _select_model(env, _Strings.arrivals, model, debug)
    return model.run(env, _Strings.arrivals, debug, fname_base)

def compute_eigenrays(env, source_depth_ndx=0, receiver_depth_ndx=0, receiver_range_ndx=0, model=None, debug=False, fname_base=None):
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

def compute_rays(env, source_depth_ndx=0, model=None, debug=False, fname_base=None):
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

def compute_transmission_loss(env, source_depth_ndx=0, mode=_Strings.coherent, model=None, source_type="default", debug=False, fname_base=None):
    """Compute transmission loss from a given transmitter to all receviers.

    :param env: environment definition
    :param source_depth_ndx: transmitter depth index
    :param mode: coherent, incoherent or semicoherent
    :param model: propagation model to use (None to auto-select)
    :param source_type: point or line
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
    validate_source_type(source_type)
    if env['source_type'] == 'default':
        env['source_type'] = source_type
    else:
        if not(source_type == 'default') and not(env['source_type'] == source_type):
            raise ValueError('ENV file defines source type "'+env['source_type']+'" inconsistent with Python argument source_type="'+source_type+'"')
    if _np.size(env['source_depth']) > 1:
        env = env.copy()
        env['source_depth'] = env['source_depth'][source_depth_ndx]
    model = _select_model(env, mode, model, debug)
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

def _select_model(env, task, model, debug):
    if model is not None:
        for m in _models:
            if m[0] == model:
                if debug:
                    print('[DEBUG] Model: '+m[0])
                return m[1]()
        raise ValueError('Unknown model: '+model)
    for m in _models:
        mm = m[1]()
        if mm.supports(env, task):
            if debug:
                print('[DEBUG] Model: '+m[0])
            return mm
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
        na = _np.size(a)
        if nn is None:
            nn = na
        if nn == 1 or na == 1:
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
        svp_interp = _Maps.interp_rev[env['soundspeed_interp']]
        svp_boundcond = _Maps.boundcond_rev[env['surface_boundary_condition']]
        svp_attunits = _Maps.attunits_rev[env['attenuation_units']]
        svp_volatt = _Maps.volatt_rev[env['volume_attenuation']]
        svp_alti = _Maps.surface_rev[env['_altimetry']]
        svp_singlebeam = _Maps.single_beam_rev[env['_single_beam']]
        if isinstance(svp, _pd.DataFrame):
            if len(svp.columns) > 1:
                assert svp_interp == 'Q', "SVP DataFrame with multiple columns implies quadrilateral interpolation."
            else:
                svp = _np.hstack((_np.array([svp.index]).T, _np.asarray(svp)))
        comment = "SSP parameters: Interp / Top Boundary Cond / Attenuation Units / Volume Attenuation)"
        topopt = f"{svp_interp}{svp_boundcond}{svp_attunits}{svp_volatt}{svp_alti}{svp_singlebeam}".strip()
        self._print(fh, f"'{topopt}'    ! {comment}")
        if env['surface'] is not None:
            self._create_bty_ati_file(fname_base+'.ati', env['surface'], env['surface_interp'])

        if env['volume_attenuation'] == _Strings.francois_garrison:
            comment = "Francois-Garrison volume attenuation parameters (sal, temp, pH, depth)"
            self._print(fh,f"{env['fg_salinity']} {env['fg_temperature']} {env['fg_pH']} {env['fg_depth']}    ! {comment}")

        if env['surface_boundary_condition'] == _Strings.acousto_elastic:
            comment = "DEPTH_Top (m)  TOP_SoundSpeed (m/s)  TOP_SoundSpeed_Shear (m/s)  TOP_Density (g/cm^3)  [ TOP_Absorp [ TOP_Absorp_Shear ] ]"
            if env['surface_absorption'] is None:
                self._print(fh, f"{env['surface_depth']} {env['surface_soundspeed']} {env['surface_soundspeed_shear']} {env['surface_density']/1000} /  ! {comment}")
            elif env['surface_absorption_shear'] is None:
                self._print(fh, "%0.6f %0.6f %0.6f %0.6f %0.6f /" % (env['depth_max'], env['surface_soundspeed'], env['surface_soundspeed_shear'], env['surface_density']/1000, env['surface_absorption']))
            else:
                self._print(fh, "%0.6f %0.6f %0.6f %0.6f %0.6f %0.6f /" % (env['depth_max'], env['surface_soundspeed'], env['surface_soundspeed_shear'], env['surface_density']/1000, env['surface_absorption'], env['surface_absorption_shear']))

        # max depth should be the depth of the acoustic domain, which can be deeper than the max depth bathymetry
        comment = "DEPTH_Npts  DEPTH_SigmaZ  DEPTH_Max"
        self._print(fh, f"{env['depth_npts']} {env['depth_sigmaz']} {env['depth_max']}    ! {comment}")

        if _np.size(svp) == 1:
            self._print(fh, f"0.0 {svp} /    ! '0.0' SSP_Const")
            #self._print(fh, f"{env['depth_max']} {svp} /    ! MAXDEPTH SSP_Const")
        elif svp_interp == 'Q':
            sspenv = env['_ssp_env']
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

        bot_bc = _Maps.boundcond_rev[env['bottom_boundary_condition']]
        dp_flag = _Maps.bottom_rev[env['_bathymetry']]
        comment = "BOT_Boundary_cond / BOT_Roughness"
        self._print(fh, f"{_quoted_opt(bot_bc,dp_flag)} {env['bottom_roughness']}    ! {comment}")

        if _np.size(env['depth']) > 1:
            self._create_bty_ati_file(fname_base+'.bty', env['depth'], env['depth_interp'])

        if env['bottom_boundary_condition'] == "acousto-elastic":
            comment = "DEPTH_Max  BOT_SoundSpeed  BOT_SoundSpeed_Shear BOT_Density [ BOT_Absorp [ BOT_Absorp_Shear ] ]"
            if env['bottom_soundspeed'] is None:
                self._print(fh, f"/  ! {comment}")
            elif env['bottom_absorption'] is None:
                self._print(fh, f"{env['depth_max']} {env['bottom_soundspeed']} {env['bottom_soundspeed_shear']} {env['bottom_density']/1000} /  ! {comment}")
            elif env['bottom_absorption_shear'] is None:
                self._print(fh, "%0.6f %0.6f %0.6f %0.6f %0.6f /" % (env['depth_max'], env['bottom_soundspeed'], env['bottom_soundspeed_shear'], env['bottom_density']/1000, env['bottom_absorption']))
            else:
                self._print(fh, "%0.6f %0.6f %0.6f %0.6f %0.6f %0.6f /" % (env['depth_max'], env['bottom_soundspeed'], env['bottom_soundspeed_shear'], env['bottom_density']/1000, env['bottom_absorption'], env['bottom_absorption_shear']))

        if env['bottom_boundary_condition'] == "from-file":
            self._create_refl_coeff_file(fname_base+".brc", env['bottom_reflection_coefficient'])

        if env['surface_boundary_condition'] == "from-file":
            self._create_refl_coeff_file(fname_base+".trc", env['surface_reflection_coefficient'])

        self._print_array(fh, env['source_depth'], nn=env['source_ndepth'], label="TX_DEPTH")
        self._print_array(fh, env['receiver_depth'], nn=env['receiver_ndepth'], label="RX_DEPTH")
        self._print_array(fh, env['receiver_range']/1000, nn=env['receiver_nrange'], label="RX_RANGE")

        beamtype = _Maps.beam_rev[env['beam_type']]
        beampattern = " "
        txtype = _Maps.source_rev[env['source_type']]
        gridtype = _Maps.grid_rev[env['grid']]
        if env['source_directionality'] is not None:
            beampattern = "*"
            self._create_sbp_file(fname_base+'.sbp', env['source_directionality'])
        runtype_str = taskcode + beamtype + beampattern + txtype + gridtype
        self._print(fh, f"'{runtype_str.rstrip()}'  ! RUN TYPE")
        if env['single_beam_index'] is None:
            self._print(fh, f"{env['beam_num']} ! NBeams") #beam_single_index
        else:
            self._print(fh, f"{env['beam_num']}  {env['single_beam_index']}    ! NBeams Single_Beam_Index")
        self._print(fh, f"{env['beam_angle_min']}  { env['beam_angle_max']}  /   ! Beam angle range: ALPHA1,2 (degrees)")
        step_size = env["step_size"]
        box_depth = env["box_depth"] or 1.01*env['depth_max']
        box_range = env["box_range"] or 1.01*_np.max(_np.abs(env['receiver_range']))
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
                source_depth_info = self._readf(f, (int,), float)
                source_depth_count = source_depth_info[0]
                source_depth = source_depth_info[1:]
                assert source_depth_count == len(source_depth)
                receiver_depth_info = self._readf(f, (int,), float)
                receiver_depth_count = receiver_depth_info[0]
                receiver_depth = receiver_depth_info[1:]
                assert receiver_depth_count == len(receiver_depth)
                receiver_range_info = self._readf(f, (int,), float)
                receiver_range_count = receiver_range_info[0]
                receiver_range = receiver_range_info[1:]
                assert receiver_range_count == len(receiver_range)
            else:
                freq, source_depth_count, receiver_depth_count, receiver_range_count = self._readf(hdr, (float, int, int, int))
                source_depth = self._readf(f, (float,)*source_depth_count)
                receiver_depth = self._readf(f, (float,)*receiver_depth_count)
                receiver_range = self._readf(f, (float,)*receiver_range_count)
            arrivals = []
            for j in range(source_depth_count):
                f.readline()
                for k in range(receiver_depth_count):
                    for m in range(receiver_range_count):
                        count = int(f.readline())
                        for n in range(count):
                            data = self._readf(f, (float, float, float, float, float, float, int, int))
                            arrivals.append(_pd.DataFrame({
                                'source_depth_ndx': [j],
                                'receiver_depth_ndx': [k],
                                'receiver_range_ndx': [m],
                                'source_depth': [source_depth[j]],
                                'receiver_depth': [receiver_depth[k]],
                                'receiver_range': [receiver_range[m]],
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
