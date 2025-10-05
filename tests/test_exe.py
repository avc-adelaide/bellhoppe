import pytest
import bellhop as bh
import pandas as pd


def test_exe_pass():
    status = bh.bellhop._Bellhop._run_exe(bh,"tests/Munk_SSP/MunkB_ray_rot", debug=True)
    assert status

def test_exe_fail():
    status = bh.bellhop._Bellhop._run_exe(bh,"tests/malformed_env/eof_ssp", debug=True)
    assert not status

def test_exe_testrun_pass():
    status = bh.bellhop._Bellhop._run_exe(bh,"tests/malformed_env/eof_ssp", debug=True, testrun=True, exe="bellhop.exe")
    assert status

def test_exe_testrun_fail():
    status = bh.bellhop._Bellhop._run_exe(bh,"tests/malformed_env/eof_ssp", debug=True, testrun=True, exe="does_not_exist.exe")
    assert not status
