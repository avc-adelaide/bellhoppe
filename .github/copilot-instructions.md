# BELLHOP Underwater Acoustic Simulator

BELLHOP is an underwater acoustic simulator written in Fortran with Python and MATLAB interfaces. This repository contains the forked version maintained by Adelaide University, Australia.

**ALWAYS reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

### Bootstrap, Build, and Install
Bootstrap and build the complete system:
- `make clean` -- cleans build artifacts (harmless error about tests/ is expected)  
- `make` -- compiles Fortran executables. Takes ~19 seconds. NEVER CANCEL. Set timeout to 60+ seconds minimum.
- `make install` -- installs bellhop.exe and bellhop3d.exe to ./bin/. Takes ~0.5 seconds. NEVER CANCEL. Set timeout to 60+ seconds minimum.
- Add binaries to PATH: `export PATH="$PWD/bin:$PATH"`

### Dependencies
Core build requires only:
- `gfortran` (GNU Fortran compiler) - installed by default on most Linux systems
- Standard C compiler (`gcc`) - installed by default
- `make` utility - installed by default

Python interfaces require:
- Python 3.12
- `hatch` package manager (`pipx install hatch`)
- Dependencies: `matplotlib`, `gcovr`, `numpy`, `scipy`, `pandas`, `bokeh` (may fail due to network timeouts in restricted environments)

Optional tools:
- `gcov-15` or `gcov` for coverage analysis
- `ford` for documentation generation

MATLAB interfaces require:
- MATLAB with paths configured per README.md instructions

### Testing
**Fortran Executables:**
- Test basic functionality: Navigate to `examples/Munk` directory
- Run: `bellhop.exe MunkB_ray` (creates .prt and .ray output files)  
- Run: `bellhop.exe MunkB_Coh` (creates .prt and .shd output files)
- Run: `bellhop3d.exe freeBhat` from `examples/Bellhop3DTests/free/` (3D acoustic simulation)

**Python Tests:**
- `export PATH="$PWD/bin:$PATH"`
- `hatch run test` -- runs Python test suite. Takes ~30 seconds when network access available. NEVER CANCEL. Set timeout to 180+ seconds minimum.
- Alternative if hatch not available: `python3 -m pytest tests/ -v`
- **NOTE**: Python tests may fail due to network timeouts downloading dependencies (arlpy, matplotlib). This is expected in restricted environments.

### Manual Validation Scenarios
ALWAYS test acoustic simulation functionality after making changes:

1. **Basic 2D Ray Tracing:**
   ```bash
   cd examples/Munk
   export PATH="$PWD/../../bin:$PATH"
   bellhop.exe MunkB_ray
   # Verify outputs: MunkB_ray.prt (text log), MunkB_ray.ray (ray data)
   ```

2. **2D Coherent Field Simulation:**
   ```bash  
   cd examples/Munk
   export PATH="$PWD/../../bin:$PATH"
   bellhop.exe MunkB_Coh
   # Verify outputs: MunkB_Coh.prt (text log), MunkB_Coh.shd (field data)
   ```

3. **3D Acoustic Simulation:**
   ```bash
   cd examples/Bellhop3DTests/free
   export PATH="$PWD/../../../bin:$PATH"
   bellhop3d.exe freeBhat
   # Verify 3D simulation completes without error
   ```

## Timing Expectations and Critical Warnings

**NEVER CANCEL builds or tests**. Set explicit timeouts:
- `make` build: ~15 seconds actual, **set 60+ second timeout minimum**
- `make install`: ~1 second actual, **set 60+ second timeout minimum**  
- `hatch run test`: ~30 seconds when working, up to 5+ minutes with network issues, **set 180+ second timeout minimum**
- Individual acoustic simulations: typically <1 second, **set 30+ second timeout**
- Coverage builds: ~30-60 seconds, **set 120+ second timeout minimum**

**NETWORK DEPENDENCY ISSUES:**
- Python package installation may fail with network timeouts
- This is expected in restricted environments  
- Document as known limitation: "Python tests fail due to network restrictions"

## Repository Structure and Navigation

### Key Directories
- `fortran/` -- All Fortran source files (bellhop.f90, bellhop3D.f90, 32 .f90 files total)
- `bin/` -- Installed executables (created by `make install`)
- `examples/` -- 267+ example input files across 23+ test scenarios
- `Matlab/` -- MATLAB interfaces and plotting functions
- `python/` -- Python package source code and interfaces
- `tests/` -- Python test suite (7+ test files)
- `docs/` -- Documentation including user guides and change logs

### Important Files  
- `Makefile` (348 lines) -- Main build system with coverage and testing support
- `README.md` -- Installation and usage instructions
- `pyproject.toml` -- Python package configuration with hatch build system
- `fpm.toml` -- FORD documentation generation configuration
- `.github/workflows/check.yml` -- CI/CD pipeline
- `docs/CHANGES.md` -- Detailed change log from UC San Diego team
- `examples/Makefile` -- Example test suite

### Frequently Used Examples
Navigate to these for testing and validation:
- `examples/Munk/` -- Classic Munk sound speed profile tests
- `examples/free/` -- Free space acoustic propagation
- `examples/Bellhop3DTests/free/` -- 3D acoustic simulation examples
- `examples/halfspace/` -- Simple environment tests

## Common Validation Tasks

### After Code Changes
Always run these validation steps:
1. `make clean && make && make install` -- rebuild completely
2. Test basic 2D: `cd examples/Munk && bellhop.exe MunkB_ray`  
3. Test 3D functionality: `cd examples/Bellhop3DTests/free && bellhop3d.exe freeBhat`
4. Run Python tests if network available: `hatch run test`

### Coverage Testing
The build system supports code coverage analysis:
- `make coverage-full` -- Complete coverage build, test, and report generation
- `make coverage-test` -- Run tests with coverage instrumentation
- `make coverage-report` -- Generate GCOV reports
- `make coverage-html` -- Generate HTML coverage reports for FORD integration

### Documentation Generation
- `hatch run doc` -- Generate FORD documentation in `doc/` directory
- `make docs` -- Alternative documentation generation command

### Code Quality and Linting
- `hatch run lint` -- Run fortitude Fortran linter on source code
- Linter checks code style, formatting, and potential issues
- Configuration in pyproject.toml limits line length to 129 characters

### File Output Verification
Successful runs create:
- `.prt` files -- Detailed text logs and results
- `.ray` files -- Ray path data for ray-based runs  
- `.shd` files -- Acoustic field data for coherent field calculations
- Files are typically 1KB-4MB in size

### Debugging Failed Runs
- Check `.prt` files for detailed error messages
- Verify input `.env` files have correct format
- Ensure PATH includes `./bin` directory
- Common issue: Input files require exact format - refer to working examples

## Build System Details

The build uses a modernized Makefile system:
- Root `Makefile` contains all build logic in a single file
- All Fortran sources are unified in the `fortran/` directory
- Compiler flags are optimized for performance (`-O2`, `-ffast-math`)
- Architecture-specific optimizations automatically selected
- Support for coverage builds with GCOV integration
- Hatch package manager integration for Python components

## Network-Independent Operation

Core BELLHOP functionality works without network access:
- Fortran compilation and execution
- All example acoustic simulations  
- MATLAB interfaces (if MATLAB installed)
- Basic functionality testing

Network required only for:
- Python package installation (`matplotlib`, `gcovr`, `numpy`, `scipy`, `pandas`, `bokeh`)
- Full Python test suite execution
- Documentation builds with FORD (if using network-dependent tools)