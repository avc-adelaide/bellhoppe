##############################################################################
#
# Copyright (c) 2025-, Will Robertson
# Copyright (c) 2018-2025, Mandar Chitre
#
# This file was originally part of arlpy, released under Simplified BSD License.
# It has been relicensed in this repository to be compatible with the Bellhop licence (GPL).
#
##############################################################################

"""File reading utilities for BELLHOP acoustic simulation files.

This module contains functions for reading various BELLHOP file formats including
environment files (.env), sound speed profiles (.ssp), bathymetry files (.bty),
and reflection coefficient files (.brc).
"""

import os as _os
import re as _re
import numpy as _np
from scipy import interpolate as _interp
import pandas as _pd

# Import the mapping dictionaries from the main module
# These will be populated when the module is imported
interp_map = {}
boundcond_map = {}
attunits_map = {}
volatt_map = {}
bottom_map = {}
source_map = {}
grid_map = {}
beam_map = {}

# reverse mappings - these will be populated from main module
interp_rev = {}
boundcond_rev = {}
attunits_rev = {}
volatt_rev = {}
bottom_rev = {}
source_rev = {}
grid_rev = {}
beam_rev = {}

def _populate_mappings(parent_globals):
    """Populate the mapping dictionaries from the parent module."""
    global interp_map, boundcond_map, attunits_map, volatt_map, bottom_map, source_map, grid_map, beam_map
    global interp_rev, boundcond_rev, attunits_rev, volatt_rev, bottom_rev, source_rev, grid_rev, beam_rev
    
    interp_map.update(parent_globals['interp_map'])
    boundcond_map.update(parent_globals['boundcond_map'])
    attunits_map.update(parent_globals['attunits_map'])
    volatt_map.update(parent_globals['volatt_map'])
    bottom_map.update(parent_globals['bottom_map'])
    source_map.update(parent_globals['source_map'])
    grid_map.update(parent_globals['grid_map'])
    beam_map.update(parent_globals['beam_map'])
    
    interp_rev.update(parent_globals['interp_rev'])
    boundcond_rev.update(parent_globals['boundcond_rev'])
    attunits_rev.update(parent_globals['attunits_rev'])
    volatt_rev.update(parent_globals['volatt_rev'])
    bottom_rev.update(parent_globals['bottom_rev'])
    source_rev.update(parent_globals['source_rev'])
    grid_rev.update(parent_globals['grid_rev'])
    beam_rev.update(parent_globals['beam_rev'])


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
    :top_boundary_condition: ('vacuum', 'acousto-elastic', 'rigid', 'from-file')
    :volume_attenuation: ('none', 'thorp', 'francois-garrison', 'biological')
    :attenuation_units: ('nepers per meter', 'frequency dependent', 'dB per meter', 'frequency scaled dB per meter', 'dB per wavelength', 'quality factor', 'loss parameter')
    :tx_depth: transmitter depth(s) in meters
    :tx_directionality: transmitter beam pattern (None if omnidirectional)
    :rx_depth: receiver depth(s) in meters
    :rx_range: receiver range(s) in meters
    :depth: maximum water depth in meters
    :depth_interp: bathymetry interpolation method ('linear', 'curvilinear')
    :min_angle: minimum beam angle in degrees
    :max_angle: maximum beam angle in degrees
    :nbeams: number of beams (0 for automatic)
    :step_size: (maximum) step size to trace rays in meters (0 for automatic)
    :box_depth: box extent to trace rays in meters (auto-calculated based on max depth data if not specified)
    :box_range: box extent to trace rays in meters (auto-calculated based on max receiver range if not specified)
    :tx_type: point (default) or line

    :example:

    >>> import bellhop as bh
    >>> env = bh.read_env2d('example.env')
    >>> bh.plot_env(env)
    """

    # Add .env extension if not present
    if not fname.endswith('.env'):
        fname = fname + '.env'

    env = {}

    def _parse_quoted_string(line):
        """Extract quoted string from environment file line"""
        match = _re.search(r"'([^']*)'", line)
        if match:
            return match.group(1)
        else:
            return line.strip()

    def _parse_line(line):
        """Remove comments and strip line"""
        if '!' in line:
            line = line.split('!')[0]
        return line.strip()

    def _parse_vector(f, dtype=float):
        """Parse a line that might contain multiple space-separated values"""
        line = f.readline().strip()
        line = _parse_line(line)

        # Count how many values we have
        values_line = line.split('/')[-1].strip() if '/' in line else line
        if not values_line:
            return None, 0

        # Try to read one line that can contain the depth/range count followed by the actual values
        parts = values_line.split()
        linecount = int(parts[0])

        # The remaining parts should be the values - if not enough, read from next lines
        if len(parts) > 1:
            values = [dtype(p) for p in parts[1:]]
        else:
            values = []

        # Read additional lines if needed
        while len(values) < linecount:
            next_line = f.readline().strip()
            next_line = _parse_line(next_line)
            if next_line:
                next_parts = next_line.split()
                values.extend([dtype(p) for p in next_parts])

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

            # Parse the line for sound speed profile points
            line = _parse_line(line)
            if line:
                # Remove trailing '/' if present
                if line.endswith('/'):
                    line = line[:-1].strip()
                
                parts = line.split()
                # Format is: depth soundspeed [absorption] [density]
                if len(parts) >= 2:
                    depth = float(parts[0])
                    soundspeed = float(parts[1])
                    absorption = float(parts[2]) if len(parts) > 2 else 0.0
                    density = float(parts[3]) if len(parts) > 3 else 1.0
                    ssp_points.append([depth, soundspeed, absorption, density])

        return _np.array(ssp_points) if ssp_points else None

    with open(fname, 'r') as f:
        # Read environment title
        env['name'] = _parse_quoted_string(f.readline())

        # Read frequency
        freq_line = f.readline().strip()
        freq_line = _parse_line(freq_line)
        env['frequency'] = float(freq_line.split()[0])

        # Read number of media
        media_line = f.readline().strip()
        media_line = _parse_line(media_line)
        n_media = int(media_line.split()[0])

        # Read sound speed profile options line
        ssp_opt_line = f.readline().strip()
        ssp_opt_line = _parse_line(ssp_opt_line)
        
        # Handle quoted format like 'PVF' or separate parameters
        if ssp_opt_line.startswith("'") and ssp_opt_line.endswith("'"):
            # Quoted format like 'PVF'
            options = ssp_opt_line.strip("'")
            if len(options) >= 1:
                env['soundspeed_interp'] = interp_map.get(options[0], 'linear')
            if len(options) >= 2:
                env['volume_attenuation'] = volatt_map.get(options[1], 'none')
            if len(options) >= 3:
                env['attenuation_units'] = attunits_map.get(options[2], 'default')
            else:
                env['attenuation_units'] = 'default'
        else:
            # Space-separated format
            ssp_parts = ssp_opt_line.split()
            env['soundspeed_interp'] = interp_map.get(ssp_parts[1] if len(ssp_parts) > 1 else 'L', 'linear')
            env['attenuation_units'] = attunits_map.get(ssp_parts[2] if len(ssp_parts) > 2 else '', 'default')
            env['volume_attenuation'] = volatt_map.get(ssp_parts[3] if len(ssp_parts) > 3 else '', 'none')

        # Read sound speed profile depth/range points
        ssp_points = _read_ssp_points(f)
        if ssp_points is not None and len(ssp_points) > 0:
            if ssp_points.shape[1] >= 2:
                # Standard depth-dependent profile: [depth, soundspeed]
                env['soundspeed'] = ssp_points[:, :2]
            else:
                env['soundspeed'] = 1500.0  # Default sound speed
        else:
            env['soundspeed'] = 1500.0  # Default sound speed

        # Read bottom boundary condition line
        bottom_line = f.readline().strip()
        bottom_line = _parse_line(bottom_line)
        bottom_line = _parse_quoted_string(bottom_line)

        # Parse bottom boundary
        bottom_parts = bottom_line.split()
        if len(bottom_parts) > 0:
            # Parse boundary condition character (first character)
            bc_char = bottom_parts[0][0] if bottom_parts[0] else 'A'
            env['top_boundary_condition'] = boundcond_map.get(bc_char, 'acousto-elastic')

        # Continue reading bottom parameters
        if len(bottom_parts) >= 5:
            env['bottom_soundspeed'] = float(bottom_parts[1])
            env['bottom_soundspeed_shear'] = float(bottom_parts[2])
            env['bottom_density'] = float(bottom_parts[3])
            env['bottom_absorption'] = float(bottom_parts[4])
            if len(bottom_parts) >= 6:
                env['bottom_absorption_shear'] = float(bottom_parts[5])
            else:
                env['bottom_absorption_shear'] = 0.0
            if len(bottom_parts) >= 7:
                env['bottom_roughness'] = float(bottom_parts[6])
            else:
                env['bottom_roughness'] = 0.0

        # Read bathymetry/depth information
        depth_line = f.readline().strip()
        depth_line = _parse_line(depth_line)

        if depth_line:
            depth_parts = depth_line.split()
            n_bathymetry = int(depth_parts[0])

            if n_bathymetry == 1:
                # Simple constant depth
                env['depth'] = float(depth_parts[1])
                env['depth_interp'] = 'linear'
            else:
                # Variable bathymetry - read range/depth pairs
                # Read interpolation character
                env['depth_interp'] = interp_map.get(depth_parts[1], 'linear')

                bathymetry_points = []
                for i in range(n_bathymetry):
                    bathy_line = f.readline().strip()
                    bathy_line = _parse_line(bathy_line)
                    if bathy_line:
                        range_depth = bathy_line.split()
                        if len(range_depth) >= 2:
                            range_km = float(range_depth[0])
                            depth_m = float(range_depth[1])
                            bathymetry_points.append([range_km * 1000, depth_m])  # Convert km to m

                if bathymetry_points:
                    env['depth'] = _np.array(bathymetry_points)
                    # Set max depth
                    env['depth_max'] = _np.max(env['depth'][:, 1])
                else:
                    env['depth'] = 100.0  # Default depth
                    env['depth_max'] = 100.0

        # Read sound profiles (if any)
        # For now, skip this section - would need more complex parsing

        # Read beam/ray options
        beam_line = f.readline().strip()
        beam_line = _parse_line(beam_line)

        if beam_line:
            beam_parts = beam_line.split()
            if len(beam_parts) >= 3:
                env['min_angle'] = float(beam_parts[0])
                env['max_angle'] = float(beam_parts[1])
                env['nbeams'] = int(beam_parts[2])

        # Read step size, box depth, box range
        try:
            limits_line = f.readline().strip()
            limits_line = _parse_line(limits_line)
            limits_parts = limits_line.split()
            env['step_size'] = float(limits_parts[0])
            env['box_depth'] = float(limits_parts[1])
            env['box_range'] = 1000*float(limits_parts[2])
        except:
            pass

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

    The returned data structure depends on the number of profiles:
    - Single profile: numpy array of shape (n_depths, 2) with columns [depth, soundspeed]
    - Multiple profiles: pandas DataFrame with depth as index and range positions as columns

    :example:

    >>> import bellhop as bh
    >>> # Read single profile
    >>> ssp = bh.read_ssp('sound_speed.ssp')
    >>> # Read range-dependent profile
    >>> ssp_rd = bh.read_ssp('range_dependent.ssp')
    """

    # Add .ssp extension if not present
    if not fname.endswith('.ssp'):
        fname = fname + '.ssp'

    with open(fname, 'r') as f:
        # Read number of profiles
        first_line = f.readline().strip()
        nprofiles = int(first_line.split()[0])

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
            depth_indices = _np.arange(ndepths)

            # Create DataFrame with ranges as columns and depth indices as index
            df = _pd.DataFrame(ssp_array, columns=ranges_m, index=depth_indices)
            return df


