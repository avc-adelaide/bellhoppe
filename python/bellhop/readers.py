
import os
import re

from typing import Any, Dict, Optional, Tuple, Union, TextIO, List, cast
from numpy.typing import NDArray

import numpy as _np
import pandas as _pd
from bellhop.constants import _Strings, _Maps, _File_Ext
import bellhop.environment

def _read_next_valid_line(f: TextIO) -> str:
    """Read the next valid text line of an input file, discarding invalid lines"""
    while True:
        line = f.readline()
        if not line: # EOF
            raise EOFError("End of file reached before finding a valid line")
        line = line.strip()
        if not line: # empty
            continue
        if '!' in line: # strip comments
            line = line[:line.index('!')].strip()
        if line:
            return line.strip()

def _parse_line(line: str) -> list[str]:
    """Parse a line, removing comments, /, and whitespace, and return the parts in a list"""
    line = line.split("!", 1)[0].split('/', 1)[0].strip()
    return line.split()

def _parse_quoted_string(line: str) -> str:
    """Extract string from within quotes

    Sometimes (why??) the leading quote was being stripped, so we also try to catch
    this case with the regexp, stripping only a trailing '.
    """
    mtch = re.search(r"'([^']*)'", line)
    mtch2 = re.search(r"([^']*)'$", line)
    return mtch.group(1) if mtch else mtch2.group(1) if mtch2 else line.strip()

def _parse_vector(f: Any, dtype: type = float) -> Tuple[Any, int]:
    """Parse a vector that starts with count then values, ending with '/'"""
    line = _read_next_valid_line(f)

    # First line is the count
    linecount = int(_parse_line(line)[0])

    # Second line has the values
    values_line = _read_next_valid_line(f)
    parts = _parse_line(values_line)
    val = [dtype(p) for p in parts]

    valout = _np.array(val) if len(val) > 1 else val[0]
    return valout, linecount

def _read_ssp_points(f: Any) -> _pd.DataFrame:
    """Read sound speed profile points until we find the bottom boundary line

       Default values are according to 'EnvironmentalFile.htm'."""

    ssp_depth: list[float] = []
    ssp_speed: list[float] = []
    ssp = dict(depth=0.0, speed=1500.0, speed_shear=0.0, density=1000.0, att=0.0, att_shear=0.0)

    while True:
        line = f.readline()
        if not line:
            raise EOFError("File ended during env file reading of SSP points.")
        line = line.strip()
        if not line: # completely empty line
            continue
        if line.startswith("'"): # Check if this is a bottom boundary line (starts with quote)
            # This is the bottom boundary line, put it back
            f.seek(f.tell() - len(line.encode()) - 1)
            break

        parts = (_parse_line(line) + [None] * 6)[0:6]
        if parts[0] is None: # empty line after stripping comments
            continue
        ssp.update({
            k: float(v) if v is not None else ssp[k] for k, v in zip(ssp.keys(), parts)
        })
        ssp_depth.append(ssp["depth"])
        ssp_speed.append(ssp["speed"])
        # TODO: add extra terms (but this needs adjustments elsewhere)

    if len(ssp_speed) == 0:
        raise ValueError("No SSP points were found in the env file.")
    elif len(ssp_speed) == 1:
        raise ValueError("Only one SSP point found but at least two required (top and bottom)")

    df = _pd.DataFrame(ssp_speed,index=ssp_depth,columns=["speed"])
    df.index.name = "depth"
    return df

def _opt_lookup(name: str, opt: str, _map: dict[str, _Strings]) -> Optional[str]:
    opt_str = _map.get(opt)
    if opt_str is None:
        raise ValueError(f"{name} option {opt!r} not available")
    return opt_str

def _float(x: Any, scale: float = 1) -> Optional[float]:
    """Permissive float-enator with unit scaling"""
    return None if x is None else float(x) * scale

def _int(x: Any) -> Optional[int]:
    """Permissive int-enator"""
    return None if x is None else int(x)

