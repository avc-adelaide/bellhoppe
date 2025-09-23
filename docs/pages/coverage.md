# Coverage Documentation

BELLHOP supports comprehensive code coverage analysis for both **Fortran** and **Python** components, providing insights into code execution and test effectiveness.

## Prerequisites

Coverage analysis requires:

**For Fortran Coverage:**
- `gfortran` (GNU Fortran compiler) with GCOV support
- `gcc` to provide `gcov` binary

**For Python Coverage:**
- Python 3.12+
- `coverage` package (included in dev dependencies)

These are typically available on most Linux systems. On Ubuntu/Debian:

```bash
sudo apt install gfortran
pip install coverage
```

## Generating Coverage Reports Locally

### Complete Coverage Analysis (Recommended)

To generate comprehensive coverage reports for both Fortran and Python:

```bash
make coverage-full
```

This single command performs the complete workflow:
- Cleans previous coverage data
- Builds Fortran code with coverage instrumentation  
- Runs all tests with coverage collection
- Generates HTML reports for both Fortran and Python
- Creates a unified coverage dashboard

### Individual Coverage Components

You can also run coverage analysis for individual components:

**Fortran Coverage Only:**
```bash
make coverage-clean
make coverage-build
make coverage-install
make coverage-test
make coverage-report
make coverage-html
```

**Python Coverage Only:**
```bash
make python-coverage-test
make python-coverage-report
make python-coverage-html
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

### 1. Unified Coverage Dashboard

Access both Fortran and Python coverage from a single entry point:

```bash
make coverage-full    # Generate all coverage reports
# Open _coverage_unified/index.html in web browser
```

The unified dashboard provides:
- **Navigation Links** - Direct access to both Fortran and Python coverage reports
- **Status Indicators** - Shows which coverage reports are available
- **Coverage Overview** - Summary information for both languages

### 2. Individual Report Access

**Fortran Coverage (GCOV):**
- Raw text reports: Check `.gcov` files in `fortran/` directory
- HTML reports: Open `_coverage/coverage-index.html`

**Python Coverage:**
- Console report: `make python-coverage-report`
- HTML reports: Open `_coverage_python/index.html`

### 3. Coverage Report Features

**Fortran Reports:**
- Line-by-line execution counts
- Branch coverage analysis 
- Call coverage statistics
- Color-coded coverage visualization

**Python Reports:**
- Statement coverage percentages
- Missing line identification
- Function and class coverage
- Interactive source code browsing
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
- **Generates**: Complete coverage analysis for both Fortran (GCOV) and Python (coverage.py)
- **Uploads**: All coverage artifacts (HTML reports, unified dashboard) to GitHub Pages
- **Provides**: Direct access to coverage reports through the online documentation

### Workflow Steps
1. **Build Phase**: Compiles Fortran code with coverage instrumentation
2. **Test Phase**: Runs full test suite with coverage collection for both languages
3. **Report Generation**: Creates HTML reports and unified coverage dashboard
4. **Deployment**: Uploads coverage reports to GitHub Pages for easy access

### Accessing Reports
Coverage reports are automatically published to GitHub Pages and linked from the main documentation at:
- **Unified Dashboard**: `/coverage/index.html` - Single entry point for all coverage reports
- **Fortran Coverage**: `/coverage/_coverage/coverage-index.html` - Detailed Fortran coverage
- **Python Coverage**: `/coverage/_coverage_python/index.html` - Detailed Python coverage

## Cleaning Coverage Files

To remove all coverage-related files:

```bash
make coverage-clean
```

This removes:
- Fortran coverage data (`.gcda`, `.gcno`, `.gcov` files)
- Python coverage data (`.coverage` file)
- Generated HTML reports (`_coverage/`, `_coverage_python/`, `_coverage_unified/`)

