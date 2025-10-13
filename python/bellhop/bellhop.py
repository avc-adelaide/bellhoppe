
import os as _os
import re as _re
import subprocess as _proc
import shutil

from struct import unpack as _unpack
from tempfile import mkstemp as _mkstemp
from typing import Any, Dict, List, Optional, Tuple, IO

import numpy as _np
import pandas as _pd

from .constants import Defaults, _Strings, _Maps, _File_Ext

class _Bellhop:
    """
    Interface to the Bellhop 2D underwater acoustics ray tracing propagation model
    
    Parameters
    ----------
    exe : str
        Filename of executable to call Bellhop with
    """

    def __init__(self,
                      exe: Optional[str] = Defaults.exe
                ) -> None:
        self.exe = exe


    def supports(self,
                       env: Optional[Dict[str, Any]] = None,
                       task: Optional[str] = None,
                       exe: Optional[str] = None,
                ) -> bool:
        """Check whether the model supports the task.

           This function is supposed to diagnose whether this combination of environment
           and task is supported by the model, but really it just checks that the binary
           can be found."""

        return shutil.which(exe or self.exe) is not None

    def _rm_files(self, fname_base: str) -> None:
        """Remove files that would be constructed as bellhop inputs or created as bellhop outputs."""
        self._unlink(fname_base+'.bty')
        self._unlink(fname_base+'.ssp')
        self._unlink(fname_base+'.ati')
        self._unlink(fname_base+'.sbp')
        self._unlink(fname_base+'.prt')
        self._unlink(fname_base+'.log')
        self._unlink(fname_base+'.arr')
        self._unlink(fname_base+'.ray')
        self._unlink(fname_base+'.shd')

    def run(self, env: Dict[str, Any], task: str, debug: bool = False, fname_base: Optional[str] = None) -> Any:
        taskmap: Dict[Any, List[Any]] = {
            _Strings.arrivals:     ['A', self._load_arrivals, _File_Ext.arr],
            _Strings.eigenrays:    ['E', self._load_rays, _File_Ext.ray],
            _Strings.rays:         ['R', self._load_rays, _File_Ext.ray],
            _Strings.coherent:     ['C', self._load_shd, _File_Ext.shd],
            _Strings.incoherent:   ['I', self._load_shd, _File_Ext.shd],
            _Strings.semicoherent: ['S', self._load_shd, _File_Ext.shd]
        }
        fname_flag=False
        if fname_base is not None:
            fname_flag = True

        if fname_base:
            print('[CUSTOM FILES] Deleting prior working files: '+fname_base+'.*')
            self._rm_files(fname_base)

        fname_base = self._create_env_file(env, taskmap[task][0], fname_base, debug)

        results = None
        self._run_exe(fname_base)
        try:
            ext = taskmap[task][2]
            results = taskmap[task][1](fname_base, ext)
        except FileNotFoundError:
            raise RuntimeError(f'Bellhop did not generate expected output file ({task})')

        if debug:
            print('[DEBUG] Bellhop working files: '+fname_base+'.*')
        elif fname_flag:
            print('[CUSTOM FILES] Bellhop working files: '+fname_base+'.*')
        else:
            self._rm_files(fname_base)

        return results

    def _run_exe(self, fname_base: str,
                       args: str = "",
                       debug: bool = False,
                       exe: str = None,
                ) -> None:
        """Run the executable and raise exceptions if there are errors."""

        exe_path = shutil.which(exe or self.exe)
        if exe_path is None:
            raise FileNotFoundError(f"Executable ({exe}) not found in PATH.")

        runcmd = [exe_path, fname_base] + args.split()
        if debug:
            print("RUNNING:", " ".join(runcmd))
        result = _proc.run(runcmd, stderr=_proc.STDOUT, stdout=_proc.PIPE, text=True)

        if debug and result.stdout:
            print(result.stdout.strip())

        if result.returncode != 0:
            err = self._check_error(fname_base)
            raise RuntimeError(
                f"Execution of '{exe}' failed with return code {result.returncode}.\n"
                f"\nCommand: {' '.join(runcmd)}\n"
                f"\nOutput:\n{result.stdout.strip()}\n"
                f"\nExtract from PRT file:\n{err}"
            )

    def _check_error(self, fname_base: str) -> Optional[str]:
        try:
            err = ""
            fatal = False
            with open(fname_base+'.prt', 'rt') as f:
                for s in f:
                    if fatal and len(s.strip()) > 0:
                        err += '[FATAL] ' + s.strip() + '\n'
                    if '*** FATAL ERROR ***' in s:
                        fatal = True
        except FileNotFoundError:
            pass
        return err if err != "" else None

    def _unlink(self, f: str) -> None:
        try:
            _os.unlink(f)
        except FileNotFoundError:
            pass

    def _print(self, fh: int, s: str, newline: bool = True) -> None:
        _os.write(fh, (s+'\n' if newline else s).encode())

    COMMENT_PAD = 50

    def _print_env_line(self, fh: int, data: Any, comment: str = "") -> None:
        data_str = data if isinstance(data,str) else f"{data}"
        comment_str = comment if isinstance(comment,str) else f"{comment}"
        line_str = (data_str + " " * self.COMMENT_PAD)[0:max(len(data_str),self.COMMENT_PAD)]
        if comment_str != "":
            line_str = line_str + " ! " + comment_str
        self._print(fh,line_str)

    def _print_array(self, fh: int, a: Any, label: str = "", nn: Optional[int] = None) -> None:
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

    def _open_env_file(self, fname_base: Optional[str]) -> Tuple[int, str]:
        if fname_base is not None:
            fname = fname_base+'.env'
            fh = _os.open(_os.path.abspath(fname), _os.O_WRONLY | _os.O_CREAT | _os.O_TRUNC)
        else:
            fh, fname = _mkstemp(suffix='.env')
            fname_base = fname[:-4]
        return fh, fname_base

    def _create_env_file(self, env: Dict[str, Any], taskcode: str, fname_base: Optional[str] = None, debug: bool = False) -> str:

        fh, fname_base = self._open_env_file(fname_base)

        def _array2str(values: List[Any]) -> str:
            """Format list into space-separated string, trimmed at first None, ending with '/'."""
            try:
                values = values[:values.index(None)]
            except ValueError:
                pass
            return " ".join(
                f"{v}" if isinstance(v, (int, float)) else str(v)
                for v in values
            ) + " /"

        self._print_env_line(fh,"")
        self._print_env_line(fh,"'"+env['name']+"'","Bellhop environment name/description")
        self._print_env_line(fh,env['frequency'],"Frequency (Hz)")
        self._print_env_line(fh,1,"NMedia -- always =1 for Bellhop")
        self._print_env_line(fh,"")

        svp = env['soundspeed']
        svp_interp = _Maps.interp_rev[env['soundspeed_interp']]
        svp_boundcond = _Maps.boundcond_rev[env['surface_boundary_condition']]
        svp_attunits = _Maps.attunits_rev[env['attenuation_units']]
        svp_volatt = _Maps.volatt_rev[env['volume_attenuation']]
        svp_alti = _Maps.surface_rev[env['_altimetry']]
        svp_singlebeam = _Maps.single_beam_rev[env['_single_beam']]

        comment = "SSP parameters: Interp / Top Boundary Cond / Attenuation Units / Volume Attenuation)"
        topopt = self._quoted_opt(svp_interp, svp_boundcond, svp_attunits, svp_volatt, svp_alti, svp_singlebeam)
        self._print_env_line(fh,f"{topopt}",comment)

        if env['volume_attenuation'] == _Strings.francois_garrison:
            comment = "Francois-Garrison volume attenuation parameters (sal, temp, pH, depth)"
            self._print_env_line(fh,f"{env['fg_salinity']} {env['fg_temperature']} {env['fg_pH']} {env['fg_depth']}",comment)

        if env['surface_boundary_condition'] == _Strings.acousto_elastic:
            comment = "DEPTH_Top (m)  TOP_SoundSpeed (m/s)  TOP_SoundSpeed_Shear (m/s)  TOP_Density (g/cm^3)  [ TOP_Absorp [ TOP_Absorp_Shear ] ]"
            array_str = _array2str([
              env['depth_max'],
              env['surface_soundspeed'],
              env['surface_soundspeed_shear'],
              self._float(env['surface_density'],scale=1/1000),
              env['surface_attenuation'],
              env['surface_attenuation_shear']
            ])
            self._print_env_line(fh,array_str,comment)

        elif env['surface_boundary_condition'] == "from-file":
            self._create_refl_coeff_file(fname_base+".trc", env['surface_reflection_coefficient'])

        if env['surface'] is not None:
            self._create_bty_ati_file(fname_base+'.ati', env['surface'], env['surface_interp'])

        comment = "DEPTH_Npts  DEPTH_SigmaZ  DEPTH_Max"
        self._print_env_line(fh,f"{env['depth_npts']} {env['depth_sigmaz']} {env['depth_max']}",comment)

        if isinstance(svp, _pd.DataFrame) and len(svp.columns) == 1:
            svp = _np.hstack((_np.array([svp.index]).T, _np.asarray(svp)))
        if svp.size == 1:
            debug and print("One SSP point only")
            self._print_env_line(fh,_array2str([0.0, svp]),"Min_Depth SSP_Const")
            self._print_env_line(fh,_array2str([env['depth_max'], svp]),"Max_Depth SSP_Const")
        elif svp_interp == "Q":
            debug and print("SSP: Q interpolation")
            for j in range(svp.shape[0]):
                self._print_env_line(fh,_array2str([svp.index[j], svp.iloc[j,0]]),f"ssp_{j}")
            self._create_ssp_quad_file(fname_base+'.ssp', svp)
        else:
            debug and print(f"SSP: standard 2xN array of depths and sound speeds -- interpolation: {svp_interp}")
            for j in range(svp.shape[0]):
                self._print_env_line(fh,_array2str([svp[j,0], svp[j,1]]),f"ssp_{j}")

        self._print_env_line(fh,"")
        bot_bc = _Maps.boundcond_rev[env['bottom_boundary_condition']]
        dp_flag = _Maps.bottom_rev[env['_bathymetry']]
        comment = "BOT_Boundary_cond / BOT_Roughness"
        self._print_env_line(fh,f"{self._quoted_opt(bot_bc,dp_flag)} {env['bottom_roughness']}",comment)

        if _np.size(env['depth']) > 1:
            self._create_bty_ati_file(fname_base+'.bty', env['depth'], env['depth_interp'])

        if env['bottom_boundary_condition'] == "acousto-elastic":
            comment = "Depth_Max  BOT_SoundSpeed  BOT_SS_Shear  BOT_Density  BOT_Absorp  BOT_Absorp Shear"
            array_str = _array2str([
              env['depth_max'],
              env['bottom_soundspeed'],
              env['bottom_soundspeed_shear'],
              self._float(env['bottom_density'],scale=1/1000),
              env['bottom_attenuation'],
              env['bottom_attenuation_shear']
            ])
            self._print_env_line(fh,array_str,comment)

        if env['bottom_boundary_condition'] == "from-file":
            self._create_refl_coeff_file(fname_base+".brc", env['bottom_reflection_coefficient'])

        self._print_env_line(fh,"")
        self._print_array(fh, env['source_depth'], nn=env['source_ndepth'], label="Source depth (m)")
        self._print_array(fh, env['receiver_depth'], nn=env['receiver_ndepth'], label="Receiver depth (m)")
        self._print_array(fh, env['receiver_range']/1000, nn=env['receiver_nrange'], label="Receiver range (km)")
        self._print_env_line(fh,"")

        beamtype = _Maps.beam_rev[env['beam_type']]
        beampattern = " "
        txtype = _Maps.source_rev[env['source_type']]
        gridtype = _Maps.grid_rev[env['grid']]
        if env['source_directionality'] is not None:
            beampattern = "*"
            self._create_sbp_file(fname_base+'.sbp', env['source_directionality'])
        runtype_str = self._quoted_opt(taskcode, beamtype, beampattern, txtype, gridtype)
        self._print_env_line(fh,f"{runtype_str}","RUN TYPE")
        self._print_env_line(fh,_array2str([env['beam_num'], env['single_beam_index']]),"Num_Beams [ Single_Beam_Index ]")
        self._print_env_line(fh,f"{env['beam_angle_min']} {env['beam_angle_max']} /","ALPHA1,2 (degrees)")
        self._print_env_line(fh,f"{env['step_size']} {env['box_depth']} {env['box_range'] / 1000}","Step_Size (m), ZBOX (m), RBOX (km)")
        self._print_env_line(fh,"","End of Bellhop environment file")
        _os.close(fh)
        return fname_base

    def _create_bty_ati_file(self, filename: str, depth: Any, interp: _Strings) -> None:
        with open(filename, 'wt') as f:
            f.write(f"'{_Maps.bty_interp_rev[interp]}'\n")
            f.write(str(depth.shape[0])+"\n")
            for j in range(depth.shape[0]):
                f.write(f"{depth[j,0]/1000} {depth[j,1]}\n")

    def _create_sbp_file(self, filename: str, dir: Any) -> None:
        with open(filename, 'wt') as f:
            f.write(str(dir.shape[0])+"\n")
            for j in range(dir.shape[0]):
                f.write(f"{dir[j,0]}  {dir[j,1]}\n")

    def _create_refl_coeff_file(self, filename: str, rc: Any) -> None:
        with open(filename, 'wt') as f:
            f.write(str(rc.shape[0])+"\n")
            for j in range(rc.shape[0]):
                f.write(f"{rc[j,0]}  {rc[j,1]}  {rc[j,2]}\n")

    def _create_ssp_quad_file(self, filename: str, svp: _pd.DataFrame) -> None:
        with open(filename, 'wt') as f:
            f.write(str(svp.shape[1])+"\n") # number of SSP points
            for j in range(svp.shape[1]):
                f.write("%0.6f%c" % (svp.columns[j]/1000, '\n' if j == svp.shape[1]-1 else ' '))
            for k in range(svp.shape[0]):
                for j in range(svp.shape[1]):
                    f.write("%0.6f%c" % (svp.iloc[k,j], '\n' if j == svp.shape[1]-1 else ' '))

    def _readf(self, f: IO[str], types: Tuple[Any, ...], dtype: type = str) -> Tuple[Any, ...]:
        p = _re.split(r' +', f.readline().strip())
        for j in range(len(p)):
            if len(types) > j:
                p[j] = types[j](p[j])
            else:
                p[j] = dtype(p[j])
        return tuple(p)

    def _load_arrivals(self, fname_base: str, ext: str) -> _pd.DataFrame:
        with open(fname_base+ext, 'rt') as f:
            hdr = f.readline()
            if hdr.find('2D') >= 0:
                freq = self._readf(f, (float,))
                source_depth_info = self._readf(f, (int,), float)
                source_depth_count = source_depth_info[0]
                source_depth = source_depth_info[1:]
                assert source_depth_count == len(source_depth)
                receiver_depth_info = self._readf(f, (int,), float)
                receiver_depth_count = receiver_depth_info[0]
                receiver_depth = receiver_depth_info[1:]
                assert receiver_depth_count == len(receiver_depth)
                receiver_range_info = self._readf(f, (int,), float)
                receiver_range_count = receiver_range_info[0]
                receiver_range = receiver_range_info[1:]
                assert receiver_range_count == len(receiver_range)
