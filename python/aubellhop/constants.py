"""Constants and defaults for aubellhop.

This file contains various dataclasses and wrapper classes for storing:

* List of all external file types and their extensions
* String constants used throughout the codebase for autocomplete and error-checking
* Mappngs between Bellhop character "flags" and their user-level option name
* Default settings for various Bellhop classes
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class FileExt:
    """Strings to define file extensions.

    Using this class avoids typos in the source.
    It is also used to loop through files to delete them
    when needed before/after Bellhop execution.
    """

    arr = ".arr"
    ati = ".ati"
    bty = ".bty"
    log = ".log"
    sbp = ".sbp"
    shd = ".shd"
    prt = ".prt"
    ray = ".ray"
    env = ".env"
    ssp = ".ssp"
    brc = ".brc"
    trc = ".trc"


class BHStrings(str, Enum):
    """String definitions to avoid hard-coding magic strings in the source code

    This helps prevent typos and permits autocomplete (if your editor is smart enough).
    """

    default = "default"
    none = "none"

    # dimension
    two_d = "2D"
    two_half_d = "2.5D"
    three_d = "3D"

    # interpolation
    linear = "linear"
    spline = "spline"
    pchip = "pchip"
    nlinear = "nlinear"
    quadrilateral = "quadrilateral"
    hexahedral = "hexahedral"

    # ati/bty interpolation
    curvilinear = "curvilinear"

    # boundaries
    vacuum = "vacuum"
    acousto_elastic = "acousto-elastic"
    rigid = "rigid"
    grain = "grain"

    # bathymetry
    from_file = "from-file"
    flat = "flat"

    # sources
    line = "line"
    point = "point"

    # beam
    cartesian = "cartesian",
    ray = "ray",
    hat_cartesian = "hat-cartesian",
    hat_ray = "hat-ray",
    gaussian_simple = "gaussian-simple",
    gaussian_cartesian = "gaussian-cartesian",
    gaussian_ray = "gaussian-ray",
    omnidirectional = "omnidirectional"
    single_beam = "single beam"

    # grid
    rectilinear = "rectilinear"
    irregular = "irregular"

    # volume attenuation
    thorp = "thorp"
    francois_garrison = "francois-garrison"
    biological = "biological"

    # attenuation units
    nepers_per_meter = "nepers per meter"
    frequency_dependent = "frequency dependent"
    db_per_meter = "dB per meter"
    db_per_wavelength = "dB per wavelength"
    quality_factor = "quality factor"
    loss_parameter = "loss parameter"

    # tasks
    rays = "rays"
    eigenrays = "eigenrays"
    arrivals = "arrivals"
    arrivals_b = "arrivals-binary"
    coherent = "coherent"
    incoherent = "incoherent"
    semicoherent = "semicoherent"



class FlagMaps:
    """Mappings from Bellhop single-char input file options to readable Python options

    These are also defined with reverse mappings in the form:

    >>> FlagMaps.soundspeed_interp["S"]
    "spline"

    >>> FlagMaps.soundspeed_interp_rev["spline"]
    "S"

    """

    soundspeed_interp = {
        "S": BHStrings.spline,
        "C": BHStrings.linear,
        "Q": BHStrings.quadrilateral, # TODO: add test
        "P": BHStrings.pchip,
        "H": BHStrings.hexahedral, # TODO: add test
        "N": BHStrings.nlinear,
        " ": BHStrings.default,
    }
    bottom_interp = {
        "L": BHStrings.linear,
        "C": BHStrings.curvilinear,
    }
    surface_interp = {
        "L": BHStrings.linear,
        "C": BHStrings.curvilinear,
    }
    bottom_boundary_condition = {
        "V": BHStrings.vacuum,
        "A": BHStrings.acousto_elastic,
        "R": BHStrings.rigid,
        "G": BHStrings.grain,
        "F": BHStrings.from_file,
        " ": BHStrings.default,
    }
    surface_boundary_condition = {
        "V": BHStrings.vacuum,
        "A": BHStrings.acousto_elastic,
        "R": BHStrings.rigid,
        "F": BHStrings.from_file,
        " ": BHStrings.default,
    }
    attenuation_units = {
        "N": BHStrings.nepers_per_meter,
        "F": BHStrings.frequency_dependent,
        "M": BHStrings.db_per_meter,
        "W": BHStrings.db_per_wavelength,
        "Q": BHStrings.quality_factor,
        "L": BHStrings.loss_parameter,
        " ": BHStrings.default,
    }
    volume_attenuation = {
        "T": BHStrings.thorp,
        "F": BHStrings.francois_garrison,
        "B": BHStrings.biological,
        " ": BHStrings.none,
    }
    _bathymetry = {
        "_": BHStrings.flat,
        "~": BHStrings.from_file,
        "*": BHStrings.from_file,
        " ": BHStrings.default,
    }
    _altimetry = {
        "_": BHStrings.flat,
        "~": BHStrings.from_file,
        "*": BHStrings.from_file,
        " ": BHStrings.default,
    }
    source_type = {
        "R": BHStrings.point,
        "X": BHStrings.line,
        " ": BHStrings.default,
    }
    _sbp_file = {
        "*": BHStrings.from_file,
        "O": BHStrings.omnidirectional,
        " ": BHStrings.default,
    }
    grid_type = {
        "R": BHStrings.rectilinear,
        "I": BHStrings.irregular,
        " ": BHStrings.default,
    }
    beam_type = {
        "C": BHStrings.cartesian,
        "R": BHStrings.ray,
        "^": BHStrings.hat_cartesian,
        "G": BHStrings.hat_cartesian,  # after "^" so the reverse map emits the documented flag
        "g": BHStrings.hat_ray,
        "S": BHStrings.gaussian_simple,
        "B": BHStrings.gaussian_cartesian,
        "b": BHStrings.gaussian_ray,
        " ": BHStrings.default, # = "G"
    }
    dimension = {
        " ": BHStrings.two_d,
        "2": BHStrings.two_half_d,
        "3": BHStrings.three_d,
    }
    _single_beam = {
        "I": BHStrings.single_beam,
        " ": BHStrings.default,
    }
    task = {
        "R": BHStrings.rays,
        "E": BHStrings.eigenrays,
        "A": BHStrings.arrivals,
        "a": BHStrings.arrivals_b,
        "C": BHStrings.coherent,
        "I": BHStrings.incoherent,
        "S": BHStrings.semicoherent,
    }
    mode = {
        "C": BHStrings.coherent,
        "I": BHStrings.incoherent,
        "S": BHStrings.semicoherent,
    }

    # reverse maps
    soundspeed_interp_rev = {v: k for k, v in soundspeed_interp.items()}
    bottom_interp_rev = {v: k for k, v in bottom_interp.items()}
    surface_interp_rev = {v: k for k, v in surface_interp.items()}
    bottom_boundary_condition_rev = {v: k for k, v in bottom_boundary_condition.items()}
    surface_boundary_condition_rev = {v: k for k, v in surface_boundary_condition.items()}
    attenuation_units_rev = {v: k for k, v in attenuation_units.items()}
    volume_attenuation_rev = {v: k for k, v in volume_attenuation.items()}
    _bathymetry_rev = {v: k for k, v in _bathymetry.items()}
    _altimetry_rev = {v: k for k, v in _altimetry.items()}
    source_type_rev = {v: k for k, v in source_type.items()}
    grid_type_rev = {v: k for k, v in grid_type.items()}
    beam_type_rev = {v: k for k, v in beam_type.items()}
    _single_beam_rev = {v: k for k, v in _single_beam.items()}
    task_rev = {v: k for k, v in task.items()}
    mode_rev = {v: k for k, v in mode.items()}
    dimension_rev = {v: k for k, v in dimension.items()}

@dataclass
class ModelDefaults:
    """Defaults within the Bellhop model class."""
    name_2d: str = field(default="bellhop",      metadata={"desc": "Name of the class instance for the 2D model"})
    name_3d: str = field(default="bellhop3d",    metadata={"desc": "Name of the class instance for the 3D model"})
    exe_2d:  str = field(default="bellhop.exe",  metadata={"desc": "Executable filename for the 2D model"})
    exe_3d:  str = field(default="bellhop3d.exe",metadata={"desc": "Executable filename for the 3D model"})
    dim_2d:  int = field(default=2,              metadata={"desc": "Number of dimensions in the 2D model"})
    dim_3d:  int = field(default=3,              metadata={"desc": "Number of dimensions in the 3D model"})

@dataclass
class MiscDefaults:
    """Defaults for parameters within setup code."""
    beam_angle_halfspace: float = field(default=90.0, metadata={"units": "deg"})
    beam_angle_fullspace: float = field(default=180.0, metadata={"units": "deg"})
    beam_bearing_halfspace: float = field(default=90.0, metadata={"units": "deg"})
    beam_bearing_fullspace: float = field(default=180.0, metadata={"units": "deg"})
    density: float = field(default=1000.0, metadata={"units": "kg/m^3", "desc": "Constant density of the medium"})
    sound_speed: float = field(default=1500.0, metadata={"units": "m/s", "desc": "Constant speed of sound in the medium"})

@dataclass
class EnvDefaults:
    """Defaults for the Environment class."""
    attenuation_units: str = field(default=BHStrings.frequency_dependent, metadata={"desc": "Attenuation units to define volume attenuation (when setting `bottom_attenuation`, etc)"})
    bottom_attenuation: float = field(default=0.1, metadata={"units": "scale factor","desc": "When acousto-elastic bottom boundary condition is selected, this is the attenuation factor"})
    bottom_boundary_condition: str = field(default=BHStrings.acousto_elastic, metadata={"desc": "Standard boundary condition for seabed"})
    bottom_interp: str = field(default=BHStrings.linear, metadata={"desc": "Interpolation for bathymetry depths"})
    comment_pad: int = field(default=50, metadata={"desc": "Number of characters used before the comment in the constructed .env files."})
    dimension: str = field(default=BHStrings.two_d, metadata={"desc": "Dimension of simulation (2D, 2.5D, 3D)"})
    _dimension: int = field(default=2, metadata={"desc": "Dimension of model (2, 3)"})
    frequency: float = field(default=25000.0, metadata={"desc": "Frequency of sound propagation", "units": "Hz"})
    interference_mode: str = field(default=BHStrings.coherent, metadata={"desc": "Mode of interference when calculating transmission loss"})
    simulation_depth_scale: float = field(default=1.01,metadata={'desc': 'Scaling factor on the maximum depth of the bathymetry to calculate the maximum simulation depth extent.'})
    simulation_range_scale: float = field(default=1.1,metadata={'desc': 'Scaling factor on the maximum range of the receivers to calculate the maximum simulation range extent.'})
    simulation_cross_range_scale: float = field(default=2.0,metadata={'desc': 'Scaling factor on the maximum cross range of the receivers (based on maximum bearing angle) to calculate the maximum simulation cross range extent.'})
    simulation_cross_range_min: float = field(default=10.0,metadata={'desc': 'For very small bearing angles there may be numerical issues with a cross range size approaching zero. This parameter specifies the minimum cross range size of the simulation extent.',"units": "m"})
    soundspeed_interp: str = field(default=BHStrings.linear, metadata={"desc": "Interpolation for sound speed profile data"})
    surface_depth: float = field(default=0.0, metadata={"units": "m", "desc": "Depth of the surface. Should always be `0.0` for flat altimetry."})
    surface_interp: str = field(default=BHStrings.linear, metadata={"desc": "Interpolation for altimetry surface depths"})
    volume_attenuation: str = field(default=BHStrings.none, metadata={"desc": "Type of volume attenuation to apply"})

