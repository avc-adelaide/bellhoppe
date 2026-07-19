"""File writing class methods for aubellhop.

These files are the input files passed directly into the `bellhop(3d).exe` binaries.

The `EnvironmentWriter` class provides encapsulation of methods. It is not intended
to be user-facing. It is the end of the chain for env writing:

    ~~bellhop.py~~         ~~environment.py~~   ~~writers.py~~
    model_fn.write_env() → env.to_file()      → EnvironmentWriter().write()

"""

from __future__ import annotations

from typing import Any, TextIO
import numpy as np
import pandas as pd
from .environment import Environment
from .constants import BHStrings, FlagMaps


class EnvironmentWriter:
    """Bellhop file-writer class which creates the `.env` and related input files."""

    def __init__(self,
                 env: Environment,
                 file_handle: TextIO,
                 fname_base: str,
                 taskcode: str
                ):
        """Initialize writer with existing file reference and filename base, plus taskcode.

        The filename base is, e.g., the `foo.env` file stripped of its extension.

        Although the taskcode can be stored within the environment, it is so common to
        override this that we use an explicit function input.

        Parameters
        ----------
        env : Environment
            The Environment instance
        fh : file object
            File reference (already opened)
        fname_base : str
            Filename base (without extension)
        taskcode : str
            Task char which defines the computation to run (`R`, `I`, `C`, etc.)

        """
        self.env = env
        self.file_handle = file_handle
        self.fname_base = fname_base
        self.taskcode = taskcode


    def write(self) -> None:
        """Writes a complete .env file for specifying a Bellhop simulation

        Returns
        -------
        self.fname_base : str
            Filename base (no extension) of written file

        We liberally insert comments and empty lines for readability and take care to
        ensure that comments are consistently aligned.
        This doesn't make a difference to bellhop.exe, it just makes debugging far easier.
        """

        fh = self.file_handle
        self._print_env_line(fh,"")
        self._write_env_header(fh)
        self._print_env_line(fh,"")
        self._write_env_surface_depth(fh)
        self._write_env_sound_speed(fh)
        self._print_env_line(fh,"")
        self._write_env_bottom(fh)
        self._print_env_line(fh,"")
        self._write_env_source_receiver(fh)
        self._print_env_line(fh,"")
        self._write_env_task(fh, self.taskcode)
        self._write_env_beam_footer(fh)
        self._print_env_line(fh,"")
        self._write_gaussian_params(fh)
        self._print_env_line(fh,"","End of Bellhop environment file")

        if self.env['surface_boundary_condition'] == BHStrings.from_file:
            self._create_refl_coeff_file(self.fname_base+".trc", self.env['surface_reflection_coefficient'])
        if np.size(self.env["surface_depth"]) > 1:
            self._create_bty_ati_file(self.fname_base+'.ati', self.env['surface_depth'], self.env['surface_interp'])
        if self.env['soundspeed_interp'] == BHStrings.quadrilateral:
            self._create_ssp_quad_file(self.fname_base+'.ssp', self.env['soundspeed'])
        if np.size(self.env['bottom_depth']) > 1:
            self._create_bty_ati_file(self.fname_base+'.bty', self.env['bottom_depth'], self.env['bottom_interp'])
        if self.env['bottom_boundary_condition'] == BHStrings.from_file:
            self._create_refl_coeff_file(self.fname_base+".brc", self.env['bottom_reflection_coefficient'])
        if self.env['source_directionality'] is not None:
            self._create_sbp_file(self.fname_base+'.sbp', self.env['source_directionality'])


    def _write_env_header(self, fh: TextIO) -> None:
        """Writes header of env file."""
        self._print_env_line(fh,"'"+self.env['name']+"'","Bellhop environment name/description")
        self._print_env_line(fh,self.env['frequency'],"Frequency (Hz)")
        self._print_env_line(fh,1,"NMedia -- always =1 for Bellhop")

    def _write_env_surface_depth(self, fh: TextIO) -> None:
        """Writes surface boundary and depth lines of env file."""

        svp_interp = FlagMaps.soundspeed_interp_rev[self.env['soundspeed_interp']]
        svp_boundcond = FlagMaps.surface_boundary_condition_rev[self.env['surface_boundary_condition']]
        svp_attenuation_units = FlagMaps.attenuation_units_rev[self.env['attenuation_units']]
        svp_volume_attenuation = FlagMaps.volume_attenuation_rev[self.env['volume_attenuation']]
        svp_alti = FlagMaps._altimetry_rev[self.env['_altimetry']]
        svp_singlebeam = FlagMaps._single_beam_rev[self.env['_single_beam']]

        # Line 4
        comment = "SSP parameters: Interp / Top Boundary Cond / Attenuation Units / Volume Attenuation)"
        topopt = self._quoted_opt(svp_interp, svp_boundcond, svp_attenuation_units, svp_volume_attenuation, svp_alti, svp_singlebeam)
        self._print_env_line(fh,f"{topopt}",comment)

        if self.env['volume_attenuation'] == BHStrings.francois_garrison:
            comment = "Francois-Garrison volume attenuation parameters (sal, temp, pH, depth)"
            self._print_env_line(fh,f"{self.env['_fg_salinity']} {self.env['_fg_temperature']} {self.env['_fg_pH']} {self.env['_fg_depth']}",comment)

        # Line 4a
        if self.env['surface_boundary_condition'] == BHStrings.acousto_elastic:
            comment = "DEPTH_Top (m)  TOP_SoundSpeed (m/s)  TOP_SoundSpeed_Shear (m/s)  TOP_Density (g/cm^3)  [ TOP_Absorp [ TOP_Absorp_Shear ] ]"
            array_str = self._array2str([
              self.env['_surface_min'],
              self.env['surface_soundspeed'],
              self.env['_surface_soundspeed_shear'],
              self._float(self.env['surface_density'],scale=1/1000),
              self.env['surface_attenuation'],
              self.env['_surface_attenuation_shear']
            ])
            self._print_env_line(fh,array_str,comment)

        # Line 4b
        if self.env['biological_layer_parameters'] is not None:
            self._write_env_biological(fh, self.env['biological_layer_parameters'])

    def _write_env_biological(self, fh: TextIO, biol: pd.DataFrame) -> None:
        """Writes biological layer parameters to env file."""
        self._print_env_line(fh, biol.shape[0], "N_Biol_Layers / z1 z2 w0 Q a0")
        for j, row in enumerate(biol.values):
            self._print_env_line(fh, self._array2str(row), f"biol_{j}")

    def _write_env_sound_speed(self, fh: TextIO) -> None:
        """Writes sound speed profile lines of env file."""

        comment = "[Npts - ignored]  [Sigma - ignored]  [Depth_Max - inferred]"
        self._print_env_line(fh,f"{self.env['_mesh_npts']} {self.env['_depth_sigma']} {self.env['_depth_max']}",comment)

        svp = self.env['soundspeed']
        if "density" in svp.columns:
            svp["density"] *= 1/1000  # kg/m^3 -> g/cm^3

        if self.env['soundspeed_interp'] == BHStrings.quadrilateral:
            for j in range(svp.shape[0]):
                # only print a single "dummy" column -- rest of data in .ssp file
                self._print_env_line(fh,self._array2str([svp.index[j], svp.iloc[j,0]]),f"ssp_{j}")
        else:
            for j in range(svp.shape[0]):
                row_values = [svp.index[j]] + svp.iloc[j,:].tolist()
                self._print_env_line(fh, self._array2str(row_values), f"ssp_{j}")

    def _write_env_bottom(self, fh: TextIO) -> None:
        """Writes bottom boundary lines of env file."""
        bot_bc = FlagMaps.bottom_boundary_condition_rev[self.env['bottom_boundary_condition']]
        dp_flag = FlagMaps._bathymetry_rev[self.env['_bathymetry']]
        bot_str = self._quoted_opt(bot_bc,dp_flag)
        comment = "BOT_Boundary_cond / BOT_Roughness"
        self._print_env_line(fh,f"{bot_str} {self.env['bottom_roughness']}",comment)
        if self.env['bottom_boundary_condition'] == BHStrings.acousto_elastic:
            comment = "Depth_Max  BOT_SoundSpeed  BOT_SS_Shear  BOT_Density  BOT_Absorp  BOT_Absorp Shear"
            array_str = self._array2str([
              self.env['_bottom_depth'] or self.env['_depth_max'],
              self.env['bottom_soundspeed'],
              self.env['_bottom_soundspeed_shear'],
              self._float(self.env['bottom_density'],scale=1/1000),
              self.env['bottom_attenuation'],
              self.env['_bottom_attenuation_shear']
            ])
            self._print_env_line(fh,array_str,comment)
        elif self.env['bottom_boundary_condition'] == BHStrings.grain:
            comment = "Grain_Depth  Grain_Size"
            array_str = self._array2str([
              self.env['_bottom_depth'] or self.env['_depth_max'],
              self.env['bottom_grain_size']
            ])
            self._print_env_line(fh,array_str,comment)

    def _write_env_source_receiver(self, fh: TextIO) -> None:
        """Writes source and receiver lines of env file."""
        if self.env._dimension == 2:
            self._print_array(fh, self.env['source_depth'], nn=self.env['source_ndepth'], label="Source depth (m)")
            self._print_array(fh, self.env['receiver_depth'], nn=self.env['receiver_ndepth'], label="Receiver depth (m)")
            self._print_array(fh, self.env['receiver_range']/1000, nn=self.env['receiver_nrange'], label="Receiver range (km)")
        elif self.env._dimension == 3:
            self._print_array(fh, self.env['source_range']/1000, nn=self.env['source_nrange'], label="Source range (km)")
            self._print_array(fh, self.env['source_cross_range']/1000, nn=self.env['source_ncrossrange'], label="Source cross range (km)")
            self._print_array(fh, self.env['source_depth'], nn=self.env['source_ndepth'], label="Source depth (m)")
            self._print_array(fh, self.env['receiver_depth'], nn=self.env['receiver_ndepth'], label="Receiver depth (m)")
            self._print_array(fh, self.env['receiver_range']/1000, nn=self.env['receiver_nrange'], label="Receiver range (km)")
            self._print_array(fh, self.env['receiver_bearing'], nn=self.env['receiver_nbearing'], label="Receiver bearing (°)")

    def _write_env_task(self, fh: TextIO, taskcode: str) -> None:
        """Writes task lines of env file."""
        beamtype = FlagMaps.beam_type_rev[self.env['beam_type']]
        beampattern = " " if self.env['source_directionality'] is None else "*"
        txtype = FlagMaps.source_type_rev[self.env['source_type']]
        gridtype = FlagMaps.grid_type_rev[self.env['grid_type']]
        runtype_str = self._quoted_opt(taskcode, beamtype, beampattern, txtype, gridtype)
        self._print_env_line(fh,f"{runtype_str}","RUN TYPE")

    def _write_env_beam_footer(self, fh: TextIO) -> None:
        """Writes beam and footer lines of env file."""
        self._print_env_line(fh,self._array2str([self.env['beam_num'], self.env['single_beam_index']]),"Num_Beams_Inclination [ Single_Beam_Index ]")
        self._print_env_line(fh,f"{self.env['beam_angle_min']} {self.env['beam_angle_max']} /","Inclination angle min/max (°)")
        if self.env['_dimension'] == 3:
            self._print_env_line(fh,f"{self.env['beam_bearing_num']}","Num_Beams_Bearing")
            self._print_env_line(fh,f"{self.env['beam_bearing_min']} {self.env['beam_bearing_max']} /","Bearing angle min/max (°)")
        if self.env['_dimension'] == 2:
            self._print_env_line(fh,f"{self.env['step_size']} {self.env['simulation_depth']} {self.env['simulation_range'] / 1000}","Step_Size (m), ZBOX (m), RBOX (km)")
        elif self.env['_dimension'] == 3:
            self._print_env_line(fh,f"{self.env['step_size']} {self.env['simulation_range'] / 1000} {self.env['simulation_cross_range'] / 1000} {self.env['simulation_depth']}","Step_Size (m), BoxRange (x) (km), BoxCrossRange (y) (km), BoxDepth (z) (m)")

    def _write_gaussian_params(self, fh: TextIO) -> None:
        """Read parameters for Cerveny Gaussian Beams, if applicable"""
        if self.env['beam_type'] not in (BHStrings.cartesian, BHStrings.ray):
            return None
        rloop = None if self.env['beam_range_loop'] is None else self.env['beam_range_loop'] / 1000
        self._print_env_line(fh,self._array2str([self.env['beam_width_type'], self.env['beam_epsilon_multipler'], rloop]),"Beam_width_type Eps_Mult Range_Loop")
        self._print_env_line(fh,self._array2str([self.env['beam_images_num'], self.env['beam_window'], self.env['beam_component']]),"Beam_width_type Eps_Mult Range_Loop")

    def _print(self, fh: TextIO, s: str, newline: bool = True) -> None:
        """Write a line of text with or w/o a newline char to the output file"""
        fh.write(s+'\n' if newline else s)

    def _print_env_line(self, fh: TextIO, data: Any, comment: str = "") -> None:
        """Write a complete line to the .env file with a descriptive comment

        We do some char counting (well, padding and stripping) to ensure the code comments all start from the same char.
        """
        data_str = data if isinstance(data,str) else f"{data}"
        comment_str = comment if isinstance(comment,str) else f"{comment}"
        line_str = (data_str + " " * self.env['comment_pad'])[0:max(len(data_str),self.env['comment_pad'])]
        if comment_str != "":
            line_str = line_str + " ! " + comment_str
        self._print(fh,line_str)

    def _print_array(self, fh: TextIO, a: Any, label: str = "", nn: int | None = None) -> None:
        """Print a 1D array to the .env file, prefixed by a count of the array length"""
        na = np.size(a)
        if nn is None:
            nn = na
        if nn < na:
            raise ValueError(f"Cannot write '{label}': point count ({nn}) is smaller than the number of values ({na})")
        if na == 1:
            self._print_env_line(fh, nn, f"{label} (single value)")
            self._print_env_line(fh, f"{np.ravel(a)[0]} /", f"{label} (single value)")
        else:
            self._print_env_line(fh, nn, f"{label}s ({nn} values)")
            for j in np.ravel(a):
                self._print(fh, f"{j} ", newline=False)
            self._print(fh, " /")

    def _array2str(self, values: list[Any]) -> str:
        """Format list into space-separated string, trimmed at first None, ending with '/'."""
        try:
            values = values[:values.index(None)]
        except ValueError:
            pass
        return " ".join(
            f"{v}" if isinstance(v, (int, float)) else str(v)
            for v in values
        ) + " /"

    def _quoted_opt(self, *args: str) -> str:
        """Concatenate N input BHStrings. strip whitespace, surround with single quotes
        """
        combined = "".join(args).strip()
        return f"'{combined}'"

    def _float(self, x: float | None, scale: float = 1) -> float | None:
        """Permissive floatenator"""
        return None if x is None else float(x) * scale

    def _create_bty_ati_file(self, filename: str, depth: Any, interp: BHStrings) -> None:
        """Write data to bathymetry/altimetry file

        The short/long ("S"/"L") flags are hard-coded to keep it simple.
        """
        with open(filename, 'wt') as f:
            format_flag = "S" if depth.shape[1] == 2 else "L"
            f.write(f"'{FlagMaps.bottom_interp_rev[interp]}{format_flag}'\n")
            f.write(str(depth.shape[0])+"\n")
            if depth.shape[1] == 2:
                for j in range(depth.shape[0]):
                    f.write(f"{depth[j,0]/1000} {depth[j,1]}\n")
            elif depth.shape[1] == 7:
                for j in range(depth.shape[0]):
                    f.write(f"{depth[j,0]/1000} {depth[j,1]} {depth[j,2]} {depth[j,3]} {depth[j,4]} {depth[j,5]} {depth[j,6]}\n")

    def _create_sbp_file(self, filename: str, dir: Any) -> None:
        """Write data to sbp file"""
        with open(filename, 'wt') as f:
            f.write(str(dir.shape[0])+"\n")
            for j in range(dir.shape[0]):
                f.write(f"{dir[j,0]}  {dir[j,1]}\n")

    def _create_refl_coeff_file(self, filename: str, rc: Any) -> None:
        """Write data to brc/trc file"""
        with open(filename, 'wt') as f:
            f.write(str(rc.shape[0])+"\n")
            for j in range(rc.shape[0]):
                f.write(f"{rc[j,0]}  {rc[j,1]}  {rc[j,2]}\n")

    def _create_ssp_quad_file(self, filename: str, svp: pd.DataFrame) -> None:
        """Write 2D SSP data to file"""
        with open(filename, 'wt') as f:
            f.write(str(svp.shape[1])+"\n") # number of SSP points
            for j in range(svp.shape[1]):
                f.write("%0.6f%c" % (svp.columns[j]/1000, '\n' if j == svp.shape[1]-1 else ' '))
            for k in range(svp.shape[0]):
                for j in range(svp.shape[1]):
                    f.write("%0.6f%c" % (svp.iloc[k,j], '\n' if j == svp.shape[1]-1 else ' '))
