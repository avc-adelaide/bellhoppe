
"""
Environment configuration for BELLHOP.

This module provides dataclass-based environment configuration with automatic validation,
replacing manual option checking with field validators.
"""

from dataclasses import dataclass, fields
from typing import Optional, Union, Any, Dict

from .constants import _Strings, _Maps


@dataclass
class EnvironmentConfig:
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
    grid: str = 'default'

    # Attenuation parameters
    volume_attenuation: str = 'none'
    attenuation_units: str = 'frequency dependent'

    # Francois-Garrison volume attenuation parameters
    fg_salinity: Optional[float] = None
    fg_temperature: Optional[float] = None
    fg_pH: Optional[float] = None
    fg_depth: Optional[float] = None

    def __post_init__(self) -> None:
        """Validate field values after initialization."""
        self._validate_interpolation_types()
        self._validate_boundary_conditions()
        self._validate_grid_types()
        self._validate_beam_types()
        self._validate_attenuation_options()
        self._validate_volume_attenuation()

    def _validate_interpolation_types(self) -> None:
        """Validate interpolation type options."""
        valid_interp = set(_Maps.interp_rev.keys())
        if self.soundspeed_interp not in valid_interp:
            raise ValueError(f"Invalid soundspeed_interp: {self.soundspeed_interp}. "
                           f"Must be one of: {sorted(valid_interp)}")

        valid_bty_interp = set(_Maps.bty_interp_rev.keys())
        if self.depth_interp not in valid_bty_interp:
            raise ValueError(f"Invalid depth_interp: {self.depth_interp}. "
                           f"Must be one of: {sorted(valid_bty_interp)}")

        if self.surface_interp not in valid_bty_interp:
            raise ValueError(f"Invalid surface_interp: {self.surface_interp}. "
                           f"Must be one of: {sorted(valid_bty_interp)}")

    def _validate_boundary_conditions(self) -> None:
        """Validate boundary condition options."""
        valid_boundary = set(_Maps.boundcond_rev.keys())
        if self.bottom_boundary_condition not in valid_boundary:
            raise ValueError(f"Invalid bottom_boundary_condition: {self.bottom_boundary_condition}. "
                           f"Must be one of: {sorted(valid_boundary)}")

        if self.surface_boundary_condition not in valid_boundary:
            raise ValueError(f"Invalid surface_boundary_condition: {self.surface_boundary_condition}. "
                           f"Must be one of: {sorted(valid_boundary)}")

    def _validate_grid_types(self) -> None:
        """Validate grid type options."""
        valid_grid = set(_Maps.grid_rev.keys())
        if self.grid not in valid_grid:
            raise ValueError(f"Invalid grid: {self.grid}. "
                           f"Must be one of: {sorted(valid_grid)}")

    def _validate_beam_types(self) -> None:
        """Validate beam type options."""
        valid_beam = set(_Maps.beam_rev.keys())
        if self.beam_type not in valid_beam:
            raise ValueError(f"Invalid beam_type: {self.beam_type}. "
                           f"Must be one of: {sorted(valid_beam)}")

    def _validate_attenuation_options(self) -> None:
        """Validate attenuation unit options."""
        valid_attunits = set(_Maps.attunits_rev.keys())
        if self.attenuation_units not in valid_attunits:
            raise ValueError(f"Invalid attenuation_units: {self.attenuation_units}. "
                           f"Must be one of: {sorted(valid_attunits)}")

    def _validate_volume_attenuation(self) -> None:
        """Validate volume attenuation options."""
        valid_volatt = set(_Maps.volatt_rev.keys())
        if self.volume_attenuation not in valid_volatt:
            raise ValueError(f"Invalid volume_attenuation: {self.volume_attenuation}. "
                           f"Must be one of: {sorted(valid_volatt)}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert dataclass to dictionary format for backward compatibility."""
        result = {}
        for field_obj in fields(self):
            value = getattr(self, field_obj.name)
            result[field_obj.name] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnvironmentConfig':
        """Create EnvironmentConfig from dictionary."""
        # Filter out any keys that aren't valid field names
        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)


def new() -> Dict[str, Any]:
    """Get default environment dictionary for 2D underwater acoustic modeling.

    Creates a new environment using the dataclass and returns it as a dictionary
    for backward compatibility.

    Returns
    -------
    dict
        Default environment parameters as a dictionary.
    """
    config = EnvironmentConfig()
    return config.to_dict()


def _validate_transmission_loss_mode(mode: str) -> None:
    """Validate transmission loss mode using predefined options.

    Parameters
    ----------
    mode : str
        The transmission loss mode to validate.

    Raises
    ------
    ValueError
        If the mode is not valid.
    """
    valid_modes = {_Strings.coherent, _Strings.incoherent, _Strings.semicoherent}
    if mode not in valid_modes:
        raise ValueError(f'Invalid transmission loss mode: {mode}. '
                        f'Must be one of: {sorted(valid_modes)}')


def _validate_source_type(source_type: str) -> None:
    """Validate source type using predefined options.

    Parameters
    ----------
    source_type : str
        The source type to validate.

    Raises
    ------
    ValueError
        If the source type is not valid.
    """
    valid_source_types = set(_Maps.source_rev.keys())
    if source_type not in valid_source_types:
        raise ValueError(f'Invalid source type: {source_type}. '
                        f'Must be one of: {sorted(valid_source_types)}')
