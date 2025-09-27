
from enum import Enum

class _Strings(str, Enum):
    """String definitions to avoid hard-coding magic strings in the source code

    This helps prevent typos and permits autocomplete (if your editor is smart enough).
    """

    default = "default"
    none = "none"

    # interpolation
    linear = "linear"
    spline = "spline"
    curvilinear = "curvilinear"
    quadrilateral = "quadrilateral"
    pchip = "pchip"
    hexahedral = "hexahedral"
    arrivals = "arrivals"
    nlinear = "nlinear"

    # tasks
    eigenrays = "eigenrays"
    rays = "rays"
    coherent = "coherent"
    incoherent = "incoherent"
    semicoherent = "semicoherent"

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
    frequency_scaled_db_per_meter = "frequency scaled dB per meter"
    db_per_wavelength = "dB per wavelength"
    quality_factor = "quality factor"
    loss_parameter = "loss parameter"

    single_beam = "single beam"

class _Maps:
    """Mappings from Bellhop single-char input file options to readable Python options

    These are also defined with reverse mappings in the form:

    >>> _Maps.interp["S"]
    "spline"

    >>> _Maps.interp_rev["spline"]
    "S"

    """

    interp = {
        "S": _Strings.spline,
        "C": _Strings.linear,
        "Q": _Strings.quadrilateral,
        "P": _Strings.pchip,
        "H": _Strings.hexahedral,
        "N": _Strings.nlinear,
        " ": _Strings.default,
    }
    bty_interp = {
        "L": _Strings.linear,
        "C": _Strings.curvilinear,
    }
    boundcond = {
        "V": _Strings.vacuum,
        "A": _Strings.acousto_elastic,
        "R": _Strings.rigid,
        "F": _Strings.from_file,
        " ": _Strings.default,
    }
    attunits = {
        "N": _Strings.nepers_per_meter,
        "F": _Strings.frequency_dependent,
        "M": _Strings.db_per_meter,
        "m": _Strings.frequency_scaled_db_per_meter,
        "W": _Strings.db_per_wavelength,
        "Q": _Strings.quality_factor,
        "L": _Strings.loss_parameter,
        " ": _Strings.default,
    }
    volatt = {
        "T": _Strings.thorp,
        "F": _Strings.francois_garrison,
        "B": _Strings.biological,
        " ": _Strings.none,
    }
    bottom = {
        "_": _Strings.flat,
        "~": _Strings.from_file,
        "*": _Strings.from_file,
        " ": _Strings.default,
    }
    surface = {
        "_": _Strings.flat,
        "~": _Strings.from_file,
        "*": _Strings.from_file,
        " ": _Strings.default,
    }
    source = {
        "R": _Strings.point,
        "X": _Strings.line,
        " ": _Strings.default,
    }
    grid = {
        "R": _Strings.rectilinear,
        "I": _Strings.irregular,
        " ": _Strings.default,
    }
    beam = {
        "G": _Strings.hat_cartesian,
        "^": _Strings.hat_cartesian,
        "g": _Strings.hat_ray,
        "B": _Strings.gaussian_cartesian,
        "b": _Strings.gaussian_ray,
        " ": _Strings.default,
    }
    single_beam = {
        "I": _Strings.single_beam,
        " ": _Strings.default,
    }

    # reverse maps
    interp_rev = {v: k for k, v in interp.items()}
    bty_interp_rev = {v: k for k, v in bty_interp.items()}
    boundcond_rev = {v: k for k, v in boundcond.items()}
    attunits_rev = {v: k for k, v in attunits.items()}
    volatt_rev = {v: k for k, v in volatt.items()}
    bottom_rev = {v: k for k, v in bottom.items()}
    surface_rev = {v: k for k, v in surface.items()}
    source_rev = {v: k for k, v in source.items()}
    grid_rev = {v: k for k, v in grid.items()}
    beam_rev = {v: k for k, v in beam.items()}
    single_beam_rev = {v: k for k, v in single_beam.items()}
