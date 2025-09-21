
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