def read_env2d(fname: str) -> Dict[str, Any]:
    """Read a 2D underwater environment from a BELLHOP .env file.

    This function parses a BELLHOP .env file and returns a Python data structure
    that is compatible with create_env2d(). This enables round-trip testing and
    compatibility between file-based and programmatic environment definitions.

    :param fname: path to .env file (with or without .env extension)

    :returns: environment dictionary compatible with create_env2d()

    **Unit conversions performed:**

    - Receiver ranges: km → m
    - Bottom density: g/cm³ → kg/m³
    - All other units preserved as in ENV file

    **Examples:**

    >>> import bellhop as bh
    >>> env = bh.read_env2d('examples/Munk/MunkB_ray.env')
    >>> print(env['name'])
    'Munk profile'
    >>> print(env['frequency'])
    50.0

    >>> # Use with existing functions
    >>> checked_env = bh.check_env2d(env)
    >>> rays = bh.compute_rays(env)

    >>> # Round-trip compatibility
    >>> env_orig = bh.create_env2d(name="test", frequency=100)
    >>> # ... write to file via BELLHOP ...
    >>> env_read = bh.read_env2d("test.env")
    >>> assert env_read['frequency'] == env_orig['frequency']

    """

    reader = EnvironmentReader(fname)
    return reader.read()

