# Coverage (GCOV) documentation

## Prerequisites

Coverage analysis requires:
- `gfortran` (GNU Fortran compiler) with GCOV support
- `gcc` to provide `gcov` binary

These are typically available on most Linux systems. On Ubuntu/Debian:

```bash
sudo apt install gfortran
```

## Generating Coverage Reports Locally

To generate and view code coverage reports:

1. **Clean any previous coverage data:**
   ```bash
   make coverage-clean
   ```

2. **Build with coverage instrumentation:**
   ```bash
   make coverage-build
   ```

3. **Install coverage-enabled executables:**
   ```bash
   make coverage-install
   ```

4. **Run tests to generate coverage data:**
   ```bash
   make coverage-test
   ```

5. **Generate coverage reports:**
   ```bash
   make coverage-report
   ```

6. **Or run the complete workflow in one command:**
   ```bash
   make coverage-full
   ```

## Understanding Coverage Reports

The coverage analysis generates several types of files:

- **`.gcno` files**: Coverage note files created during compilation
- **`.gcda` files**: Coverage data files created when running instrumented executables
- **`.gcov` files**: Human-readable coverage reports showing line-by-line execution counts

Coverage reports show:
- **Lines executed**: Percentage of executable lines that were run
- **Branches executed**: Percentage of conditional branches that were taken
- **Calls executed**: Percentage of function/procedure calls that were made

Example coverage output:
```
File 'monotonicMod.f90'
Lines executed:100.00% of 8
Branches executed:100.00% of 16
Taken at least once:62.50% of 16
```

## Viewing Coverage Reports

Coverage reports are available in multiple formats:

### 1. Raw GCOV Files
Coverage reports are created as `.gcov` files in the source directories (`Bellhop/` and `misc/`). Each report shows the original source code with execution counts:

```
        -: 1:!! Monotonicity testing utilities
        1: 2:MODULE monotonicMod
        -: 3:  IMPLICIT NONE
```

Where:
- Numbers indicate how many times each line was executed
- `-` indicates non-executable lines (comments, declarations)
- `#####` indicates executable lines that were never run

### 2. Interactive HTML Reports (FORD Integration)

For enhanced browsability, coverage reports are automatically integrated with the FORD documentation system as interactive HTML reports:

```bash
make coverage-html    # Generate HTML reports in docs/ directory
# Note: Coverage reports are no longer integrated with documentation
make docs            # Generate FORD documentation (separate from coverage)
```

The HTML reports provide:
- **Interactive Coverage Dashboard** - Overview of all source files with coverage statistics
- **Color-Coded Source Views** - Line-by-line coverage visualization with execution counts
- **Coverage Metrics** - Detailed line, branch, and call coverage percentages
- **Browsable Navigation** - Easy switching between different source files

**Accessing HTML Coverage Reports:**
- Locally: Generate with `make coverage-html` then open generated HTML files in the `docs/` directory
- The coverage reports are standalone HTML files, not integrated with FORD documentation

### 3. Coverage Report Features

The HTML coverage reports include:
- **Green highlighting**: Lines executed during testing
- **Red highlighting**: Lines that were never executed
- **Gray highlighting**: Non-executable lines (comments, declarations)
- **Execution counts**: Number of times each line was executed
- **Summary statistics**: Overall coverage percentages for lines, branches, and calls

## GitHub Actions Integration

Code coverage analysis runs automatically in GitHub Actions:

### Coverage Workflow
- **Triggered on**: Pull requests and pushes to the main branch
- **Generates**: Raw GCOV files and HTML coverage reports
- **Uploads**: Coverage artifacts available for download from the Actions page

### Documentation Workflow
- **Separate from coverage**: The documentation workflow generates FORD documentation without coverage integration
- **Independent**: Documentation builds are not dependent on coverage data

## Cleaning Coverage Files

To remove all coverage-related files:

```bash
make coverage-clean
```

This removes `.gcda`, `.gcno`, and `.gcov` files from the repository.

