
from dataclasses import dataclass

from bellhop.constants import _Strings

@dataclass(frozen=True)
class Defaults:
    beam_angle_halfspace: int = 89.999
    beam_angle_fullspace: int = 179.999


def new():
    """Get default environment dictionary for 2D underwater acoustic modeling.

    This function provides the shared default values used by both create_env2d()
    and read_env2d() to avoid duplication.

    :returns: dictionary with default environment parameters
    """
    return {
        'name': 'bellhop/python default',
        'type': '2D',                   # 2D/3D
        'frequency': 25000,             # Hz
        'ssp_env': None,                #
        'soundspeed': 1500,             # m/s
        'soundspeed_interp': _Strings.spline,    # spline/linear
        'bottom_soundspeed': 1600,      # m/s
        'bottom_soundspeed_shear': 0,   # m/s
        'bottom_density': 1600,         # kg/m^3
        'bottom_absorption': None,       # dB/wavelength??
        'bottom_absorption_shear': None, # dB/wavelength??
        'bottom_roughness': 0,          # m (rms)
        'bottom_beta': None,            #
        'bottom_transition_freq': None, # Hz
        'bottom_boundary_condition': _Strings.acousto_elastic,
        'bottom_reflection_coefficient': None,
        '_bottom_bathymetry': _Strings.flat,   #
        'surface': None,                # surface profile
        'surface_interp': _Strings.linear,       # curvilinear/linear
        'tx_depth': 5,                  # m
        'tx_ndepth': None,              #
        'tx_directionality': None,      # [(deg, dB)...]
        'rx_depth': 10,                 # m
        'rx_ndepth': None,              #
        'rx_range': 1000,               # m
        'rx_nrange': None,              #
        'depth': 25,                    # m
        'depth_interp': _Strings.linear,         # curvilinear/linear
        'depth_npts': 0,                #
        'depth_sigmaz': 0,              #
        'depth_max': None,              # m
        'min_angle': None,              # deg
        'max_angle': None,              # deg
        'nbeams': 0,                    # number of beams (0 = auto)
        'top_boundary_condition': _Strings.vacuum,
        'volume_attenuation': 'none',
        'attenuation_units': 'frequency dependent',
        'step_size': None,
        'box_depth': None,
        'box_range': None,
        'tx_type': 'default',
        'beam_type': 'default',
        'grid': 'default',
        # francois_garrison volume attenuation parameters:
        'fg_salinity': None,
        'fg_temperature': None,
        'fg_pH': None,
        'fg_depth': None,
    }
