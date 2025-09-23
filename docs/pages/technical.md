---
title: Technical details
---

## Repository contributions

The following are the major changes or additions:

* Remove non-Bellhop files entirely. If other components of the AT should be similarly modernised, in my view independent repositories should be used. The shared code is relatively small.

* Improve Makefile to attempt to auto-configure compiler flags. This is mostly a stub as I have limited platforms and compilers to experiment with.

* Alter the commenting style of the code to permit automatic documentation using FORD. This tool creates the current documentation you are reading.

* Add a Python test suite. This has multiple purposes:

    * Provide a fully documented and automated regression test suite that checks numerical outputs. The original Bellhop tests required manual checking that the output was valid.

    * Integrate the tests with a code coverage tool that allows us to ensure that all possible code paths are tested (work in progress).

    * Allow GitHub workflows to automatically test the repository for every code change. This allows refactoring and algorithm improvements without added risk of introducing bugs.

* The base code compilation processes are based on Makefiles. These have been extended to support the code coverage tool. The [key Makefile](https://github.com/AUMAG/bellhop/blob/main/Makefile) is at the root of the repository.

* A modern build system using Hatch is also used for building documentation and running tests. These are configured using [pyproject.toml](https://github.com/AUMAG/bellhop/blob/main/pyproject.toml). This build system makes the GitHub CI processes quite straightforward to define.

* The documentation system uses FORD, configured using [fdm.toml](https://github.com/AUMAG/bellhop/blob/main/fpm.toml). Executing the documentation process is managed by Hatch with

    hatch run doc

* The test suite uses `pytest` with a build process set up using Hatch. Run the test suite using

    make && make install # if necessary
    hatch run test

* The code coverage system uses both GCC tool `gcov` for Fortran code and `coverage.py` for Python code. This is controlled via the Makefile, with results compiled into HTML files. The unified coverage dashboard provides access to both Fortran and Python coverage reports in a single interface.

* There are two GitHub CI workflows: regression testing, and documentation build (which includes code coverage). They are set up using [check.yml](https://github.com/AUMAG/bellhop/blob/main/.github/workflows/check.yml) and [docs.yml](https://github.com/AUMAG/bellhop/blob/main/.github/workflows/docs.yml).
