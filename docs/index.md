
## Overview

BELLHOP is a beam/ray tracing model by Michael B. Porter (Heat, Light, and Sound Research, Inc.) for predicting acoustic pressure fields in ocean environments. The model accounts for:

- Sound speed profiles (SSPs) varying with depth and range
- Ocean boundaries (surface and seafloor) with complex reflection properties
- Acoustic sources and receiver arrays in arbitrary geometries
- Both 2D (range-depth) and 3D (range-depth-azimuth) propagation modeling

The core algorithms implement:

- Geometric ray tracing
- Gaussian beam superposition for smooth field predictions
- Arrival time and amplitude calculations
- Coherent and incoherent field summation


## Documentation

The BELLHOP code base includes extensive historic documentation from the original
Acoustics Toolbox project and subsequent development efforts:

### User guides
- **[Compilation and installation](page/installation.html)** - If you need/want to build from source
- **[Getting started](page/index.html)** - Overview of both Fortran and Python interfaces
- **[aubellhop tutorials](media/quarto/index.html)** — Detailed "howto" documentation for `aubellhop`
- **[aubellhop API reference](media/python/index.html)** - API interface to Bellhop using Python
- **[BELLHOP User Guide](media/bellhop.htm)** - Original guide for 2D acoustic modeling
- **[BELLHOP3D User Guide](media/bellhop3d.htm)** - Original guide for 3D acoustic modeling with azimuthal coupling

### Text file formats
- **[Environmental File Format](media/EnvironmentalFile.htm)** - Detailed specification of input environment file
- **[Reflection Coefficient Files](media/ReflectionCoefficientFile.htm)** - Format for specifying boundary reflection properties
- **[Range-Dependent Sound Speed Profiles](media/RangeDepSSPFile.htm)** - Sound speed profile specification
- **[Bathymetry Files](media/ATI_BTY_File.htm)** - Bathymetry data format specification

### Original Acoustics Toolbox documentation
- **[Original Repository Information](media/doc_index.htm)** - General information about the Acoustics Toolbox project structure
- **[Acoustics Toolbox Index](media/at_index.htm)** - Overview of the complete Acoustics Toolbox suite

### PDF documentation
- **[BELLHOP3D User Guide (PDF)](media/Bellhop3D%20User%20Guide%202016_7_25.pdf)** - Comprehensive PDF guide for 3D modeling
- **[Technical Report HLS-2010-1](media/HLS-2010-1.pdf)** - Detailed technical documentation

### Coverage documentation
- **[Coverage details](page/coverage.html)**
- **[Fortran Coverage](media/coverage/_coverage/coverage-index.html)** - Code coverage analysis for Fortran acoustic simulation components
- **[Python Coverage](media/coverage/_coverage_python/index.html)** - Code coverage analysis for Python API and utilities

### Changelogs
- **[AUBELLHOP Changes](page/CHANGES.html)**
- **[University of California Changes](page/changes_uc.html)**
- **[Acoustics Toolbox Changes](page/changes_at.html)**

### Miscellaneous
- [Code repository](https://github.com/avc-adelaide/aubellhop)
- [Repository information](page/technical.html)
- [Compiler notes from original Makefile](page/compiler.html)