#             else: # worry about 3D later
#                 freq, source_depth_count, receiver_depth_count, receiver_range_count = self._readf(hdr, (float, int, int, int))
#                 source_depth = self._readf(f, (float,)*source_depth_count)
#                 receiver_depth = self._readf(f, (float,)*receiver_depth_count)
#                 receiver_range = self._readf(f, (float,)*receiver_range_count)
            arrivals: List[_pd.DataFrame] = []
            for j in range(source_depth_count):
                f.readline()
                for k in range(receiver_depth_count):
                    for m in range(receiver_range_count):
                        count = int(f.readline())
                        for n in range(count):
                            data = self._readf(f, (float, float, float, float, float, float, int, int))
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


    def _load_shd(self, fname_base: str, ext: str) -> _pd.DataFrame:
        with open(fname_base+ext, 'rb') as f:
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


    def _load_rays(self, fname_base: str, ext: str) -> _pd.DataFrame:
        with open(fname_base+ext, 'rt') as f:
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

    def _quoted_opt(self, *args: str) -> str:
        """Concatenate N input _Strings. strip whitespace, surround with single quotes
        """
        combined = "".join(args).strip()
        return f"'{combined}'"

    def _float(self, x: Optional[float], scale: float = 1) -> Optional[float]:
        """Permissive floatenator"""
        return None if x is None else float(x) * scale

