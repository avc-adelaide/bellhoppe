---
title: Compilation and installation
---

## Installation -- PyPI

### `uv`

`aubellhop` is distributed through PyPI with precompiled binaries.
It should be enough to get started using:

```bash
mkdir bhex && cd bhex
uv init --bare
uv add aubellhop
uv run python -c "import aubellhop as bh; bh.demo()"
```

I strongly recommend using `uv` for command line use, as it avoids the need to set up `pip` and virtual environments manually.
Using a Jupyter notebook is likely more convenient for more in-depth studies.

## Installation -- manual

### Mac

Use Homebrew to install `gfortran`:

    brew install gfortran

For using the Python wrapper, additional packages are needed.
These sometimes require a fixed version of Python,
which at time of writing required something like:

    brew install python@3.12
    pip3 install -e .

To run the test suite and compile the package documentation, you will also need:

    brew install FORD graphvis

### Linux

Install the required dependencies on Ubuntu (for other distributions like RHEL/CentOS/Fedora or Arch Linux, use the appropriate package manager):

```bash
sudo apt update
sudo apt install gfortran liblapack-dev liblapacke-dev python3.12 python3.12-pip python3.12-venv graphviz
```


### Windows

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

### Make

Once you have proceeded with the steps above for your relevant platform, the Makefile
can be used to build the source code.
It should automatically set up the correct compiler flags, in which case run:

    make
    make install

This will install binaries `bellhop(3d).exe` into the `./bin` directory, which should be
added to your path via your standard shell configuration.
The Makefile message outputs an example of how
to do this for a ZSH or BASH setup.



### Matlab

If you wish to use the Matlab interfaces, the following commands should be added to your
`startup.m` file to add `bellhop` to the Matlab path:

    addpath(genpath('<path to bellhop>/Matlab/'))
    addpath('<path to bellhop>/bin/')




## Testing and linting

If the build and installation steps were successful, you should now be able to run
the Python test suite located in the `tests/` subfolder:

    make test

The code can be statically tested with the respective Python and Fortran linters with:

    pip install ruff
    make lintp

    pip install fortitude-lint
    make lintf

The Python code can also be type checked using:

    make typep

These steps can all be run together with:

    make lint


## Building documentation locally

### Fortran Documentation

Generate Fortran documentation locally with:

    pip install FORD # if needed
    make docf

This uses FORD to build the HTML documentation in `doc/` with the static pages `docs/` copied
into the `doc/media` subdirectory, with main page `doc/index.html`.

### Python API Documentation

Generate Python API documentation with:

    pip install sphinx # if needed
    make docp

The generated documentation will be in the `doc/media/python/` subdirectory.

### Quarto tutorials

    brew install --cask quarto # Mac, if needed
    make docq

### Make interface

These steps are all combined together with:

    make doc


## Code coverage analysis

BELLHOP includes integrated support for code coverage analysis using GCOV.
This helps assess how much of the codebase is exercised by tests and identify areas that may need additional testing.

Generate the code coverage locally with:

    make cov

This requires a complete rebuild of the binary to enable the coverage instrumentation.
The resulting coverage report is saved to `docs/coverage-index.html`.


## Running

Now that you've got this far, head over the to the **[BELLHOP Documentation](https://avc-adelaide.github.io/aubellhop/)** to find out more about what the code can do.
