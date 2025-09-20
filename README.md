# The BELLHOP underwater acoustics ray tracing tool

## Documentation

- [Main Bellhop documentation](https://avc-adelaide.github.io/bellhop/)
- [Python API documentation](https://avc-adelaide.github.io/bellhop/media/python/)
- [Fortran code coverage for the new test suite](https://avc-adelaide.github.io/bellhop/media/coverage-index.html)
- [Github repository link](https://github.com/avc-adelaide/bellhop) (what you are reading now)

[![Test Suite](https://github.com/avc-adelaide/bellhop/actions/workflows/check.yml/badge.svg)](https://github.com/avc-adelaide/bellhop/actions/workflows/check.yml)
[![Code Lint](https://github.com/avc-adelaide/bellhop/actions/workflows/lint.yml/badge.svg)](https://github.com/avc-adelaide/bellhop/actions/workflows/lint.yml)


## Background

* Bellhop is an underwater acoustics simulator, part of the [Acoustics Toolbox](http://oalib.hlsresearch.com/AcousticsToolbox/) by Michael B. Porter and colleagues.

* The Bellhop component of the Acoustics Toolbox has been extracted UCal San Diego to support the [multithreaded C++/CUDA version: `bellhopcuda`](https://github.com/A-New-BellHope/bellhopcuda). The UCal team also [maintain a fork of the Fortran sources](https://github.com/A-New-BellHope/bellhop) with numerical properties and robustness improved and bugs fixed; some of these changes have been back-ported into the Acoustics Toolbox directly but the codebases are no longer identical

* A Python wrapper for Bellhop was previously provided within the [`arlpy` package](https://github.com/org-arl/arlpy) by Mandar Chitre at the Acoustic Research Laboratory, National University of Singapore. arlpy has been superceded by a Julia wrapper by the same author within [UnderwaterAcoustics.jl](https://github.com/org-arl/UnderwaterAcoustics.jl).

* This repository, from Adelaide University, Australia, is a subsequent fork and consolidation of these works, with the intention of providing a clean and well-documented repository to provide easier access to the code. The main features of the AU work are:
    * Consolidation of code files and build processes with a single set of clean sources
    * Adaptation and extension of the arlpy-based Python wrapper for Bellhop
    * Updated Fortran source code with automated documentation using FORD and lint checking using fortitude
    * Addition of explicit regression and unit test files using pytest
    * Continuous integration through Github for all documentation, linting, test suite, and code coverage


## Installation

### Mac

Use Homebrew to install `gfortran`:

    brew install gfortran

For using the Python wrapper, additional packages are needed.
These sometimes require a fixed version of Python,
which at time of writing required something like:

    brew install python@3.12
    pip3 install -e .

To run the test suite and compile the package documentation, you will also need:

    brew install hatch FORD graphvis

### Linux

Install the required dependencies on Ubuntu (for other distributions like RHEL/CentOS/Fedora or Arch Linux, use the appropriate package manager):

```bash
sudo apt update
sudo apt install gfortran liblapack-dev liblapacke-dev python3.12 python3.12-pip python3.12-venv graphviz
```


### Windows

Install MSYS2 following the instructions at [https://www.msys2.org/](https://www.msys2.org/).
After installation, open the MSYS2 terminal and install the required development tools:

```bash
# Update the package database
pacman -Syu

# Install development tools and dependencies
pacman -S mingw-w64-x86_64-gcc-fortran mingw-w64-x86_64-gcc make
pacman -S mingw-w64-x86_64-python mingw-w64-x86_64-python-pip
```

Add the MinGW64 tools to your PATH by adding this line to your `~/.bashrc`:
```bash
export PATH="/mingw64/bin:$PATH"
```

### Make

Once you have proceeded with the steps above for your relevant platform, the Makefile
can be used to build the source code.
It should automatically set up the correct compiler flags, in which case run:

    make
    make install

This will install binaries `bellhop(3d).exe` into the `./bin` directory, which should be
added to your path via your standard shell configuration.
The Makefile message outputs an example of how
to do this for a ZSH or BASH setup.


### Python

Although the `hatch` build system should set up paths and environments automatically,
you will likely wish to run Bellhop locally for your own purposes. You can do this with
`hatch` with:

    hatch shell
    <custom scripts running Bellhop>
    exit

Alternatively, to use `venv` directly in a local environment:

    $(brew --prefix python@3.12)/bin/python3.12 -m venv .venv
    ln -fs "$(pwd)/bin/bellhop.exe" .venv/bin/bellhop.exe
    ln -fs "$(pwd)/bin/bellhop3d.exe" .venv/bin/bellhop3d.exe

    source .venv/bin/activate
    <custom scripts running Bellhop>
    deactivate


### Matlab

If you wish to use the Matlab interfaces, the following commands should be added to your
`startup.m` file to add `bellhop` to the Matlab path:

    addpath(genpath('<path to bellhop>/Matlab/'))
    addpath('<path to bellhop>/bin/')




## Testing and linting

If the build and installation steps were successful, you should now be able to run
the Python test suite located in the `tests/` subfolder:

    hatch test

Or:

    make test

The code can be statically tested with the respective Python and Fortran linters with:

    pip install ruff
    hatch run lintp

    pip install fortitude-lint
    hatch run lintf

These steps can be run together with:

    make lint


## Building documentation locally

### Fortran Documentation

Generate Fortran documentation locally with:
```bash
pip install FORD # if needed
hatch run docf
```
This uses FORD to build the HTML documentation in `doc/` with the static pages `docs/` copied
into the `doc/media` subdirectory, with main page `doc/index.html`.

### Python API Documentation

Generate Python API documentation with:
```bash
pip install sphinx # if needed
hatch run docp
```
The generated documentation will be in the `doc/media/python/` subdirectory.

### Make interface

These two steps are combined together with:
```bash
make doc
```


## Code coverage analysis

BELLHOP includes integrated support for code coverage analysis using GCOV.
This helps assess how much of the codebase is exercised by tests and identify areas that may need additional testing.

Generate the code coverage locally with:

    make coverage-full

This requires a complete rebuild of the binary to enable the coverage instrumentation.
The resulting coverage report is saved to `docs/coverage-index.html`.


## Running

Now that you've got this far, head over the to the **[BELLHOP Documentation](https://avc-adelaide.github.io/bellhop/)** to find out more about what the code can do.


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


