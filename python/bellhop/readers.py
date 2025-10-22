
import os

from struct import unpack as _unpack
from pathlib import Path
from typing import Any, Optional, Tuple, Union, TextIO, List, cast, IO
from numpy.typing import NDArray

import numpy as _np
import pandas as _pd
from bellhop.constants import _Strings, _Maps, _File_Ext
from bellhop.environment import Environment

def _read_next_valid_line(f: TextIO) -> str:
    """Read the next valid text line of an input file, discarding empty content.

    Args:
        f: File handle to read from

    Returns:
        Non-empty line with comments and whitespace removed

    Raises:
        EOFError: If end of file reached without finding valid content
    """
    while True:
        raw_line = f.readline()
        if not raw_line: # EOF
            raise EOFError("End of file reached before finding a valid line")
        line = raw_line.split('!', 1)[0].strip()
        if line:
            return line

def _parse_line(line: str) -> list[str]:
    """Parse a line, removing comments, /, and whitespace, and return the parts in a list"""
    line = line.split("!", 1)[0].split('/', 1)[0].strip()
    return line.split()

def _unquote_string(line: str) -> str:
    """Extract string from within single quotes, possibly with commas too."""
    return line.strip().strip(",'")

def _read_ssp_points(f: TextIO) -> _pd.DataFrame:
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

def _prepare_filename(fname: str, ext: str, name: str) -> Tuple[str,str]:
    """Checks filename is present and file exists."""
    if fname.endswith(ext):
        nchar = len(ext)
        fname_base = fname[:-nchar]
    else:
        fname_base = fname
        fname = fname + ext

    if not os.path.exists(fname):
        raise FileNotFoundError(f"{name} file not found: {fname}")

    return fname, fname_base

