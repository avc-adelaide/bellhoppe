#
# To install the Acoustics Toolbox:
#
# 1) Uncomment the appropriate lines below to select your FORTRAN compiler
#    (also be sure to comment out all of the lines corresponding to the other compilers).

# 2) If you're using gfortran check the -march switch that selects the chip you're using.
#    Usually -march=native works

# 3) From a command line shell, run:
#    % make clean
#    % make

# on some machines you need to say -mcmodel=medium (or large) to allow for variables larger than 2 gig

# *** Windows ***
# If you don't have a FORTRAN compiler, the MinGW ("Minimalist GNU for Windows") compiler suite
# is a good choice as it is much easier to install than Cygwin. See http://www.mingw.org/ for details.
# Not sure if this is still necessary, but we used to have to change the options -O3 to -O2 below when using gfortran

# *** Linux ***
# Most Linux distributions have gfortran already packaged and it can be installed with the respective 
# package manager (e.g. apt-get, dnf, yum). The packaged versions of the LAPACK library are generally
# compatible with Krakel. If you want statically linked executables, "-static" works with gfortran.

# *** Mac ***
# The option to create an executable that uses a static library has been a problem.
# The gcc community seems to feel that dynamic vs. static libraries is an issue of religious importance.
# I prefer static libraries because users have a lot fewer problems installing the code when they don't have
# to worry about getting the LD_LIBRARY_PATH set, or the fact that some programs (e.g. Matlab) may reset
# that path to an incompatible version.
# -static is supposed to work if gfortran has been compiled to enable that option.
# However, crt0.o comes up as misssing
# -Bstatic worked

# The make utility tends to get confused with modules because it does not necessarily update the *.mod file
# when it compiles the *.f90 file. (The *.mod file contains interface information that doesn't necessarily change
# even then the *.f90 file has changed.)
# As a result, you may find that make keeps compiling a module, that was already compiled.
# A 'make clean' will fix that
# ______________________________________________________________________________

# *** ifort
# These lines are used under Mac OSX; the syntax is different under Windows
# !!!!!!! You also need to use xiar instead of ar
# That change needs to be made in at/misc/Makefile and at/tslib/Makefile
# Note that the -assume byterecl is important, otherwise the output files have the wrong format

# If you use the -parallel option, the compiler links into a dynamic library for OpenMP
# Then you need to make sure that dylib is in the path

# Choose the best architecture (target machine) using the -x switch
# According to the latest benchmarks on polyhedron, it looks like -parallel is very helpful

# need -heap-arrays to avoid stack overflows for big runs ...
# export FC=ifort
# export FFLAGS= -O3 -parallel -axSSE4.2 -nologo -inline-level=2 -assume byterecl -threads -heap-arrays
# export FFLAGS= -fast -axAVX                           -parallel              -nologo -inline-level=2 -assume byterecl -threads -heap-arrays
# export FFLAGS= -O3 -axAVX              -funroll-loops -parallel -no-prec-div -nologo -inline-level=2 -assume byterecl -threads -heap-arrays
# export FFLAGS= -O3 -axAVX              -funroll-loops -parallel -no-prec-div -nologo -inline-level=2 -assume byterecl -threads -heap-arrays
# export FFLAGS= -O3 -xHost -qopt-report -funroll-loops -parallel -no-prec-div -nologo -inline-level=2 -assume byterecl -threads -heap-arrays
# export FFLAGS= -O3 -xHost              -funroll-loops           -no-prec-div -nologo -inline-level=2 -assume byterecl -threads -heap-arrays

# recommended settings from POLYHEDRON site
# export FFLAGS= -O3 -fast           -ipo -nostandard-realloc-lhs
# export FFLAGS= -O3 -fast -parallel -ipo -nostandard-realloc-lhs
# export FFLAGS= -O3 -fast -parallel -ipo -no-prec-div                                       -assume byterecl -heap-arrays
# export FFLAGS= -O3 -fast -parallel -ipo -no-prec-div -qopt-report-phase=par -qopt-report:5 -assume byterecl -heap-arrays
# export FFLAGS= -O3 -nologo                                               -inline-level=2 -assume byterecl -threads -heap-arrays
# export FFLAGS= -O3 -ipo -funroll-loops -xAVX -no-prec-div -axAVX -nologo -inline-level=2 -assume byterecl -threads -heap-arrays

