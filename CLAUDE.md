# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

AUBELLHOP is an underwater acoustic propagation simulator — the Adelaide University fork of BELLHOP. The core engine is 33 Fortran modules compiled into two executables (`bellhop.exe` for 2D, `bellhop3d.exe` for 3D). The Python package (`python/aubellhop/`) is a high-level wrapper around those binaries.

## Build and Install

```bash
make clean          # remove all build artifacts
make                # compile Fortran (~15–20 s)
make install        # copy executables to ./bin/
export PATH="$PWD/bin:$PATH"
```

**Never cancel a build or test run.** Use these minimum timeouts:
- `make` build: 60 s
- `uv run pytest tests/`: 180 s (can be longer with network issues)
- Individual acoustic simulations: 30 s

## Python Environment

```bash
uv sync --extra dev   # install all Python dependencies
```

Python ≥ 3.12 and `uv` are required. Tests may fail in network-restricted environments when `uv sync` cannot download packages — this is expected and not a code bug.

## Running Tests

```bash
# Full Python test suite
uv run python -m pytest tests/

# Verbose with output capture (good for debugging)
uv run python -m pytest --capture=tee-sys --exitfirst tests/

# Single test file
uv run python -m pytest tests/test_01_simple.py
```

## Manual Validation (always do this after Fortran changes)

```bash
# 2D ray tracing
cd examples/Munk
bellhop.exe MunkB_ray     # produces MunkB_ray.prt, MunkB_ray.ray
bellhop.exe MunkB_Coh     # produces MunkB_Coh.prt, MunkB_Coh.shd

# 3D simulation
cd examples/Bellhop3DTests/free
bellhop3d.exe freeBhat
```

Output files: `.prt` (text log), `.ray` (ray paths), `.shd` (acoustic field), `.arr` (arrivals). Check `.prt` first when debugging — it contains detailed error messages.

## Linting and Type Checking

```bash
make lint       # runs all three linters below
make lintp      # Python: ruff check python/aubellhop/
make typep      # Python: ty check python/aubellhop/ (excludes plotutils.py)
make lintf      # Fortran: fortitude check --line-length 130
```

Max line length is 130 characters for Fortran (129 for Python via ruff).

## Coverage

```bash
make covf           # Fortran coverage (build → test → report → HTML)
make covp           # Python coverage with pytest
make cov            # both

make coverage-full  # alias for the full Fortran pipeline
make coverage-html  # generate HTML reports in _coverage/
```

Fortran coverage uses GCOV; Python coverage output lands in `_coverage_python/`.

## Architecture

### Data Flow

1. Python code constructs an `Environment` object (`python/aubellhop/environment.py`) describing the acoustic scenario.
2. `writers.py` serialises it to a BELLHOP `.env` input file.
3. `bellhop.py` (the `BellhopSimulator` class) shells out to `bellhop.exe` or `bellhop3d.exe`.
4. `readers.py` parses the binary/text output files back into Python structures.
5. `compute.py` exposes high-level functions (`compute_arrivals`, `compute_rays`, `compute_eigenrays`, `compute_transmission_loss`, `arrivals_to_impulse_response`) that orchestrate steps 2–4.
6. `plot.py` / `plotutils.py` / `pyplot.py` visualise the results.

The `Models` registry (`models.py`) holds named `BellhopSimulator` instances so callers don't manage simulator lifecycle manually. `main.py` re-exports the public API surface; `__init__.py` imports from `main.py`.

### Fortran Side

`bellhop.f90` (2D) and `bellhop3D.f90` (3D) are the main programs. Key shared modules:

| Module | Role |
|---|---|
| `sspMod.f90` | Sound speed profile interpolation |
| `influence.f90` / `influence3D.f90` | Gaussian beam superposition (the inner loop) |
| `Step.f90` / `Step3DMod.f90` | Ray-tracing stepping |
| `bdryMod.f90` / `bdry3DMod.f90` | Surface/bottom boundary conditions |
| `ReadEnvironmentBell.f90` | Parses the `.env` input file |
| `ArrMod.f90` | Arrival time/amplitude recording |
| `RefCoef.f90` / `ReflectMod.f90` | Reflection coefficients |

The Fortran `Makefile` in `fortran/` compiles all `.f90` files with `-O2` (disabled for coverage builds, which use `-fprofile-arcs -ftest-coverage`).

### Key API Names

- `aubellhop.Environment` — acoustic scenario container
- `aubellhop.Models` — simulator registry
- `aubellhop.compute_arrivals()`, `compute_rays()`, `compute_eigenrays()`, `compute_transmission_loss()`
- `aubellhop.demo()` — minimal working example

Notable naming change (v0.2): `depth` → `bottom_depth`, `surface` → `surface_depth`.

## CI

`.github/workflows/check.yml` — runs `make test` on Python 3.12, 3.13, 3.14 (ubuntu-latest).  
`.github/workflows/lint.yml` — runs `make lintp`, `make typep`, `make lintf`.  
`.github/workflows/docs.yml` — coverage + FORD/Sphinx/Quarto docs, deploys to GitHub Pages on push to `main`.  
`.github/workflows/publish.yml` — builds multi-platform wheels (Linux/macOS/Windows) via cibuildwheel on version tags.

## Documentation Generation

```bash
make docf   # FORD → docs/_build/index.html
make docp   # Sphinx → docs/_build/media/python/
make docq   # Quarto → docs/_build/media/quarto/
make doc    # all three
```

FORD reads `docs/index.md` with config in `docs/fpm.toml`.

## `make push` Gate

`make push` enforces: clean git working tree → lint → test → `git clean -fx` → `git pull && git push`. Do not bypass it.
