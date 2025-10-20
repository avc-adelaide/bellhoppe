---
title: Usage
---

## Getting started

* [Installation instructions](page/installation.html)

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

Bellhop writes output files in either text or binary form (depending on the data), which
can be post-processed and visualised using either Matlab or Python tools.

Although this repository provides a comprehensive Python wrapper for running the Fortran
executable, being able to use the binary directly is recommended for debugging purposes.

## Python

A modern [Python interface](media/python/index.html) is provided in this package. Basic usage:
```
import bellhop as bh
import bellhop.plot as bhp

env = bh.create_env() # create a default example environment
arr = bh.compute_arrivals(env)
bhp.plot_arrivals(arr,env=env)
```
This approach uses a modern Python interface for specifying parameters and executing calculation tasks, by writing bellhop-native input files to disk.

The Python interface also allows reading input files directly:
```
import bellhop as bh
import bellhop.plot as bhp

env = bh.read_env("tests/MunkB_geo_rot/MunkB_geo_rot.env")
tl = bh.compute_transmission_loss(env)
bhp.plot_transmission_loss(tl,env=env)
```
Secondary files such as sound speed profiles (SSP), bathymetry (BTY), and others, are
automatically written.

The automated test suite for this repository is written using this Python `bellhop` module.

This Python interface is extended from the [`arlpy` module `uwapm`](https://arlpy.readthedocs.io/en/latest/uwapm.html) by Mandar Chitre.
