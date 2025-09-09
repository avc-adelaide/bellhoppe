##############################################################################
#
# Copyright (c) 2025-, Will Robertson
# Copyright (c) 2018-2025, Mandar Chitre
#
# This file was originally part of arlpy, released under Simplified BSD License.
# It has been relicensed in this repository to be compatible with the Bellhop licence (GPL).
#
##############################################################################

"""Underwater acoustic propagation modeling toolbox.

This toolbox currently uses the Bellhop acoustic propagation model. For this model
to work, the `acoustic toolbox <https://oalib-acoustics.org/>`_
must be installed on your computer and `bellhop.exe` should be in your PATH.

.. sidebar:: Sample Jupyter notebook

    For usage examples of this toolbox, see `Bellhop notebook <_static/bellhop.html>`_.
"""

import os as _os
import re as _re
import subprocess as _proc
import numpy as _np
from scipy import interpolate as _interp
import pandas as _pd
from tempfile import mkstemp as _mkstemp
from struct import unpack as _unpack
from sys import float_info as _fi
import bellhop.plot as _plt
import matplotlib.pyplot as _pyplt
import matplotlib.cm as _cm
import bokeh as _bokeh

# constants
linear = 'linear'
spline = 'spline'
curvilinear = 'curvilinear'
arrivals = 'arrivals'
eigenrays = 'eigenrays'
rays = 'rays'
coherent = 'coherent'
incoherent = 'incoherent'
semicoherent = 'semicoherent'

# models (in order of preference)
_models = []

def create_env2d(**kv):
    """Create a new 2D underwater environment.

    A basic environment is created with default values. To see all the parameters
    available and their default values:

    >>> import arlpy.uwapm as pm
    >>> env = pm.create_env2d()
    >>> pm.print_env(env)

    The environment parameters may be changed by passing keyword arguments
    or modified later using a dictionary notation:

    >>> import arlpy.uwapm as pm
    >>> env = pm.create_env2d(depth=40, soundspeed=1540)
    >>> pm.print_env(env)
    >>> env['depth'] = 25
    >>> env['bottom_soundspeed'] = 1800
    >>> pm.print_env(env)

    The default environment has a constant sound speed. A depth dependent sound speed
    profile be provided as a Nx2 array of (depth, sound speed):

    >>> import arlpy.uwapm as pm
    >>> env = pm.create_env2d(depth=20, soundspeed=[[0,1540], [5,1535], [10,1535], [20,1530]])

    A range-and-depth dependent sound speed profile can be provided as a Pandas frame:

    >>> import arlpy.uwapm as pm
    >>> import pandas as pd
    >>> ssp2 = pd.DataFrame({
              0: [1540, 1530, 1532, 1533],     # profile at 0 m range
            100: [1540, 1535, 1530, 1533],     # profile at 100 m range
            200: [1530, 1520, 1522, 1525] },   # profile at 200 m range
            index=[0, 10, 20, 30])             # depths of the profile entries in m
    >>> env = pm.create_env2d(depth=20, soundspeed=ssp2)

    The default environment has a constant water depth. A range dependent bathymetry
    can be provided as a Nx2 array of (range, water depth):

    >>> import arlpy.uwapm as pm
    >>> env = pm.create_env2d(depth=[[0,20], [300,10], [500,18], [1000,15]])
    """
    env = {
        'name': 'arlpy',
        'type': '2D',                   # 2D/3D
        'frequency': 25000,             # Hz
        'soundspeed': 1500,             # m/s
        'soundspeed_interp': spline,    # spline/linear
        'bottom_soundspeed': 1600,      # m/s
        'bottom_density': 1600,         # kg/m^3
        'bottom_absorption': 0.1,       # dB/wavelength
        'bottom_roughness': 0,          # m (rms)
        'surface': None,                # surface profile
        'surface_interp': linear,       # curvilinear/linear
        'tx_depth': 5,                  # m
        'tx_directionality': None,      # [(deg, dB)...]
        'rx_depth': 10,                 # m
        'rx_range': 1000,               # m
        'depth': 25,                    # m
        'depth_interp': linear,         # curvilinear/linear
        'min_angle': -80,               # deg
        'max_angle': 80,                # deg
        'nbeams': 0                     # number of beams (0 = auto)
    }
    for k, v in kv.items():
        if k not in env.keys():
            raise KeyError('Unknown key: '+k)
        env[k] = _np.asarray(v, dtype=_np.float64) if not isinstance(v, _pd.DataFrame) and _np.size(v) > 1 else v
    env = check_env2d(env)
    return env

