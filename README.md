# BELLHOP
A mirror of the original Fortran `BELLHOP`/`BELLHOP3D` underwater acoustics
simulators, with numerical properties and robustness improved and bugs fixed.
These changes were made in support of the [multithreaded C++/CUDA version of
BELLHOP/BELLHOP3D: `bellhopcxx`/`bellhopcuda`](https://github.com/A-New-BellHope/bellhopcuda).

### Impressum

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
* See docs/at_index.htm for historic changes

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