def read_bty(fname):
    """Read a bathymetry (.bty) file used by BELLHOP.

    This function reads BELLHOP's .bty files which define the seafloor bathymetry.
    The file format is:
    - Line 1: Quoted bathymetry type and interpolation character
    - Line 2: Number of bathymetry points
    - Lines 3+: Range (km) and depth (m) pairs

    :param fname: path to .bty file (with or without .bty extension)
    :returns: tuple of (bathymetry_array, interpolation_method)
              bathymetry_array: numpy array with [range, depth] pairs (range in meters)
              interpolation_method: string describing interpolation method

    The bathymetry array contains [range, depth] coordinates where:
    - range is in meters (converted from km in file)
    - depth is in meters (positive downward)

    :example:

    >>> import bellhop as bh
    >>> bty, interp = bh.read_bty('bathymetry.bty')
    >>> print(f"Bathymetry has {len(bty)} points using {interp} interpolation")
    """

    # Add .bty extension if not present
    if not fname.endswith('.bty'):
        fname = fname + '.bty'

    with open(fname, 'r') as f:
        # Read interpolation line (quoted)
        interp_line = f.readline().strip()
        # Extract interpolation character (usually 'L' for linear or 'C' for curvilinear)
        match = _re.search(r"'([^']*)'", interp_line)
        if match:
            interp_char = match.group(1)[-1] if match.group(1) else 'L'  # Last character
        else:
            interp_char = 'L'  # Default to linear

        interp_method = interp_map.get(interp_char, 'linear')

        # Read number of bathymetry points
        npoints_line = f.readline().strip()
        npoints = int(npoints_line.split()[0])

        # Read bathymetry points
        bathymetry = []
        for i in range(npoints):
            line = f.readline().strip()
            if line and not line.startswith('#'):
                parts = line.split()
                if len(parts) >= 2:
                    range_km = float(parts[0])
                    depth_m = float(parts[1])
                    bathymetry.append([range_km * 1000, depth_m])  # Convert km to m

        if len(bathymetry) != npoints:
            raise ValueError(f"Expected {npoints} bathymetry points, but found {len(bathymetry)}")

        # Return as [range, depth] pairs
        return _np.array(bathymetry), interp_method


