# BELLHOP

* Bellhop is an underwater acoustics simulator, part of the [Acoustics Toolbox](http://oalib.hlsresearch.com/AcousticsToolbox/)
* It has been forked by UCal San Diego to support the [multithreaded C++/CUDA version of
BELLHOP/BELLHOP3D: `bellhopcxx`/`bellhopcuda`](https://github.com/A-New-BellHope/bellhopcuda)
* The UCal team maintain a fork with numerical properties and robustness improved and bugs fixed
* This repository is a subsequent fork from Adelaide University, Australia, with the intention of providing a clean and well-documented repository to provide easier access to the code
* (Yes, it would be better to try not to proliferate forks; if this is successful we will open pull requests)


## Impressum

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


## Documentation Overview

### 📚 Complete Documentation Suite

**[📖 BELLHOP Documentation](https://aumag.github.io/bellhop/)** - Comprehensive API documentation with:
- Automatically generated module and subroutine references
- Interactive call graphs showing code relationships  
- Source code browsing with syntax highlighting
- Full-text search functionality

### 🔧 User Guides and Technical References

**Core Documentation:**
- **[BELLHOP User Guide](docs/bellhop.htm)** - Complete guide for 2D acoustic modeling
- **[BELLHOP3D User Guide](docs/bellhop3d.htm)** - 3D acoustic modeling with azimuthal coupling
- **[Environmental File Format](docs/EnvironmentalFile.htm)** - Input file specifications
- **[BELLHOP3D PDF Guide](docs/Bellhop3D%20User%20Guide%202016_7_25.pdf)** - Comprehensive PDF documentation

**Input File Formats:**
- **[Range-Dependent SSP Files](docs/RangeDepSSPFile.htm)** - Sound speed profile specification
- **[Reflection Coefficient Files](docs/ReflectionCoefficientFile.htm)** - Boundary reflection properties
- **[Bathymetry Files](docs/ATI_BTY_File.htm)** - Bathymetry data format

### 📝 Development History and Changes

**Recent Developments:**
- **[UC San Diego Changes](docs/CHANGES.md)** - Technical improvements, bug fixes, and algorithmic changes
- **[Acoustics Toolbox Changes](docs/at_changes.md)** - Historical development log

**Project Background:**
- **[Acoustics Toolbox Overview](docs/at_index.htm)** - Complete toolbox suite information
- **[Original Repository Info](docs/index.htm)** - Project structure and background

### 🏗️ Building Documentation Locally

Generate documentation on your machine:
```bash
# Install FORD and system dependencies
pip install FORD
sudo apt install graphviz  # Required for call graphs and flow diagrams

# Generate documentation with graphs
make docs
open doc/index.html  # View generated documentation
```


## Installation

### Mac

Use Homebrew to install `gfortran`:

    brew install gfortran

The Makefile should automatically set up the correct compiler flags, in which case run:

    make
    make install

This will install binaries `bellhop(3d).exe` into the `./bin` directory, which should be
added via your standard shell configuration. The Makefile message outputs an example of how
to do this for a `.zshrc` setup.

For using `arlpy` (Python), additional packages are needed. These sometimes require a fixed version of Python,
which at time of writing required something like: (you may not wish to use `venv`, for instance)

    brew install python@3.12
    brew install pipx
    brew install hatch
    
    $(brew --prefix python@3.12)/bin/python3.12 -m venv ~/.venvs/bellhop
    source ~/.venvs/bellhop/bin/activate
    ln -fs `pwd`/bin/bellhop.exe ~/.venvs/bellhop/bin/bellhop.exe

    pip3 install matplotlib
    pip3 install arlpy

### Linux

> [!NOTE]
> This section is work in progress and drafted by copilot.

Install the required dependencies on Ubuntu (for other distributions like RHEL/CentOS/Fedora or Arch Linux, use the appropriate package manager):

```bash
sudo apt update
sudo apt install gfortran liblapack-dev liblapacke-dev python3.12 python3.12-pip python3.12-venv graphviz

# If python3.12 is not available, python3 (>= 3.10) may work but python3.12 is recommended
# sudo apt install gfortran liblapack-dev liblapacke-dev python3 python3-pip python3-venv graphviz
```

Build and install the Fortran executables:
```bash
make
make install
```

This will install `bellhop.exe` and `bellhop3d.exe` in the `./bin` directory. Add this directory to your PATH:
```bash
echo "export PATH=\$PATH:$(pwd)/bin" >> ~/.bashrc
source ~/.bashrc
```

For Python environment setup (recommended using virtual environment):
```bash
# Use python3.12 if installed, otherwise python3
python3.12 -m venv ~/.venvs/bellhop
# OR: python3 -m venv ~/.venvs/bellhop

source ~/.venvs/bellhop/bin/activate

# Install Python dependencies
pip install hatch matplotlib arlpy pytest

# Link bellhop executables to the virtual environment (optional)
ln -s "$(pwd)/bin/bellhop.exe" ~/.venvs/bellhop/bin/bellhop.exe
ln -s "$(pwd)/bin/bellhop3d.exe" ~/.venvs/bellhop/bin/bellhop3d.exe
```

**Note:** Remember to activate the virtual environment in future sessions:
```bash
source ~/.venvs/bellhop/bin/activate
```

### Windows

> [!NOTE]
> This section is work in progress and drafted by copilot.

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

Build and install the Fortran executables:
```bash
make
make install
```

This will install `bellhop.exe` and `bellhop3d.exe` in the `./bin` directory. Add this directory to your PATH:
```bash
echo "export PATH=\$PATH:$(pwd)/bin" >> ~/.bashrc
source ~/.bashrc
```

For Python environment setup (recommended using virtual environment):
```bash
python -m venv ~/.venvs/bellhop
source ~/.venvs/bellhop/bin/activate

# Install Python dependencies
pip install hatch matplotlib arlpy pytest

# Link bellhop executables to the virtual environment (optional)
ln -s "$(pwd)/bin/bellhop.exe" ~/.venvs/bellhop/bin/bellhop.exe
ln -s "$(pwd)/bin/bellhop3d.exe" ~/.venvs/bellhop/bin/bellhop3d.exe
```

**Note:** Remember to activate the virtual environment in future MSYS2 sessions:
```bash
source ~/.venvs/bellhop/bin/activate
```

### Matlab

If you wish to use the Matlab interfaces, the following commands should be added to your
`startup.m` file to add `bellhop` to the Matlab path:

    addpath(genpath('<path to bellhop>/Matlab/'))
    addpath('<path to bellhop>/bin/')







## Testing

If the build and installation steps were successful, you should now be able to run
the Python test suite:

    hatch run test

Alternatively, if you have pytest installed directly, you can run:

    pytest --capture=tee-sys




## Other information

See index.htm for information from the original repo.

Code initially retrieved 12/17/21 from http://oalib.hlsresearch.com/AcousticsToolbox/ ,
the version labeled 11/4/20. In late 2022, the diff between mbp's newer 4/20/22
and 11/4/20 releases was computed, and the changes were applied to this code
(with appropriate changes to integrate them).

Files pertaining to the other simulators (Krakel, Kraken, KrakenField, Scooter)
have been removed.
