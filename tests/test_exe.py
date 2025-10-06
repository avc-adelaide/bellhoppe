import pytest
import bellhop as bh
import pandas as pd


def test_exe_pass():
    bh.main._Bellhop._run_exe(bh,"tests/Munk_SSP/MunkB_ray_rot", debug=True)
    # no error => test passes

def test_exe_fail():
    with pytest.raises(RuntimeError, match=r"Execution of '.*' failed with return code"):
        bh.main._Bellhop._run_exe(bh,"tests/malformed_env/eof_ssp", debug=True)

def test_exe_not_found():
    with pytest.raises(FileNotFoundError, match=r"Executable (.*) not found in PATH."):
        bh.main._Bellhop._run_exe(bh,"tests/malformed_env/eof_ssp", debug=True, exe="bellhop_not_found.exe")
    # note that bellhop.py would give a better error message when reading that .env file

