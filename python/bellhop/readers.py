
import numpy as _np
import pandas as _pd
from bellhop.constants import _Strings, _Maps
import bellhop.environment

def read_env2d(fname):
    """Read a 2D underwater environment from a BELLHOP .env file.

    This function parses a BELLHOP .env file and returns a Python data structure
    that is compatible with create_env2d(). This enables round-trip testing and
    compatibility between file-based and programmatic environment definitions.

    :param fname: path to .env file (with or without .env extension)

    :returns: environment dictionary compatible with create_env2d()

    The environment dictionary used in this code contains a large
    number of parameters, documented here to keep the code later more concise:

    ENV parameters
    ---------------

    :name: environment title/name
    :type: '2D' (fixed for 2D environments)
    :frequency: acoustic frequency in Hz
    :soundspeed: sound speed profile (scalar for constant, array for depth-dependent)
    :soundspeed_interp: interpolation method ('linear', 'spline', 'quadrilateral')
    :bottom_soundspeed: bottom sediment sound speed in m/s
    :bottom_soundspeed_shear: bottom sediment sound speed in m/s
    :bottom_density: bottom sediment density in kg/m³
    :bottom_absorption: bottom sediment absorption in dB/wavelength
    :bottom_absorption_shear: bottom sediment absorption in dB/wavelength
    :bottom_roughness: bottom roughness RMS in meters
    :surface: surface altimetry profile (None if flat surface)
    :surface_interp: surface interpolation method ('linear', 'curvilinear')
    :surface_boundary_condition: ('vacuum', 'acousto-elastic', 'rigid', 'from-file')
    :volume_attenuation: ('none', 'thorp', 'francois-garrison', 'biological')
    :attenuation_units: ('nepers per meter', 'frequency dependent', 'dB per meter', 'frequency scaled dB per meter', 'dB per wavelength', 'quality factor', 'loss parameter')
    :tx_depth: transmitter depth(s) in meters
    :tx_directionality: transmitter beam pattern (None if omnidirectional)
    :rx_depth: receiver depth(s) in meters
    :rx_range: receiver range(s) in meters
    :depth: maximum water depth in meters
    :depth_interp: bathymetry interpolation method ('linear', 'curvilinear')
    :beam_angle_min: minimum beam angle in degrees
    :beam_angle_max: maximum beam angle in degrees
    :beam_num: number of beams (0 for automatic)
    :step_size: (maximum) step size to trace rays in meters (0 for automatic)
    :box_depth: box extent to trace rays in meters (auto-calculated based on max depth data if not specified)
    :box_range: box extent to trace rays in meters (auto-calculated based on max receiver range if not specified)
    :tx_type: point (default) or line
    :beam_type: todo
    :grid: rectilinear or irregular

    **Supported ENV file formats:**

    - Standard BELLHOP format with various boundary conditions
    - Constant or depth-dependent sound speed profiles
    - Compressed vector notation (e.g., "0.0 5000.0 /" for linearly spaced values)
    - Comments (lines with ! are handled correctly)
    - Different top/bottom boundary options (halfspace, file-based, etc.)

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
    if not fname.endswith('.env'):
        fname = fname + '.env'

    if not os.path.exists(fname):
        raise FileNotFoundError(f"Environment file not found: {fname}")

    # Initialize environment with default values
    env = bellhop.environment.new()

    def _parse_quoted_string(line):
        """Extract string from within quotes

        Sometimes (why??) the leading quote was being stripped, so we also try to catch
        this case with the regexp, stripping only a trailing '.
        """
        mtch = re.search(r"'([^']*)'", line)
        mtch2 = re.search(r"([^']*)'$", line)
        return mtch.group(1) if mtch else mtch2.group(1) if mtch2 else line.strip()

    def _parse_line(line):
        """Parse a line, removing comments and whitespace"""
        # Remove comments (everything after !)
        if '!' in line:
            line = line[:line.index('!')].strip()
        return line.strip()

    def _parse_vector(f, dtype=float):
        """Parse a vector that starts with count then values, ending with '/'"""
        line = f.readline().strip()
        if not line:
            raise ValueError("Unexpected end of file while reading vector")

        # First line is the count
        linecount = int(_parse_line(line))

        # Second line has the values
        values_line = f.readline().strip()
        values_line = _parse_line(values_line)

        # Split by '/' and take only the first part (before the '/')
        if '/' in values_line:
            values_line = values_line.split('/')[0].strip()

        parts = values_line.split()
        values = [dtype(p) for p in parts]

        # Note that we do not try to interpolate here, since Bellhop has its own routines
        return _np.array(values), linecount

    def _read_ssp_points(f):
        """Read sound speed profile points until we find the bottom boundary line"""
        ssp_points = []

        while True:
            line = f.readline().strip()
            if not line:
                break

            # Check if this is a bottom boundary line (starts with quote)
            if line.startswith("'"):
                # This is the bottom boundary line, put it back
                f.seek(f.tell() - len(line.encode()) - 1)
                break

            # Parse SSP point
            line = _parse_line(line)
            if line.endswith('/'):
                line = line[:-1].strip()

            parts = line.split()
            if len(parts) >= 2:
                try:
                    depth = float(parts[0])
                    speed = float(parts[1])
                    ssp_points.append([depth, speed])
                except ValueError:
                    # This might be the end of SSP or a different format
                    # Put the line back and break
                    f.seek(f.tell() - len(line.encode()) - 1)
                    break

        return _np.array(ssp_points) if ssp_points else None

    with open(fname, 'r') as f:
        # Line 1: Title
        title_line = f.readline().strip()
        env['name'] = _parse_quoted_string(title_line)

        # Line 2: Frequency
        freq_line = f.readline().strip()
        env['frequency'] = float(_parse_line(freq_line))

        # Line 3: NMedia (should be 1 for BELLHOP)
        nmedia_line = f.readline().strip()
        nmedia = int(_parse_line(nmedia_line))
        if nmedia != 1:
            raise ValueError(f"BELLHOP only supports 1 medium, found {nmedia}")

        # Line 4: Top boundary options
        topopt_line = f.readline().strip()
        topopt = _parse_quoted_string(topopt_line)

        # Parse SSP interpolation type from first character
        def _invalid(opt):
            raise ValueError(f"Interpolation option {opt!r} not available")
        opt = topopt[0]
        env["soundspeed_interp"] = _Maps.interp.get(opt) or _invalid(opt)

        # Top boundary condition
        def _invalid(opt):
            raise ValueError(f"Top boundary condition option {opt!r} not available")
        opt = topopt[1]
        env["surface_boundary_condition"] = _Maps.boundcond.get(opt) or _invalid(opt)

        # Attenuation units
        def _invalid(opt):
            raise ValueError(f"Attenuation units option {opt!r} not available")
        opt = topopt[2]
        env["attenuation_units"] = _Maps.attunits.get(opt) or _invalid(opt)

        # Volume attenuation
        def _invalid(opt):
            raise ValueError(f"Volume attenuation option {opt!r} not available")
        env["volume_attenuation"] = 'none'
        if len(topopt) > 3:
            opt = topopt[3]
        else:
            opt = ""
        env["volume_attenuation"] = _Maps.volatt.get(opt) or _invalid(opt)

        if env["volume_attenuation"] == _Strings.francois_garrison:
            fg_spec_line = f.readline().strip()
            fg_parts = _parse_line(fg_spec_line).split()
            env["fg_salinity"] = float(fg_parts[0])
            env["fg_temperature"] = float(fg_parts[1])
            env["fg_pH"] = float(fg_parts[2])
            env["fg_depth"] = float(fg_parts[3])


        if 'A' in topopt:
            # Read halfspace parameters line
            f.readline().strip()
            # This line contains: depth, alphaR, betaR, rho, alphaI, betaI
            # We skip this for now as it's not part of the standard env structure

        # Check for surface altimetry (indicated by * in topopt)
        if '*' in topopt:
            # Surface altimetry file exists - would need to read .ati file
            # For now, just note that surface is present
            env['surface'] = _np.array([[0, 0], [1000, 0]])  # placeholder

        # Line 5 or 6: SSP depth specification (format: npts sigma_z max_depth)
        ssp_spec_line = f.readline().strip()
        ssp_parts = _parse_line(ssp_spec_line).split()
        env['depth_npts'] = int(ssp_parts[0])
        if len(ssp_parts) > 1:
            env['depth_sigmaz'] = float(ssp_parts[1])
        if len(ssp_parts) > 2:
            env['depth_max'] = float(ssp_parts[2])
            env['depth'] = float(ssp_parts[2])

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
        print("  ")
        print(fname)

        line = f.readline()
        bottom_line = line.strip()
        bottom_parts = _parse_line(bottom_line).split()
        botopt = _parse_quoted_string(bottom_parts[0])
        def _invalid(opt):
            raise ValueError(f"Bottom boundary condition option {opt!r} not available")
        opt = botopt[0]
        env["bottom_boundary_condition"] = _Maps.boundcond.get(opt) or _invalid(opt)

        if len(botopt) > 1:
            opt = botopt[1]
            env["_bottom_bathymetry"] = _Maps.bottom.get(opt) or _invalid(opt)
            if env["_bottom_bathymetry"] == _Strings.from_file:
                print("TODO: automatically read bty file")
            else:
                pass # nothing needs to be done

        if len(bottom_parts) >= 2:
            env['bottom_roughness'] = float(bottom_parts[1])
        if len(bottom_parts) >= 3:
            env['bottom_beta'] = float(bottom_parts[2])
            env['bottom_transition_freq'] = float(bottom_parts[3])

        # Bottom properties (depth, sound_speed, density, absorption)
        bottom_props_line = f.readline().strip()
        bottom_props_line = _parse_line(bottom_props_line)
        if bottom_props_line.endswith('/'):
            bottom_props_line = bottom_props_line[:-1].strip()

        bottom_props = bottom_props_line.split()
        # fortran sources say: "z, alphaR, betaR, rhoR, alphaI, betaI"
        # docs say:
        #       Syntax:
        #
        #       ZB  CPB  CSB  RHOB  APB  ASB
        #
        #       Description:
        #
        #       ZB:   Depth (m).
        #       CPB:  Bottom P-wave speed (m/s).
        #       CSB:  Bottom S-wave speed (m/s).
        #       RHOB: Bottom density (g/cm3).
        #       APB:  Bottom P-wave attenuation. (units as given by TOPOPT(3:3) )
        #       ASB:  Bottom S-wave attenuation. (  "   "    "    "   "   "     )
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

        # Source depths
        tx_depths, env['tx_ndepth'] = _parse_vector(f)
        if len(tx_depths) == 1:
            env['tx_depth'] = tx_depths[0]
        else:
            env['tx_depth'] = tx_depths

        # Receiver depths
        rx_depths, env['rx_ndepth'] = _parse_vector(f)
        if len(rx_depths) == 1:
            env['rx_depth'] = rx_depths[0]
        else:
            env['rx_depth'] = rx_depths

        # Receiver ranges (in km, need to convert to m)
        rx_ranges, env['rx_nrange'] = _parse_vector(f)
        env['rx_range'] = rx_ranges * 1000  # convert km to m

        # Task/run type (e.g., 'R', 'C', etc.)
        task_line = f.readline().strip()
        task_code = _parse_quoted_string(task_line)
        env['task'] = task_code[0]
        if len(task_code) > 1:
            env['beam_type'] = _Maps.beam.get(task_code[1])
        if len(task_code) > 3:
            env['tx_type'] = _Maps.source.get(task_code[3])
        if len(task_code) > 4:
            env['grid'] = _Maps.grid.get(task_code[4])

        # Check for source directionality (indicated by * in task code)
        if '*' in task_code:
            # Source directionality file exists - would need to read .sbp file
            # For now, just note that directionality is present
            env['tx_directionality'] = _np.array([[0, 0]])  # placeholder

        # Number of beams
        beam_num_line = f.readline().strip()
        env['beam_num'] = int(_parse_line(beam_num_line))

        # Beam angles (beam_angle_min, beam_angle_max)
        angles_line = f.readline().strip()
        angles_line = _parse_line(angles_line)
        if angles_line.endswith('/'):
            angles_line = angles_line[:-1].strip()

        angle_parts = angles_line.split()
        if len(angle_parts) >= 2:
            env['beam_angle_min'] = float(angle_parts[0])
            env['beam_angle_max'] = float(angle_parts[1])

        # Ray tracing limits (step, max_depth, max_range) - last line
        limits_line = f.readline().strip()
        limits_parse = _parse_line(limits_line)
        limits_parts = limits_parse.split()
        env['step_size'] = float(limits_parts[0])
        env['box_depth'] = float(limits_parts[1])
        env['box_range'] = 1000*float(limits_parts[2])

    return env

def read_ssp(fname):
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
        nprofiles = int(f.readline().strip())

        # Read range coordinates (in km)
        range_line = f.readline().strip()
        ranges = _np.array([float(x) for x in range_line.split()])

        if len(ranges) != nprofiles:
            raise ValueError(f"Expected {nprofiles} range profiles, but found {len(ranges)} ranges")

        # Read sound speed data - read all remaining lines as a matrix
        ssp_data = []
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                values = [float(x) for x in line.split()]
                if len(values) == nprofiles:
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

def read_bty(fname):
    """Read a bathymetry (.bty) file used by BELLHOP.

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

    # Add .bty extension if not present
    if not fname.endswith('.bty'):
        fname = fname + '.bty'

    if not os.path.exists(fname):
        raise FileNotFoundError(f"BTY file not found: {fname}")

    with open(fname, 'r') as f:
        # Read interpolation type (usually 'L' or 'C')
        interp_type = f.readline().strip().strip("'\"")

        # Read number of points
        npoints = int(f.readline().strip())

        # Read range,depth pairs
        ranges = []
        depths = []

        for i in range(npoints):
            line = f.readline().strip()
            if line:  # Skip empty lines
                parts = line.split()
                if len(parts) >= 2:
                    ranges.append(float(parts[0]))  # Range in km
                    depths.append(float(parts[1]))  # Depth in m

        if len(ranges) != npoints:
            raise ValueError(f"Expected {npoints} bathymetry points, but found {len(ranges)}")

        # Convert ranges from km to m for consistency with bellhop env structure
        ranges_m = _np.array(ranges) * 1000
        depths_array = _np.array(depths)

        # Return as [range, depth] pairs
        return _np.column_stack([ranges_m, depths_array]), _Maps.bty_interp[interp_type]

def read_refl_coeff(fname):
    """Read a reflection coefficient (.brc) file used by BELLHOP.

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

    The returned array can be assigned to env["bottom_reflection_coefficient"] or env["top_reflection_coefficient"] .

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
        npoints = int(f.readline().strip())

        # Read range,depth pairs
        theta = []
        rmagn = []
        rphas = []

        for i in range(npoints):
            line = f.readline().strip()
            if line:  # Skip empty lines
                parts = line.split()
                if len(parts) == 3:
                    theta.append(float(parts[0]))
                    rmagn.append(float(parts[1]))
                    rphas.append(float(parts[2]))

        if len(theta) != npoints:
            raise ValueError(f"Expected {npoints} bathymetry points, but found {len(theta)}")

        # Return as [range, depth] pairs
        return _np.column_stack([theta, rmagn, rphas])