class EnvironmentReader:
    """Read and parse Bellhop environment files.
    
    Although this class is only used for one task,
    the use of a class provides the clearest code interface compared
    to nested functions, which either implicitly set
    dict parameters, or have many repeated and superfluous
    arguments as dicts are passed in and returned at
    each stage.
    """
    
    def __init__(self, fname: str):
        """Initialize reader with filename.
        
        Args:
            fname: Path to .env file (with or without extension)
        """
        self.fname, self.fname_base = _prepare_filename(fname, _File_Ext.env)
        self.env: Dict[str, Any] = bellhop.environment.new()

    def read(self) -> Dict[str, Any]:
        """Do the reading..."""
        with open(self.fname, 'r') as f:
            self._read_header(f)
            self._read_top_boundary(f)
            self._read_sound_speed_profile(f)
            self._read_bottom_boundary(f)
            self._read_sources_receivers_task(f)
            self._read_beams_limits(f)
        return self.env

    def _read_header(self, f: TextIO) -> None:
        """Read environment file header"""

        # Line 1: Title
        title_line = _read_next_valid_line(f)
        self.env['name'] = _parse_quoted_string(title_line)
        # Line 2: Frequency
        freq_line = _read_next_valid_line(f)
        self.env['frequency'] = float(_parse_line(freq_line)[0])
        # Line 3: NMedia (should be 1 for BELLHOP)
        nmedia_line = _read_next_valid_line(f)
        self.env["_num_media"] = int(_parse_line(nmedia_line)[0])

    def _read_top_boundary(self, f: TextIO) -> None:
        """Read environment file top boundary options (multiple lines)"""

        # Line 4: Top boundary options
        topopt_line = _read_next_valid_line(f)
        topopt = _parse_quoted_string(topopt_line) + "      "
        self.env["soundspeed_interp"]          = _opt_lookup("Interpolation",          topopt[0], _Maps.interp)
        self.env["surface_boundary_condition"] = _opt_lookup("Top boundary condition", topopt[1], _Maps.boundcond)
        self.env["attenuation_units"]          = _opt_lookup("Attenuation units",      topopt[2], _Maps.attunits)
        self.env["volume_attenuation"]         = _opt_lookup("Volume attenuation",     topopt[3], _Maps.volatt)
        self.env["_altimetry"]                 = _opt_lookup("Altimetry",              topopt[4], _Maps.surface)
        self.env["_single_beam"]               = _opt_lookup("Single beam",            topopt[5], _Maps.single_beam)
        if self.env["_altimetry"] == _Strings.from_file:
            self.env["surface"], self.env["surface_interp"] = read_ati(self.fname_base)

        # Line 4a: Volume attenuation params
        if self.env["volume_attenuation"] == _Strings.francois_garrison:
            fg_spec_line = _read_next_valid_line(f)
            fg_parts = _parse_line(fg_spec_line)
            self.env["fg_salinity"]    = float(fg_parts[0])
            self.env["fg_temperature"] = float(fg_parts[1])
            self.env["fg_pH"]          = float(fg_parts[2])
            self.env["fg_depth"]       = float(fg_parts[3])

        # Line 4b: Boundary condition params
        if self.env["surface_boundary_condition"] == _Strings.acousto_elastic:
            surface_props_line = _read_next_valid_line(f)
            surface_props = _parse_line(surface_props_line) + [None] * 6
            self.env['surface_depth']             = _float(surface_props[0])
            self.env['surface_soundspeed']        = _float(surface_props[1])
            self.env['surface_soundspeed_shear']  = _float(surface_props[2])
            self.env['surface_density']           = _float(surface_props[3], scale=1000)  # convert from g/cm³ to kg/m³
            self.env['surface_attenuation']       = _float(surface_props[4])
            self.env['surface_attenuation_shear'] = _float(surface_props[5])

    def _read_sound_speed_profile(self, f: TextIO) -> None:
        """Read environment file sound speed profile"""

        # SSP depth specification
        ssp_spec_line = _read_next_valid_line(f)
        ssp_parts = _parse_line(ssp_spec_line) + [None] * 3
        self.env['depth_npts']   = _int(ssp_parts[0])
        self.env['depth_sigmaz'] = _float(ssp_parts[1])
        self.env['depth_max']    = _float(ssp_parts[2])
        self.env['depth'] = self.env['depth_max']

        # Read SSP points and from file if applicable
        self.env['soundspeed'] = _read_ssp_points(f)
        if self.env["soundspeed_interp"] == _Strings.quadrilateral:
            self.env['soundspeed'] = read_ssp(self.fname_base, self.env['soundspeed'].index)

    def _read_bottom_boundary(self, f: TextIO) -> None:
        """Read environment file bottom boundary condition"""

        # Bottom boundary options
        bottom_line = _read_next_valid_line(f)
        bottom_parts = _parse_line(bottom_line) + [None] * 3
        botopt = _parse_quoted_string(cast(str,bottom_parts[0])) + "  " # cast() => I promise this is a str :)
        self.env["bottom_boundary_condition"] = _opt_lookup("Bottom boundary condition", botopt[0], _Maps.boundcond)
        self.env["_bathymetry"]               = _opt_lookup("Bathymetry",                botopt[1], _Maps.bottom)
        self.env['bottom_roughness']       = _float(bottom_parts[1])
        self.env['bottom_beta']            = _float(bottom_parts[2])
        self.env['bottom_transition_freq'] = _float(bottom_parts[3])
        if self.env["_bathymetry"] == _Strings.from_file:
            self.env["depth"], self.env["bottom_interp"] = read_bty(self.fname_base)

        # Bottom properties (depth, sound_speed, density, absorption)
        if self.env["bottom_boundary_condition"] == _Strings.acousto_elastic:
            bottom_props_line = _read_next_valid_line(f)
            bottom_props = _parse_line(bottom_props_line) + [None] * 6
            self.env['bottom_soundspeed'] = _float(bottom_props[1])
            self.env['bottom_soundspeed_shear'] = _float(bottom_props[2])
            self.env['bottom_density'] = _float(bottom_props[3], 1000)  # convert from g/cm³ to kg/m³
            self.env['bottom_attenuation'] = _float(bottom_props[4])
            self.env['bottom_attenuation_shear'] = _float(bottom_props[5])

    def _read_sources_receivers_task(self, f: TextIO) -> None:
        """Read environment file sources, receivers, and task"""
        
        # Source & receiver depths
        self.env['source_depth'],   self.env['source_ndepth']   = _parse_vector(f)
        self.env['receiver_depth'], self.env['receiver_ndepth'] = _parse_vector(f)

        # Receiver ranges (in km, need to convert to m)
        receiver_ranges, self.env['receiver_nrange'] = _parse_vector(f)
        self.env['receiver_range'] = receiver_ranges * 1000  # convert km to m

        # Task/run type (e.g., 'R', 'C', etc.)
        task_line = _read_next_valid_line(f)
        task_code = _parse_quoted_string(task_line) + "    "
        self.env['task']        = _Maps.task.get(task_code[0])
        self.env['beam_type']   = _Maps.beam.get(task_code[1])
        self.env['_sbp_file']   = _Maps.sbp.get(task_code[2])
        self.env['source_type'] = _Maps.source.get(task_code[3])
        self.env['grid']        = _Maps.grid.get(task_code[4])

        # Check for source directionality
        if self.env["_sbp_file"] == _Strings.from_file:
            self.env["source_directionality"] = read_sbp(self.fname_base)

    def _read_beams_limits(self, f: TextIO) -> None:
        """Read environment file beams and limits"""
        
        # Number of beams
        beam_num_line = _read_next_valid_line(f)
        beam_num_parts = _parse_line(beam_num_line) + [None] * 1
        self.env['beam_num'] = int(beam_num_parts[0] or 0)
        self.env['single_beam_index'] = _int(beam_num_parts[1])

        # Beam angles (beam_angle_min, beam_angle_max)
        angles_line = _read_next_valid_line(f)
        angle_parts = _parse_line(angles_line) + [None] * 2
        self.env['beam_angle_min'] = _float(angle_parts[0])
        self.env['beam_angle_max'] = _float(angle_parts[1])

        # Ray tracing limits (step, max_depth, max_range) - last line
        limits_line = _read_next_valid_line(f)
        limits_parts = _parse_line(limits_line)
        self.env['step_size'] = float(limits_parts[0])
        self.env['box_depth'] = float(limits_parts[1])
        self.env['box_range'] = float(limits_parts[2]) * 1000  # convert km to m


