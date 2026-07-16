"""Tests for Cerveny (paraxial) beam options, 2D.

Covers two bugs fixed together:

1. Fortran: `InfluenceCervenyRayCen` errored with "Unknown RunType" on coherent
   TL runs — the coherent case is a pass-through and must not hit the
   error-handling default branch (`fortran/influence.f90`).
2. Python: `_read_gaussian_params` gated the two extra Cerveny beam lines on
   `(gaussian_simple, ray)` instead of `(cartesian, ray)`, so Cerveny-Cartesian
   env files lost their beam parameters on read, and simple-Gaussian files
   would consume lines that Bellhop itself never reads.
"""

import aubellhop as bh


def test_cerveny_raycen_coherent_exe():
    """Coherent TL with Cerveny ray-centered beams must run to completion."""
    bh.bellhop.BellhopSimulator()._run_exe("tests/Cerveny/CervenyR_Coh", debug=True)
    # no error => test passes


def test_cerveny_cart_coherent_exe():
    """Coherent TL with Cerveny Cartesian beams (control case)."""
    bh.bellhop.BellhopSimulator()._run_exe("tests/Cerveny/CervenyC_Coh", debug=True)


def test_read_cerveny_cartesian_params():
    """Cerveny-Cartesian env files carry two extra beam lines: read them."""
    env = bh.Environment.from_file("tests/Cerveny/CervenyC_Coh.env")
    assert env['beam_type'] == "cartesian"
    assert env['beam_width_type'] == "MS"
    assert env['beam_epsilon_multipler'] == 2.0
    assert env['beam_range_loop'] == 5000.0  # 5 km in file, stored in m
    assert env['beam_images_num'] == 1
    assert env['beam_window'] == 5
    assert env['beam_component'] == "P"


def test_read_cerveny_ray_params():
    """Same two lines for Cerveny ray-centered beams."""
    env = bh.Environment.from_file("tests/Cerveny/CervenyR_Coh.env")
    assert env['beam_type'] == "ray"
    assert env['beam_width_type'] == "MS"
    assert env['beam_epsilon_multipler'] == 2.0
    assert env['beam_range_loop'] == 5000.0
    assert env['beam_images_num'] == 1
    assert env['beam_window'] == 5
    assert env['beam_component'] == "P"


def test_read_sgb_skips_cerveny_lines():
    """Bellhop ignores the Cerveny lines for simple Gaussian beams ('S');
    the reader must skip them too, leaving the beam parameters unset."""
    env = bh.Environment.from_file("tests/Cerveny/SGB_Coh.env")
    assert env['beam_type'] == "gaussian-simple"
    assert env['beam_width_type'] is None
    assert env['beam_epsilon_multipler'] is None
    assert env['beam_range_loop'] is None
    assert env['beam_images_num'] is None
    assert env['beam_window'] is None
    assert env['beam_component'] is None
