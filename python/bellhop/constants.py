from dataclasses import dataclass, field
from enum import Enum



class _File_Ext:
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


class _Strings(str, Enum):
    """String definitions to avoid hard-coding magic strings in the source code

    This helps prevent typos and permits autocomplete (if your editor is smart enough).
    """

    exe = "bellhop.exe"

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

    # bathymetry
    from_file = "from-file"
    flat = "flat"

    # sources
    line = "line"
    point = "point"

    # beam
    hat_cartesian = "hat-cartesian",
    hat_ray = "hat-ray",
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
    coherent = "coherent"
    incoherent = "incoherent"
    semicoherent = "semicoherent"
    amplitude = "amplitude"
    amplitude_b = "amplitude-binary"



class _Maps:
    """Mappings from Bellhop single-char input file options to readable Python options

    These are also defined with reverse mappings in the form:

    >>> _Maps.soundspeed_interp["S"]
    "spline"

    >>> _Maps.soundspeed_interp_rev["spline"]
    "S"

    """

    soundspeed_interp = {
        "S": _Strings.spline,
        "C": _Strings.linear,
        "Q": _Strings.quadrilateral, # TODO: add test
        "P": _Strings.pchip,
        "H": _Strings.hexahedral, # TODO: add test
        "N": _Strings.nlinear,
        " ": _Strings.default,
    }
    depth_interp = {
        "L": _Strings.linear,
        "C": _Strings.curvilinear,
    }
    surface_interp = {
        "L": _Strings.linear,
        "C": _Strings.curvilinear,
    }
    bottom_boundary_condition = {
        "V": _Strings.vacuum,
        "A": _Strings.acousto_elastic,
        "R": _Strings.rigid,
        "F": _Strings.from_file,
        " ": _Strings.default,
    }
    surface_boundary_condition = {
        "V": _Strings.vacuum,
        "A": _Strings.acousto_elastic,
        "R": _Strings.rigid,
        "F": _Strings.from_file,
        " ": _Strings.default,
    }
    attenuation_units = {
        "N": _Strings.nepers_per_meter,
        "F": _Strings.frequency_dependent,
        "M": _Strings.db_per_meter,
        "W": _Strings.db_per_wavelength,
        "Q": _Strings.quality_factor,
        "L": _Strings.loss_parameter,
        " ": _Strings.default,
    }
    volume_attenuation = {
        "T": _Strings.thorp,
        "F": _Strings.francois_garrison,
        "B": _Strings.biological,
        " ": _Strings.none,
    }
    _bathymetry = {
        "_": _Strings.flat,
        "~": _Strings.from_file,
        "*": _Strings.from_file,
        " ": _Strings.default,
    }
    _altimetry = {
        "_": _Strings.flat,
        "~": _Strings.from_file,
        "*": _Strings.from_file,
        " ": _Strings.default,
    }
    source_type = {
        "R": _Strings.point,
        "X": _Strings.line,
        " ": _Strings.default,
    }
    _sbp_file = {
        "*": _Strings.from_file,
        "O": _Strings.omnidirectional,
        " ": _Strings.default,
    }
    grid_type = {
        "R": _Strings.rectilinear,
        "I": _Strings.irregular,
        " ": _Strings.default,
    }
    beam_type = {
        "G": _Strings.hat_cartesian,
        "^": _Strings.hat_cartesian,
        "g": _Strings.hat_ray,
        "B": _Strings.gaussian_cartesian,
        "b": _Strings.gaussian_ray,
        " ": _Strings.default,
    }
    dimension = {
        " ": _Strings.two_d,
        "2": _Strings.two_half_d,
        "3": _Strings.three_d,
    }
    _single_beam = {
        "I": _Strings.single_beam,
        " ": _Strings.default,
    }
    task = {
        "R": _Strings.rays,
        "E": _Strings.eigenrays,
        "A": _Strings.amplitude,
        "a": _Strings.amplitude_b,
        "C": _Strings.coherent,
        "I": _Strings.incoherent,
        "S": _Strings.semicoherent,
    }
    mode = {
        "C": _Strings.coherent,
        "I": _Strings.incoherent,
        "S": _Strings.semicoherent,
    }

    # reverse maps
    soundspeed_interp_rev = {v: k for k, v in soundspeed_interp.items()}
    depth_interp_rev = {v: k for k, v in depth_interp.items()}
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

@dataclass(frozen=True)
class Defaults:
    """Dataclass of hard-coded defaults used throughout the Bellhop interface."""
    model_name: str = field(default="bellhop", metadata={"desc": "Name of the class instance for the model"})
    exe: str = field(default="bellhop.exe", metadata={"desc": "Executable name"})
    beam_angle_halfspace: float = field(default=90.0, metadata={"units": "deg"})
    beam_angle_fullspace: float = field(default=180.0, metadata={"units": "deg"})
    env_comment_pad: int = field(default=50, metadata={"desc": "Number of characters used before the comment in the constructed .env files."})
    interference_mode: str = field(default=_Strings.coherent, metadata={"desc": "Mode of interference when calculating transmission loss"})
    dimension: str = field(default=_Strings.two_d, metadata={"desc": "Dimension of simulation (2D, 2.5D, 3D)"})