def read_env(fname: str) -> Environment:
    """Read a 2D underwater environment from a BELLHOP .env file.

    This function parses a BELLHOP .env file and returns a Python data structure
    that is compatible with create_env(). This enables round-trip testing and
    compatibility between file-based and programmatic environment definitions.

    Parameters
    ----------
    fname : str
        Path to .env file (with or without .env extension)

    Returns
    -------
    dict
        Environment dictionary compatible with create_env()

    Notes
    -----
    **Unit conversions performed:**

    - Receiver ranges: km → m
    - Bottom density: g/cm³ → kg/m³
    - All other units preserved as in ENV file

    Examples
    --------
    >>> import bellhop as bh
    >>> env = bh.read_env('examples/Munk/MunkB_ray.env')
    >>> print(env['name'])
    'Munk profile'
    >>> print(env['frequency'])
    50.0

    >>> # Use with existing functions
    >>> checked_env = bh.check_env(env)
    >>> rays = bh.compute_rays(env)

    >>> # Round-trip compatibility
    >>> env_orig = bh.create_env(name="test", frequency=100)
    >>> # ... write to file via BELLHOP ...
    >>> env_read = bh.read_env("test.env")
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
        self.fname, self.fname_base = _prepare_filename(fname, _File_Ext.env, "Environment")
        self.env: Environment = Environment()

    def read(self) -> Environment:
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
        self.env['name'] = _unquote_string(title_line)
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
        topopt = _unquote_string(topopt_line) + "      "
        self.env["soundspeed_interp"]          = _opt_lookup("Interpolation",          topopt[0], _Maps.soundspeed_interp)
        self.env["surface_boundary_condition"] = _opt_lookup("Top boundary condition", topopt[1], _Maps.surface_boundary_condition)
        self.env["attenuation_units"]          = _opt_lookup("Attenuation units",      topopt[2], _Maps.attenuation_units)
        self.env["volume_attenuation"]         = _opt_lookup("Volume attenuation",     topopt[3], _Maps.volume_attenuation)
        self.env["_altimetry"]                 = _opt_lookup("Altimetry",              topopt[4], _Maps._altimetry)
        self.env["_single_beam"]               = _opt_lookup("Single beam",            topopt[5], _Maps._single_beam)
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
            self.env['_surface_soundspeed_shear']  = _float(surface_props[2])
            self.env['surface_density']           = _float(surface_props[3], scale=1000)  # convert from g/cm³ to kg/m³
            self.env['surface_attenuation']       = _float(surface_props[4])
            self.env['_surface_attenuation_shear'] = _float(surface_props[5])

    def _read_sound_speed_profile(self, f: TextIO) -> None:
        """Read environment file sound speed profile"""

        # SSP depth specification
        ssp_spec_line = _read_next_valid_line(f)
        ssp_parts = _parse_line(ssp_spec_line) + [None] * 3
        self.env['_mesh_npts']   = _int(ssp_parts[0])
        self.env['_depth_sigma'] = _float(ssp_parts[1])
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
        botopt = _unquote_string(cast(str,bottom_parts[0])) + "  " # cast() => I promise this is a str :)
        self.env["bottom_boundary_condition"] = _opt_lookup("Bottom boundary condition", botopt[0], _Maps.bottom_boundary_condition)
        self.env["_bathymetry"]               = _opt_lookup("Bathymetry",                botopt[1], _Maps._bathymetry)
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
            self.env['_bottom_soundspeed_shear'] = _float(bottom_props[2])
            self.env['bottom_density'] = _float(bottom_props[3], 1000)  # convert from g/cm³ to kg/m³
            self.env['bottom_attenuation'] = _float(bottom_props[4])
            self.env['_bottom_attenuation_shear'] = _float(bottom_props[5])

    def _read_sources_receivers_task(self, f: TextIO) -> None:
        """Read environment file sources, receivers, and task.

        Bellhop and Bellhop3D have different numbers of variables specified before
        the task line. Luckily we can detect that reliably by looking for a line which
        starts with `'`."""

        next_line = ""
        sr_lines = []
        while not next_line.startswith("'"):
            if next_line:
                sr_lines.append(next_line)
            next_line = _read_next_valid_line(f)
        self._read_task(f, next_line)

        nlines = len(sr_lines)
        if nlines == 6:
            self.env['type'] = "2D"
            self.env['source_ndepth']   = self._parse_line_count(sr_lines[0])
            self.env['receiver_ndepth'] = self._parse_line_count(sr_lines[2])
            self.env['receiver_nrange'] = self._parse_line_count(sr_lines[4])
            self.env['source_depth']    = self._parse_vector(sr_lines[1])
            self.env['receiver_depth']  = self._parse_vector(sr_lines[3])
            self.env['receiver_range']  = self._parse_vector(sr_lines[5]) * 1000.0 # convert km to m
        elif nlines == 12:
            self.env['type'] = "3D"
        else:
            raise RuntimeError(f"The python parsing of Bellhop's so-called 'list-directed IO' is not robust. Expected to read 6 or 12 lines (2D or 3D cases); found: {nlines}")

        if self.env["_sbp_file"] == _Strings.from_file:
            self.env["source_directionality"] = read_sbp(self.fname_base)

    def _parse_vector(self,line: str) -> Union[NDArray[_np.float64], float]:
        """Parse a vector of floats with unknown number of values"""
        parts = _parse_line(line)
        val = [float(p) for p in parts]
        valout = _np.array(val) if len(val) > 1 else val[0]
        return valout

    def _parse_line_count(self,line: str) -> int:
        """Parse an integer on a line by itself"""
        parts = _parse_line(line)
        return int(parts[0])

    def _read_task(self, f: TextIO, task_line: str) -> None:
        task_code = _unquote_string(task_line) + "    "
        self.env['task']        = _Maps.task.get(task_code[0])
        self.env['beam_type']   = _Maps.beam_type.get(task_code[1])
        self.env['_sbp_file']   = _Maps._sbp_file.get(task_code[2])
        self.env['source_type'] = _Maps.source_type.get(task_code[3])
        self.env['grid_type']   = _Maps.grid_type.get(task_code[4])

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
        self.env['box_range'] = float(limits_parts[2]) * 1000.0  # convert km to m


def read_ssp(fname: str,
             depths: Optional[Union[
                        List[float],
                        NDArray[_np.float64],
                        _pd.DataFrame]] = None
            ) -> Union[NDArray[_np.float64], _pd.DataFrame]:
    """Read a 2D sound speed profile (.ssp) file used by BELLHOP.

    This function reads BELLHOP's .ssp files which contain range-dependent
    sound speed profiles. The file format is:
    - Line 1: Number of range profiles (NPROFILES)
    - Line 2: Range coordinates in km (space-separated)
    - Line 3+: Sound speed values, one line per depth point across all ranges

    Parameters
    ----------
    fname : str
        Path to .ssp file (with or without .ssp extension)

    Returns
    -------
    numpy.ndarray or pandas.DataFrame
        For single-profile files: numpy array with [depth, soundspeed] pairs;
        for multi-profile files: pandas DataFrame with range-dependent sound speed data

    Notes
    -----
    **Return format:**

    - **Single-profile files (1 range)**: Returns a 2D numpy array with [depth, soundspeed] pairs,
      compatible with create_env() soundspeed parameter.

    - **Multi-profile files (>1 ranges)**: Returns a pandas DataFrame where:

      - **Columns**: Range coordinates (in meters, converted from km in file)
      - **Index**: Depth indices (0, 1, 2, ... for each depth level in the file)
      - **Values**: Sound speeds (m/s)

      This DataFrame can be directly assigned to create_env() soundspeed parameter
      for range-dependent acoustic modeling.

    **Note on depths**: For multi-profile files, depth indices are used (0, 1, 2, ...)
    since the actual depth coordinates come from the associated BELLHOP .env file.
    Users can modify the DataFrame index if actual depth values are known.

    Examples
    --------
    >>> import bellhop as bh
    >>> # Single-profile file
    >>> ssp1 = bh.read_ssp("single_profile.ssp")  # Returns numpy array
    >>> env = bh.create_env()
    >>> env["soundspeed"] = ssp1
    >>>
    >>> # Multi-profile file
    >>> ssp2 = bh.read_ssp("tests/MunkB_geo_rot/MunkB_geo_rot.ssp")  # Returns DataFrame
    >>> env = bh.create_env()
    >>> env["soundspeed"] = ssp2  # Range-dependent sound speed

    **File format example:**

    ::

        30
        -50 -5 -1 -.8 -.75 -.6 -.4 -.2 0 0.2 0.4 0.6 0.8 1.0 1.2 1.4 1.6 1.8 2.0 2.2 2.4 2.6 2.8 3.0 3.2 3.4 3.6 3.8 4.0 10.0
        1500 1500 1548.52 1530.29 1526.69 1517.78 1509.49 1504.30 1501.38 1500.14 1500.12 1501.02 1502.57 1504.62 1507.02 1509.69 1512.55 1515.56 1518.67 1521.85 1525.10 1528.38 1531.70 1535.04 1538.39 1541.76 1545.14 1548.52 1551.91 1551.91
        1500 1500 1548.52 1530.29 1526.69 1517.78 1509.49 1504.30 1501.38 1500.14 1500.12 1501.02 1502.57 1504.62 1507.02 1509.69 1512.55 1515.56 1518.67 1521.85 1525.10 1528.38 1531.70 1535.04 1538.39 1541.76 1545.14 1548.52 1551.91 1551.91
    """

    fname, _ = _prepare_filename(fname, _File_Ext.ssp, "SSP")
    with open(fname, 'r') as f:
        nranges = int(_read_next_valid_line(f))
        range_line = _read_next_valid_line(f)
        ranges = _np.array([float(x) for x in _parse_line(range_line)])
        ranges_m = ranges * 1000 # Convert ranges from km to meters (as expected by create_env)

        if len(ranges) != nranges:
            raise ValueError(f"Expected {nranges} ranges, but found {len(ranges)}")

        # Read sound speed data - read all remaining lines as a matrix
        ssp_data = []
        line_num = 0
        for line in f:
            line_num += 1
            line = line.strip()
            if line:  # Skip empty lines
                values = [float(x) for x in line.split()]
                if len(values) != nranges:
                    raise ValueError(f"SSP line {line_num} has {len(values)} range values, expected {nranges}")
                ssp_data.append(values)

        ssp_array = _np.array(ssp_data)
        ndepths = ssp_array.shape[0]

        # Create depth indices (actual depths would normally come from associated .env file)
        if depths is None:
            depths = _np.arange(ndepths, dtype=float)

        if ndepths == 0 or len(depths) != ndepths:
            raise ValueError("Wrong number of depths found in sound speed data file"
                             f" (expected {ndepths}, found {ssp_array.shape[0]})")

        df = _pd.DataFrame(ssp_array, index=depths, columns=ranges_m)
        df.index.name = "depth"
        return df

def read_bty(fname: str) -> Tuple[NDArray[_np.float64], str]:
    """Read a bathymetry file used by Bellhop."""
    fname, _ = _prepare_filename(fname, _File_Ext.bty, "BTY")
    return read_ati_bty(fname)

def read_ati(fname: str) -> Tuple[NDArray[_np.float64], str]:
    """Read an altimetry file used by Bellhop."""
    fname, _ = _prepare_filename(fname, _File_Ext.ati, "ATI")
    return read_ati_bty(fname)

def read_ati_bty(fname: str) -> Tuple[NDArray[_np.float64], str]:
    """Read an altimetry (.ati) or bathymetry (.bty) file used by BELLHOP.

    This function reads BELLHOP's .bty files which define the bottom depth
    profile. The file format is:
    - Line 1: Interpolation type ('L' for linear, 'C' for curvilinear)
    - Line 2: Number of points
    - Line 3+: Range (km) and depth (m) pairs

    Parameters
    ----------
    fname : str
        Path to .bty file (with or without .bty extension)

    Returns
    -------
    numpy.ndarray
        Numpy array with [range, depth] pairs compatible with create_env()

    Notes
    -----
    The returned array can be assigned to env["depth"] for range-dependent bathymetry.

    **Examples:**

    >>> import bellhop as bh
    >>> bty,bty_interp = bh.read_bty("tests/MunkB_geo_rot/MunkB_geo_rot.bty")
    >>> env = bh.create_env()
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

    with open(fname, 'r') as f:
        # Read interpolation type (usually 'L' or 'C')
        interp_type = _read_next_valid_line(f).strip("'\"")
        npoints = int(_read_next_valid_line(f))
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
        return _np.column_stack([ranges_m, depths_array]), _Maps.depth_interp[interp_type]

