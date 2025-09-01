
## Overview

BELLHOP is a beam/ray tracing model for predicting acoustic pressure fields in ocean environments. The model accounts for:

- Sound speed profiles (SSPs) varying with depth and range
- Ocean boundaries (surface and seafloor) with complex reflection properties  
- Acoustic sources and receiver arrays in arbitrary geometries
- Both 2D (range-depth) and 3D (range-depth-azimuth) propagation modeling

The core algorithms implement:
- Geometric ray tracing 
- Gaussian beam superposition for smooth field predictions
- Arrival time and amplitude calculations
- Coherent and incoherent field summation

## Key Components

The BELLHOP system consists of several main modules:

### Core Acoustic Engine
- `bellhop.f90` - Main 2D acoustic propagation program
- `bellhop3D.f90` - 3D acoustic propagation with azimuthal coupling
- `influence.f90` / `influence3D.f90` - Field computation from ray/beam contributions

### Physical Models  
- `sspMod.f90` - Sound speed profile handling and interpolation
- `bdryMod.f90` / `bdry3DMod.f90` - Boundary condition modeling
- `ReflectMod.f90` / `Reflect3DMod.f90` - Reflection coefficient calculations

### Numerical Methods
- `Step.f90` / `Step3DMod.f90` - Ray stepping algorithms with adaptive step control
- `angleMod.f90` - Ray angle calculations and coordinate transformations
- `ArrMod.f90` - Arrival management and caustic handling

### Utilities
- `ReadEnvironmentBell.f90` - Input file parsing and environment setup
- `WriteRay.f90` - Output formatting for ray data
- Mathematical support modules in `misc/`


## Installation and Usage

See the main [README.md](../README.md) for build instructions.

Basic usage:
```
bellhop.exe inputfile  
bellhop3d.exe inputfile
```

Input files use `.env` extension and specify:
- Ocean environment (sound speed, boundaries, bathymetry)
- Source characteristics (frequency, depth, beam pattern)  
- Receiver array geometry
- Run parameters (ray angles, output options)


## Documentation

The BELLHOP code base includes extensive historic documentation from the original 
Acoustics Toolbox project and subsequent development efforts:

### User Guides and Technical Documentation
- **[Original Repository Information](media/index.htm)** - General information about the Acoustics Toolbox project structure
- **[BELLHOP User Guide](media/bellhop.htm)** - Comprehensive guide for 2D acoustic modeling
- **[BELLHOP3D User Guide](media/bellhop3d.htm)** - Guide for 3D acoustic modeling with azimuthal coupling
- **[Environmental File Format](media/EnvironmentalFile.htm)** - Detailed specification of input file formats

### PDF Documentation
- **[BELLHOP3D User Guide (PDF)](media/Bellhop3D%20User%20Guide%202016_7_25.pdf)** - Comprehensive PDF guide for 3D modeling
- **[Technical Report HLS-2010-1](media/HLS-2010-1.pdf)** - Detailed technical documentation

### Change Logs and Development History
- **[University of California Changes](media/CHANGES.md)** - Detailed technical changes, bug fixes, and algorithmic improvements made by the UC San Diego team
- **[Acoustics Toolbox Changes](media/at_changes.md)** - Historical change log from the original Acoustics Toolbox development
- **[Acoustics Toolbox Index](media/at_index.htm)** - Overview of the complete Acoustics Toolbox suite

### Field Computation and Analysis
- **[Field Documentation](media/fields.htm)** - General field computation methods
- **[Field Processing](media/field.htm)** - Field output processing and analysis
- **[3D Field Methods](media/field3d.htm)** - Three-dimensional field computation approaches

### Additional Technical Resources
- **[Reflection Coefficient Files](media/ReflectionCoefficientFile.htm)** - Format for specifying boundary reflection properties
- **[Range-Dependent Sound Speed Profiles](media/RangeDepSSPFile.htm)** - Sound speed profile specification
- **[Bathymetry Files](media/ATI_BTY_File.htm)** - Bathymetry data format specification



## Code Coverage Analysis

BELLHOP includes code coverage analysis using GCOV to assess test suite effectiveness and identify untested code paths.

- **[Coverage Index](media/coverage-index.html)** - Interactive dashboard showing coverage statistics for all source files
 
### Generating Coverage Reports
To generate fresh coverage reports from the test suite:
```bash
make coverage-build # Enable coverage diagnostics in the binary
make install
hatch run test
make coverage-html    # Create reports from generated coverage data
```

The coverage system provides quantitative assessment of test suite completeness and helps identify areas requiring additional testing.