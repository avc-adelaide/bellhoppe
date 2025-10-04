
####################################
# This is the new Bellhop Makefile #
####################################


####### Executables ######

export FC = gfortran
export CC = gcc
export CFLAGS = -g
export LAPACK_LIBS = -llapack

# use gcov-15 if available (needed on Mac) otherwise just use normal gcov (normal on Linux)
GCOV := $(shell command -v gcov-15 2>/dev/null || command -v gcov)

###### Flags #######

# Detect architecture
UNAME_M := $(shell uname -m)

# Base flags (common to all)
FFLAGS_BASE = -g -Waliasing -Wampersand -Wsurprising -Wintrinsics-std \
                 -Wno-tabs -Wintrinsic-shadow -Wline-truncation \
                 -std=gnu -frecursive

# Optimisation flags (common, but not used for coverage)
FFLAGS_OPTIM = -O2 -ffast-math -funroll-all-loops -fomit-frame-pointer

# Coverage flags (for GCOV code coverage analysis)
FFLAGS_COVERAGE = -fprofile-arcs -ftest-coverage -fcheck=all

# Arch-specific flags
ifeq ($(UNAME_M),x86_64) # Windows/Intel/Linux Intel
    FFLAGS_ARCH = -march=native -mtune=native
else ifeq ($(UNAME_M),arm64) # Apple Silicon
    FFLAGS_ARCH = -mcpu=apple-m2
else ifeq ($(UNAME_M),aarch64) # Linux ARM
    FFLAGS_ARCH = -march=armv8.5-a
else
    $(warning Unknown architecture $(UNAME_M), using generic flags)
    FFLAGS_ARCH =
endif


# Combine
FFLAGS = $(FFLAGS_BASE) $(FFLAGS_OPTIM) $(FFLAGS_ARCH)
export FFLAGS



####### TARGETS #######

.PHONY: all install clean test doc docs cov lint \
        coverage-clean coverage-build coverage-install coverage-test \
        coverage-report coverage-html coverage-full

all:
	(cd fortran;	make -k all)
	@echo " "
	@echo "*************************"
	@echo "***** BELLHOP built *****"
	@echo "*************************"

install: all
	(cd fortran;	make -k install)
	@echo " "
	@echo "***************************************"
	@echo "***** BELLHOP installed in ./bin/ *****"
	@echo "Add it to your path using something like: (zsh — macOS default)"
	@echo '    echo "export PATH=\$$PATH:$(shell pwd)/bin" >> "$$HOME/.zshrc"  && source ~/.zshrc'
	@echo 'or: (bash — Linux / Windows-MSYS2 default)'
	@echo '    echo "export PATH=\$$PATH:$(shell pwd)/bin" >> "$$HOME/.bashrc" && source ~/.bashrc'
	@echo "***************************************"
	@echo "Python installation is site-specific, you may need something like:"
	@echo "    pip install -e ."
	@echo "***************************************"

