
from dataclasses import dataclass

from bellhop.constants import _Strings

@dataclass(frozen=True)
class Defaults:
    beam_angle_halfspace: float = 89.999
    beam_angle_fullspace: float = 179.999


def new():
    """Get default environment dictionary for 2D underwater acoustic modeling.

    This function provides the shared default values used by both create_env2d()
    and read_env2d() to avoid duplication. Where defaults are not provided (equal to None)
    some will be supplied in a "clean up" step as part of check_env2d().

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