# compilation diagnostics on:
# export FFLAGS= -O3 -fast -parallel -ipo -nostandard-realloc-lhs -nologo -inline-level=2 -assume byterecl -threads -heap-arrays -check -traceback
# export FFLAGS= -O3 -fast           -ipo -nostandard-realloc-lhs -nologo -inline-level=2 -assume byterecl -threads -heap-arrays -check -traceback

# runtime diagnostics on as well:
#export FFLAGS= -nologo     -inline-level=2 -assume byterecl -threads -heap-arrays -check all -ftrapuv -fpe0 -gen-interfaces -traceback
# export FFLAGS= -nologo     -inline-level=2 -assume byterecl -threads -heap-arrays -check all -ftrapuv                       -traceback -check noarg_temp_created

# profiling:
# export FFLAGS= -g -O3 -profile-functions -profile-loops=all -xHost -nologo -inline-level=2 -assume byterecl -threads -heap-arrays -traceback

###########export FFLAGS+= -I/opt/intel/compilers_and_libraries_2018.2.164/mac/compiler/lib/libiomp5.dylib

# ______________________________________________________________________________

# *** GNU Compiler Collection GFORTRAN

# use -march=generic if you get warning messages about instructions that don't make sense
# -march=generic assumes an old Intel architecture that the newer versions can all execute (slowly)
# -march=native should normally be the best; however, it produced AVX instructions on the Mac that the default assembler could not process
# -O2 was the highest level of optimization that worked under Windows

# -static can be used to tell gfortran not to rely on a dynamic link library (the compiler may or may not support)
# -static does not seem to work on Macs though, and produces larger executables

# Have had various problems where some installed dynamic link library is incompatible with the one the compiler used and expects at run time
# For instance, Matlab changes paths and may point to an incompatible library.
# One user found that it was necessary to delete /usr/local/gfortran/lib/libquadmath.dylib to force a static link. See:
# http://stackoverflow.com/questions/17590525/correct-way-to-statically-link-in-gfortran-libraries-on-osx
#
# The -Wa,-q flag can be used to select the Mac CLANG assembler instead of the GNU assembler
# At one time that was necessary to get the AVX operations; however, I saw no speed benefit
# -march=corei7-avx works on my Mac

export FC=gfortran

# export FFLAGS= -march=native  -Wall -std=gnu -O3 -ffast-math -funroll-all-loops -msse3 -fomit-frame-pointer -mtune=native -Q
# export FFLAGS= -march=corei7 -Bstatic -Waliasing -Wampersand -Wsurprising -Wintrinsics-std -Wno-tabs -Wintrinsic-shadow -Wline-truncation       -std=f2008 -O3 -ffast-math -funroll-all-loops -fomit-frame-pointer -mtune=native
# -L/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.8.sdk/usr/lib
# export FFLAGS= -march=corei7 -Bstatic -Waliasing -Wampersand -Wsurprising -Wintrinsics-std -Wno-tabs -Wintrinsic-shadow -Wline-truncation        -std=f2008 -O3 -ffast-math -funroll-all-loops -fomit-frame-pointer
# export FFLAGS= -march=native          -Waliasing -Wampersand -Wsurprising -Wintrinsics-std -Wno-tabs -Wintrinsic-shadow -Wline-truncation -Wa,-q -std=f2008 -O3 -ffast-math -funroll-all-loops -fomit-frame-pointer -mtune=native

# Detect architecture
UNAME_M := $(shell uname -m)

# Base flags (common to all)
FFLAGS_BASE = -g -Waliasing -Wampersand -Wsurprising -Wintrinsics-std -Wno-tabs -Wintrinsic-shadow -Wline-truncation -std=gnu -frecursive 
FFLAGS_OPTIM = -O2 -ffast-math -funroll-all-loops -fomit-frame-pointer

# Arch-specific flags
ifeq ($(UNAME_M),x86_64) # Windows/Intel/Linux Intel
    FFLAGS_ARCH = -march=native -mtune=native