clean: coverage-clean
	-rm -f bin/*.exe
	-rm -rf doc
	find . -name '*.dSYM' -exec rm -r {} +
	find . -name '*.png'  -exec rm -r {} +
	find . -name '*.eps'  -exec rm -r {} +
	find . -name '*.mod'  -exec rm -r {} +
	find . -name '*.grn'  -exec rm -r {} +
	find . -name '*.shd.mat'  -exec rm -r {} +
	find . -name '*.prt'  -exec rm -r {} +
	find . -name '*.gcno' -exec rm {} +
	(cd fortran;	make -k -i clean)


###### HELP ######

help:
	@echo "  CODE BUILDING"
	@echo "    [all] - default — build binaries"
	@echo "    clean - remove all temporary files"
	@echo "  install - copy built binaries into ./bin"
	@echo "                                    "
	@echo "  CODE CHECKING"
	@echo "     test - run test suite"
	@echo "cleantest - rebuild entire codebase and run test suite"
	@echo "     lint - run code linters"
	@echo "      doc - build online documentation"
	@echo "      cov - run code coverage processes"
	@echo "          -                         "
	@echo "  DEVELOPMENT TOOLS"
	@echo "     push - push code changes to repository"

###### HATCH ######

HATCH := hatch env run # was "hatch run" but Github workflows started failing (??)

cleantest: clean all install test

test:
	@echo "Running Python test suite..."
	$(HATCH) test

doc: docs

docs:
	@echo "Generating Fortran/FORD documentation..."
	$(HATCH) docf
	@echo "Generating Python/Sphinx documentation..."
	$(HATCH) docp
	@echo "Documentation generated in ./doc/ directory"
	@echo "Open ./doc/index.html in a web browser to view"

cov:
	@echo "Generating Fortran coverage report..."
	$(HATCH) covf
	@echo "Generating Python coverage report..."
	$(HATCH) covp

lint:
	@echo "Running ruff Python linter..."
	$(HATCH) lintp
	@echo "Running mypy Python type checker..."
	$(HATCH) typep
	@echo "Running fortitude Fortran linter..."
	$(HATCH) lintf

###### COVERAGE ######

coverage-clean:
	@echo "Cleaning coverage output files..."
	find . -name '*.gcda' -exec rm {} +
	find . -name '*.gcov' -exec rm {} +
	@echo "Cleaning Python coverage files..."
	rm -f .coverage
	rm -rf _coverage_python/

coverage-build: clean
	@echo "Building BELLHOP with coverage instrumentation..."
	$(MAKE) FC=gfortran FFLAGS="$(FFLAGS_BASE) $(FFLAGS_ARCH) $(FFLAGS_COVERAGE)" all

coverage-install: coverage-build
	@echo "Installing BELLHOP with coverage instrumentation..."
	mkdir -p ./bin
	for f in fortran/*.exe ; do \
		echo "----- Installing $$f"; cp -p $$f ./bin/; \
	done

coverage-test: coverage-install
	@echo "Running fortran coverage test..."
	export PATH="$(PWD)/bin:$$PATH" && \
	export PYTHONPATH="$(PWD)/python:$$PYTHONPATH" && \
	export COVERAGE_RUN="true" && pytest --capture=tee-sys --ignore=tests/only_python/

coverage-report:
	@echo "Generating coverage report from existing data..."
	@echo "Coverage data files found:"
	@find . -name '*.gcda' | head -10
	@if [ ! $$(find . -name '*.gcda' | wc -l) -gt 0 ]; then \
		echo "No coverage data found. Run 'make coverage-test' as a check first."; \
		exit 1; \
	fi
	@echo "Generating GCOV reports for main source files..."
	cd fortran && \
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
	@echo "Coverage reports generated. .gcov files created in fortran/ directory."
	@echo "Summary of coverage for main executables:"
	@cd fortran && ls -la *.gcov 2>/dev/null | head -10 || echo "No .gcov files found in fortran/"

coverage-html: coverage-report
	@echo "Generating HTML coverage reports for FORD integration..."
	@if [ ! $$(find . -name '*.gcov' | wc -l) -gt 0 ]; then \
		echo "No .gcov files found. Run 'make coverage-report' first."; \
		exit 1; \
	fi
	@echo "Creating HTML reports in _coverage/ directory..."
	python3 python/generate_coverage_html.py _coverage
	@echo "HTML coverage reports generated."

# although this is much lighter, I don't like the output -- maybe it needs more finetuning
coverage-gcovr:
	@echo "Generating HTML coverage reports with gcovr..."
	mkdir -p _coverage
	gcovr --verbose --html --html-details \
		--gcov-executable gcov-15 \
		--gcov-object-directory ./fortran \
		--output _coverage/index.html \
		--root ./fortran \
		--exclude-directories examples \
		--exclude-directories tests \
		--html-medium-threshold 50 \
		--html-high-threshold 80 \
		--html-tab-size 4 \
		./fortran/

coverage-full: clean coverage-build coverage-install coverage-test coverage-report coverage-html
	@echo "Full coverage analysis complete."

#######################################

gitokay:
	@if [ -z "$$(git status --porcelain)" ]; then \
	    echo "    clean repo, continuing..."; \
	else \
		echo "    uncommitted changes!"; \
		false; \
	fi

gitclean:
	@if [ -z "$$(git clean -nx)" ]; then \
	    true; \
	else \
		if [ -f "._GIT_CLEAN_CHECK" ]; then \
			git clean -fx; \
		else \
			git clean -nx; \
			echo "" > ._GIT_CLEAN_CHECK; \
			echo "Git repository not clean. Re-run this command to automatically execute:"; \
			echo "    git clean -fx"; \
			false; \
		fi \
	fi


push: gitokay gitclean lint test
	@echo "============================"
	@echo "Testing okay, now pushing..."
	@echo "============================"
	git pull && git push