def read_env2d(fname):
    """Read a 2D underwater environment from a BELLHOP .env file.

    This function parses a BELLHOP .env file and returns a Python data structure
    that is compatible with create_env2d(). This enables round-trip testing and
    compatibility between file-based and programmatic environment definitions.

    :param fname: path to .env file (with or without .env extension)
    :returns: environment dictionary compatible with create_env2d()

    The returned environment dictionary contains the following keys:

    - name: environment title/name
    - type: '2D' (fixed for 2D environments)
    - frequency: acoustic frequency in Hz
    - soundspeed: sound speed profile (scalar for constant, array for depth-dependent)
    - soundspeed_interp: interpolation method ('linear', 'spline', 'quadrilateral')
    - bottom_soundspeed: bottom sediment sound speed in m/s
    - bottom_density: bottom sediment density in kg/m³
    - bottom_absorption: bottom sediment absorption in dB/wavelength
    - bottom_roughness: bottom roughness RMS in meters
    - surface: surface altimetry profile (None if flat surface)
    - surface_interp: surface interpolation method ('linear', 'curvilinear')
    - tx_depth: transmitter depth(s) in meters
    - tx_directionality: transmitter beam pattern (None if omnidirectional)
    - rx_depth: receiver depth(s) in meters
    - rx_range: receiver range(s) in meters
    - depth: maximum water depth in meters
    - depth_interp: bathymetry interpolation method ('linear', 'curvilinear')
    - min_angle: minimum beam angle in degrees
    - max_angle: maximum beam angle in degrees
    - nbeams: number of beams (0 for automatic)

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

    # Initialize environment with default values from create_env2d
    env = {
        'name': 'arlpy',
        'type': '2D',
        'frequency': 25000,
        'soundspeed': 1500,
        'soundspeed_interp': spline,
        'bottom_soundspeed': 1600,
        'bottom_density': 1600,
        'bottom_absorption': 0.1,
        'bottom_roughness': 0,
        'surface': None,
        'surface_interp': linear,
        'tx_depth': 5,
        'tx_directionality': None,
        'rx_depth': 10,
        'rx_range': 1000,
        'depth': 25,
        'depth_interp': linear,
        'min_angle': -80,
        'max_angle': 80,
        'nbeams': 0
    }

    def _parse_quoted_string(line):
        """Extract string from within quotes"""
        match = re.search(r"'([^']*)'", line)
        return match.group(1) if match else line.strip()

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
        count = int(_parse_line(line))

        # Second line has the values
        values_line = f.readline().strip()
        values_line = _parse_line(values_line)

        # Split by '/' and take only the first part (before the '/')
        if '/' in values_line:
            values_line = values_line.split('/')[0].strip()

        parts = values_line.split()
        values = [dtype(p) for p in parts]

        # Handle compressed notation: if we have exactly 2 values and count > 2, it's start and end
        if len(values) == 2 and count > 2:
            start, end = values
            # Generate linearly spaced values
            return _np.linspace(start, end, count)
        else:
            return _np.array(values)

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
        if topopt[0] == 'S':
            env['soundspeed_interp'] = spline
        elif topopt[0] == 'C':
            env['soundspeed_interp'] = linear
        elif topopt[0] == 'Q':
            env['soundspeed_interp'] = 'quadrilateral'  # 2D SSP from file
        else:
            env['soundspeed_interp'] = linear  # default

        # Check for surface altimetry (indicated by * in topopt)
        if '*' in topopt:
            # Surface altimetry file exists - would need to read .ati file
            # For now, just note that surface is present
            env['surface'] = _np.array([[0, 0], [1000, 0]])  # placeholder

        # Check if top boundary has halfspace parameters (indicated by 'A' option)
        if 'A' in topopt:
            # Read halfspace parameters line
            halfspace_line = f.readline().strip()
            # This line contains: depth, alphaR, betaR, rho, alphaI, betaI
            # We skip this for now as it's not part of the standard env structure

        # Line 5 or 6: SSP depth specification (format: npts sigma_z max_depth)
        ssp_spec_line = f.readline().strip()
        ssp_parts = _parse_line(ssp_spec_line).split()
        if len(ssp_parts) >= 3:
            max_depth = float(ssp_parts[2])
            env['depth'] = max_depth

        # Read SSP points
        ssp_points = _read_ssp_points(f)
        if ssp_points is not None and len(ssp_points) > 0:
            if len(ssp_points) == 1:
                # Single sound speed value
                env['soundspeed'] = ssp_points[0, 1]
            else:
                # Multiple points - depth, sound speed pairs
                env['soundspeed'] = ssp_points

        # Bottom boundary options
        bottom_line = f.readline().strip()
        bottom_parts = _parse_line(bottom_line).split()
        if len(bottom_parts) >= 2:
            bottom_opt = _parse_quoted_string(bottom_parts[0])
            env['bottom_roughness'] = float(bottom_parts[1])

            # Check for bathymetry file (indicated by * in bottom option)
            if '*' in bottom_opt:
                # Bathymetry file exists - would need to read .bty file
                # For now, note that depth is range-dependent
                pass

        # Bottom properties (depth, sound_speed, density, absorption)
        bottom_props_line = f.readline().strip()
        bottom_props_line = _parse_line(bottom_props_line)
        if bottom_props_line.endswith('/'):
            bottom_props_line = bottom_props_line[:-1].strip()

        bottom_props = bottom_props_line.split()
        if len(bottom_props) >= 5:
            env['bottom_soundspeed'] = float(bottom_props[1])
            # Skip shear speed (bottom_props[2])
            env['bottom_density'] = float(bottom_props[3]) * 1000  # convert from g/cm³ to kg/m³
            env['bottom_absorption'] = float(bottom_props[4])

        # Source depths
        tx_depths = _parse_vector(f)
        if len(tx_depths) == 1:
            env['tx_depth'] = tx_depths[0]
        else:
            env['tx_depth'] = tx_depths

        # Receiver depths
        rx_depths = _parse_vector(f)
        if len(rx_depths) == 1:
            env['rx_depth'] = rx_depths[0]
        else:
            env['rx_depth'] = rx_depths

        # Receiver ranges (in km, need to convert to m)
        rx_ranges = _parse_vector(f)
        env['rx_range'] = rx_ranges * 1000  # convert km to m

        # Task/run type (e.g., 'R', 'C', etc.)
        task_line = f.readline().strip()
        task_code = _parse_quoted_string(task_line)

        # Check for source directionality (indicated by * in task code)
        if '*' in task_code:
            # Source directionality file exists - would need to read .sbp file
            # For now, just note that directionality is present
            env['tx_directionality'] = _np.array([[0, 0]])  # placeholder

        # Number of beams
        nbeams_line = f.readline().strip()
        env['nbeams'] = int(_parse_line(nbeams_line))

        # Beam angles (min_angle, max_angle)
        angles_line = f.readline().strip()
        angles_line = _parse_line(angles_line)
        if angles_line.endswith('/'):
            angles_line = angles_line[:-1].strip()

        angle_parts = angles_line.split()
        if len(angle_parts) >= 2:
            env['min_angle'] = float(angle_parts[0])
            env['max_angle'] = float(angle_parts[1])

        # Ray tracing limits (step, max_depth, max_range) - last line
        limits_line = f.readline().strip()
        # We don't store these in the env structure as they're computational parameters

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
            raise ValueError(f"No sound speed data found in file")

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
    >>> bty = bh.read_bty("tests/MunkB_geo_rot/MunkB_geo_rot.bty")
    >>> env = bh.create_env2d()
    >>> env["depth"] = bty
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
        return _np.column_stack([ranges_m, depths_array])

def check_env2d(env):
    """Check the validity of a 2D underwater environment definition.

    :param env: environment definition

    Exceptions are thrown with appropriate error messages if the environment is invalid.

    >>> import arlpy.uwapm as pm
    >>> env = pm.create_env2d()
    >>> check_env2d(env)
    """
    try:
        assert env['type'] == '2D', 'Not a 2D environment'
        max_range = _np.max(env['rx_range'])
        if env['surface'] is not None:
            assert _np.size(env['surface']) > 1, 'surface must be an Nx2 array'
            assert env['surface'].ndim == 2, 'surface must be a scalar or an Nx2 array'
            assert env['surface'].shape[1] == 2, 'surface must be a scalar or an Nx2 array'
            assert env['surface'][0,0] <= 0, 'First range in surface array must be 0 m'
            assert env['surface'][-1,0] >= max_range, 'Last range in surface array must be beyond maximum range: '+str(max_range)+' m'
            assert _np.all(_np.diff(env['surface'][:,0]) > 0), 'surface array must be strictly monotonic in range'
            assert env['surface_interp'] == curvilinear or env['surface_interp'] == linear, 'Invalid interpolation type: '+str(env['surface_interp'])
        if _np.size(env['depth']) > 1:
            assert env['depth'].ndim == 2, 'depth must be a scalar or an Nx2 array'
            assert env['depth'].shape[1] == 2, 'depth must be a scalar or an Nx2 array'
            assert env['depth'][0,0] <= 0, 'First range in depth array must be 0 m'
            assert env['depth'][-1,0] >= max_range, 'Last range in depth array must be beyond maximum range: '+str(max_range)+' m'
            assert _np.all(_np.diff(env['depth'][:,0]) > 0), 'Depth array must be strictly monotonic in range'
            assert env['depth_interp'] == curvilinear or env['depth_interp'] == linear, 'Invalid interpolation type: '+str(env['depth_interp'])
            max_depth = _np.max(env['depth'][:,1])
        else:
            max_depth = env['depth']
        if isinstance(env['soundspeed'], _pd.DataFrame):
            assert env['soundspeed'].shape[0] > 3, 'soundspeed profile must have at least 4 points'
            assert env['soundspeed'].index[0] <= 0, 'First depth in soundspeed array must be 0 m'
            assert env['soundspeed'].index[-1] >= max_depth, 'Last depth in soundspeed array must be beyond water depth: '+str(max_depth)+' m'
            assert _np.all(_np.diff(env['soundspeed'].index) > 0), 'Soundspeed array must be strictly monotonic in depth'
        elif _np.size(env['soundspeed']) > 1:
            assert env['soundspeed'].ndim == 2, 'soundspeed must be a scalar or an Nx2 array'
            assert env['soundspeed'].shape[1] == 2, 'soundspeed must be a scalar or an Nx2 array'
            # Minimum points depend on interpolation type
            if env['soundspeed_interp'] == 'spline':
                assert env['soundspeed'].shape[0] > 3, 'soundspeed profile must have at least 4 points for spline interpolation'
            else:
                assert env['soundspeed'].shape[0] > 1, 'soundspeed profile must have at least 2 points'
            assert env['soundspeed'][0,0] <= 0, 'First depth in soundspeed array must be 0 m'
            assert env['soundspeed'][-1,0] >= max_depth, 'Last depth in soundspeed array must be beyond water depth: '+str(max_depth)+' m'
            assert _np.all(_np.diff(env['soundspeed'][:,0]) > 0), 'Soundspeed array must be strictly monotonic in depth'
            assert env['soundspeed_interp'] == spline or env['soundspeed_interp'] == linear or env['soundspeed_interp'] == 'quadrilateral', 'Invalid interpolation type: '+str(env['soundspeed_interp'])
            if not(max_depth in env['soundspeed'][:,0]):
                indlarger = _np.argwhere(env['soundspeed'][:,0]>max_depth)[0][0]
                if env['soundspeed_interp'] == spline:
                    tck = _interp.splrep(env['soundspeed'][:,0], env['soundspeed'][:,1], s=0)
                    insert_ss_val = _interp.splev(max_depth, tck, der=0)
                else:
                    insert_ss_val = _np.interp(max_depth, env['soundspeed'][:,0], env['soundspeed'][:,1])
                env['soundspeed'] = _np.insert(env['soundspeed'],indlarger,[max_depth,insert_ss_val],axis = 0)
                env['soundspeed'] = env['soundspeed'][:indlarger+1,:]
        assert _np.max(env['tx_depth']) <= max_depth, 'tx_depth cannot exceed water depth: '+str(max_depth)+' m'
        assert _np.max(env['rx_depth']) <= max_depth, 'rx_depth cannot exceed water depth: '+str(max_depth)+' m'
        assert env['min_angle'] > -180 and env['min_angle'] < 180, 'min_angle must be in range (-180, 180)'
        assert env['max_angle'] > -180 and env['max_angle'] < 180, 'max_angle must be in range (-180, 180)'
        if env['tx_directionality'] is not None:
            assert _np.size(env['tx_directionality']) > 1, 'tx_directionality must be an Nx2 array'
            assert env['tx_directionality'].ndim == 2, 'tx_directionality must be an Nx2 array'
            assert env['tx_directionality'].shape[1] == 2, 'tx_directionality must be an Nx2 array'
            assert _np.all(env['tx_directionality'][:,0] >= -180) and _np.all(env['tx_directionality'][:,0] <= 180), 'tx_directionality angles must be in [-90, 90]'
        return env
    except AssertionError as e:
        raise ValueError(e.args)

def print_env(env):
    """Display the environment in a human readable form.

    :param env: environment definition

    >>> import arlpy.uwapm as pm
    >>> env = pm.create_env2d(depth=40, soundspeed=1540)
    >>> pm.print_env(env)
    """
    env = check_env2d(env)
    keys = ['name'] + sorted(list(env.keys()-['name']))
    for k in keys:
        v = str(env[k])
        if '\n' in v:
            v = v.split('\n')
            print('%20s : '%(k) + v[0])
            for v1 in v[1:]:
                print('%20s   '%('') + v1)
        else:
            print('%20s : '%(k) + v)

def plot_env(env, surface_color='dodgerblue', bottom_color='peru', tx_color='orangered', rx_color='midnightblue', rx_plot=None, **kwargs):
    """Plots a visual representation of the environment.

    :param env: environment description
    :param surface_color: color of the surface (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    :param bottom_color: color of the bottom (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    :param tx_color: color of transmitters (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    :param rx_color: color of receviers (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    :param rx_plot: True to plot all receivers, False to not plot any receivers, None to automatically decide

    Other keyword arguments applicable for `arlpy.plot.plot()` are also supported.

    The surface, bottom, transmitters (marker: '*') and receivers (marker: 'o')
    are plotted in the environment. If `rx_plot` is set to None and there are
    more than 2000 receivers, they are not plotted.

    >>> import arlpy.uwapm as pm
    >>> env = pm.create_env2d(depth=[[0, 40], [100, 30], [500, 35], [700, 20], [1000,45]])
    >>> pm.plot_env(env)
    """
    env = check_env2d(env)
    min_x = 0
    max_x = _np.max(env['rx_range'])
    if max_x-min_x > 10000:
        divisor = 1000
        min_x /= divisor
        max_x /= divisor
        xlabel = 'Range (km)'
    else:
        divisor = 1
        xlabel = 'Range (m)'
    if env['surface'] is None:
        min_y = 0
    else:
        min_y = _np.min(env['surface'][:,1])
    if _np.size(env['depth']) > 1:
        max_y = _np.max(env['depth'][:,1])
    else:
        max_y = env['depth']
    mgn_x = 0.01*(max_x-min_x)
    mgn_y = 0.1*(max_y-min_y)
    oh = _plt.hold()
    if env['surface'] is None:
        _plt.plot([min_x, max_x], [0, 0], xlabel=xlabel, ylabel='Depth (m)', xlim=(min_x-mgn_x, max_x+mgn_x), ylim=(-max_y-mgn_y, -min_y+mgn_y), color=surface_color, **kwargs)
    else:
        # linear and curvilinear options use the same altimetry, just with different normals
        s = env['surface']
        _plt.plot(s[:,0]/divisor, -s[:,1], xlabel=xlabel, ylabel='Depth (m)', xlim=(min_x-mgn_x, max_x+mgn_x), ylim=(-max_y-mgn_y, -min_y+mgn_y), color=surface_color, **kwargs)
    if _np.size(env['depth']) == 1:
        _plt.plot([min_x, max_x], [-env['depth'], -env['depth']], color=bottom_color)
    else:
        # linear and curvilinear options use the same bathymetry, just with different normals
        s = env['depth']
        _plt.plot(s[:,0]/divisor, -s[:,1], color=bottom_color)
    txd = env['tx_depth']
    _plt.plot([0]*_np.size(txd), -txd, marker='*', style=None, color=tx_color)
    if rx_plot is None:
        rx_plot = _np.size(env['rx_depth'])*_np.size(env['rx_range']) < 2000
    if rx_plot:
        rxr = env['rx_range']
        if _np.size(rxr) == 1:
            rxr = [rxr]
        for r in _np.array(rxr):
            rxd = env['rx_depth']
            _plt.plot([r/divisor]*_np.size(rxd), -rxd, marker='o', style=None, color=rx_color)
    _plt.hold(oh)

def plot_ssp(env, **kwargs):
    """Plots the sound speed profile.

    :param env: environment description

    Other keyword arguments applicable for `arlpy.plot.plot()` are also supported.

    If the sound speed profile is range-dependent, this function only plots the first profile.

    >>> import arlpy.uwapm as pm
    >>> env = pm.create_env2d(soundspeed=[[ 0, 1540], [10, 1530], [20, 1532], [25, 1533], [30, 1535]])
    >>> pm.plot_ssp(env)
    """
    env = check_env2d(env)
    svp = env['soundspeed']
    if isinstance(svp, _pd.DataFrame):
        svp = _np.hstack((_np.array([svp.index]).T, _np.asarray(svp)))
    if _np.size(svp) == 1:
        if _np.size(env['depth']) > 1:
            max_y = _np.max(env['depth'][:,1])
        else:
            max_y = env['depth']
        _plt.plot([svp, svp], [0, -max_y], xlabel='Soundspeed (m/s)', ylabel='Depth (m)', **kwargs)
    elif env['soundspeed_interp'] == spline:
        s = svp
        ynew = _np.linspace(_np.min(svp[:,0]), _np.max(svp[:,0]), 100)
        tck = _interp.splrep(svp[:,0], svp[:,1], s=0)
        xnew = _interp.splev(ynew, tck, der=0)
        _plt.plot(xnew, -ynew, xlabel='Soundspeed (m/s)', ylabel='Depth (m)', hold=True, **kwargs)
        _plt.plot(svp[:,1], -svp[:,0], marker='.', style=None, **kwargs)
    else:
        _plt.plot(svp[:,1], -svp[:,0], xlabel='Soundspeed (m/s)', ylabel='Depth (m)', **kwargs)

def compute_arrivals(env, model=None, debug=False, fname_base=None, local_env=False):
    """Compute arrivals between each transmitter and receiver.

    :param env: environment definition
    :param model: propagation model to use (None to auto-select)
    :param debug: generate debug information for propagation model
    :param fname_base: base file name for Bellhop working files, default (None), creates a temporary file
    :returns: arrival times and coefficients for all transmitter-receiver combinations

    >>> import arlpy.uwapm as pm
    >>> env = pm.create_env2d()
    >>> arrivals = pm.compute_arrivals(env)
    >>> pm.plot_arrivals(arrivals)
    """
    env = check_env2d(env)
    (model_name, model) = _select_model(env, arrivals, model)
    if debug:
        print('[DEBUG] Model: '+model_name)
    return model.run(env, arrivals, debug, fname_base, local_env)

def compute_eigenrays(env, tx_depth_ndx=0, rx_depth_ndx=0, rx_range_ndx=0, model=None, debug=False, fname_base=None):
    """Compute eigenrays between a given transmitter and receiver.

    :param env: environment definition
    :param tx_depth_ndx: transmitter depth index
    :param rx_depth_ndx: receiver depth index
    :param rx_range_ndx: receiver range index
    :param model: propagation model to use (None to auto-select)
    :param debug: generate debug information for propagation model
    :param fname_base: base file name for Bellhop working files, default (None), creates a temporary file
    :returns: eigenrays paths

    >>> import arlpy.uwapm as pm
    >>> env = pm.create_env2d()
    >>> rays = pm.compute_eigenrays(env)
    >>> pm.plot_rays(rays, width=1000)
    """
    env = check_env2d(env)
    env = env.copy()
    if _np.size(env['tx_depth']) > 1:
        env['tx_depth'] = env['tx_depth'][tx_depth_ndx]
    if _np.size(env['rx_depth']) > 1:
        env['rx_depth'] = env['rx_depth'][rx_depth_ndx]
    if _np.size(env['rx_range']) > 1:
        env['rx_range'] = env['rx_range'][rx_range_ndx]
    (model_name, model) = _select_model(env, eigenrays, model)
    if debug:
        print('[DEBUG] Model: '+model_name)
    return model.run(env, eigenrays, debug, fname_base)

def compute_rays(env, tx_depth_ndx=0, model=None, debug=False, fname_base=None):
    """Compute rays from a given transmitter.

    :param env: environment definition
    :param tx_depth_ndx: transmitter depth index
    :param model: propagation model to use (None to auto-select)
    :param debug: generate debug information for propagation model
    :param fname_base: base file name for Bellhop working files, default (None), creates a temporary file
    :returns: ray paths

    >>> import arlpy.uwapm as pm
    >>> env = pm.create_env2d()
    >>> rays = pm.compute_rays(env)
    >>> pm.plot_rays(rays, width=1000)
    """
    env = check_env2d(env)
    if _np.size(env['tx_depth']) > 1:
        env = env.copy()
        env['tx_depth'] = env['tx_depth'][tx_depth_ndx]
    (model_name, model) = _select_model(env, rays, model)
    if debug:
        print('[DEBUG] Model: '+model_name)
    return model.run(env, rays, debug, fname_base)

def compute_transmission_loss(env, tx_depth_ndx=0, mode=coherent, model=None, debug=False, fname_base=None):
    """Compute transmission loss from a given transmitter to all receviers.

    :param env: environment definition
    :param tx_depth_ndx: transmitter depth index
    :param mode: coherent, incoherent or semicoherent
    :param model: propagation model to use (None to auto-select)
    :param debug: generate debug information for propagation model
    :param fname_base: base file name for Bellhop working files, default (None), creates a temporary file
    :returns: complex transmission loss at each receiver depth and range

    >>> import arlpy.uwapm as pm
    >>> env = pm.create_env2d()
    >>> tloss = pm.compute_transmission_loss(env, mode=pm.incoherent)
    >>> pm.plot_transmission_loss(tloss, width=1000)
    """
    env = check_env2d(env)
    if mode not in [coherent, incoherent, semicoherent]:
        raise ValueError('Unknown transmission loss mode: '+mode)
    if _np.size(env['tx_depth']) > 1:
        env = env.copy()
        env['tx_depth'] = env['tx_depth'][tx_depth_ndx]
    (model_name, model) = _select_model(env, mode, model)
    if debug:
        print('[DEBUG] Model: '+model_name)
    return model.run(env, mode, debug, fname_base)

def arrivals_to_impulse_response(arrivals, fs, abs_time=False):
    """Convert arrival times and coefficients to an impulse response.

    :param arrivals: arrivals times (s) and coefficients
    :param fs: sampling rate (Hz)
    :param abs_time: absolute time (True) or relative time (False)
    :returns: impulse response

    If `abs_time` is set to True, the impulse response is placed such that
    the zero time corresponds to the time of transmission of signal.

    >>> import arlpy.uwapm as pm
    >>> env = pm.create_env2d()
    >>> arrivals = pm.compute_arrivals(env)
    >>> ir = pm.arrivals_to_impulse_response(arrivals, fs=192000)
    """
    t0 = 0 if abs_time else min(arrivals.time_of_arrival)
    irlen = int(_np.ceil((max(arrivals.time_of_arrival)-t0)*fs))+1
    ir = _np.zeros(irlen, dtype=_np.complex128)
    for _, row in arrivals.iterrows():
        ndx = int(_np.round((row.time_of_arrival.real-t0)*fs))
        ir[ndx] = row.arrival_amplitude
    return ir

def plot_arrivals(arrivals, dB=False, color='blue', **kwargs):
    """Plots the arrival times and amplitudes.

    :param arrivals: arrivals times (s) and coefficients
    :param dB: True to plot in dB, False for linear scale
    :param color: line color (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)

    Other keyword arguments applicable for `arlpy.plot.plot()` are also supported.

    >>> import arlpy.uwapm as pm
    >>> env = pm.create_env2d()
    >>> arrivals = pm.compute_arrivals(env)
    >>> pm.plot_arrivals(arrivals)
    """
    t0 = min(arrivals.time_of_arrival)
    t1 = max(arrivals.time_of_arrival)
    oh = _plt.hold()
    if dB:
        min_y = 20*_np.log10(_np.max(_np.abs(arrivals.arrival_amplitude)))-60
        ylabel = 'Amplitude (dB)'
    else:
        ylabel = 'Amplitude'
        _plt.plot([t0, t1], [0, 0], xlabel='Arrival time (s)', ylabel=ylabel, color=color, **kwargs)
        min_y = 0
    for _, row in arrivals.iterrows():
        t = row.time_of_arrival.real
        y = _np.abs(row.arrival_amplitude)
        if dB:
            y = max(20*_np.log10(_fi.epsilon+y), min_y)
        _plt.plot([t, t], [min_y, y], xlabel='Arrival time (s)', ylabel=ylabel, ylim=[min_y, min_y+70], color=color, **kwargs)
    _plt.hold(oh)

def plot_rays(rays, env=None, invert_colors=False, **kwargs):
    """Plots ray paths.

    :param rays: ray paths
    :param env: environment definition
    :param invert_colors: False to use black for high intensity rays, True to use white

    If environment definition is provided, it is overlayed over this plot using default
    parameters for `arlpy.uwapm.plot_env()`.

    Other keyword arguments applicable for `arlpy.plot.plot()` are also supported.

    >>> import arlpy.uwapm as pm
    >>> env = pm.create_env2d()
    >>> rays = pm.compute_eigenrays(env)
    >>> pm.plot_rays(rays, width=1000)
    """
    rays = rays.sort_values('bottom_bounces', ascending=False)
    max_amp = _np.max(_np.abs(rays.bottom_bounces)) if len(rays.bottom_bounces) > 0 else 0
    if max_amp <= 0:
        max_amp = 1
    divisor = 1
    xlabel = 'Range (m)'
    r = []
    for _, row in rays.iterrows():
        r += list(row.ray[:,0])
    if max(r)-min(r) > 10000:
        divisor = 1000
        xlabel = 'Range (km)'
    oh = _plt.hold()
    for _, row in rays.iterrows():
        c = int(255*_np.abs(row.bottom_bounces)/max_amp)
        if invert_colors:
            c = 255-c
        c = _bokeh.colors.RGB(c, c, c)
        _plt.plot(row.ray[:,0]/divisor, -row.ray[:,1], color=c, xlabel=xlabel, ylabel='Depth (m)', **kwargs)
    if env is not None:
        plot_env(env)
    _plt.hold(oh)

def plot_transmission_loss(tloss, env=None, **kwargs):
    """Plots transmission loss.

    :param tloss: complex transmission loss
    :param env: environment definition

    If environment definition is provided, it is overlayed over this plot using default
    parameters for `arlpy.uwapm.plot_env()`.

    Other keyword arguments applicable for `arlpy.plot.image()` are also supported.

    >>> import arlpy.uwapm as pm
    >>> import numpy as np
    >>> env = pm.create_env2d(
            rx_depth=np.arange(0, 25),
            rx_range=np.arange(0, 1000),
            min_angle=-45,
            max_angle=45
        )
    >>> tloss = pm.compute_transmission_loss(env)
    >>> pm.plot_transmission_loss(tloss, width=1000)
    """
    xr = (min(tloss.columns), max(tloss.columns))
    yr = (-max(tloss.index), -min(tloss.index))
    xlabel = 'Range (m)'
    if xr[1]-xr[0] > 10000:
        xr = (min(tloss.columns)/1000, max(tloss.columns)/1000)
        xlabel = 'Range (km)'
    oh = _plt.hold()
    _plt.image(20*_np.log10(_fi.epsilon+_np.abs(_np.flipud(_np.array(tloss)))), x=xr, y=yr, xlabel=xlabel, ylabel='Depth (m)', xlim=xr, ylim=yr, **kwargs)
    if env is not None:
        plot_env(env, rx_plot=False)
    _plt.hold(oh)

def pyplot_env(env, surface_color='dodgerblue', bottom_color='peru', tx_color='orangered', rx_color='midnightblue',
               rx_plot=None, **kwargs):
    """Plots a visual representation of the environment with matplotlib.

    :param env: environment description
    :param surface_color: color of the surface (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    :param bottom_color: color of the bottom (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    :param tx_color: color of transmitters (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    :param rx_color: color of receviers (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)
    :param rx_plot: True to plot all receivers, False to not plot any receivers, None to automatically decide

    Other keyword arguments applicable for `arlpy.plot.plot()` are also supported.

    The surface, bottom, transmitters (marker: '*') and receivers (marker: 'o')
    are plotted in the environment. If `rx_plot` is set to None and there are
    more than 2000 receivers, they are not plotted.

    >>> import arlpy.uwapm as pm
    >>> env = pm.create_env2d(depth=[[0, 40], [100, 30], [500, 35], [700, 20], [1000,45]])
    >>> pm.plot_env(env)
    """
    env = check_env2d(env)
    if _np.array(env['rx_range']).size > 1:
        min_x = _np.min(env['rx_range'])
    else:
        min_x = 0
    max_x = _np.max(env['rx_range'])
    if max_x - min_x > 10000:
        divisor = 1000
        min_x /= divisor
        max_x /= divisor
        xlabel = 'Range (km)'
    else:
        divisor = 1
        xlabel = 'Range (m)'
    if env['surface'] is None:
        min_y = 0
    else:
        min_y = _np.min(env['surface'][:, 1])
    if _np.size(env['depth']) > 1:
        max_y = _np.max(env['depth'][:, 1])
    else:
        max_y = env['depth']
    mgn_x = 0.01 * (max_x - min_x)
    mgn_y = 0.1 * (max_y - min_y)
    oh = _plt.hold()
    if env['surface'] is None:
        _pyplt.plot([min_x, max_x], [0, 0], color=surface_color, **kwargs)
        _pyplt.xlabel(xlabel)
        _pyplt.ylabel('Depth (m)')
        print(min_x, mgn_x, max_x, mgn_x)
        _pyplt.xlim([min_x - mgn_x, max_x + mgn_x])
        _pyplt.ylim([-max_y - mgn_y, -min_y + mgn_y])
    else:
        # linear and curvilinear options use the same altimetry, just with different normals
        s = env['surface']
        _pyplt.plot(s[:, 0] / divisor, -s[:, 1], color=surface_color, **kwargs)
        _pyplt.xlabel(xlabel)
        _pyplt.ylabel('Depth (m)')
        _pyplt.xlim([min_x - mgn_x, max_x + mgn_x])
        _pyplt.ylim([-max_y - mgn_y, -min_y + mgn_y])
    if _np.size(env['depth']) == 1:
        _pyplt.plot([min_x, max_x], [-env['depth'], -env['depth']], color=bottom_color, **kwargs)
    else:
        # linear and curvilinear options use the same bathymetry, just with different normals
        s = env['depth']
        _pyplt.plot(s[:, 0] / divisor, -s[:, 1], color=bottom_color, **kwargs)
    txd = env['tx_depth']
    # print(txd, [0]*_np.size(txd))
    _pyplt.plot([0] * _np.size(txd), -txd, marker='*', markersize=6, color=tx_color, **kwargs)
    if rx_plot is None:
        rx_plot = _np.size(env['rx_depth']) * _np.size(env['rx_range']) < 2000
    if rx_plot:
        rxr = env['rx_range']
        if _np.size(rxr) == 1:
            rxr = [rxr]
        for r in _np.array(rxr):
            rxd = env['rx_depth']
            _pyplt.plot([r / divisor] * _np.size(rxd), -rxd, marker='o', color=rx_color, **kwargs)

def pyplot_ssp(env, **kwargs):
    """Plots the sound speed profile with matplotlib.

    :param env: environment description

    Other keyword arguments applicable for `arlpy.plot.plot()` are also supported.

    If the sound speed profile is range-dependent, this function only plots the first profile.

    >>> import arlpy.uwapm as pm
    >>> env = pm.create_env2d(soundspeed=[[ 0, 1540], [10, 1530], [20, 1532], [25, 1533], [30, 1535]])
    >>> pm.plot_ssp(env)
    """
    env = check_env2d(env)
    svp = env['soundspeed']
    if isinstance(svp, _pd.DataFrame):
        svp = _np.hstack((_np.array([svp.index]).T, _np.asarray(svp)))
    if _np.size(svp) == 1:
        if _np.size(env['depth']) > 1:
            max_y = _np.max(env['depth'][:, 1])
        else:
            max_y = env['depth']
        _pyplt.plot([svp, svp], [0, -max_y], **kwargs)
        _pyplt.xlabel('Soundspeed (m/s)')
        _pyplt.ylabel('Depth (m)')
    elif env['soundspeed_interp'] == spline:
        s = svp
        ynew = _np.linspace(_np.min(svp[:, 0]), _np.max(svp[:, 0]), 100)
        tck = _interp.splrep(svp[:, 0], svp[:, 1], s=0)
        xnew = _interp.splev(ynew, tck, der=0)
        _pyplt.plot(xnew, -ynew, **kwargs)
        _pyplt.xlabel('Soundspeed (m/s)')
        _pyplt.ylabel('Depth (m)')
        _pyplt.plot(svp[:, 1], -svp[:, 0], marker='.', **kwargs)
    else:
        _pyplt.plot(svp[:, 1], -svp[:, 0], **kwargs)
        _pyplt.xlabel('Soundspeed (m/s)')
        _pyplt.ylabel('Depth (m)')

def pyplot_arrivals(arrivals, dB=False, color='blue', **kwargs):
    """Plots the arrival times and amplitudes with matplotlib.

    :param arrivals: arrivals times (s) and coefficients
    :param dB: True to plot in dB, False for linear scale
    :param color: line color (see `Bokeh colors <https://bokeh.pydata.org/en/latest/docs/reference/colors.html>`_)

    Other keyword arguments applicable for `arlpy.plot.plot()` are also supported.

    >>> import arlpy.uwapm as pm
    >>> env = pm.create_env2d()
    >>> arrivals = pm.compute_arrivals(env)
    >>> pm.plot_arrivals(arrivals)
    """
    t0 = min(arrivals.time_of_arrival)
    t1 = max(arrivals.time_of_arrival)
    if dB:
        min_y = 20 * _np.log10(_np.max(_np.abs(arrivals.arrival_amplitude))) - 60
        ylabel = 'Amplitude (dB)'
    else:
        ylabel = 'Amplitude'
        _pyplt.plot([t0, t1], [0, 0], color=color, **kwargs)
        _pyplt.xlabel('Arrival time (s)')
        _pyplt.ylabel(ylabel)
        min_y = 0
    for _, row in arrivals.iterrows():
        t = row.time_of_arrival.real
        y = _np.abs(row.arrival_amplitude)
        if dB:
            y = max(20 * _np.log10(_fi.epsilon + y), min_y)
        _pyplt.plot([t, t], [min_y, y], color=color, **kwargs)
        _pyplt.xlabel('Arrival time (s)')
        _pyplt.ylabel(ylabel)

def pyplot_rays(rays, env=None, invert_colors=False, **kwargs):
    """Plots ray paths with matplotlib

    :param rays: ray paths
    :param env: environment definition
    :param invert_colors: False to use black for high intensity rays, True to use white

    If environment definition is provided, it is overlayed over this plot using default
    parameters for `arlpy.uwapm.plot_env()`.

    Other keyword arguments applicable for `arlpy.plot.plot()` are also supported.

    >>> import arlpy.uwapm as pm
    >>> env = pm.create_env2d()
    >>> rays = pm.compute_eigenrays(env)
    >>> pm.plot_rays(rays, width=1000)
    """
    rays = rays.sort_values('bottom_bounces', ascending=False)
    max_amp = _np.max(_np.abs(rays.bottom_bounces)) if len(rays.bottom_bounces) > 0 else 0
    if max_amp <= 0:
        max_amp = 1
    divisor = 1
    xlabel = 'Range (m)'
    r = []
    for _, row in rays.iterrows():
        r += list(row.ray[:, 0])
    if max(r) - min(r) > 10000:
        divisor = 1000
        xlabel = 'Range (km)'
    oh = _plt.hold()
    for _, row in rays.iterrows():
        c = _np.abs(row.bottom_bounces) / max_amp
        if invert_colors:
            c = 1.0 - c
        c = _cm.gray(c)
        if "color" in kwargs.keys():
            _pyplt.plot(row.ray[:, 0] / divisor, -row.ray[:, 1], **kwargs)
        else:
            _pyplt.plot(row.ray[:, 0] / divisor, -row.ray[:, 1], color=c, **kwargs)
        _pyplt.xlabel(xlabel)
        _pyplt.ylabel('Depth (m)')
    if env is not None:
        pyplot_env(env)

def pyplot_transmission_loss(tloss, env=None, **kwargs):
    """Plots transmission loss with matplotlib.

    :param tloss: complex transmission loss
    :param env: environment definition

    If environment definition is provided, it is overlayed over this plot using default
    parameters for `arlpy.uwapm.plot_env()`.

    Other keyword arguments applicable for `arlpy.plot.image()` are also supported.

    >>> import arlpy.uwapm as pm
    >>> import numpy as np
    >>> env = pm.create_env2d(
            rx_depth=np.arange(0, 25),
            rx_range=np.arange(0, 1000),
            min_angle=-45,
            max_angle=45
        )
    >>> tloss = pm.compute_transmission_loss(env)
    >>> pm.plot_transmission_loss(tloss, width=1000)
    """
    xr = (min(tloss.columns), max(tloss.columns))
    yr = (-max(tloss.index), -min(tloss.index))
    xlabel = 'Range (m)'
    if xr[1] - xr[0] > 10000:
        xr = (min(tloss.columns) / 1000, max(tloss.columns) / 1000)
        xlabel = 'Range (km)'
    oh = _plt.hold()
    trans_loss = 20 * _np.log10(_fi.epsilon + _np.abs(_np.flipud(_np.array(tloss))))
    x_mesh, ymesh = _np.meshgrid(_np.linspace(xr[0], xr[1], trans_loss.shape[1]),
                                 _np.linspace(yr[0], yr[1], trans_loss.shape[0]))
    trans_loss = trans_loss.reshape(-1)
    # print(trans_loss.shape)
    if "vmin" in kwargs.keys():
        trans_loss[trans_loss < kwargs["vmin"]] = kwargs["vmin"]
    if "vmax" in kwargs.keys():
        trans_loss[trans_loss > kwargs["vmax"]] = kwargs["vmax"]
    trans_loss = trans_loss.reshape((x_mesh.shape[0], -1))
    _pyplt.contourf(x_mesh, ymesh, trans_loss, cmap="jet", **kwargs)
    _pyplt.xlabel(xlabel)
    _pyplt.ylabel('Depth (m)')
    _pyplt.colorbar(label="Transmission Loss(dB)")
    if env is not None:
        pyplot_env(env, rx_plot=False)

def models(env=None, task=None):
    """List available models.

    :param env: environment to model
    :param task: arrivals/eigenrays/rays/coherent/incoherent/semicoherent
    :returns: list of models that can be used

    >>> import arlpy.uwapm as pm
    >>> pm.models()
    ['bellhop']
    >>> env = pm.create_env2d()
    >>> pm.models(env, task=coherent)
    ['bellhop']
    """
    if env is not None:
        env = check_env2d(env)
    if (env is None and task is not None) or (env is not None and task is None):
        raise ValueError('env and task should be both specified together')
    rv = []
    for m in _models:
        if m[1]().supports(env, task):
            rv.append(m[0])
    return rv

def _select_model(env, task, model):
    if model is not None:
        for m in _models:
            if m[0] == model:
                return (m[0], m[1]())
        raise ValueError('Unknown model: '+model)
    for m in _models:
        mm = m[1]()
        if mm.supports(env, task):
            return (m[0], mm)
    raise ValueError('No suitable propagation model available')

### Bellhop propagation model ###

class _Bellhop:

    def __init__(self):
        pass

    def supports(self, env=None, task=None):
        if env is not None and env['type'] != '2D':
            return False
        fh, fname = _mkstemp(suffix='.env')
        _os.close(fh)
        fname_base = fname[:-4]
        self._unlink(fname_base+'.env')
        rv = self._bellhop(fname_base)
        self._unlink(fname_base+'.prt')
        self._unlink(fname_base+'.log')
        return rv

    def run(self, env, task, debug=False, fname_base=None, local_env=False):
        taskmap = {
            arrivals:     ['A', self._load_arrivals],
            eigenrays:    ['E', self._load_rays],
            rays:         ['R', self._load_rays],
            coherent:     ['C', self._load_shd],
            incoherent:   ['I', self._load_shd],
            semicoherent: ['S', self._load_shd]
        }
        fname_flag=False
        if fname_base is not None:
            fname_flag = True

        if local_env:
            if debug:
                print('[DEBUG] Bellhop using local env file: '+fname_base+'.env')
        else:
            fname_base = self._create_env_file(env, taskmap[task][0], fname_base)

        results = None
        if self._bellhop(fname_base):
            err = self._check_error(fname_base)
            if err is not None:
                print(err)
            else:
                try:
                    results = taskmap[task][1](fname_base)
                except FileNotFoundError:
                    print('[WARN] Bellhop did not generate expected output file')
        if debug:
            print('[DEBUG] Bellhop working files: '+fname_base+'.*')
        elif fname_flag:
            print('[CUSTOM FILES] Bellhop working files: '+fname_base+'.*')
        else:
            self._unlink(fname_base+'.env')
            self._unlink(fname_base+'.bty')
            self._unlink(fname_base+'.ssp')
            self._unlink(fname_base+'.ati')
            self._unlink(fname_base+'.sbp')
            self._unlink(fname_base+'.prt')
            self._unlink(fname_base+'.log')
            self._unlink(fname_base+'.arr')
            self._unlink(fname_base+'.ray')
            self._unlink(fname_base+'.shd')
        return results

    def _bellhop(self,*args):
        try:
            result = _proc.run(f'bellhop.exe {" ".join(list(args))}',
                        stderr=_proc.STDOUT, stdout=_proc.PIPE,
                        shell=True)
            if result.returncode == 127:
                return False
        except OSError:
            return False
        return True

    def _unlink(self, f):
        try:
            _os.unlink(f)
        except:
            pass

    def _print(self, fh, s, newline=True):
        _os.write(fh, (s+'\n' if newline else s).encode())

    def _print_array(self, fh, a):
        if _np.size(a) == 1:
            self._print(fh, "1")
            self._print(fh, "%0.6f /" % (a))
        else:
            self._print(fh, str(_np.size(a)))
            for j in a:
                self._print(fh, "%0.6f " % (j), newline=False)
            self._print(fh, "/")

    def _create_env_file(self, env, taskcode, fname_base=None):

        # get env file name
        if fname_base is not None:
            fname = fname_base+'.env'
            fh = _os.open(_os.path.abspath(fname), _os.O_WRONLY | _os.O_CREAT | _os.O_TRUNC)
        else:
            fh, fname = _mkstemp(suffix='.env')
            fname_base = fname[:-4]

        self._print(fh, "'"+env['name']+"'")
        self._print(fh, "%0.6f" % (env['frequency']))
        self._print(fh, "1")
        svp = env['soundspeed']
        svp_depth = 0.0
        svp_interp = 'S' if env['soundspeed_interp'] == spline else 'C'
        if isinstance(svp, _pd.DataFrame):
            svp_depth = svp.index[-1]
            if len(svp.columns) > 1:
                svp_interp = 'Q'
            else:
                svp = _np.hstack((_np.array([svp.index]).T, _np.asarray(svp)))
        if env['surface'] is None:
            self._print(fh, "'%cVWT'" % svp_interp)
        else:
            self._print(fh, "'%cVWT*'" % svp_interp)
            self._create_bty_ati_file(fname_base+'.ati', env['surface'], env['surface_interp'])
        # max depth should be the depth of the acoustic domain, which can be deeper than the max depth bathymetry
        max_depth = env['depth'] if _np.size(env['depth']) == 1 else max(_np.max(env['depth'][:,1]), svp_depth)
        self._print(fh, "1 0.0 %0.6f" % (max_depth))
        if _np.size(svp) == 1:
            self._print(fh, "0.0 %0.6f /" % (svp))
            self._print(fh, "%0.6f %0.6f /" % (max_depth, svp))
        elif svp_interp == 'Q':
            for j in range(svp.shape[0]):
                self._print(fh, "%0.6f %0.6f /" % (svp.index[j], svp.iloc[j,0]))
            self._create_ssp_file(fname_base+'.ssp', svp)
        else:
            for j in range(svp.shape[0]):
                self._print(fh, "%0.6f %0.6f /" % (svp[j,0], svp[j,1]))
        depth = env['depth']
        if _np.size(depth) == 1:
            self._print(fh, "'A' %0.6f" % (env['bottom_roughness']))
        else:
            self._print(fh, "'A*' %0.6f" % (env['bottom_roughness']))
            self._create_bty_ati_file(fname_base+'.bty', depth, env['depth_interp'])
        self._print(fh, "%0.6f %0.6f 0.0 %0.6f %0.6f /" % (max_depth, env['bottom_soundspeed'], env['bottom_density']/1000, env['bottom_absorption']))
        self._print_array(fh, env['tx_depth'])
        self._print_array(fh, env['rx_depth'])
        self._print_array(fh, env['rx_range']/1000)
        if env['tx_directionality'] is None:
            self._print(fh, "'"+taskcode+"'")
        else:
            self._print(fh, "'"+taskcode+" *'")
            self._create_sbp_file(fname_base+'.sbp', env['tx_directionality'])
        self._print(fh, "%d" % (env['nbeams']))
        self._print(fh, "%0.6f %0.6f /" % (env['min_angle'], env['max_angle']))
        self._print(fh, "0.0 %0.6f %0.6f" % (1.01*max_depth, 1.01*_np.max(env['rx_range'])/1000))
        _os.close(fh)
        return fname_base

    def _create_bty_ati_file(self, filename, depth, interp):
        with open(filename, 'wt') as f:
            f.write("'%c'\n" % ('C' if interp == curvilinear else 'L'))
            f.write(str(depth.shape[0])+"\n")
            for j in range(depth.shape[0]):
                f.write("%0.6f %0.6f\n" % (depth[j,0]/1000, depth[j,1]))

    def _create_sbp_file(self, filename, dir):
        with open(filename, 'wt') as f:
            f.write(str(dir.shape[0])+"\n")
            for j in range(dir.shape[0]):
                f.write("%0.6f %0.6f\n" % (dir[j,0], dir[j,1]))

    def _create_ssp_file(self, filename, svp):
        with open(filename, 'wt') as f:
            f.write(str(svp.shape[1])+"\n")
            for j in range(svp.shape[1]):
                f.write("%0.6f%c" % (svp.columns[j]/1000, '\n' if j == svp.shape[1]-1 else ' '))
            for k in range(svp.shape[0]):
                for j in range(svp.shape[1]):
                    f.write("%0.6f%c" % (svp.iloc[k,j], '\n' if j == svp.shape[1]-1 else ' '))

    def _readf(self, f, types, dtype=str):
        if type(f) is str:
            p = _re.split(r' +', f.strip())
        else:
            p = _re.split(r' +', f.readline().strip())
        for j in range(len(p)):
            if len(types) > j:
                p[j] = types[j](p[j])
            else:
                p[j] = dtype(p[j])
        return tuple(p)

    def _check_error(self, fname_base):
        err = None
        try:
            with open(fname_base+'.prt', 'rt') as f:
                for lno, s in enumerate(f):
                    if err is not None:
                        err += '[BELLHOP] ' + s
                    elif '*** FATAL ERROR ***' in s:
                        err = '\n[BELLHOP] ' + s
        except:
            pass
        return err

    def _load_arrivals(self, fname_base):
        with open(fname_base+'.arr', 'rt') as f:
            hdr = f.readline()
            if hdr.find('2D') >= 0:
                freq = self._readf(f, (float,))
                tx_depth_info = self._readf(f, (int,), float)
                tx_depth_count = tx_depth_info[0]
                tx_depth = tx_depth_info[1:]
                assert tx_depth_count == len(tx_depth)
                rx_depth_info = self._readf(f, (int,), float)
                rx_depth_count = rx_depth_info[0]
                rx_depth = rx_depth_info[1:]
                assert rx_depth_count == len(rx_depth)
                rx_range_info = self._readf(f, (int,), float)
                rx_range_count = rx_range_info[0]
                rx_range = rx_range_info[1:]
                assert rx_range_count == len(rx_range)
            else:
                freq, tx_depth_count, rx_depth_count, rx_range_count = self._readf(hdr, (float, int, int, int))
                tx_depth = self._readf(f, (float,)*tx_depth_count)
                rx_depth = self._readf(f, (float,)*rx_depth_count)
                rx_range = self._readf(f, (float,)*rx_range_count)
            arrivals = []
            for j in range(tx_depth_count):
                f.readline()
                for k in range(rx_depth_count):
                    for m in range(rx_range_count):
                        count = int(f.readline())
                        for n in range(count):
                            data = self._readf(f, (float, float, float, float, float, float, int, int))
                            arrivals.append(_pd.DataFrame({
                                'tx_depth_ndx': [j],
                                'rx_depth_ndx': [k],
                                'rx_range_ndx': [m],
                                'tx_depth': [tx_depth[j]],
                                'rx_depth': [rx_depth[k]],
                                'rx_range': [rx_range[m]],
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

    def _load_rays(self, fname_base):
        with open(fname_base+'.ray', 'rt') as f:
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
                pts, sb, bb = self._readf(f, (int, int, int))
                ray = _np.empty((pts, 2))
                for k in range(pts):
                    ray[k,:] = self._readf(f, (float, float))
                rays.append(_pd.DataFrame({
                    'angle_of_departure': [a],
                    'surface_bounces': [sb],
                    'bottom_bounces': [bb],
                    'ray': [ray]
                }))
        return _pd.concat(rays)

    def _load_shd(self, fname_base):
        with open(fname_base+'.shd', 'rb') as f:
            recl, = _unpack('i', f.read(4))
            title = str(f.read(80))
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

_models.append(('bellhop', _Bellhop))