else ifeq ($(UNAME_M),arm64) # Apple Silicon
    FFLAGS_ARCH = -mcpu=apple-m2
else ifeq ($(UNAME_M),aarch64) # Linux ARM (e.g., Raspberry Pi, ARM server)
    FFLAGS_ARCH = -march=armv8.5-a
else
    $(warning Unknown architecture $(UNAME_M), using generic flags)
    FFLAGS_ARCH =
endif

# Coverage flags (for GCOV code coverage analysis)
FFLAGS_COVERAGE = -fprofile-arcs -ftest-coverage

# Combine
FFLAGS = $(FFLAGS_BASE) $(FFLAGS_OPTIM) $(FFLAGS_ARCH)
export FFLAGS

# Compilation and run-time diagnostics on:
# omni.env fails trap=invalid
# export FFLAGS= -march=native -ffpe-trap=invalid,zero,overflow -Wall                  -std=gnu -O1 -fcheck=all -fbacktrace
# export FFLAGS= -march=native -ffpe-trap=zero,overflow         -Wall                  -std=gnu -O1 -fcheck=all -fbacktrace
# export FFLAGS= -march=native -ffpe-trap=zero,overflow         -Wall -pedantic-errors -std=gnu -O1 -g -fcheck=all -fbacktrace

# Profiling:
# I read that the -pg flag is needed for profiling, but there's some problem with the library and it doesn't compile
# It does compile with just the -p and -g flags but does not appear to have enough info for the xcode instruments
# export FFLAGS= -p -g -pg -march=native -Wall -std=gnu
# export FFLAGS= -p -g -march=native -Bstatic -Wa,-q -Waliasing -Wampersand -Wsurprising -Wintrinsics-std -Wno-tabs -Wintrinsic-shadow -Wline-truncation -std=gnu -O3 -ffast-math -funroll-all-loops -fcheck=all

# ______________________________________________________________________________

# *** g95
# This is no longer working with the Acoustics Toolbox because it uses Fortran features that the g95 compiler has not implemented
# export FC=g95
# export FFLAGS = -Wall -std=f2003 -O3

# compilation diagnostics on:
# export FFLAGS = -Wall -std=f2003 -ftrace=full -fbounds-check
# export FFLAGS = -pg   -std=f2003

# ______________________________________________________________________________

# *** Portland Group FORTRAN
# -Mnoframe caused erroneous results
# -Munroll  caused erroneous results
# These are defaults under -fast, so can't use -fast either

# export FC=pgfortran
# export FFLAGS= -Mconcur
# export FFLAGS= -fast
# export FFLAGS= -O2 -Munroll=c:1 -Mnoframe -Mlre -Mpre -Mvect=sse -Mcache_align -Mflushz -Mvect
# export FFLAGS= -O2 -Mlre -Mpre -Mvect=sse -Mcache_align -Mflushz -Mvect

# compilation diagnostics on:
# export FFLAGS= -g -Minfo=ccff -Minform=inform -C

# ______________________________________________________________________________

# use gcov-15 if available (needed on Mac) otherwise just use normal gcov (normal on Linux)
GCOV := $(shell command -v gcov-15 2>/dev/null || command -v gcov)

export RM=rm
export CC=gcc
export CFLAGS=-g
#export FFLAGS+= -I../misc -I../tslib -I/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/include
export FFLAGS+= -I../misc #-I../tslib

export LAPACK_LIBS = -llapack

all:
	(cd misc;	make -k all)
	(cd Bellhop;	make -k all)
	@echo " "
	@echo "*************************"
	@echo "***** BELLHOP built *****"
	@echo "*************************"

install: all
	(cd Bellhop;	make -k install)
	@echo " "
	@echo "*****************************"
	@echo "***** BELLHOP installed *****"
	@echo "Add it to your path using something like:"
	@echo '    echo "export PATH=\$$PATH:$(shell pwd)/bin" >> "$$HOME/.zshrc"'
	@echo "*****************************"

