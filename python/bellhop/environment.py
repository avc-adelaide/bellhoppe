
"""
Environment configuration for BELLHOP.

This module provides dataclass-based environment configuration with automatic validation,
replacing manual option checking with field validators.
"""

from collections.abc import MutableMapping
from dataclasses import dataclass, asdict, fields
from typing import Optional, Union, Any, Dict, Iterator
from pprint import pformat
import warnings

import numpy as _np
import pandas as _pd

from .constants import _Strings, _Maps, Defaults


@dataclass
class EnvironmentConfig(MutableMapping[str, Any]):
    """Dataclass for 2D underwater acoustic environment configuration.

    This class provides automatic validation of environment parameters,
    eliminating the need for manual checking of option validity.
    """

    # Basic environment properties
    name: str = 'bellhop/python default'
    type: str = '2D'
    frequency: float = 25000.0  # Hz
    _num_media: int = 1

    # Sound speed parameters
    soundspeed: Union[float, Any] = 1500.0  # m/s - Any allows for np.ndarray, pd.DataFrame
    soundspeed_interp: str = _Strings.linear  # spline/linear/quadrilateral/pchip/hexahedral/nlinear

    # Bottom parameters
    bottom_interp: Optional[str] = None
    bottom_soundspeed: float = 1600.0  # m/s
    bottom_soundspeed_shear: float = 0.0  # m/s
    bottom_density: float = 1600  # kg/m^3  # this value doesn't seem right but is copied from ARLpy
    bottom_attenuation: Optional[float] = None  # dB/wavelength
    bottom_attenuation_shear: Optional[float] = None  # dB/wavelength
    bottom_roughness: float = 0.0  # m (rms)
    bottom_beta: Optional[float] = None
    bottom_transition_freq: Optional[float] = None  # Hz
    bottom_boundary_condition: str = _Strings.acousto_elastic
    bottom_reflection_coefficient: Optional[Any] = None
    _bathymetry: str = _Strings.flat  # set to "from-file" if multiple bottom depths

    # Surface parameters
    surface: Optional[Any] = None  # surface profile
    surface_interp: str = _Strings.linear  # curvilinear/linear
    surface_boundary_condition: str = _Strings.vacuum
    surface_reflection_coefficient: Optional[Any] = None
    surface_depth: float = 0.0  # m
    surface_soundspeed: float = 1600.0  # m/s
    surface_soundspeed_shear: float = 0.0  # m/s
    surface_density: float = 1000.0  # kg/m^3
    surface_attenuation: Optional[float] = None  # dB/wavelength
    surface_attenuation_shear: Optional[float] = None  # dB/wavelength
    _altimetry: str = _Strings.flat  # set to "from-file" if multiple surface heights

    # Source parameters
    source_type: str = 'default'
    source_depth: Union[float, Any] = 5.0  # m - Any allows for np.ndarray
    source_ndepth: Optional[int] = None
    source_directionality: Optional[Any] = None  # [(deg, dB)...] - Any allows for np.ndarray
    _sbp_file: str = _Strings.default

    # Receiver parameters
    receiver_depth: Union[float, Any] = 10.0  # m - Any allows for np.ndarray
    receiver_ndepth: Optional[int] = None
    receiver_range: Union[float, Any] = 1000.0  # m - Any allows for np.ndarray
    receiver_nrange: Optional[int] = None

    # Bathymetry parameters
    depth: Union[float, Any] = 25.0  # m - Any allows for np.ndarray
    depth_interp: str = _Strings.linear  # curvilinear/linear
    depth_npts: int = 0
    depth_sigmaz: float = 0.0
    depth_max: Optional[float] = None  # m

    # Beam settings
    beam_type: str = _Strings.default
    beam_angle_min: Optional[float] = None  # deg
    beam_angle_max: Optional[float] = None  # deg
    beam_num: int = 0  # number of beams (0 = auto)
    single_beam_index: Optional[int] = None # if a single beam is traced only, select this one
    _single_beam: str = _Strings.default

    # Solution parameters
    step_size: Optional[float] = 0.0
    box_depth: Optional[float] = None
    box_range: Optional[float] = None
    grid_type: str = 'default'
    interference_mode: Optional[str] = None
    task: Optional[str] = None

    # Attenuation parameters
    volume_attenuation: str = 'none'
    attenuation_units: str = 'frequency dependent'

    # Francois-Garrison volume attenuation parameters
    fg_salinity: Optional[float] = None
    fg_temperature: Optional[float] = None
    fg_pH: Optional[float] = None
    fg_depth: Optional[float] = None

    # --- Mapping interface ---
    def __getitem__(self, key: str) -> Any:
        if not hasattr(self, key):
            raise KeyError(key)
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        if not hasattr(self, key):
            raise KeyError(key)
        # Generalized validation
        allowed = getattr(_Maps, key, None)

        if allowed is not None and value not in set(allowed.values()):
            raise ValueError(f"Invalid value for {key!r}: {value}. Allowed: {set(allowed.values())}")
        setattr(self, key, value)

    def __delitem__(self, key: str) -> None:
        raise KeyError("Environment parameters cannot be deleted")

    def __iter__(self) -> Iterator[str]:
        return (f.name for f in fields(self))

    def __len__(self) -> int:
        return len(fields(self))

    def to_dict(self) -> Dict[str,Any]:
        """Return a dictionary representation of the environment."""
        return asdict(self)

    def __post_init__(self) -> None:
        """Validate field values after initialization."""
        self._validate_interpolation_types()
        self._validate_boundary_conditions()
        self._validate_grid_types()
        self._validate_beam_types()
        self._validate_attenuation_options()
        self._validate_volume_attenuation()
        self._validate_interference_mode()

    def _validate_interpolation_types(self) -> None:
        """Validate interpolation type options."""
        valid_interp = set(_Maps.soundspeed_interp_rev.keys())
        if self.soundspeed_interp not in valid_interp:
            raise ValueError(f"Invalid soundspeed_interp: {self.soundspeed_interp}. "
                           f"Must be one of: {sorted(valid_interp)}")

        valid_bty_interp = set(_Maps.depth_interp_rev.keys())
        if self.depth_interp not in valid_bty_interp:
            raise ValueError(f"Invalid depth_interp: {self.depth_interp}. "
                           f"Must be one of: {sorted(valid_bty_interp)}")

        if self.surface_interp not in valid_bty_interp:
            raise ValueError(f"Invalid surface_interp: {self.surface_interp}. "
                           f"Must be one of: {sorted(valid_bty_interp)}")

    def _validate_boundary_conditions(self) -> None:
        """Validate boundary condition options."""
        valid_boundary = set(_Maps.bottom_boundary_condition_rev.keys())
        if self.bottom_boundary_condition not in valid_boundary:
            raise ValueError(f"Invalid bottom_boundary_condition: {self.bottom_boundary_condition}. "
                           f"Must be one of: {sorted(valid_boundary)}")

        if self.surface_boundary_condition not in valid_boundary:
            raise ValueError(f"Invalid surface_boundary_condition: {self.surface_boundary_condition}. "
                           f"Must be one of: {sorted(valid_boundary)}")

    def _validate_grid_types(self) -> None:
        """Validate grid type options."""
        valid_grid = set(_Maps.grid_type_rev.keys())
        if self.grid_type not in valid_grid:
            raise ValueError(f"Invalid grid: {self.grid_type}. "
                           f"Must be one of: {sorted(valid_grid)}")

    def _validate_beam_types(self) -> None:
        """Validate beam type options."""
        valid_beam = set(_Maps.beam_type_rev.keys())
        if self.beam_type not in valid_beam:
            raise ValueError(f"Invalid beam_type: {self.beam_type}. "
                           f"Must be one of: {sorted(valid_beam)}")

    def _validate_attenuation_options(self) -> None:
        """Validate attenuation unit options."""
        valid_attenuation_units = set(_Maps.attenuation_units_rev.keys())
        if self.attenuation_units not in valid_attenuation_units:
            raise ValueError(f"Invalid attenuation_units: {self.attenuation_units}. "
                           f"Must be one of: {sorted(valid_attenuation_units)}")

    def _validate_volume_attenuation(self) -> None:
        """Validate volume attenuation options."""
        valid_volume_attenuation = set(_Maps.volume_attenuation_rev.keys())
        if self.volume_attenuation not in valid_volume_attenuation:
            raise ValueError(f"Invalid volume_attenuation: {self.volume_attenuation}. "
                           f"Must be one of: {sorted(valid_volume_attenuation)}")

    def _validate_interference_mode(self) -> None:
        """Validate transmission loss mode."""
        valid_modes = set(_Maps.mode_rev.keys())
        if self.interference_mode and self.interference_mode not in valid_modes:
            raise ValueError(f'Invalid transmission loss mode: {self.interference_mode}. '
                            f'Must be one of: {sorted(valid_modes)}')

    def copy(self) -> "EnvironmentConfig":
        """Return a shallow copy of the environment."""
        # Copy all fields
        data = {f.name: getattr(self, f.name) for f in fields(self)}
        # Return a new instance
        new_env = type(self)(**data)
        return new_env

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnvironmentConfig':
        """Create EnvironmentConfig from dictionary."""
        # Filter out any keys that aren't valid field names
        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)

    def __repr__(self) -> str:
        return pformat(self.to_dict())

    def check(self) -> "EnvironmentConfig":
        self._finalise()
        try:
            self._check_env_header()
            self._check_env_surface()
            self._check_env_depth()
            self._check_env_ssp()
            self._check_env_sbp()
            self._check_env_beam()
            return self
        except AssertionError as e:
            raise ValueError(str(e))

    def _finalise(self) -> "EnvironmentConfig":
        """Reviews the data within an environment and updates settings for consistency.

        This function is run as the first step of check_env().
        """

        if _np.size(self['depth']) > 1:
            self["_bathymetry"] = _Strings.from_file
        if self["surface"] is not None:
            self["_altimetry"] = _Strings.from_file
        if self["bottom_reflection_coefficient"] is not None:
            self["bottom_boundary_condition"] = _Strings.from_file
        if self["surface_reflection_coefficient"] is not None:
            self["surface_boundary_condition"] = _Strings.from_file

        if self['depth_max'] is None:
            self['depth_max'] = _np.max(self['depth'])

        if not isinstance(self['soundspeed'], _pd.DataFrame):
            if _np.size(self['soundspeed']) == 1:
                speed = [float(self["soundspeed"]), float(self["soundspeed"])]
                depth = [0, float(self['depth_max'])]
                self["soundspeed"] = _pd.DataFrame(speed, columns=["speed"], index=depth)
                self["soundspeed"].index.name = "depth"
            elif self['soundspeed'].shape[0] == 1 and self['soundspeed'].shape[1] == 2:
                speed = [float(self["soundspeed"][0,1]), float(self["soundspeed"][0,1])]
                d1 = float(min([0.0, self["soundspeed"][0,0]]))
                d2 = float(max([self["soundspeed"][0,0], self['depth_max']]))
                self["soundspeed"] = _pd.DataFrame(speed, columns=["speed"], index=[d1, d2])
                self["soundspeed"].index.name = "depth"
            elif self['soundspeed'].ndim == 2 and self['soundspeed'].shape[1] == 2:
                depth = self['soundspeed'][:,0]
                speed = self['soundspeed'][:,1]
                self["soundspeed"] = _pd.DataFrame(speed, columns=["speed"], index=depth)
                self["soundspeed"].index.name = "depth"
            else:
                raise ValueError("Soundspeed array must be a 2xN array (better to use a DataFrame)")

        if "depth" in self["soundspeed"].columns:
            self["soundspeed"] = self["soundspeed"].set_index("depth")

        if len(self['soundspeed'].columns) > 1:
            self['soundspeed_interp'] == _Strings.quadrilateral

        # Beam angle ranges default to half-space if source is left-most, otherwise full-space:
        if self['beam_angle_min'] is None:
            if _np.min(self['receiver_range']) < 0:
                self['beam_angle_min'] = - Defaults.beam_angle_fullspace
            else:
                self['beam_angle_min'] = - Defaults.beam_angle_halfspace
        if self['beam_angle_max'] is None:
            if _np.min(self['receiver_range']) < 0:
                self['beam_angle_max'] =  Defaults.beam_angle_fullspace
            else:
                self['beam_angle_max'] = Defaults.beam_angle_halfspace

        self['box_depth'] = self['box_depth'] or 1.01 * self['depth_max']
        self['box_range'] = self['box_range'] or 1.01 * (_np.max(self['receiver_range']) - min(0,_np.min(self['receiver_range'])))

        return self


    def _check_env_header(self) -> None:
        assert self['type'] == '2D', 'Not a 2D environment'
        assert self["_num_media"] == 1, f"BELLHOP only supports 1 medium, found {self['_num_media']}"

    def _check_env_surface(self) -> None:
        max_range = _np.max(self['receiver_range'])
        if self['surface'] is not None:
            assert _np.size(self['surface']) > 1, 'surface must be an Nx2 array'
            assert self['surface'].ndim == 2, 'surface must be a scalar or an Nx2 array'
            assert self['surface'].shape[1] == 2, 'surface must be a scalar or an Nx2 array'
            assert self['surface'][0,0] <= 0, 'First range in surface array must be 0 m'
            assert self['surface'][-1,0] >= max_range, 'Last range in surface array must be beyond maximum range: '+str(max_range)+' m'
            assert _np.all(_np.diff(self['surface'][:,0]) > 0), 'surface array must be strictly monotonic in range'
        if self["surface_reflection_coefficient"] is not None:
            assert self["surface_boundary_condition"] == _Strings.from_file, "TRC values need to be read from file"

    def _check_env_depth(self) -> None:
        max_range = _np.max(self['receiver_range'])
        if _np.size(self['depth']) > 1:
            assert self['depth'].ndim == 2, 'depth must be a scalar or an Nx2 array'
            assert self['depth'].shape[1] == 2, 'depth must be a scalar or an Nx2 array'
            assert self['depth'][0,0] <= 0, 'First range in depth array must be 0 m'
            assert self['depth'][-1,0] >= max_range, 'Last range in depth array must be beyond maximum range: '+str(max_range)+' m'
            assert _np.all(_np.diff(self['depth'][:,0]) > 0), 'Depth array must be strictly monotonic in range'
            assert self["_bathymetry"] == _Strings.from_file, 'len(depth)>1 requires BTY file'
        if self["bottom_reflection_coefficient"] is not None:
            assert self["bottom_boundary_condition"] == _Strings.from_file, "BRC values need to be read from file"
        assert _np.max(self['source_depth']) <= self['depth_max'], 'source_depth cannot exceed water depth: '+str(self['depth_max'])+' m'
        assert _np.max(self['receiver_depth']) <= self['depth_max'], 'receiver_depth cannot exceed water depth: '+str(self['depth_max'])+' m'

    def _check_env_ssp(self) -> None:
        assert isinstance(self['soundspeed'], _pd.DataFrame), 'Soundspeed should always be a DataFrame by this point'
        assert self['soundspeed'].size > 1, "Soundspeed DataFrame should have been constructed internally to be two elements"
        if self['soundspeed'].size > 1:
            if len(self['soundspeed'].columns) > 1:
                assert self['soundspeed_interp'] == _Strings.quadrilateral, "SVP DataFrame with multiple columns implies quadrilateral interpolation."
            if self['soundspeed_interp'] == _Strings.spline:
                assert self['soundspeed'].shape[0] > 3, 'soundspeed profile must have at least 4 points for spline interpolation'
            else:
                assert self['soundspeed'].shape[0] > 1, 'soundspeed profile must have at least 2 points'
            assert self['soundspeed'].index[0] <= 0.0, 'First depth in soundspeed array must be 0 m'
            assert _np.all(_np.diff(self['soundspeed'].index) > 0), 'Soundspeed array must be strictly monotonic in depth'
            if self['depth_max'] != self['soundspeed'].index[-1]:
                if self['soundspeed'].shape[1] > 1:
                    # TODO: generalise interpolation trimming from np approach below
                    assert self['soundspeed'].index[-1] == self['depth_max'], '2D SSP: Final entry in soundspeed array must be at the maximum water depth: '+str(self['depth_max'])+' m'
                else:
                    indlarger = _np.argwhere(self['soundspeed'].index > self['depth_max'])[0][0]
                    prev_ind = self['soundspeed'].index[:indlarger].tolist()
                    insert_ss_val = _np.interp(self['depth_max'], self['soundspeed'].index, self['soundspeed'].iloc[:,0])
                    new_row = _pd.DataFrame([self['depth_max'], insert_ss_val], columns=self['soundspeed'].columns)
                    self['soundspeed'] = _pd.concat([
                            self['soundspeed'].iloc[:(indlarger-1)],  # rows before insertion
                            new_row,                             # new row
                        ], ignore_index=True)
                    self['soundspeed'].index = prev_ind + [self['depth_max']]
                    warnings.warn("Bellhop.py has used linear interpolation to ensure the sound speed profile ends at the max depth. Ensure this is what you want.", UserWarning)
                    print("ATTEMPTING TO FIX")
            # TODO: check soundspeed range limits

    def _check_env_sbp(self) -> None:
        if self['source_directionality'] is not None:
            assert _np.size(self['source_directionality']) > 1, 'source_directionality must be an Nx2 array'
            assert self['source_directionality'].ndim == 2, 'source_directionality must be an Nx2 array'
            assert self['source_directionality'].shape[1] == 2, 'source_directionality must be an Nx2 array'
            assert _np.all(self['source_directionality'][:,0] >= -180) and _np.all(self['source_directionality'][:,0] <= 180), 'source_directionality angles must be in (-180, 180]'

    def _check_env_beam(self) -> None:
        assert self['beam_angle_min'] >= -180 and self['beam_angle_min'] <= 180, 'beam_angle_min must be in range (-180, 180]'
        assert self['beam_angle_max'] >= -180 and self['beam_angle_max'] <= 180, 'beam_angle_max must be in range (-180, 180]'
        if self['_single_beam'] == _Strings.single_beam:
            assert self['single_beam_index'] is not None, 'Single beam was requested with option I but no index was provided in NBeam line'
