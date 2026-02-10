# AUBELLHOP: underwater acoustics ray tracing

[![PyPI](https://img.shields.io/pypi/v/aubellhop)](https://pypi.org/project/aubellhop/)
[![Test Suite](https://github.com/avc-adelaide/aubellhop/actions/workflows/check.yml/badge.svg)](https://github.com/avc-adelaide/bellhop/actions/workflows/check.yml)
[![Code Lint](https://github.com/avc-adelaide/aubellhop/actions/workflows/lint.yml/badge.svg)](https://github.com/avc-adelaide/aubellhop/actions/workflows/lint.yml)

## Installation and demo

You can (hopefully) install `aubellhop` with pre-compiled binaries included straight from PyPI.
This short script will create a demo folder, install `aubellhop` using `uv`, and then run the demo function:
```bash
dir=bellhop-example && mkdir -p "$dir" && cd "$dir"
uv init --bare
uv add aubellhop
uv run python -c "import aubellhop as bh; bh.demo()"
```
This creates the demo file `bellhop_demo.py` and runs it.
Then to re-run the demo:
```bash
uv run bellhop_demo.py
```

If you use Python with different build/environment setups, the standard approaches should work just fine:
```bash
pip install aubellhop
```
Followed by setting up a virtual environment with `venv` and so on.

See the [compilation and installation guide](https://avc-adelaide.github.io/aubellhop/page/installation.html) for building from source if you wish to edit the code or the prebuilt binaries don't work for you.

## Documentation

- [Bellhop documentation](https://avc-adelaide.github.io/aubellhop/)
- [aubellhop tutorials](https://avc-adelaide.github.io/aubellhop/media/quarto/index.html)
- [Python API documentation](https://avc-adelaide.github.io/aubellhop/media/python/)
- [Changelog](https://avc-adelaide.github.io/aubellhop/page/CHANGES.html)
- [Github package repository](https://github.com/avc-adelaide/aubellhop)
- [PyPi package site](https://pypi.org/project/aubellhop/)


## Background

* Bellhop is an underwater acoustics simulator, part of the [Acoustics Toolbox](http://oalib.hlsresearch.com/AcousticsToolbox/) by Michael B. Porter and colleagues.

* The Bellhop component of the Acoustics Toolbox has been extracted UCal San Diego to support the [multithreaded C++/CUDA version: `bellhopcuda`](https://github.com/A-New-BellHope/bellhopcuda). The UCal team also [maintain a fork of the Fortran sources](https://github.com/A-New-BellHope/bellhop) with numerical properties and robustness improved and bugs fixed; some of these changes have been back-ported into the Acoustics Toolbox directly but the codebases are no longer identical

* A Python wrapper for Bellhop was previously provided within the [`arlpy` package](https://github.com/org-arl/arlpy) by Mandar Chitre at the Acoustic Research Laboratory, National University of Singapore. arlpy has been superceded by a Julia wrapper by the same author within [UnderwaterAcoustics.jl](https://github.com/org-arl/UnderwaterAcoustics.jl).

* An alternative Python interface is provided in [PYAT](https://github.com/BochicTrdar/PYAT) by Orlando Camargo Rodríguez.

* This repository, from Adelaide University, Australia, is a subsequent consolidation of several components of these works, with the intention of providing a clean and well-documented repository to provide easier access to the Bellhop code. The main features of the AU work are:
    * Consolidation of code files and build processes with a single set of clean sources
    * Adaptation and extension of the `arlpy`-based Python wrapper for Bellhop
    * Updated Fortran source code with automated documentation using FORD and lint checking using `fortitude`
    * Addition of explicit regression and unit test files using `pytest`
    * Continuous integration through Github for all documentation, linting, test suite, and code coverage
    * PyPI packaging with pre-compiled binaries for easy installation across Linux, macOS, and Windows


## Impressum

Copyright (C) 2025-2026 Adelaide University, Australia \
Copyright (C) 2021-2025 The Regents of the University of California Marine Physical Lab at Scripps Oceanography, c/o Jules Jaffe, jjaffe@ucsd.edu \
Copyright (C) 1983-2024 Michael B. Porter

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
