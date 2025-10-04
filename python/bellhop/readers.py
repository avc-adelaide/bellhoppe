
from typing import Any, Dict, Optional, Tuple, Union
import numpy as _np
import pandas as _pd
from bellhop.constants import _Strings, _Maps
import bellhop.environment

def _read_next_valid_line(f: Any) -> str:
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

def _float(x: Any, scale: float = 1) -> Optional[float]:
    """Permissive floatenator"""
    return None if x is None else float(x) * scale

def _int(x: Any) -> Optional[int]:
    """Permissive floatenator"""
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

    **Limitations:**

    - External files (.ssp, .bty, .ati, .sbp) are noted but not automatically loaded
    - Some advanced BELLHOP features may not be fully supported
    - Assumes standard 2D BELLHOP format (not BELLHOP3D)
    """
    import os
    import re

    # Add .env extension if not present
    if fname.endswith('.env'):
        fname_base = fname[:-4]
    else:
        fname_base = fname
        fname = fname + '.env'

    if not os.path.exists(fname):
        raise FileNotFoundError(f"Environment file not found: {fname}")

    # Initialize environment with default values
    env = bellhop.environment.new()

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

    def _read_ssp_points(f: Any) -> Optional[Any]:
        """Read sound speed profile points until we find the bottom boundary line"""
        ssp_points: list[list[float]] = []

        # according to "EnvironmentalFile.htm":
        prev_speed = 1500.0
        prev_speed_shear = 0.0
        prev_density = 1000.0
        prev_att = 0.0
        prev_att_shear = 0.0
        while True:
            line = f.readline().strip()
            if not line:
                continue # skip empty

            # Check if this is a bottom boundary line (starts with quote)
            if line.startswith("'"):
                # This is the bottom boundary line, put it back
                f.seek(f.tell() - len(line.encode()) - 1)
                break

            # Parse SSP point and pad with 6x None to allow numerical indexing
            parts = _parse_line(line) + [None] * 6
            if parts[0] is None:
                continue # skip empty lines

            try:
                depth = float(parts[0])
                speed = float(parts[1] or prev_speed)
                speed_shear = float(parts[2] or prev_speed_shear)
                density = float(parts[3] or prev_density)
                att = float(parts[4] or prev_att)
                att_shear = float(parts[5] or prev_att_shear)
                ssp_points.append([depth, speed])
                # TODO: add extra terms to ssp_points array (but other fixes needed)
                prev_speed = speed
                prev_speed_shear = speed_shear
                prev_density = density
                prev_att = att
                prev_att_shear = att_shear
            except ValueError:
                # This might be the end of SSP or a different format
                # Put the line back and break
                f.seek(f.tell() - len(line.encode()) - 1)
                break

        return _np.array(ssp_points) if ssp_points else None

    def _invalid_option(name: str, opt: str) -> Any:
        raise ValueError(f"{name} option {opt!r} not available")

    # the proper start to the function:
    with open(fname, 'r') as f:
        # Line 1: Title
        title_line = _read_next_valid_line(f)
        env['name'] = _parse_quoted_string(title_line)

        # Line 2: Frequency
        freq_line = _read_next_valid_line(f)
        env['frequency'] = float(_parse_line(freq_line)[0])

        # Line 3: NMedia (should be 1 for BELLHOP)
        nmedia_line = _read_next_valid_line(f)
        nmedia = int(_parse_line(nmedia_line)[0])
        if nmedia != 1:
            raise ValueError(f"BELLHOP only supports 1 medium, found {nmedia}")

        # Line 4: Top boundary options
        topopt_line = _read_next_valid_line(f)
        topopt = _parse_quoted_string(topopt_line)

        # Parse SSP interpolation type from first character
        opt = topopt[0]
        env["soundspeed_interp"] = _Maps.interp.get(opt) or _invalid_option("Interpolation",opt)

        # Top boundary condition
        opt = topopt[1]
        env["surface_boundary_condition"] = _Maps.boundcond.get(opt) or _invalid_option("Top boundary condition",opt)

        # Attenuation units
        opt = topopt[2]
        env["attenuation_units"] = _Maps.attunits.get(opt) or _invalid_option("Attenuation units",opt)

        # Volume attenuation
        if len(topopt) > 3:
            opt = topopt[3]
        else:
            opt = " "
        env["volume_attenuation"] = _Maps.volatt.get(opt) or _invalid_option("Volume attenuation",opt)

        # Altimetry
        if len(topopt) > 4:
            opt = topopt[4]
            env["_altimetry"] = _Maps.surface.get(opt) or _invalid_option("Altimetry",opt)
            if env["_altimetry"] == _Strings.from_file:
                env["surface"], env["surface_interp"] = read_ati(fname_base)

        # Single beam
        if len(topopt) > 5:
            opt = topopt[5]
            env["_single_beam"] = _Maps.single_beam.get(opt) or _invalid_option("Single beam",opt)

        if env["volume_attenuation"] == _Strings.francois_garrison:
            fg_spec_line = _read_next_valid_line(f)
            fg_parts = _parse_line(fg_spec_line)
            env["fg_salinity"] = float(fg_parts[0])
            env["fg_temperature"] = float(fg_parts[1])
            env["fg_pH"] = float(fg_parts[2])
            env["fg_depth"] = float(fg_parts[3])


        if env["surface_boundary_condition"] == _Strings.acousto_elastic:

            surface_props_line = _read_next_valid_line(f)
            surface_props = _parse_line(surface_props_line) + [None] * 6

            env['surface_depth'] = _float(surface_props[0])
            env['surface_soundspeed'] = _float(surface_props[1])
            env['surface_soundspeed_shear'] = _float(surface_props[2])
            env['surface_density'] = _float(surface_props[3], scale=1000)  # convert from g/cm³ to kg/m³
            env['surface_absorption'] = _float(surface_props[4])
            env['surface_absorption_shear'] = _float(surface_props[5])

        # SSP depth specification (format: npts sigma_z max_depth)
        ssp_spec_line = _read_next_valid_line(f)
        ssp_parts = _parse_line(ssp_spec_line) + [None] * 3
        env['depth_npts'] = int(ssp_parts[0] or 0)
        env['depth_sigmaz'] = _float(ssp_parts[1])
        env['depth_max'] = _float(ssp_parts[2])
        env['depth'] = _float(ssp_parts[2])

        # Read SSP points
        ssp_points = _read_ssp_points(f)
        if ssp_points is not None and len(ssp_points) > 0:
            if len(ssp_points) == 1:
                # Single sound speed value
                env['soundspeed'] = ssp_points[0, 1]
            else:
                # Multiple points - depth, sound speed pairs
                env['soundspeed'] = ssp_points
        env['_ssp_env'] = ssp_points

        # Bottom boundary options
        bottom_line = _read_next_valid_line(f)
        bottom_parts = _parse_line(bottom_line)
        botopt = _parse_quoted_string(bottom_parts[0])
        opt = botopt[0]
        env["bottom_boundary_condition"] = _Maps.boundcond.get(opt) or _invalid_option("Bottom boundary condition",opt)

        if len(botopt) > 1:
            opt = botopt[1]
            env["_bathymetry"] = _Maps.bottom.get(opt) or _invalid_option("Bathymetry",opt)
            if env["_bathymetry"] == _Strings.from_file:
                bty,interp_bty = read_bty(fname_base)
                env["depth"] = bty
                env["bottom_interp"] = interp_bty

        if len(bottom_parts) >= 2:
            env['bottom_roughness'] = float(bottom_parts[1])
        if len(bottom_parts) >= 3:
            env['bottom_beta'] = float(bottom_parts[2])
            env['bottom_transition_freq'] = float(bottom_parts[3])

        # Bottom properties (depth, sound_speed, density, absorption)
        if env["bottom_boundary_condition"] == _Strings.acousto_elastic:

            bottom_props_line = _read_next_valid_line(f)
            bottom_props = _parse_line(bottom_props_line)

            if len(bottom_props) > 1:
                env['bottom_soundspeed'] = float(bottom_props[1])
            if len(bottom_props) > 2:
                env['bottom_soundspeed_shear'] = float(bottom_props[2])
            if len(bottom_props) > 3:
                env['bottom_density'] = float(bottom_props[3]) * 1000  # convert from g/cm³ to kg/m³
            if len(bottom_props) > 4:
                env['bottom_absorption'] = float(bottom_props[4])
            if len(bottom_props) > 5:
                env['bottom_absorption_shear'] = float(bottom_props[5])

        # Source & receiver depths
        env['source_depth'], env['source_ndepth'] = _parse_vector(f)
        env['receiver_depth'], env['receiver_ndepth'] = _parse_vector(f)

        # Receiver ranges (in km, need to convert to m)
        receiver_ranges, env['receiver_nrange'] = _parse_vector(f)
        env['receiver_range'] = receiver_ranges * 1000  # convert km to m

        # Task/run type (e.g., 'R', 'C', etc.)
        task_line = _read_next_valid_line(f)
        task_code = _parse_quoted_string(task_line)
        env['task'] = _Maps.task.get(task_code[0])
        if len(task_code) > 1:
            env['beam_type'] = _Maps.beam.get(task_code[1])
        if len(task_code) > 2:
            env['_sbp_file'] = _Maps.sbp.get(task_code[2])
        if len(task_code) > 3:
            env['source_type'] = _Maps.source.get(task_code[3])
        if len(task_code) > 4:
            env['grid'] = _Maps.grid.get(task_code[4])

        # Check for source directionality (indicated by * in task code)
        if env["_sbp_file"] == _Strings.from_file:
            env["source_directionality"] = read_sbp(fname_base)

        # Number of beams
        beam_num_line = _read_next_valid_line(f)
        beam_num_parts = _parse_line(beam_num_line) + [None] * 1
        env['beam_num'] = int(beam_num_parts[0] or 0)
        env['single_beam_index'] = _int(beam_num_parts[1])

        # Beam angles (beam_angle_min, beam_angle_max)
        angles_line = _read_next_valid_line(f)
        angle_parts = _parse_line(angles_line) + [None] * 2
        env['beam_angle_min'] = _float(angle_parts[0])
        env['beam_angle_max'] = _float(angle_parts[1])

        # Ray tracing limits (step, max_depth, max_range) - last line
        limits_line = _read_next_valid_line(f)
        limits_parts = _parse_line(limits_line)
        env['step_size'] = float(limits_parts[0])
        env['box_depth'] = float(limits_parts[1])
        env['box_range'] = 1000*float(limits_parts[2])

    return env

def read_ssp(fname: str) -> Union[Any, _pd.DataFrame]:
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
    import os

    # Add .ssp extension if not present
    if not fname.endswith('.ssp'):
        fname = fname + '.ssp'

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
            ndepths = ssp_array.shape[0]
            depths = _np.arange(ndepths, dtype=float)

            # Create DataFrame with ranges as columns and depths as index
            # ssp_array is [ndepths, nprofiles] which is the correct orientation
            return _pd.DataFrame(ssp_array, index=depths, columns=ranges_m)

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