def read_refl_coeff(fname):
    """Read a reflection coefficient (.brc) file used by BELLHOP.

    This function reads BELLHOP's .brc files which define bottom reflection coefficients
    as a function of angle. The file format is:
    - Line 1: Number of angle points
    - Lines 2+: Angle (degrees), magnitude, and phase (degrees)

    :param fname: path to .brc file (with or without .brc extension)
    :returns: numpy array with [angle, magnitude, phase] columns

    The returned array contains:
    - Column 0: Angle in degrees
    - Column 1: Reflection coefficient magnitude (0-1)
    - Column 2: Reflection coefficient phase in degrees

    :example:

    >>> import bellhop as bh
    >>> refl = bh.read_refl_coeff('reflection.brc')
    >>> angles, magnitudes, phases = refl[:, 0], refl[:, 1], refl[:, 2]
    """

    # Add .brc extension if not present
    if not fname.endswith('.brc'):
        fname = fname + '.brc'

    with open(fname, 'r') as f:
        # Read number of angle points
        npoints_line = f.readline().strip()
        npoints = int(npoints_line.split()[0])

        # Read reflection coefficient data
        theta = []
        rmagn = []
        rphas = []

        for i in range(npoints):
            line = f.readline().strip()
            if line and not line.startswith('#'):
                parts = line.split()
                if len(parts) >= 3:
                    theta.append(float(parts[0]))
                    rmagn.append(float(parts[1]))
                    rphas.append(float(parts[2]))

        if len(theta) != npoints:
            raise ValueError(f"Expected {npoints} bathymetry points, but found {len(theta)}")

        # Return as [range, depth] pairs
        return _np.column_stack([theta, rmagn, rphas])