
from dataclasses import dataclass

from bellhop.constants import _Strings

@dataclass(frozen=True)
class Defaults:
    beam_angle_halfspace: float = 89.999
    beam_angle_fullspace: float = 179.999

# Import the new dataclass-based environment
try:
    from bellhop.environment_dataclass import EnvironmentConfig, create_env2d_dataclass, dataclass_to_legacy_dict
except ImportError:
    # Fallback if there are any import issues
    EnvironmentConfig = None
    create_env2d_dataclass = None
    dataclass_to_legacy_dict = None


def new():
    """Get default environment dictionary for 2D underwater acoustic modeling.

    This function provides the shared default values used by both create_env2d()
    and read_env2d() to avoid duplication. Where defaults are not provided (equal to None)
    some will be supplied in a "clean up" step as part of check_env2d().

    ENV parameters
    ---------------

    :name: environment title/name
    :type: '2D' (fixed for 2D environments)
    :frequency: acoustic frequency in Hz
    :soundspeed: sound speed profile (scalar for constant, array for depth-dependent)
    :soundspeed_interp: interpolation method ('linear', 'spline', 'quadrilateral')
    :bottom_soundspeed: bottom sediment sound speed in m/s
    :bottom_soundspeed_shear: bottom sediment sound speed in m/s
    :bottom_density: bottom sediment density in kg/m³
    :bottom_absorption: bottom sediment absorption in dB/wavelength
    :bottom_absorption_shear: bottom sediment absorption in dB/wavelength
    :bottom_roughness: bottom roughness RMS in meters
    :surface: surface altimetry profile (None if flat surface)
    :surface_interp: surface interpolation method ('linear', 'curvilinear')
    :surface_boundary_condition: ('vacuum', 'acousto-elastic', 'rigid', 'from-file')
    :volume_attenuation: ('none', 'thorp', 'francois-garrison', 'biological')
    :attenuation_units: ('nepers per meter', 'frequency dependent', 'dB per meter', 'frequency scaled dB per meter', 'dB per wavelength', 'quality factor', 'loss parameter')
    :source_depth: transmitter depth(s) in meters
    :source_directionality: transmitter beam pattern (None if omnidirectional)
    :receiver_depth: receiver depth(s) in meters
    :receiver_range: receiver range(s) in meters
    :depth: maximum water depth in meters
    :depth_interp: bathymetry interpolation method ('linear', 'curvilinear')
    :beam_angle_min: minimum beam angle in degrees
    :beam_angle_max: maximum beam angle in degrees
    :beam_num: number of beams (0 for automatic)
    :step_size: (maximum) step size to trace rays in meters (0 for automatic)
    :box_depth: box extent to trace rays in meters (auto-calculated based on max depth data if not specified)
    :box_range: box extent to trace rays in meters (auto-calculated based on max receiver range if not specified)
    :source_type: point (default) or line
    :beam_type: todo
    :grid: rectilinear or irregular

    :returns: dictionary with default environment parameters
    """
    return {
        'name': 'bellhop/python default',
        'type': '2D',                   # 2D/3D
        'frequency': 25000,             # Hz
        # sound speed parameters
        'soundspeed': 1500,              # m/s
        'soundspeed_interp': _Strings.spline,  # spline/linear
        '_ssp_env': None,                #
        # bottom parameters
        'bottom_soundspeed': 1600,       # m/s
        'bottom_soundspeed_shear': 0,    # m/s
        'bottom_density': 1600,          # kg/m^3
        'bottom_absorption': None,       # dB/wavelength??
        'bottom_absorption_shear': None, # dB/wavelength??
        'bottom_roughness': 0,           # m (rms)
        'bottom_beta': None,             #
        'bottom_transition_freq': None,  # Hz
        'bottom_boundary_condition': _Strings.acousto_elastic,
        'bottom_reflection_coefficient': None,
        '_bathymetry': _Strings.flat,    # set to "from-file" if multiple bottom depths
        # surface parameters
        'surface': None,                # surface profile
        'surface_interp': _Strings.linear,       # curvilinear/linear
        'surface_boundary_condition': _Strings.vacuum,
        'surface_reflection_coefficient': None,
        '_altimetry': _Strings.flat,    # set to "from-file" if multiple surface heights
        # source parameters
        'source_type': 'default',
        'source_depth': 5,                  # m
        'source_ndepth': None,              #
        'source_directionality': None,      # [(deg, dB)...]
        '_sbp_file': _Strings.default,
        # receiver parameters
        'receiver_depth': 10,                 # m
        'receiver_ndepth': None,              #
        'receiver_range': 1000,               # m
        'receiver_nrange': None,              #
        # bathymetry parameters
        'depth': 25,                    # m
        'depth_interp': _Strings.linear,         # curvilinear/linear
        'depth_npts': 0,                #
        'depth_sigmaz': 0,              #
        'depth_max': None,              # m
        # beam settings
        'beam_angle_min': None,         # deg
        'beam_angle_max': None,         # deg
        'beam_num': 0,                  # number of beams (0 = auto)
        'beam_type': 'default',
        # solution parameters
        'step_size': None,
        'box_depth': None,
        'box_range': None,
        'grid': 'default',
        # attentuation parameters
        'volume_attenuation': 'none',
        'attenuation_units': 'frequency dependent',
        # francois_garrison volume attenuation parameters
        'fg_salinity': None,
        'fg_temperature': None,
        'fg_pH': None,
        'fg_depth': None,
    }