def _prepare_filename(fname: str, ext: str) -> Tuple[str,str]:
    """Checks filename is present and file exists."""
    if fname.endswith(ext):
        nchar = len(ext)
        fname_base = fname[:-nchar]
    else:
        fname_base = fname
        fname = fname + ext

    if not os.path.exists(fname):
        raise FileNotFoundError(f"File not found: {fname}")
    
    return fname, fname_base




def read_ssp(fname: str, depths: Optional[Union[List[float], NDArray[_np.float64], _pd.DataFrame]] = None) -> Union[Any, _pd.DataFrame]:
    """Read a 2D sound speed profile (.ssp) file used by BELLHOP.

    This function reads BELLHOP's .ssp files which contain range-dependent
    sound speed profiles. The file format is:
    - Line 1: Number of range profiles (NPROFILES)
    - Line 2: Range coordinates in km (space-separated)
    - Line 3+: Sound speed values, one line per depth point across all ranges

    :param fname: path to .ssp file (with or without .ssp extension)
    :returns: for single-profile files: numpy array with [depth, soundspeed] pairs;
              for multi-profile files: pandas DataFrame with range-dependent sound speed data

    **Return format:**

    - **Single-profile files (1 range)**: Returns a 2D numpy array with [depth, soundspeed] pairs,
      compatible with create_env2d() soundspeed parameter.

    - **Multi-profile files (>1 ranges)**: Returns a pandas DataFrame where:

      - **Columns**: Range coordinates (in meters, converted from km in file)
      - **Index**: Depth indices (0, 1, 2, ... for each depth level in the file)
      - **Values**: Sound speeds (m/s)

      This DataFrame can be directly assigned to create_env2d() soundspeed parameter
      for range-dependent acoustic modeling.

    **Note on depths**: For multi-profile files, depth indices are used (0, 1, 2, ...)
    since the actual depth coordinates come from the associated BELLHOP .env file.
    Users can modify the DataFrame index if actual depth values are known.

    **Examples:**

    >>> import bellhop as bh
    >>> # Single-profile file
    >>> ssp1 = bh.read_ssp("single_profile.ssp")  # Returns numpy array
    >>> env = bh.create_env2d()
    >>> env["soundspeed"] = ssp1
    >>>
    >>> # Multi-profile file
    >>> ssp2 = bh.read_ssp("tests/MunkB_geo_rot/MunkB_geo_rot.ssp")  # Returns DataFrame
    >>> env = bh.create_env2d()
    >>> env["soundspeed"] = ssp2  # Range-dependent sound speed

    **File format example:**

    ::

        30
        -50 -5 -1 -.8 -.75 -.6 -.4 -.2 0 0.2 0.4 0.6 0.8 1.0 1.2 1.4 1.6 1.8 2.0 2.2 2.4 2.6 2.8 3.0 3.2 3.4 3.6 3.8 4.0 10.0
        1500 1500 1548.52 1530.29 1526.69 1517.78 1509.49 1504.30 1501.38 1500.14 1500.12 1501.02 1502.57 1504.62 1507.02 1509.69 1512.55 1515.56 1518.67 1521.85 1525.10 1528.38 1531.70 1535.04 1538.39 1541.76 1545.14 1548.52 1551.91 1551.91
        1500 1500 1548.52 1530.29 1526.69 1517.78 1509.49 1504.30 1501.38 1500.14 1500.12 1501.02 1502.57 1504.62 1507.02 1509.69 1512.55 1515.56 1518.67 1521.85 1525.10 1528.38 1531.70 1535.04 1538.39 1541.76 1545.14 1548.52 1551.91 1551.91
    """

    if not fname.endswith(_File_Ext.ssp):
        fname = fname + _File_Ext.ssp

    if not os.path.exists(fname):
        raise FileNotFoundError(f"SSP file not found: {fname}")

    with open(fname, 'r') as f:
        # Read number of range profiles
        nprofiles = int(_read_next_valid_line(f))

        # Read range coordinates (in km)
        range_line = _read_next_valid_line(f)
        ranges = _np.array([float(x) for x in _parse_line(range_line)])

        if len(ranges) != nprofiles:
            raise ValueError(f"Expected {nprofiles} range profiles, but found {len(ranges)} ranges")

        # Read sound speed data - read all remaining lines as a matrix
        ssp_data = []
        line_num = 2  # We've already read 2 lines (nprofiles and ranges)
        for line in f:
            line_num += 1
            line = line.strip()
            if line:  # Skip empty lines
                values = [float(x) for x in line.split()]
                if len(values) != nprofiles:
                    raise ValueError(f"Line {line_num} has {len(values)} values, expected {nprofiles}")
                ssp_data.append(values)

        ssp_array = _np.array(ssp_data)

        if ssp_array.size == 0:
            raise ValueError("No sound speed data found in file")

        if nprofiles == 1:
            # Single profile - return as [depth, soundspeed] pairs for backward compatibility
            # Create depth values - linearly spaced from 0 to number of depth points
            ndepths = ssp_array.shape[0]
            depths = _np.linspace(0, ndepths-1, ndepths, dtype=float)
            return _np.column_stack([depths, ssp_array.flatten()])
        else:
            # Multiple ranges - return as pandas DataFrame for range-dependent modeling
            # Convert ranges from km to meters (as expected by create_env2d)
            ranges_m = ranges * 1000

            # Create depth indices (actual depths would come from associated .env file)
            if depths is None:
                ndepths = ssp_array.shape[0]
                depths = _np.arange(ndepths, dtype=float)

            # Create DataFrame with ranges as columns and depths as index
            # ssp_array is [ndepths, nprofiles] which is the correct orientation
            df = _pd.DataFrame(ssp_array, index=depths, columns=ranges_m)
            df.index.name = "depth"
            return df

