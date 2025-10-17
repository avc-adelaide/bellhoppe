---
title: Usage
---

## Building

See the main [README](https://github.com/avc-adelaide/bellhoppe#installation) for build and installation instructions.

## Fortran

Basic usage:
```
bellhop.exe inputfile
bellhop3d.exe inputfile
```

Input files have an `.env` extension and specify:
- Ocean environment (sound speed, boundaries, bathymetry)
- Source characteristics (frequency, depth, beam pattern)
- Receiver array geometry
- Run parameters (ray angles, output options)

Additional text files can be provided to define tables of sound speed profile (.ssp), bathometry (.bty), and so on.

## Python

A modern [Python interface](media/python/index.html) is provided in this package. Basic usage:
```
    TODO
```
This allows reading and writing of bellhop-native input and output files, with a modern Python interface for specifying parameters and executing calculation tasks.

The automated test suite for this repository is written using this Python `bellhop` module.

This Python interface is extended from the [`arlpy` module `uwapm`](https://arlpy.readthedocs.io/en/latest/uwapm.html) by Mandar Chitre.

## Documentation

The BELLHOP code base includes extensive historic documentation from the original
Acoustics Toolbox project and subsequent development efforts:

### User guides
- **[Python documentation](media/python/index.html)** - Interface to Bellhop using high-level Python approaches
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
- **[Field Documentation](media/fields.htm)** - General field computation methods
- **[Field Processing](media/field.htm)** - Field output processing and analysis
- **[3D Field Methods](media/field3d.htm)** - Three-dimensional field computation approaches

### PDF documentation
- **[BELLHOP3D User Guide (PDF)](media/Bellhop3D%20User%20Guide%202016_7_25.pdf)** - Comprehensive PDF guide for 3D modeling
- **[Technical Report HLS-2010-1](media/HLS-2010-1.pdf)** - Detailed technical documentation

### Additional material
- **[Fortran Coverage](media/coverage/_coverage/coverage-index.html)** - Code coverage analysis for Fortran acoustic simulation components
- **[Python Coverage](media/coverage/_coverage_python/index.html)** - Code coverage analysis for Python API and utilities
- **[University of California Changes](media/CHANGES.md)** - Detailed technical changes, bug fixes, and algorithmic improvements made by the UC San Diego team
- **[Acoustics Toolbox Changes](media/at_changes.md)** - Historical change log from the original Acoustics Toolbox development



## Repository architecture

As a historic codebase, Bellhop is impressively portable and easy to compile.
This repository serves as a largely untouched extraction of Bellhop from the broader Acoustics Toolbox code.

### Repository contributions

The following are the major changes or additions:

* Remove non-Bellhop files entirely. If other components of the AT should be similarly modernised, in my view independent repositories should be used. The shared code is relatively small.

* Improve Makefile to attempt to auto-configure compiler flags. This is mostly a stub as I have limited platforms and compilers to experiment with.

* Alter the commenting style of the code to permit automatic documentation using FORD. This tool creates the current documentation you are reading.

* Add a Python test suite. This has multiple purposes:

    * Provide a fully documented and automated regression test suite that checks numerical outputs. The original Bellhop tests required manual checking that the output was valid.

    * Integrate the tests with a code coverage tool that allows us to ensure that all possible code paths are tested (work in progress).

    * Allow GitHub workflows to automatically test the repository for every code change. This allows refactoring and algorithm improvements without added risk of introducing bugs.

