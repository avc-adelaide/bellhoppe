# The BELLHOP underwater acoustics ray tracing tool

## Documentation

- [Compilation and installation](https://avc-adelaide.github.io/bellhoppe/page/installation.html)
- [Main Bellhop documentation](https://avc-adelaide.github.io/bellhoppe/)
- [bellhop.py tutorials](https://avc-adelaide.github.io/bellhoppe/media/quarto/index.html)
- [Python API documentation](https://avc-adelaide.github.io/bellhoppe/media/python/)
- [Fortran Test Coverage](https://avc-adelaide.github.io/bellhoppe/media/coverage/_coverage/coverage-index.html)
- [Python Test Coverage](https://avc-adelaide.github.io/bellhoppe/media/coverage/_coverage_python/index.html)
- [Github repository link](https://github.com/avc-adelaide/bellhoppe) (what you are reading now)

[![Test Suite](https://github.com/avc-adelaide/bellhoppe/actions/workflows/check.yml/badge.svg)](https://github.com/avc-adelaide/bellhop/actions/workflows/check.yml)
[![Code Lint](https://github.com/avc-adelaide/bellhoppe/actions/workflows/lint.yml/badge.svg)](https://github.com/avc-adelaide/bellhoppe/actions/workflows/lint.yml)


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


## Impressum

Copyright (C) 2025      Adelaide University, Australia \
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