def read_bty(fname: str) -> Tuple[Any, str]:
    """Read a bathymetry file used by Bellhop."""
    if not fname.endswith('.bty'):
        fname = fname + '.bty'
    return read_ati_bty(fname)

def read_ati(fname: str) -> Tuple[Any, str]:
    """Read an altimetry file used by Bellhop."""
    if not fname.endswith('.ati'):
        fname = fname + '.ati'
    return read_ati_bty(fname)

def read_ati_bty(fname: str) -> Tuple[Any, str]:
    """Read an altimetry (.ati) or bathymetry (.bty) file used by BELLHOP.

    This function reads BELLHOP's .bty files which define the bottom depth
    profile. The file format is:
    - Line 1: Interpolation type ('L' for linear, 'C' for curvilinear)
    - Line 2: Number of points
    - Line 3+: Range (km) and depth (m) pairs

    :param fname: path to .bty file (with or without .bty extension)
    :returns: numpy array with [range, depth] pairs compatible with create_env2d()

    The returned array can be assigned to env["depth"] for range-dependent bathymetry.

    **Examples:**

    >>> import bellhop as bh
    >>> bty,bty_interp = bh.read_bty("tests/MunkB_geo_rot/MunkB_geo_rot.bty")
    >>> env = bh.create_env2d()
    >>> env["depth"] = bty
    >>> env["depth_interp"] = bty_interp
    >>> arrivals = bh.calculate_arrivals(env)

    **File format example:**

    ::

        'L'
        5
        0 3000
        10 3000
        20 500
        30 3000
        100 3000
    """
    import os

    if not os.path.exists(fname):
        raise FileNotFoundError(f"ATI/BTY file not found: {fname}")

    with open(fname, 'r') as f:
        # Read interpolation type (usually 'L' or 'C')
        interp_type = _read_next_valid_line(f).strip("'\"")

        # Read number of points
        npoints = int(_read_next_valid_line(f))

        # Read range,depth pairs
        ranges = []
        depths = []

        for i in range(npoints):
            try:
                line = _read_next_valid_line(f)
            except EOFError:
                break
            parts = _parse_line(line)
            if len(parts) >= 2:
                ranges.append(float(parts[0]))  # Range in km
                depths.append(float(parts[1]))  # Depth in m

        if len(ranges) != npoints:
            raise ValueError(f"Expected {npoints} altimetry/bathymetry points, but found {len(ranges)}")

        # Convert ranges from km to m for consistency with bellhop env structure
        ranges_m = _np.array(ranges) * 1000
        depths_array = _np.array(depths)

        # Return as [range, depth] pairs
        return _np.column_stack([ranges_m, depths_array]), _Maps.bty_interp[interp_type]