def read_sbp(fname: str) -> NDArray[_np.float64]:
    """Read an source beam patterm (.sbp) file used by BELLHOP.

    The file format is:
    - Line 1: Number of points
    - Line 2+: Angle (deg) and power (dB) pairs

    Parameters
    ----------
    fname : str
        Path to .sbp file (with or without extension)

    Returns
    -------
    numpy.ndarray
        Numpy array with [angle, power] pairs
    """

    fname, _ = _prepare_filename(fname, _File_Ext.sbp, "SBP")
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

def read_brc(fname: str) -> NDArray[_np.float64]:
    """Read a BRC file and return array of reflection coefficients.

    See `read_refl_coeff` for documentation, but use this function for extension checkking."""
    fname, _ = _prepare_filename(fname, _File_Ext.brc, "BRC")
    return read_refl_coeff(fname)

def read_trc(fname: str) -> NDArray[_np.float64]:
    """Read a TRC file and return array of reflection coefficients.

    See `read_refl_coeff` for documentation, but use this function for extension checkking."""
    fname, _ = _prepare_filename(fname, _File_Ext.trc, "TRC")
    return read_refl_coeff(fname)

def read_refl_coeff(fname: str) -> NDArray[_np.float64]:
    """Read a reflection coefficient (.brc/.trc) file used by BELLHOP.

    This function reads BELLHOP's .brc files which define the reflection coefficient
    data. The file format is:
    - Line 1: Number of points
    - Line 2+: THETA(j)       RMAG(j)       RPHASE(j)

    Where:
    - THETA():  Angle (degrees)
    - RMAG():   Magnitude of reflection coefficient
    - RPHASE(): Phase of reflection coefficient (degrees)

    Parameters
    ----------
    fname : str
        Path to .brc/.trc file (extension required)

    Returns
    -------
    numpy.ndarray
        Numpy array with [theta, rmag, rphase] triplets compatible with create_env()

    Notes
    -----
    The returned array can be assigned to env["bottom_reflection_coefficient"] or env["surface_reflection_coefficient"] .

    Examples
    --------
    >>> import bellhop as bh
    >>> brc = bh.read_refl_coeff("tests/MunkB_geo_rot/MunkB_geo_rot.brc")
    >>> env = bh.create_env()
    >>> env["bottom_reflection_coefficient"] = brc
    >>> arrivals = bh.calculate_arrivals(env)

    **File format example:**

    ::

        3
        0.0   1.00  180.0
        45.0  0.95  175.0
        90.0  0.90  170.0
    """

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


