---
title: BELLHOP Acoustic Simulator
project: BELLHOP
author: Adelaide University / UC San Diego / Michael B. Porter  
version: 2.0
license: GPL-3.0+
summary: |
  BELLHOP is an underwater acoustic simulator that uses beam/ray tracing 
  to model acoustic wave propagation in ocean environments. It is part of 
  the Acoustics Toolbox and provides both 2D and 3D acoustic modeling capabilities.
  
src_dir: Bellhop
         misc
output_dir: docs_ford
exclude_dir: bin
             examples  
             tests
             Matlab
preprocessor: gfortran -E
project_github: https://github.com/AUMAG/bellhop
project_download: https://github.com/AUMAG/bellhop/releases
email: 
website: 
facebook:
twitter:
linkedin:
google_plus:
github: https://github.com/AUMAG/bellhop
bitbucket:
creation_date: %Y-%m-%d %H:%M %Z
predocmark: >
docmark: !
predocmark_alt: #>
docmark_alt: #!
display: public
         protected
source: true
graph: true
search: true
macro: TEST
       LOGIC=.true.
extra_mods: iso_fortran_env:https://gcc.gnu.org/onlinedocs/gfortran/ISO_005fFORTRAN_005fENV.html
coloured_edges: true
sort: alpha
print_creation_date: true
creation_date: %Y-%m-%d %H:%M %Z
md_extensions: markdown.extensions.toc
               markdown.extensions.smarty
---

## Overview

BELLHOP is a beam/ray tracing model for predicting acoustic pressure fields in ocean 
environments. The model accounts for:

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

## Mathematical Background

The acoustic field is computed using ray theory where sound propagates along 
paths determined by Snell's law. The implementation includes:

- **Ray equations**: Solved using Runge-Kutta integration with adaptive stepping
- **Gaussian beam theory**: Provides smooth field predictions without ray chaos
- **Caustic handling**: Special treatment near focusing regions
- **Boundary interactions**: Reflection/transmission at interfaces

The 3D version extends this by solving the full 3D ray equations with 
azimuthal coupling effects.

## Historic Documentation

The BELLHOP code base includes extensive historic documentation from the original 
Acoustics Toolbox project and subsequent development efforts:

### Change Logs and Development History
- **[University of California Changes](../docs/CHANGES.md)** - Detailed technical changes, bug fixes, and algorithmic improvements made by the UC San Diego team
- **[Acoustics Toolbox Changes](../docs/at_changes.md)** - Historical change log from the original Acoustics Toolbox development
- **[Acoustics Toolbox Index](../docs/at_index.htm)** - Overview of the complete Acoustics Toolbox suite

### User Guides and Technical Documentation
- **[Original Repository Information](../docs/index.htm)** - General information about the Acoustics Toolbox project structure
- **[BELLHOP User Guide](../docs/bellhop.htm)** - Comprehensive guide for 2D acoustic modeling
- **[BELLHOP3D User Guide](../docs/bellhop3d.htm)** - Guide for 3D acoustic modeling with azimuthal coupling
- **[Environmental File Format](../docs/EnvironmentalFile.htm)** - Detailed specification of input file formats

### Field Computation and Analysis
- **[Field Documentation](../docs/fields.htm)** - General field computation methods
- **[Field Processing](../docs/field.htm)** - Field output processing and analysis
- **[3D Field Methods](../docs/field3d.htm)** - Three-dimensional field computation approaches

### Additional Technical Resources
- **[Reflection Coefficient Files](../docs/ReflectionCoefficientFile.htm)** - Format for specifying boundary reflection properties
- **[Range-Dependent Sound Speed Profiles](../docs/RangeDepSSPFile.htm)** - Sound speed profile specification
- **[Bathymetry Files](../docs/ATI_BTY_File.htm)** - Bathymetry data format specification

### PDF Documentation
- **[BELLHOP3D User Guide (PDF)](../docs/Bellhop3D%20User%20Guide%202016_7_25.pdf)** - Comprehensive PDF guide for 3D modeling
- **[Technical Report HLS-2010-1](../docs/HLS-2010-1.pdf)** - Detailed technical documentation

These documents provide valuable context for understanding the full capabilities and 
history of the BELLHOP acoustic modeling system.