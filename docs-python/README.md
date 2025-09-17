# Python API Documentation

This directory contains the Sphinx-based documentation for the BELLHOP Python API.

## Building the Documentation

To build the Python API documentation:

```bash
make python-docs
```

This will generate HTML documentation in `docs-python/_build/html/index.html`.

## Requirements

- Python 3.12+
- Sphinx
- Python dependencies: numpy, scipy, matplotlib, pandas, bokeh

## Contents

- `conf.py` - Sphinx configuration
- `index.rst` - Main documentation page
- `_build/html/` - Generated HTML documentation (created during build)

## Features

The documentation automatically extracts:

- Function docstrings from `python/bellhop/bellhop.py` (47 functions)
- Plotting utilities from `python/bellhop/plot.py`
- Module-level documentation
- Full API reference with source code links
- Search functionality

## Integration

This documentation is designed to complement the existing FORD-generated Fortran documentation and can be integrated into GitHub Pages workflows.