def read_arrivals(fname: str) -> _pd.DataFrame:
    """Read Bellhop arrivals file and parse data into a high level data structure"""
    path = _ensure_file_exists(fname)
    with path.open('rt') as f:
        hdr = f.readline()
        if hdr.find('2D') >= 0:
            freq = _read_array(f, (float,))
            source_depth_info = _read_array(f, (int,), float)
            source_depth_count = source_depth_info[0]
            source_depth = source_depth_info[1:]
            assert source_depth_count == len(source_depth)
            receiver_depth_info = _read_array(f, (int,), float)
            receiver_depth_count = receiver_depth_info[0]
            receiver_depth = receiver_depth_info[1:]
            assert receiver_depth_count == len(receiver_depth)
            receiver_range_info = _read_array(f, (int,), float)
            receiver_range_count = receiver_range_info[0]
            receiver_range = receiver_range_info[1:]
            assert receiver_range_count == len(receiver_range)
#             else: # worry about 3D later
#                 freq, source_depth_count, receiver_depth_count, receiver_range_count = _read_array(hdr, (float, int, int, int))
#                 source_depth = _read_array(f, (float,)*source_depth_count)
#                 receiver_depth = _read_array(f, (float,)*receiver_depth_count)
#                 receiver_range = _read_array(f, (float,)*receiver_range_count)
        arrivals: List[_pd.DataFrame] = []
        for j in range(source_depth_count):
            f.readline()
            for k in range(receiver_depth_count):
                for m in range(receiver_range_count):
                    count = int(f.readline())
                    for n in range(count):
                        data = _read_array(f, (float, float, float, float, float, float, int, int))
                        arrivals.append(_pd.DataFrame({
                            'source_depth_ndx': [j],
                            'receiver_depth_ndx': [k],
                            'receiver_range_ndx': [m],
                            'source_depth': [source_depth[j]],
                            'receiver_depth': [receiver_depth[k]],
                            'receiver_range': [receiver_range[m]],
                            'arrival_number': [n],
                            # 'arrival_amplitude': [data[0]*_np.exp(1j * data[1]* _np.pi/180)],
                            'arrival_amplitude': [data[0] * _np.exp( -1j * (_np.deg2rad(data[1]) + freq[0] * 2 * _np.pi * (data[3] * 1j +  data[2])))],
                            'time_of_arrival': [data[2]],
                            'complex_time_of_arrival': [data[2] + 1j*data[3]],
                            'angle_of_departure': [data[4]],
                            'angle_of_arrival': [data[5]],
                            'surface_bounces': [data[6]],
                            'bottom_bounces': [data[7]]
                        }, index=[len(arrivals)+1]))
    return _pd.concat(arrivals)


