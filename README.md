# BELLHOP

* Bellhop is an underwater acoustics simulator, part of the [Acoustics Toolbox](http://oalib.hlsresearch.com/AcousticsToolbox/)
* It has been forked by UCal San Diego to support the [multithreaded C++/CUDA version of
BELLHOP/BELLHOP3D: `bellhopcxx`/`bellhopcuda`](https://github.com/A-New-BellHope/bellhopcuda)
* The UCal team maintain a fork with numerical properties and robustness improved and bugs fixed
* This repository is a subsequent fork from Adelaide University, Australia, with the intention of providing a clean and well-documented repository to provide easier access to the code
* (Yes, it would be better to try not to proliferate forks; if this is successful we will open pull requests)

### Impressum

Copyright (C) 2025 Adelaide University, Australia \
Copyright (C) 2021-2023 The Regents of the University of California \
Marine Physical Lab at Scripps Oceanography, c/o Jules Jaffe, jjaffe@ucsd.edu \
Copyright (C) 1983-2022 Michael B. Porter

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

# Changes

* See docs/CHANGES.md for University of California changes to the code
* See docs/at_index.htm for changes by the Acoustics Toolbox team

# Source build

## Mac

Use Homebrew to install `gfortran`:

    brew install gfortran

The Makefile should automatically set up the correct compiler flags, in which case run:

    make
    make install

This will install binaries `bellhop(3d).exe` into the `./bin` directory, which should be
added via your standard shell configuration. The Makefile message outputs an example of how
to do this for a `.zshrc` setup.

## Linux

(todo)

## Windows

(todo)

# Installation

## Matlab

If you wish to use the Matlab interfaces 

# Other information

See index.htm for information from the original repo.

Code initially retrieved 12/17/21 from http://oalib.hlsresearch.com/AcousticsToolbox/ ,
the version labeled 11/4/20. In late 2022, the diff between mbp's newer 4/20/22
and 11/4/20 releases was computed, and the changes were applied to this code
(with appropriate changes to integrate them).

Files pertaining to the other simulators (Krakel, Kraken, KrakenField, Scooter)
have been removed.

The Makefile has been set up to build with gfortran by default (Linux or
Windows with mingw etc.)