def read_sbp(fname: str) -> Any:
    """Read an source beam patterm (.sbp) file used by BELLHOP.

    The file format is:
    - Line 1: Number of points
    - Line 2+: Angle (deg) and power (dB) pairs

    :param fname: path to .sbp file (with or without extension)
    :returns: numpy array with [angle, power] pairs
    """

    import os

    if not fname.endswith('.sbp'):
        fname = fname + '.sbp'

    if not os.path.exists(fname):
        raise FileNotFoundError(f"SBP file not found: {fname}")

    with open(fname, 'r') as f:

        # Read number of points
        npoints = int(_read_next_valid_line(f))

        # Read range,depth pairs
        angles = []
        powers = []

        for i in range(npoints):
            try:
                line = _read_next_valid_line(f)
            except EOFError:
                break
            parts = _parse_line(line)
            if len(parts) >= 2:
                angles.append(float(parts[0]))  # Range in km
                powers.append(float(parts[1]))  # Depth in m

        if len(angles) != npoints:
            raise ValueError(f"Expected {npoints} points, but found {len(angles)}")

        # Return as [range, depth] pairs
        return _np.column_stack([angles, powers])

def read_refl_coeff(fname: str) -> Any:
    """Read a reflection coefficient (.brc/.trc) file used by BELLHOP.

    This function reads BELLHOP's .brc files which define the reflection coefficient
    data. The file format is:
    - Line 1: Number of points
    - Line 2+: THETA(j)       RMAG(j)       RPHASE(j)

    Where:
    - THETA():  Angle (degrees)
    - RMAG():   Magnitude of reflection coefficient
    - RPHASE(): Phase of reflection coefficient (degrees)

    :param fname: path to .brc/.trc file (extension required)
    :returns: numpy array with [theta, rmag, rphase] triplets compatible with create_env2d()

    The returned array can be assigned to env["bottom_reflection_coefficient"] or env["surface_reflection_coefficient"] .

    **Example:**

    >>> import bellhop as bh
    >>> brc = bh.read_refl_coeff("tests/MunkB_geo_rot/MunkB_geo_rot.brc")
    >>> env = bh.create_env2d()
    >>> env["bottom_reflection_coefficient"] = brc
    >>> arrivals = bh.calculate_arrivals(env)

    **File format example:**

    ::

        3
        0.0   1.00  180.0
        45.0  0.95  175.0
        90.0  0.90  170.0
    """
    import os


    if not os.path.exists(fname):
        raise FileNotFoundError(f"Reflection coefficient file not found: {fname}")

    with open(fname, 'r') as f:

        # Read number of points
        npoints = int(_read_next_valid_line(f))

        # Read range,depth pairs
        theta = []
        rmagn = []
        rphas = []

        for i in range(npoints):
            try:
                line = _read_next_valid_line(f)
            except EOFError:
                break
            parts = _parse_line(line)
            if len(parts) == 3:
                theta.append(float(parts[0]))
                rmagn.append(float(parts[1]))
                rphas.append(float(parts[2]))

        if len(theta) != npoints:
            raise ValueError(f"Expected {npoints} reflection coefficient points, but found {len(theta)}")

        # Return as [range, depth] pairs
        return _np.column_stack([theta, rmagn, rphas])
