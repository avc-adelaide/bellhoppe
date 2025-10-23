
import os as _os
import subprocess as _proc
import shutil

from tempfile import mkstemp as _mkstemp
from typing import Any, Dict, List, Optional, Tuple, TextIO

import numpy as _np
import pandas as _pd

from .constants import Defaults, _Strings, _Maps, _File_Ext
from .environment import Environment
from .readers import read_shd, read_arrivals, read_rays

class BellhopSimulator:
    """
    Interface to the Bellhop underwater acoustics ray tracing propagation model.

    Two public methods are defined: `supports()` and `run()`.
    Both take arguments of environment and task, and respectively
    report whether the executable can perform the task, and to do so.

    Parameters
    ----------
    name : str
        User-fancing name for the model
    exe : str
        Filename of Bellhop executable
    """

    def __init__(self, name: str = Defaults.model_name,
                       exe: str = Defaults.exe,
                       dim: int = Defaults.model_dim,
                       env_comment_pad: int = Defaults.env_comment_pad,
                ) -> None:
        self.name: str = name
        self.exe: str = exe
        self.dim: int = dim
        self.env_comment_pad: int = env_comment_pad

    def supports(self, env: Optional[Environment] = None,
                       task: Optional[str] = None,
                       exe: Optional[str] = None,
                       dim: Optional[int] = None,
                ) -> bool:
        """Check whether the model supports the task.

           This function is supposed to diagnose whether this combination of environment
           and task is supported by the model."""

        which_bool = shutil.which(exe or self.exe) is not None
        task_bool = task is None or task in self.taskmap
        dim_bool = dim is None or dim == self.dim

        return (which_bool and task_bool and dim_bool)

    def run(self, env: Environment,
                  task: str,
                  debug: bool = False,
                  fname_base: Optional[str] = None,
           ) -> Any:
        """
        High-level interface function which runs the model.

        The function definition performs setup and cleanup tasks
        and passes the execution off to an auxiliary function.

        Uses the `taskmap` data structure to relate input flags to
        processng stages, in particular how to select specific "tasks"
        to be executed.
        """

        task_flag, load_task_data, task_ext = self.taskmap[task]

        fd, fname_base = self._prepare_env_file(fname_base)
        with _os.fdopen(fd, "w") as fh:
            self._create_env_file(env, task_flag, fh, fname_base)

        self._run_exe(fname_base)
        results = load_task_data(fname_base + task_ext)

        if debug:
            print('[DEBUG] Bellhop working files NOT deleted: '+fname_base+'.*')
        else:
            self._rm_files(fname_base)

        return results

    @property
    def taskmap(self) -> Dict[Any, List[Any]]:
        """Dictionary which maps tasks to execution functions and their parameters"""
        return {
            _Strings.arrivals:     ['A', read_arrivals, _File_Ext.arr],
            _Strings.eigenrays:    ['E', read_rays,     _File_Ext.ray],
            _Strings.rays:         ['R', read_rays,     _File_Ext.ray],
            _Strings.coherent:     ['C', read_shd,      _File_Ext.shd],
            _Strings.incoherent:   ['I', read_shd,      _File_Ext.shd],
            _Strings.semicoherent: ['S', read_shd,      _File_Ext.shd],
        }

    def _prepare_env_file(self, fname_base: Optional[str]) -> Tuple[int, str]:
        """Opens a file for writing the .env file, in a temp location if necessary, and delete other files with same basename.

        Parameters
        ----------
        fname_base : str, optional
            Filename base (no extension) for writing -- if not specified a temporary file (and location) will be used instead

        Returns
        -------
        fh : int
            File descriptor
        fname_base : str
            Filename base
        """
        if fname_base is not None:
            fname = fname_base + _File_Ext.env
            fh = _os.open(_os.path.abspath(fname), _os.O_WRONLY | _os.O_CREAT | _os.O_TRUNC)
        else:
            fh, fname = _mkstemp(suffix = _File_Ext.env)
            fname_base = fname[:-len(_File_Ext.env)]
        self._rm_files(fname_base, not_env=True) # delete all other files
        return fh, fname_base

    def _rm_files(self, fname_base: str, not_env: bool = False) -> None:
        """Remove files that would be constructed as bellhop inputs or created as bellhop outputs."""
        all_ext = [v for k, v in vars(_File_Ext).items() if not k.startswith('_')]
        if not_env:
            all_ext.remove(_File_Ext.env)
        for ext in all_ext:
            self._unlink(fname_base + ext)

    def _run_exe(self, fname_base: str,
                       args: str = "",
                       debug: bool = False,
                       exe: Optional[str] = None,
                ) -> None:
        """Run the executable and raise exceptions if there are errors."""

        exe_path = shutil.which(exe or self.exe)
        if exe_path is None:
            raise FileNotFoundError(f"Executable ({exe_path}) not found in PATH.")

        runcmd = [exe_path, fname_base] + args.split()
        if debug:
            print("RUNNING:", " ".join(runcmd))
        result = _proc.run(runcmd, stderr=_proc.STDOUT, stdout=_proc.PIPE, text=True)

        if debug and result.stdout:
            print(result.stdout.strip())

        if result.returncode != 0:
            err = self._check_error(fname_base)
            raise RuntimeError(
                f"Execution of '{exe_path}' failed with return code {result.returncode}.\n"
                f"\nCommand: {' '.join(runcmd)}\n"
                f"\nOutput:\n{result.stdout.strip()}\n"
                f"\nExtract from PRT file:\n{err}"
            )


    def _check_error(self, fname_base: str) -> Optional[str]:
        """Extracts Bellhop error text from the .prt file"""
        try:
            err = ""
            fatal = False
            with open(fname_base + _File_Ext.prt, 'rt') as f:
                for s in f:
                    if fatal and len(s.strip()) > 0:
                        err += '[FATAL] ' + s.strip() + '\n'
                    if '*** FATAL ERROR ***' in s:
                        fatal = True
        except FileNotFoundError:
            pass
        return err if err != "" else None

    def _unlink(self, f: str) -> None:
        """Delete file only if it exists"""
        try:
            _os.unlink(f)
        except FileNotFoundError:
            pass

    def _create_env_file(self, env: Environment, taskcode: str, fh: TextIO, fname_base: str) -> None:
        """Writes a complete .env file for specifying a Bellhop simulation

        Parameters
        ----------
        env : dict
            Environment dict
        taskcode : str
            Task string which defines the computation to run
        fh : file object
            File reference (already opened)
        fname_base : str
            Filename base (without extension)
        :returns fname_base: filename base (no extension) of written file

        We liberally insert comments and empty lines for readability and take care to
        ensure that comments are consistently aligned.
        This doesn't make a difference to bellhop.exe, it just makes debugging far easier.
        """

        self._print_env_line(fh,"")
        self._write_env_header(fh, env)
        self._print_env_line(fh,"")
        self._write_env_surface_depth(fh, env)
        self._write_env_sound_speed(fh, env)
        self._print_env_line(fh,"")
        self._write_env_bottom(fh, env)
        self._print_env_line(fh,"")
        self._write_env_source_receiver(fh, env)
        self._print_env_line(fh,"")
        self._write_env_task(fh, env, taskcode)
        self._write_env_beam_footer(fh, env)
        self._print_env_line(fh,"","End of Bellhop environment file")

        if env['surface_boundary_condition'] == _Strings.from_file:
            self._create_refl_coeff_file(fname_base+".trc", env['surface_reflection_coefficient'])
        if env['surface'] is not None:
            self._create_bty_ati_file(fname_base+'.ati', env['surface'], env['surface_interp'])
        if env['soundspeed_interp'] == _Strings.quadrilateral:
            self._create_ssp_quad_file(fname_base+'.ssp', env['soundspeed'])
        if _np.size(env['depth']) > 1:
            self._create_bty_ati_file(fname_base+'.bty', env['depth'], env['depth_interp'])
        if env['bottom_boundary_condition'] == _Strings.from_file:
            self._create_refl_coeff_file(fname_base+".brc", env['bottom_reflection_coefficient'])
        if env['source_directionality'] is not None:
            self._create_sbp_file(fname_base+'.sbp', env['source_directionality'])

    def _write_env_header(self, fh: TextIO, env: Environment) -> None:
        """Writes header of env file."""
        self._print_env_line(fh,"'"+env['name']+"'","Bellhop environment name/description")
        self._print_env_line(fh,env['frequency'],"Frequency (Hz)")
        self._print_env_line(fh,1,"NMedia -- always =1 for Bellhop")

    def _write_env_surface_depth(self, fh: TextIO, env: Environment) -> None:
        """Writes surface boundary and depth lines of env file."""

        svp_interp = _Maps.soundspeed_interp_rev[env['soundspeed_interp']]
        svp_boundcond = _Maps.surface_boundary_condition_rev[env['surface_boundary_condition']]
        svp_attenuation_units = _Maps.attenuation_units_rev[env['attenuation_units']]
        svp_volume_attenuation = _Maps.volume_attenuation_rev[env['volume_attenuation']]
        svp_alti = _Maps._altimetry_rev[env['_altimetry']]
        svp_singlebeam = _Maps._single_beam_rev[env['_single_beam']]

        comment = "SSP parameters: Interp / Top Boundary Cond / Attenuation Units / Volume Attenuation)"
        topopt = self._quoted_opt(svp_interp, svp_boundcond, svp_attenuation_units, svp_volume_attenuation, svp_alti, svp_singlebeam)
        self._print_env_line(fh,f"{topopt}",comment)

        if env['volume_attenuation'] == _Strings.francois_garrison:
            comment = "Francois-Garrison volume attenuation parameters (sal, temp, pH, depth)"
            self._print_env_line(fh,f"{env['fg_salinity']} {env['fg_temperature']} {env['fg_pH']} {env['fg_depth']}",comment)

        if env['surface_boundary_condition'] == _Strings.acousto_elastic:
            comment = "DEPTH_Top (m)  TOP_SoundSpeed (m/s)  TOP_SoundSpeed_Shear (m/s)  TOP_Density (g/cm^3)  [ TOP_Absorp [ TOP_Absorp_Shear ] ]"
            array_str = self._array2str([
              env['depth_max'],
              env['surface_soundspeed'],
              env['_surface_soundspeed_shear'],
              self._float(env['surface_density'],scale=1/1000),
              env['surface_attenuation'],
              env['_surface_attenuation_shear']
            ])
            self._print_env_line(fh,array_str,comment)

        comment = "[Npts - ignored]  [Sigma - ignored]  Depth_Max"
        self._print_env_line(fh,f"{env['_mesh_npts']} {env['_depth_sigma']} {env['depth_max']}",comment)

    def _write_env_sound_speed(self, fh: TextIO, env: Environment) -> None:
        """Writes sound speed profile lines of env file."""
        svp = env['soundspeed']
        svp_interp = _Maps.soundspeed_interp_rev[env['soundspeed_interp']]
        if isinstance(svp, _pd.DataFrame) and len(svp.columns) == 1:
            svp = _np.hstack((_np.array([svp.index]).T, _np.asarray(svp)))
        if svp.size == 1:
            self._print_env_line(fh,self._array2str([0.0, svp]),"Min_Depth SSP_Const")
            self._print_env_line(fh,self._array2str([env['depth_max'], svp]),"Max_Depth SSP_Const")
        elif svp_interp == "Q":
            for j in range(svp.shape[0]):
                self._print_env_line(fh,self._array2str([svp.index[j], svp.iloc[j,0]]),f"ssp_{j}")
        else:
            for j in range(svp.shape[0]):
                self._print_env_line(fh,self._array2str([svp[j,0], svp[j,1]]),f"ssp_{j}")

    def _write_env_bottom(self, fh: TextIO, env: Environment) -> None:
        """Writes bottom boundary lines of env file."""
        bot_bc = _Maps.bottom_boundary_condition_rev[env['bottom_boundary_condition']]
        dp_flag = _Maps._bathymetry_rev[env['_bathymetry']]
        bot_str = self._quoted_opt(bot_bc,dp_flag)
        comment = "BOT_Boundary_cond / BOT_Roughness"
        self._print_env_line(fh,f"{bot_str} {env['bottom_roughness']}",comment)
        if env['bottom_boundary_condition'] == "acousto-elastic":
            comment = "Depth_Max  BOT_SoundSpeed  BOT_SS_Shear  BOT_Density  BOT_Absorp  BOT_Absorp Shear"
            array_str = self._array2str([
              env['depth_max'],
              env['bottom_soundspeed'],
              env['_bottom_soundspeed_shear'],
              self._float(env['bottom_density'],scale=1/1000),
              env['bottom_attenuation'],
              env['_bottom_attenuation_shear']
            ])
            self._print_env_line(fh,array_str,comment)

    def _write_env_source_receiver(self, fh: TextIO, env: Environment) -> None:
        """Writes source and receiver lines of env file."""
        self._print_array(fh, env['source_depth'], nn=env['source_ndepth'], label="Source depth (m)")
        self._print_array(fh, env['receiver_depth'], nn=env['receiver_ndepth'], label="Receiver depth (m)")
        self._print_array(fh, env['receiver_range']/1000, nn=env['receiver_nrange'], label="Receiver range (km)")

    def _write_env_task(self, fh: TextIO, env: Environment, taskcode: str) -> None:
        """Writes task lines of env file."""
        beamtype = _Maps.beam_type_rev[env['beam_type']]
        beampattern = " " if env['source_directionality'] is None else "*"
        txtype = _Maps.source_type_rev[env['source_type']]
        gridtype = _Maps.grid_type_rev[env['grid_type']]
        runtype_str = self._quoted_opt(taskcode, beamtype, beampattern, txtype, gridtype)
        self._print_env_line(fh,f"{runtype_str}","RUN TYPE")

    def _write_env_beam_footer(self, fh: TextIO, env: Environment) -> None:
        """Writes beam and footer lines of env file."""
        self._print_env_line(fh,self._array2str([env['beam_num'], env['single_beam_index']]),"Num_Beams [ Single_Beam_Index ]")
        self._print_env_line(fh,f"{env['beam_angle_min']} {env['beam_angle_max']} /","ALPHA1,2 (degrees)")
        self._print_env_line(fh,f"{env['step_size']} {env['box_depth']} {env['box_range'] / 1000}","Step_Size (m), ZBOX (m), RBOX (km)")

    def _print(self, fh: TextIO, s: str, newline: bool = True) -> None:
        """Write a line of text with or w/o a newline char to the output file"""
        fh.write(s+'\n' if newline else s)

    def _print_env_line(self, fh: TextIO, data: Any, comment: str = "") -> None:
        """Write a complete line to the .env file with a descriptive comment

        We do some char counting (well, padding and stripping) to ensure the code comments all start from the same char.
        """
        data_str = data if isinstance(data,str) else f"{data}"
        comment_str = comment if isinstance(comment,str) else f"{comment}"
        line_str = (data_str + " " * self.env_comment_pad)[0:max(len(data_str),self.env_comment_pad)]
        if comment_str != "":
            line_str = line_str + " ! " + comment_str
        self._print(fh,line_str)

    def _print_array(self, fh: TextIO, a: Any, label: str = "", nn: Optional[int] = None) -> None:
        """Print a 1D array to the .env file, prefixed by a count of the array length"""
        na = _np.size(a)
        if nn is None:
            nn = na
        if nn == 1 or na == 1:
            self._print_env_line(fh, 1, f"{label} (single value)")
            self._print_env_line(fh, f"{a} /",f"{label} (single value)")
        else:
            self._print_env_line(fh, nn, f"{label}s ({nn} values)")
            for j in a:
                self._print(fh, f"{j} ", newline=False)
            self._print(fh, " /")

    def _array2str(self, values: List[Any]) -> str:
        """Format list into space-separated string, trimmed at first None, ending with '/'."""
        try:
            values = values[:values.index(None)]
        except ValueError:
            pass
        return " ".join(
            f"{v}" if isinstance(v, (int, float)) else str(v)
            for v in values
        ) + " /"

    def _create_bty_ati_file(self, filename: str, depth: Any, interp: _Strings) -> None:
        with open(filename, 'wt') as f:
            f.write(f"'{_Maps.depth_interp_rev[interp]}'\n")
            f.write(str(depth.shape[0])+"\n")
            for j in range(depth.shape[0]):
                f.write(f"{depth[j,0]/1000} {depth[j,1]}\n")

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

    def _create_ssp_quad_file(self, filename: str, svp: _pd.DataFrame) -> None:
        """Write 2D SSP data to file"""
        with open(filename, 'wt') as f:
            f.write(str(svp.shape[1])+"\n") # number of SSP points
            for j in range(svp.shape[1]):
                f.write("%0.6f%c" % (svp.columns[j]/1000, '\n' if j == svp.shape[1]-1 else ' '))
            for k in range(svp.shape[0]):
                for j in range(svp.shape[1]):
                    f.write("%0.6f%c" % (svp.iloc[k,j], '\n' if j == svp.shape[1]-1 else ' '))

    def _quoted_opt(self, *args: str) -> str:
        """Concatenate N input _Strings. strip whitespace, surround with single quotes
        """
        combined = "".join(args).strip()
        return f"'{combined}'"

    def _float(self, x: Optional[float], scale: float = 1) -> Optional[float]:
        """Permissive floatenator"""
        return None if x is None else float(x) * scale
