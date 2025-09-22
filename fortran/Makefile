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

# Minimal dependency constraints - gfortran handles most dependencies automatically
# Only specify dependencies that cannot be detected due to build order issues

# Ensure RayNormals is built before 3D modules that need it
RayNormals.o: bellhopMod.o
Reflect3DMod.o Step3DMod.o influence3D.o: RayNormals.o cross_products.o