clean: coverage-clean
	-rm -f bin/*.exe
	find . -name '*.dSYM' -exec rm -r {} +
	find . -name '*.png'  -exec rm -r {} +
	find . -name '*.eps'  -exec rm -r {} +
	find . -name '*.mod'  -exec rm -r {} +
	find . -name '*.grn'  -exec rm -r {} +
	find . -name '*.shd'  -exec rm -r {} +
	find . -name '*.shd.mat'  -exec rm -r {} +
	find . -name '*.prt'  -exec rm -r {} +
	find . -name '*.gcno' -exec rm {} +
	(cd misc;	make -k -i clean)
	(cd Bellhop;	make -k -i clean)
	
docs:
	@echo "Generating FORD documentation..."
	ford -g -d "Bellhop" -d "misc" ford.md
	@echo "Documentation generated in ./doc/ directory"
	@echo "Open ./doc/index.html in a web browser to view"

clean-docs:
	-rm -rf doc

coverage-build: clean
	@echo "Building BELLHOP with coverage instrumentation..."
	$(MAKE) FC=gfortran FFLAGS="$(FFLAGS_BASE) $(FFLAGS_ARCH) $(FFLAGS_COVERAGE) -I../misc" all

coverage-clean:
	@echo "Cleaning coverage output files..."
	find . -name '*.gcda' -exec rm {} +
	find . -name '*.gcov' -exec rm {} +

coverage-install: coverage-build
	@echo "Installing BELLHOP with coverage instrumentation..."
	$(MAKE) install

coverage-test: coverage-install
	@echo "Running basic coverage test..."
	export PATH="$(shell pwd)/bin:$$PATH" && \
	cd examples/Munk && \
	bellhop.exe MunkB_ray && \
	bellhop.exe MunkB_Coh

coverage-report:
	@echo "Generating coverage report from existing data..."
	@echo "Coverage data files found:"
	@find . -name '*.gcda' | head -10
	@if [ ! $$(find . -name '*.gcda' | wc -l) -gt 0 ]; then \
		echo "No coverage data found. Run 'make coverage-test' as a check first."; \
		exit 1; \
	fi
	@echo "Generating GCOV reports for main source files..."
	cd Bellhop && \
	for gcda_file in *.gcda; do \
		if [ -f "$$gcda_file" ]; then \
			base=$$(basename $$gcda_file .gcda); \
			if [ -f "$$base.gcno" ]; then \
				echo "Processing $$base..."; \
				$(GCOV) -b -c "$$gcda_file"; \
			else \
				echo "Warning: No .gcno file found for $$base"; \
			fi; \
		fi; \
	done
	cd misc && \
	for gcda_file in *.gcda; do \
		if [ -f "$$gcda_file" ]; then \
			base=$$(basename $$gcda_file .gcda); \
			if [ -f "$$base.gcno" ]; then \
				echo "Processing $$base..."; \
				$(GCOV) -b -c "$$gcda_file"; \
			else \
				echo "Warning: No .gcno file found for $$base"; \
			fi; \
		fi; \
	done
	@echo "Coverage reports generated. .gcov files created in Bellhop/ and misc/ directories."
	@echo "Summary of coverage for main executables:"
	@cd Bellhop && ls -la *.gcov 2>/dev/null | head -5 || echo "No .gcov files found in Bellhop/"
	@cd misc && ls -la *.gcov 2>/dev/null | head -5 || echo "No .gcov files found in misc/"

coverage-html: coverage-report
	@echo "Generating HTML coverage reports for FORD integration..."
	@if [ ! $$(find . -name '*.gcov' | wc -l) -gt 0 ]; then \
		echo "No .gcov files found. Run 'make coverage-report' first."; \
		exit 1; \
	fi
	@echo "Creating HTML reports in docs/ directory for FORD media integration..."
	python3 scripts/generate_coverage_html.py docs/
	@echo "HTML coverage reports generated and integrated with FORD documentation."
	@echo "Reports will be accessible through FORD as media files at /media/"

coverage-full: coverage-test coverage-report coverage-html
	@echo "Full coverage analysis complete."

.PHONY: all install clean docs clean-docs coverage-clean coverage-build coverage-install coverage-test coverage-report coverage-html coverage-full
