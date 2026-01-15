---
title: AUBELLHOP CHANGELOG
---

## [0.1.9] - 2026-01-13

* Remove `hatch` as package system — standardise on `uv`.
* Improve documentation breadth.
* Add `read_ssp_3d()`, `read_ati_3d()`, `read_bty_3d()` for BELLHOP3D


## [0.1.8] - 2025-11-30

* Really fix the wheel building process to omit unnecessary files.
* (I would like to switch from `setuptools` to `hatch` or `uv` but all in good time.)


## [0.1.7] - 2025-11-29

* Try to fix the wheel building process to omit unnecessary files, keeping the installation small.


## [0.1.6] - 2025-11-29

* Add code signing for macOS to avoid overly fussy security features from killing the executable
* Due to naming conflict with another unrelated `bellhop.py`, rename repo and package to `aubellhop`


## [0.1.5] - 2025-11-21

* Intermediate releases mostly just debugging how to get everything reliably into PyPi
* Compilation steps (Makefile flags) improved for more cross-platform and cross-architecture compatibility for the binary releases
* Add `bellhop.demo()` function to get up and running more easily from a fresh install from PyPi
* Building and checking now performed on Python versions 3.12 to 3.14

## [0.1] - 2025-11-17

* Initial PyPi release
* Most bellhop2d and bellhop3d interfaces are supported,
  but may not yet be well-tested and stable
* Visualisation and plotting may yet be re-designed
