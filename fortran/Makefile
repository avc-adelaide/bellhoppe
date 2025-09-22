# Simplified Fortran Makefile for BELLHOP
# Uses automatic dependency detection instead of manual rules

# Compiler and tools
FC ?= gfortran
AR = ar
ARFLAGS = r
RANLIB = ranlib

# Get compiler flags from environment or use defaults
ifeq ($(FC),gfortran)
    # If FFLAGS not set by parent Makefile, use reasonable defaults
    FFLAGS ?= -g -Waliasing -Wampersand -Wsurprising -Wintrinsics-std \
              -Wno-tabs -Wintrinsic-shadow -Wline-truncation \
              -std=gnu -frecursive -O2 -ffast-math -funroll-all-loops \
              -fomit-frame-pointer -march=native -mtune=native
endif

# Executables to build
EXECUTABLES = bellhop.exe bellhop3d.exe

# Object files for each executable
BELLHOP_OBJECTS = FatalError.o MathConstants.o monotonicMod.o SortMod.o \
                  subtabulate.o splinec.o PolyMod.o cross_products.o \
                  beampattern.o RefCoef.o pchipMod.o AttenMod.o \
                  SourceReceiverPositions.o RWSHDFile.o \
                  bellhopMod.o angleMod.o ArrMod.o bdryMod.o sspMod.o \
                  Cone.o ReflectMod.o WriteRay.o influence.o Step.o \
                  ReadEnvironmentBell.o bellhop.o

BELLHOP3D_OBJECTS = FatalError.o MathConstants.o monotonicMod.o SortMod.o \
                    subtabulate.o splinec.o PolyMod.o cross_products.o \
                    beampattern.o RefCoef.o pchipMod.o AttenMod.o \
                    SourceReceiverPositions.o RWSHDFile.o \
                    bellhopMod.o angleMod.o ArrMod.o bdryMod.o sspMod.o \
                    Cone.o bdry3DMod.o ReflectMod.o Reflect3DMod.o \
                    WriteRay.o RayNormals.o influence.o influence3D.o \
                    Step3DMod.o ReadEnvironmentBell.o bellhop3D.o

# Default target
.PHONY: all install clean

all: $(EXECUTABLES)
	@echo "Bellhop built from fortran/ directory"
	@echo "************************************"
	@echo " "

# Install executables  
install:
	mkdir -p ../bin
	for f in $(EXECUTABLES) ; do \
		echo "----- Installing $$f"; cp -p $$f ../bin/; \
	done

# Clean build artifacts
clean:
	-rm -f *.o *.mod *.exe *_genmod.f90 *.a

# Suffix rules for automatic compilation
.SUFFIXES: .f90 .o .mod

# Fortran 90 source to object
.f90.o:
	$(FC) -c $(FFLAGS) $<

# Module files are created as a side effect of object compilation
# This rule ensures make knows about the relationship
%.mod: %.o
	@true

# Main executable targets
bellhop.exe: $(BELLHOP_OBJECTS)
	$(FC) -o $@ $(FFLAGS) $(BELLHOP_OBJECTS)

bellhop3d.exe: $(BELLHOP3D_OBJECTS)
	$(FC) -o $@ $(FFLAGS) $(BELLHOP3D_OBJECTS)

# Automatic dependency detection with minimal ordering constraints
# Only specify the ordering that gfortran cannot detect automatically

# Basic modules (no USE dependencies)
BASIC_MODULES = FatalError.o MathConstants.o monotonicMod.o SortMod.o \
                subtabulate.o splinec.o PolyMod.o cross_products.o

# Modules that depend on basic modules only
LEVEL1_MODULES = beampattern.o RefCoef.o pchipMod.o AttenMod.o \
                 SourceReceiverPositions.o RWSHDFile.o bellhopMod.o \
                 angleMod.o ArrMod.o bdryMod.o sspMod.o bdry3DMod.o

# Modules that need bellhopMod and possibly others
LEVEL2_MODULES = Cone.o ReflectMod.o WriteRay.o influence.o Step.o \
                 ReadEnvironmentBell.o RayNormals.o

# 3D-specific modules
LEVEL3_MODULES = Reflect3DMod.o influence3D.o Step3DMod.o

# Ensure build order constraints
$(LEVEL1_MODULES): $(BASIC_MODULES)
$(LEVEL2_MODULES): $(BASIC_MODULES) $(LEVEL1_MODULES)
$(LEVEL3_MODULES): $(BASIC_MODULES) $(LEVEL1_MODULES) $(LEVEL2_MODULES)

# Main programs depend on their respective module sets
bellhop.o: $(BASIC_MODULES) $(LEVEL1_MODULES) $(LEVEL2_MODULES)
bellhop3D.o: $(BASIC_MODULES) $(LEVEL1_MODULES) $(LEVEL2_MODULES) $(LEVEL3_MODULES)