def read_shd(fname: str) -> _pd.DataFrame:
    """Read Bellhop shd file and parse data into a high level data structure"""
    path = _ensure_file_exists(fname)
    with path.open('rb') as f:
        recl, = _unpack('i', f.read(4))
        # _title = str(f.read(80))
        f.seek(4*recl, 0)
        ptype = f.read(10).decode('utf8').strip()
        assert ptype == 'rectilin', 'Invalid file format (expecting ptype == "rectilin")'
        f.seek(8*recl, 0)
        nfreq, ntheta, nsx, nsy, nsd, nrd, nrr, atten = _unpack('iiiiiiif', f.read(32))
        assert nfreq == 1, 'Invalid file format (expecting nfreq == 1)'
        assert ntheta == 1, 'Invalid file format (expecting ntheta == 1)'
        assert nsd == 1, 'Invalid file format (expecting nsd == 1)'
        f.seek(32*recl, 0)
        pos_r_depth = _unpack('f'*nrd, f.read(4*nrd))
        f.seek(36*recl, 0)
        pos_r_range = _unpack('f'*nrr, f.read(4*nrr))
        pressure = _np.zeros((nrd, nrr), dtype=_np.complex128)
        for ird in range(nrd):
            recnum = 10 + ird
            f.seek(recnum*4*recl, 0)
            temp = _np.array(_unpack('f'*2*nrr, f.read(2*nrr*4)))
            pressure[ird,:] = temp[::2] + 1j*temp[1::2]
    return _pd.DataFrame(pressure, index=pos_r_depth, columns=pos_r_range)


def read_rays(fname: str) -> _pd.DataFrame:
    """Read Bellhop rays file and parse data into a high level data structure"""
    path = _ensure_file_exists(fname)
    with path.open('rt') as f:
        f.readline()
        f.readline()
        f.readline()
        f.readline()
        f.readline()
        f.readline()
        f.readline()
        rays = []
        while True:
            s = f.readline()
            if s is None or len(s.strip()) == 0:
                break
            a = float(s)
            pts, sb, bb = _read_array(f, (int, int, int))
            ray = _np.empty((pts, 2))
            for k in range(pts):
                ray[k,:] = _read_array(f, (float, float))
            rays.append(_pd.DataFrame({
                'angle_of_departure': [a],
                'surface_bounces': [sb],
                'bottom_bounces': [bb],
                'ray': [ray]
            }))
    return _pd.concat(rays)

def _ensure_file_exists(fname: str) -> Path:
    path = Path(fname)
    if not path.exists():
        raise RuntimeError(f"Bellhop did not generate expected output file: {path}")
    return path

def _read_array(f: IO[str], types: Tuple[Any, ...], dtype: type = str) -> Tuple[Any, ...]:
    """Wrapper around readline() to read in a 1D array of data"""
    p = f.readline().split()
    for j in range(len(p)):
        if len(types) > j:
            p[j] = types[j](p[j])
        else:
            p[j] = dtype(p[j])
    return tuple(p)
