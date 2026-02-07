"""Environment configuration for aubellhop.

This module provides dataclass-based environment configuration with automatic validation,
replacing manual option checking with field validators.
"""

from __future__ import annotations

from collections.abc import MutableMapping
from dataclasses import dataclass, fields
from typing import Any, Iterator, Self, Callable

from pprint import pformat
import warnings
from itertools import product

import numpy as np
from numpy.typing import NDArray
import pandas as pd

from .constants import BHStrings, FlagMaps, EnvDefaults, MiscDefaults


@dataclass
class Environment(MutableMapping[str, Any]):
    """Dataclass for underwater acoustic environment configuration.

    This class provides automatic validation of environment parameters,
    eliminating the need for manual checking of option validity.

    These entries are either intended to be set or edited by the user, or with `_` prefix are
    internal state read from a .env file or inferred by other data. Some others are ignored.

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

    >>> import aubellhop as bh
    >>> env = bh.Environment()
    >>> print(env)

    The environment parameters may be changed by passing keyword arguments
    or modified later using dictionary notation:

    >>> import aubellhop as bh
    >>> env = bh.Environment(depth=40, soundspeed=1540)
    >>> print(env)
    >>> env.depth = 25
    >>> env.bottom_soundspeed = 1800
    >>> print(env)

    The default environment has a constant sound speed.
    A depth dependent sound speed profile be provided as a Nx2 array of (depth, sound speed):

    >>> import aubellhop as bh
    >>> env = bh.Environment(depth=20,
    >>>         soundspeed=[[0,1540], [5,1535], [10,1535], [20,1530]])

    A range-and-depth dependent sound speed profile can be provided as a Pandas frame:

    >>> import aubellhop as bh
    >>> import pandas as pd
    >>> ssp2 = pd.DataFrame({
    >>>       0: [1540, 1530, 1532, 1533],     # profile at 0 m range
    >>>     100: [1540, 1535, 1530, 1533],     # profile at 100 m range
    >>>     200: [1530, 1520, 1522, 1525] },   # profile at 200 m range
    >>>     index=[0, 10, 20, 30])             # depths of the profile entries in m
    >>> env = bh.Environment(depth=20, soundspeed=ssp2)

    The default environment has a constant water depth. A range dependent bathymetry
    can be provided as a Nx2 array of (range, water depth):

    >>> import aubellhop as bh
    >>> env = bh.Environment(depth=[[0,20], [300,10], [500,18], [1000,15]])
    """

    # Basic environment properties
    name: str = 'bellhop/python default'
    _from_file: str | None = None
    dimension: str = EnvDefaults.dimension
    _dimension: int = EnvDefaults._dimension
    frequency: float = EnvDefaults.frequency
    _num_media: int = 1 # must always = 1 in bellhop

    # Sound speed parameters
    soundspeed: float | Any = MiscDefaults.sound_speed  # m/s
    soundspeed_interp: str = EnvDefaults.soundspeed_interp

    # Depth parameters
    depth: float | Any = 25.0  # m
    depth_interp: str = EnvDefaults.depth_interp
    _mesh_npts: int = 0 # ignored by bellhop
    _depth_sigma: float = 0.0 # ignored by bellhop
    depth_max: float | None = None  # m
    _depth_max: float | None = None  # m
    _range_max: float | None = None  # m -- not used in the environment file

    # Flags to read/write from separate files
    _bathymetry: str = BHStrings.flat  # set to "from-file" if multiple bottom depths
    _altimetry: str = BHStrings.flat  # set to "from-file" if multiple surface heights
    _sbp_file: str = BHStrings.default # set to "from-file" if source_directionality defined

    # Bottom parameters
    bottom_interp: str | None = None
    _bottom_depth: float | None = None  # m
    bottom_soundspeed: float = MiscDefaults.sound_speed # m/s
    _bottom_soundspeed_shear: float = 0.0  # m/s (ignored)
    bottom_density: float = MiscDefaults.density  # kg/m^3
    bottom_attenuation: float | None = None  # dB/wavelength
    _bottom_attenuation_shear: float | None = None  # dB/wavelength (ignored)
    bottom_roughness: float = 0.0  # m (rms)
    bottom_beta: float | None = None
    bottom_transition_freq: float | None = None  # Hz
    bottom_boundary_condition: str = BHStrings.acousto_elastic
    bottom_reflection_coefficient: Any | None = None
    bottom_grain_size: float | None = None

    # Surface parameters
    surface: Any | None = None  # surface profile
    surface_interp: str = EnvDefaults.surface_interp  # curvilinear/linear
    surface_boundary_condition: str = BHStrings.vacuum
    surface_reflection_coefficient: Any | None = None
    surface_soundspeed: float = MiscDefaults.sound_speed # m/s
    _surface_soundspeed_shear: float = 0.0  # m/s (ignored)
    surface_density: float = MiscDefaults.density  # kg/m^3
    surface_attenuation: float | None = None  # dB/wavelength
    _surface_attenuation_shear: float | None = None  # dB/wavelength (ignored)
    _surface_min: float | None = None
    surface_min: float | None = None

    # Source parameters
    source_type: str = BHStrings.default
    source_range: float | Any = 0.0
    source_cross_range: float | Any = 0.0
    source_depth: float | Any = 5.0  # m - Any allows for np.ndarray
    source_ndepth: int | None = None
    source_nrange: int | None = None
    source_ncrossrange: int | None = None
    source_directionality: Any | None = None  # [(deg, dB)...]
    _source_num: int = 0

    # Receiver parameters
    receiver_depth: float | Any = 10.0  # m - Any allows for np.ndarray
    receiver_range: float | Any = 1000.0  # m - Any allows for np.ndarray
    receiver_bearing: float | Any = 0.0  # deg - Any allows for np.ndarray
    receiver_ndepth: int | None = None
    receiver_nrange: int | None = None
    receiver_nbearing: int | None = None
    _receiver_num: int = 0

    # Beam settings
    beam_type: str = BHStrings.default
    beam_angle_min: float | None = None  # deg
    beam_angle_max: float | None = None  # deg
    beam_bearing_min: float | None = None  # deg
    beam_bearing_max: float | None = None  # deg
    beam_num: int = 0  # (0 = auto)
    beam_bearing_num: int = 0
    single_beam_index: int | None = None
    _single_beam: str = BHStrings.default # value inferred from `single_beam_index`

    # Cerveny Gaussian Beams
    beam_width_type: str | None = None
    beam_reflection_curvature_change: str | None = None
    beam_reflection_shift: str | None = None
    beam_epsilon_multipler: float | None = None
    beam_range_loop: float | None = None # km in env file
    beam_images_num: int | None = None
    beam_window: int | None = None
    beam_component: str | None = None

    # Simulation extent
    simulation_depth: float | None = None
    simulation_range: float | None = None
    simulation_cross_range: float | None = None
    simulation_depth_scale: float | None = None
    simulation_range_scale: float | None = None
    simulation_cross_range_scale: float | None = None
    simulation_cross_range_min: float | None = None

    # Solution parameters
    step_size: float | None = 0.0 # (0 = auto)
    grid_type: str = BHStrings.default
    task: str | None = None
    interference_mode: str | None = None # subset of `task` for providing TL interface

    # Attenuation parameters
    volume_attenuation: str = EnvDefaults.volume_attenuation
    attenuation_units: str = EnvDefaults.attenuation_units
    biological_layer_parameters: Any | None = None

    # Francois-Garrison volume attenuation parameters (has setter `.set_fg_attenuation(...)`)
    _fg_salinity: float | None = None
    _fg_temperature: float | None = None
    _fg_pH: float | None = None
    _fg_depth: float | None = None

    comment_pad: int = EnvDefaults.comment_pad

    ############# CLASS METHODS ################

    @classmethod
    def from_file(cls, fname: str) -> "Environment":
        """Create an Environment from an .env file."""
        from aubellhop.readers import EnvironmentReader
        env = EnvironmentReader(cls(), fname).read()
        env._from_file = fname
        return env


    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Environment":
        """Create Environment from dictionary.

        Unlike `Environment(**data)`, unknown fields are ignored (with a warning message)."""
        valid_fields = {f.name for f in fields(cls)}
        invalid = set(data.keys()) - valid_fields
        if invalid:
            warnings.warn(f"{cls.__name__}.from_dict: ignoring unknown fields: {invalid}")
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)

    ############# WRITING ################

    def to_file(self, fname: str, task: str | None = None) -> str:
        """Write a complete .env file for specifying a Bellhop simulation.

        This is the user-facing file writer. It infers the file basename and
        resolves the task from the environment unless overridden.

        Parameters
        ----------
        fname : str
            Filename or filename base for the .env file. If no extension is
            provided, `.env` is appended.
        task : str, optional
            Task string which defines the computation to run (e.g. "rays",
            "eigenrays", "arrivals", "coherent", "incoherent", "semicoherent").
            If not provided, this is inferred from `env.task` or
            `env.interference_mode`.

        Returns
        -------
        str
            The filename base (no extension) of the written file.
        """
        from pathlib import Path
        from aubellhop.constants import FileExt, FlagMaps, EnvDefaults
        from aubellhop.writers import EnvironmentWriter

        path = Path(fname)
        if path.suffix == "":
            path = path.with_suffix(FileExt.env)

        # Resolve task
        task_val = task or self.get("task") or self.get("interference_mode") or EnvDefaults.interference_mode
        if task_val is None:
            raise ValueError("Task must be specified via argument or env.task/interference_mode")

        taskcode = FlagMaps.task_rev[task_val]
        fname_base = str(path.with_suffix(""))

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as fh:
            EnvironmentWriter(self, fh, fname_base, taskcode).write()

        return fname_base

    ############# SMALL METHODS ################

    def reset(self) -> Self:
        """Delete values for all user-facing parameters."""
        for k in self.keys():
            if not k.startswith("_"):
                self[k] = None
        return self

    def defaults(self) -> Self:
        """Applies default values if not already set."""
        for f in fields(EnvDefaults):
            if getattr(self, f.name) is None:
                setattr(self, f.name, getattr(EnvDefaults(), f.name))
        return self

    def to_dict(self) -> dict[str,Any]:
        """Return a dictionary representation of the environment."""
        from dataclasses import asdict
        return asdict(self)

    def copy(self) -> "Environment":
        """Return a shallow copy of the environment."""
        # Copy all fields
        data = {f.name: getattr(self, f.name) for f in fields(self)}
        # Return a new instance
        new_env = type(self)(**data)
        return new_env

    def unwrap(self, *keys: str) -> list[Self]:
        """Return a list of Environment copies expanded over the given keys.

        If multiple keys are provided, all combinations are produced.
        Each unwrapped Environment gets a unique `.name` derived from the
        parent name and the expanded field values.
        """

        # Ensure keys are valid
        for k in keys:
            if k not in self:
                raise KeyError(f"Environment has no field '{k}'")

        # Prepare value lists (convert scalars → singletons)
        values: list[Any] = []
        for k in keys:
            v = self[k]
            if isinstance(v, (list, tuple, np.ndarray)):
                values.append(v)
            else:
                values.append([v])

        combos = product(*values)
        envs = []

        base_name = str(self.get("name", "env"))

        for combo in combos:
            env_i = self.copy()
            name_parts = [base_name]
            for k, v in zip(keys, combo):
                env_i[k] = v
                # Replace disallowed chars and truncate floats nicely
                if isinstance(v, float):
                    v_str = f"{v:g}"
                else:
                    v_str = str(v)
                name_parts.append(f"{k}{v_str}")
            env_i["name"] = "-".join(name_parts)
            envs.append(env_i)

        return envs

    ############## SETTERS ###############

    def set_fg_attenuation(self,
                           salinity: float,
                           temperature: float,
                           pH: float,
                           depth: float
                          ) -> Self:
        """Interface to set Francois-Garrison volume attenuation parameters."""
        self.volume_attenuation = BHStrings.francois_garrison
        self._fg_salinity = salinity
        self._fg_temperature = temperature
        self._fg_pH = pH
        self._fg_depth = depth
        return self

    ############## CHECKING ###############

    def check(self) -> Self:
        """Finalise environment parameters and perform assertion checks."""
        self._finalise()
        try:
            self._check_env_header()
            self._check_env_surface()
            self._check_env_depth()
            self._check_env_ssp()
            self._check_env_source()
            self._check_env_beam()
            return self
        except AssertionError as e:
            raise ValueError(f"Env check error: {str(e)}") from None

    def _finalise(self) -> Self:
        """Reviews the data within an environment and updates settings for consistency.

        This function is run as the first step of `.check()`.
        """

        if self.dimension == BHStrings.two_d:
            self._dimension = 2
        elif self.dimension == BHStrings.two_half_d or self.dimension == BHStrings.three_d:
            self._dimension = 3

        if np.size(self['depth']) > 1:
            self["_bathymetry"] = BHStrings.from_file
        if self["surface"] is not None and np.size(self['surface']) > 1:
            self["_altimetry"] = BHStrings.from_file
        if self["bottom_reflection_coefficient"] is not None:
            self["bottom_boundary_condition"] = BHStrings.from_file
        if self["surface_reflection_coefficient"] is not None:
            self["surface_boundary_condition"] = BHStrings.from_file

        self.surface = self.surface if self.surface is not None else EnvDefaults.surface
        def _extremum(
                        expl: float | None,
                        vec: float | NDArray[np.float64],
                        fn: Callable[[NDArray[np.float64]], float]
                     ) -> float:
            if expl is not None:
                return float(expl)
            if np.size(vec) == 1:
                return float(vec)
            if isinstance(vec, np.ndarray):
                return float(fn(vec[:, 1]))
            raise TypeError(f"Unexpected type for _extremum argument: {type(vec)}")

        self._depth_max = _extremum(self.depth_max, self['depth'], np.max)
        self._surface_min = _extremum(self.surface_min, self['surface'], np.min)

        if not isinstance(self['soundspeed'], pd.DataFrame):
            if np.size(self['soundspeed']) == 1:
                speed = np.array([float(self["soundspeed"]), float(self["soundspeed"])])
                depth = np.array([self._surface_min, self._depth_max])
                self["soundspeed"] = pd.DataFrame(speed, columns=pd.Index(["speed"]), index=depth)
                self["soundspeed"].index.name = "depth"
            elif self['soundspeed'].shape[0] == 1 and self['soundspeed'].shape[1] == 2:
                # only one depth/soundspeed pair specified -- does this happen??
                speed = [float(self["soundspeed"][0,1]), float(self["soundspeed"][0,1])]
                d1 = float(min([self._surface_min, self["soundspeed"][0,0]]))
                d2 = float(max([self["soundspeed"][0,0], self._depth_max]))
                self["soundspeed"] = pd.DataFrame(speed, columns=pd.Index(["speed"]), index=pd.Index([d1, d2]))
                self["soundspeed"].index.name = "depth"
            elif self['soundspeed'].ndim == 2 and self['soundspeed'].shape[1] == 2:
                depth = self['soundspeed'][:,0]
                speed = self['soundspeed'][:,1]
                self["soundspeed"] = pd.DataFrame(speed, columns=pd.Index(["speed"]), index=depth)
                self["soundspeed"].index.name = "depth"
            else:
                raise TypeError("For an NDArray, soundspeed must be defined as a Nx2 array of [depth,soundspeed].  Use a DataFrame with 'depth' index for a 2D soundspeed profile.")

        if "depth" in self["soundspeed"].columns:
            self["soundspeed"] = self["soundspeed"].set_index("depth")

        if len(self['soundspeed'].columns) > 1:
            self['soundspeed_interp'] == BHStrings.quadrilateral

        self.bottom_attenuation = self._float_or_default('bottom_attenuation', EnvDefaults.bottom_attenuation)

        self.source_ndepth = self.source_ndepth or np.size(self.source_depth)
        self.source_nrange = self.source_nrange or np.size(self.source_range)
        self.source_ncrossrange = self.source_ncrossrange or np.size(self.source_cross_range)
        self._source_num = self.source_ndepth * self.source_nrange * self.source_ncrossrange

        self.receiver_ndepth      = self.receiver_ndepth      or np.size(self.receiver_depth)
        self.receiver_nrange      = self.receiver_nrange      or np.size(self.receiver_range)
        self.receiver_nbearing    = self.receiver_nbearing    or np.size(self.receiver_bearing)
        self._receiver_num        = self.receiver_ndepth * self.receiver_nrange * self.receiver_nbearing

        # Beam angle ranges default to half-space if source is left-most, otherwise full-space:
        if self['beam_angle_min'] is None:
            if np.min(self['receiver_range']) < 0:
                self['beam_angle_min'] = - MiscDefaults.beam_angle_fullspace
            else:
                self['beam_angle_min'] = - MiscDefaults.beam_angle_halfspace
        if self['beam_angle_max'] is None:
            if np.min(self['receiver_range']) < 0:
                self['beam_angle_max'] =  MiscDefaults.beam_angle_fullspace
            else:
                self['beam_angle_max'] = MiscDefaults.beam_angle_halfspace

        # Identical logic for bearing angles
        if np.min(self['receiver_range']) < 0:
            angle_min = -MiscDefaults.beam_bearing_fullspace
            angle_max = +MiscDefaults.beam_bearing_fullspace
        else:
            angle_min = -MiscDefaults.beam_bearing_halfspace
            angle_max = +MiscDefaults.beam_bearing_halfspace

        self.beam_bearing_min = self._float_or_default('beam_bearing_min', angle_min)
        self.beam_bearing_max = self._float_or_default('beam_bearing_max', angle_max)

        self.simulation_depth_scale = self._float_or_default('simulation_depth_scale', EnvDefaults.simulation_depth_scale)
        self.simulation_range_scale = self._float_or_default('simulation_range_scale', EnvDefaults.simulation_range_scale)
        self.simulation_cross_range_scale = self._float_or_default('simulation_cross_range_scale', EnvDefaults.simulation_cross_range_scale)
        self.simulation_cross_range_min = self._float_or_default('simulation_cross_range_min', EnvDefaults.simulation_cross_range_min)

        self._range_max = np.abs(self['receiver_range']).max()
        bearing_absmax = np.abs([self['beam_bearing_max'], self['beam_bearing_min']]).max()
        cross_range_max = self._range_max * np.sin(np.deg2rad(bearing_absmax))

        self.simulation_depth = self._float_or_default('simulation_depth', self.simulation_depth_scale * self._depth_max)
        self.simulation_range = self._float_or_default('simulation_range', self.simulation_range_scale * self._range_max)
        self.simulation_cross_range = self._float_or_default('simulation_cross_range',
            np.max([self.simulation_cross_range_min, self.simulation_cross_range_scale * cross_range_max]))

        return self

    def _float_or_default(self, key: str, default: float) -> float:
        """Return the current value if not None, otherwise return and set a default."""
        val = getattr(self, key, None)
        if val is None:
            setattr(self, key, default)
            val = default
        return val

    def _check_env_header(self) -> None:
        assert self["_num_media"] == 1, f"BELLHOP only supports 1 medium, found {self['_num_media']}"

    def _check_env_surface(self) -> None:
        assert self['surface'] is not None, 'surface must be defined or initialised'
        if np.size(self['surface']) > 1:
            assert self['surface'].ndim == 2, 'surface must be a scalar or an Nx2 array'
            assert self['surface'].shape[1] == 2, 'surface must be a scalar or an Nx2 array'
            assert self['surface'][0,0] <= 0, 'First range in surface array must be 0 m'
            assert self['surface'][-1,0] >= self._range_max, 'Last range in surface array must be beyond maximum range: '+str(self._range_max)+' m'
            assert np.all(np.diff(self['surface'][:,0]) > 0), 'surface array must be strictly monotonic in range'
        if self["surface_reflection_coefficient"] is not None:
            assert self["surface_boundary_condition"] == BHStrings.from_file, "TRC values need to be read from file"

    def _check_env_depth(self) -> None:
        assert self['depth'] is not None, 'depth must be defined or initialised'
        if np.size(self['depth']) > 1:
            assert self['depth'].ndim == 2, 'depth must be a scalar or an Nx2 array [ranges, depths]'
            assert self['depth'].shape[1] == 2, 'depth must be a scalar or an Nx2 array [ranges, depths]'
            assert self['depth'][-1,0] >= self._range_max, 'Last range in depth array must be beyond maximum range: '+str(self._range_max)+' m'
            assert np.all(np.diff(self['depth'][:,0]) > 0), 'Depth array must be strictly monotonic in range'
            assert self["_bathymetry"] == BHStrings.from_file, 'len(depth)>1 requires BTY file'
        if self["bottom_reflection_coefficient"] is not None:
            assert self["bottom_boundary_condition"] == BHStrings.from_file, "BRC values need to be read from file"
        assert np.max(self['source_depth']) <= self['_depth_max'], f'source_depth {self.source_depth} cannot exceed water depth: {str(self._depth_max)}'
        #assert np.max(self['receiver_depth']) <= self['_depth_max'], f'receiver_depth {self.receiver_depth} cannot exceed water depth: {str(self._depth_max)}'

    def _check_env_ssp(self) -> None:
        assert isinstance(self['soundspeed'], pd.DataFrame), 'Soundspeed should always be a DataFrame by this point'
        assert self['soundspeed'].size > 1, "Soundspeed DataFrame should have been constructed internally to be two elements"
        if self['soundspeed_interp'] == BHStrings.spline:
            assert self['soundspeed'].shape[0] > 3, 'soundspeed profile must have at least 4 points for spline interpolation'
        else:
            assert self['soundspeed'].shape[0] > 1, 'soundspeed profile must have at least 2 points'
        assert self['soundspeed'].index[0] <= self._surface_min, 'First depth in soundspeed array must be ≤ to minimum surface depth'
        assert np.all(np.diff(self['soundspeed'].index) > 0), 'Soundspeed array must be strictly monotonic in depth'
        if self['_depth_max'] != self['soundspeed'].index[-1]:
            indlarger = np.argwhere(self['soundspeed'].index > self['_depth_max'])[0][0]
            prev_ind = self['soundspeed'].index[:indlarger].tolist()
            insert_ss_val = [
                np.interp(self['_depth_max'],
                          self['soundspeed'].index,
                          self['soundspeed'].iloc[:, i])
                for i in range(self['soundspeed'].shape[1])
            ]
            new_row = pd.DataFrame([insert_ss_val], columns=self['soundspeed'].columns)
            new_row.index = [self._depth_max]
            self['soundspeed'] = pd.concat([
                    self['soundspeed'].iloc[:indlarger],  # rows before insertion
                    new_row,                             # new row
                ])
            self['soundspeed'].index = prev_ind + [self['_depth_max']]
            warnings.warn("aubellhop has used linear interpolation to ensure the sound speed profile ends at the max depth. Ensure this is what you want.", UserWarning)
        # TODO: check soundspeed range limits

    def _check_env_source(self) -> None:
        if self._dimension == 2:
            assert self.source_range == 0.0, "Bellhop2D does not support non-zero source range."
            assert self.source_cross_range == 0.0, "Bellhop2D does not support non-zero source cross range."
        if self['source_directionality'] is not None:
            assert np.size(self['source_directionality']) > 1, 'source_directionality must be an Nx2 array'
            assert self['source_directionality'].ndim == 2, 'source_directionality must be an Nx2 array'
            assert self['source_directionality'].shape[1] == 2, 'source_directionality must be an Nx2 array'
            assert np.all(self['source_directionality'][:,0] >= -180) and np.all(self['source_directionality'][:,0] <= 180), 'source_directionality angles must be in (-180, 180]'

    def _check_env_beam(self) -> None:
        assert (self._dimension == 2) or (self._dimension == 3 and self.source_type in (BHStrings.point, BHStrings.default)), "Can only have point source in 3D (line or point in 2D)"
        assert self['beam_angle_min'] >= -180 and self['beam_angle_min'] <= 180, 'beam_angle_min must be in range [-180, 180]'
        assert self['beam_angle_max'] >= -180 and self['beam_angle_max'] <= 180, 'beam_angle_max must be in range [-180, 180]'
        if self['_single_beam'] == BHStrings.single_beam:
            assert self['single_beam_index'] is not None, 'Single beam was requested with option I but no index was provided in NBeam line'


    ############# STANDARD INTERFACES ###############

    def __getitem__(self, key: str) -> Any:
        if not hasattr(self, key):
            raise KeyError(key)
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.__setattr__(key, value)

    def __setattr__(self, key: str, value: Any) -> None:
        if not hasattr(self, key):
            raise KeyError(f"Unknown environment configuration parameter: {key!r}")
        allowed = getattr(FlagMaps, key, None)
        if allowed is not None and value is not None and value not in set(allowed.values()):
            raise ValueError(f"Invalid value for {key!r}: {value}. Allowed: {set(allowed.values())}")
        if not (
            value is None
            or isinstance(value, pd.DataFrame)
            or np.isscalar(value)
        ):
            if not isinstance(value[0], str):
                value = np.asarray(value, dtype=np.float64)
        object.__setattr__(self, key, value)

    def __delitem__(self, key: str) -> None:
        raise KeyError("Environment parameters cannot be deleted")

    def __iter__(self) -> Iterator[str]:
        return (f.name for f in fields(self))

    def __len__(self) -> int:
        return len(fields(self))

    def __repr__(self) -> str:
        return pformat(self.to_dict())
