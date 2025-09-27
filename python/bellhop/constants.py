
from enum import Enum

class _Strings(str, Enum):
    """String definitions to avoid hard-coding magic strings in the source code

    This helps prevent typos and permits autocomplete (if your editor is smart enough).
    """

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

    # grid
    rectilinear = "rectilinear"
    irregular = "irregular"

    # volume attenuation
    thorp = "thorp"
    francois_garrison = "francois-garrison"
    biological = "biological"


class _Maps:
    """Mappings from Bellhop single-char input file options to readable Python options

    These are also defined with reverse mappings in the form:

    >>> _Maps.interp["S"]
    "spline"

    >>> _Maps.interp_rev["spline"]
    "S"

    """

    interp = {
        "S":_Strings.spline,
        "C":_Strings.linear,
        "Q":_Strings.quadrilateral,
        "P":_Strings.pchip,
        "H":_Strings.hexahedral,
        "N":_Strings.nlinear,
        " ": "default",
    }
    bty_interp = {
        "L":_Strings.linear,
        "C":_Strings.curvilinear,
    }
    boundcond = {
        "V":_Strings.vacuum,
        "A":_Strings.acousto_elastic,
        "R":_Strings.rigid,
        "F":_Strings.from_file,
        " ": "default",
    }
    attunits = {
        "N": "nepers per meter",
        "F": "frequency dependent",
        "M": "dB per meter",
        "m": "frequency scaled dB per meter",
        "W": "dB per wavelength",
        "Q": "quality factor",
        "L": "loss parameter",
        " ": "default",
    }
    volatt = {
        "": "none",
        "T": "thorp",
        "F": "francois-garrison",
        "B": "biological",
        " ": "default",
    }
    bottom = {
        "_":_Strings.flat,
        "~":_Strings.from_file,
        "*":_Strings.from_file,
        " ": "default",
    }
    surface = {
        "_":_Strings.flat,
        "~":_Strings.from_file,
        "*":_Strings.from_file,
        " ": "default",
    }
    source = {
        "R":_Strings.point,
        "X":_Strings.line,
        " ": "default",
    }
    grid = {
        "R":_Strings.rectilinear,
        "I":_Strings.irregular,
        " ": "default",
    }
    beam = {
        "G": "hat-cartesian",
        "^": "hat-cartesian",
        "g": "hat-ray",
        "B": "gaussian-cartesian",
        "b": "gaussian-ray",
        " ": "default",
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
