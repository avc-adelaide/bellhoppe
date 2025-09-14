AR = ar

# Intel compiler needed the following definition for the archiver:
#AR = xiar

ARFLAGS = r

RANLIB = ranlib

EXECUTABLES = bellhop.exe bellhop3d.exe

# Basic modules from original misc/ directory (must be compiled first)
BASIC_MODULES = FatalError.o MathConstants.o monotonicMod.o SortMod.o subtabulate.o \
                splinec.o PolyMod.o cross_products.o

# Dependent misc modules 
MISC_MODULES = beampattern.o RefCoef.o pchipMod.o AttenMod.o SourceReceiverPositions.o RWSHDFile.o

# All misc objects
MISC_OBJECTS = $(BASIC_MODULES) $(MISC_MODULES)

# Basic Bellhop modules
BELLHOP_MODULES = bellhopMod.o angleMod.o ArrMod.o bdryMod.o sspMod.o Cone.o

# Objects for bellhop executable  
BELLHOP_OBJECTS   = $(BELLHOP_MODULES) ReflectMod.o WriteRay.o influence.o Step.o ReadEnvironmentBell.o bellhop.o

# Objects for bellhop3d executable
BELLHOP3D_OBJECTS = $(BELLHOP_MODULES) bdry3DMod.o ReflectMod.o Reflect3DMod.o WriteRay.o RayNormals.o influence.o influence3D.o Step3DMod.o ReadEnvironmentBell.o bellhop3D.o

# All objects combined
ALL_OBJECTS = $(MISC_OBJECTS) $(BELLHOP_OBJECTS) $(BELLHOP3D_OBJECTS)

.PHONY: all install clean

all: $(EXECUTABLES)
	@echo "Bellhop built from fortran/ directory"
	@echo "************************************"
	@echo " "

install:
	mkdir -p ../bin
	for f in $(EXECUTABLES) ; do \
		echo "----- Installing $$f"; cp -p $$f ../bin/; \
	done

clean:
	-rm -f *.o *.mod *.exe *_genmod.f90 *.a

# Declare implicit rules (for make utilities with missing or broken build rules)

.SUFFIXES: .a .o .mod .f .f90

.f.o:
	$(FC) -c $(FFLAGS) $< 

.f90.o:
	$(FC) -c $(FFLAGS) $< 

.f90.mod:
	$(FC) -c $(FFLAGS) $< 

# Main executable targets
bellhop.exe: $(BELLHOP_OBJECTS) $(MISC_OBJECTS)
	$(FC) -o $@ $(FFLAGS) $(BELLHOP_OBJECTS) $(MISC_OBJECTS)

bellhop3d.exe: $(BELLHOP3D_OBJECTS) $(MISC_OBJECTS)
	$(FC) -o $@ $(FFLAGS) $(BELLHOP3D_OBJECTS) $(MISC_OBJECTS)

# Ensure basic modules are built first
$(MISC_MODULES): $(BASIC_MODULES)
$(BELLHOP_MODULES): $(BASIC_MODULES) $(MISC_MODULES)

# Explicit dependencies for basic modules (no dependencies)
FatalError.o fatalerror.mod: FatalError.f90
	$(FC) -c $(FFLAGS) $<

MathConstants.o mathconstants.mod: MathConstants.f90
	$(FC) -c $(FFLAGS) $<

monotonicMod.o monotonicmod.mod: monotonicMod.f90
	$(FC) -c $(FFLAGS) $<

SortMod.o sortmod.mod: SortMod.f90
	$(FC) -c $(FFLAGS) $<

subtabulate.o subtabulate.mod: subtabulate.f90
	$(FC) -c $(FFLAGS) $<

splinec.o splinec.mod: splinec.f90
	$(FC) -c $(FFLAGS) $<

PolyMod.o polymod.mod: PolyMod.f90
	$(FC) -c $(FFLAGS) $<

cross_products.o cross_products.mod: cross_products.f90
	$(FC) -c $(FFLAGS) $<

# Dependent misc modules
beampattern.o beampattern.mod: beampattern.f90 fatalerror.mod monotonicmod.mod
	$(FC) -c $(FFLAGS) $<

RefCoef.o refcoef.mod: RefCoef.f90 polymod.mod
	$(FC) -c $(FFLAGS) $<

pchipMod.o pchipmod.mod: pchipMod.f90 splinec.mod
	$(FC) -c $(FFLAGS) $<

AttenMod.o: AttenMod.f90 mathconstants.mod
	$(FC) -c $(FFLAGS) $<

SourceReceiverPositions.o sourcereceiverpositions.mod: SourceReceiverPositions.f90 monotonicmod.mod sortmod.mod subtabulate.mod
	$(FC) -c $(FFLAGS) $<

RWSHDFile.o: RWSHDFile.f90 sourcereceiverpositions.mod
	$(FC) -c $(FFLAGS) $<

# Bellhop modules (depend on basic modules)
bellhopMod.o bellhopmod.mod: bellhopMod.f90 mathconstants.mod
	$(FC) -c $(FFLAGS) $< 

angleMod.o anglemod.mod: angleMod.f90 mathconstants.mod
	$(FC) -c $(FFLAGS) $< 

ArrMod.o arrmod.mod: ArrMod.f90 mathconstants.mod
	$(FC) -c $(FFLAGS) $< 

bdryMod.o bdrymod.mod: bdryMod.f90 monotonicmod.mod
	$(FC) -c $(FFLAGS) $< 

sspMod.o sspmod.mod: sspMod.f90 fatalerror.mod
	$(FC) -c $(FFLAGS) $< 

Cone.o cone.mod: Cone.f90 bellhopmod.mod
	$(FC) -c $(FFLAGS) $<

# Additional Bellhop modules that depend on bellhopMod
ReflectMod.o reflectmod.mod: ReflectMod.f90 cone.mod
	$(FC) -c $(FFLAGS) $<

Reflect3DMod.o reflect3dmod.mod: Reflect3DMod.f90 cone.mod
	$(FC) -c $(FFLAGS) $<

WriteRay.o writeray.mod: WriteRay.f90 bellhopmod.mod
	$(FC) -c $(FFLAGS) $<

influence.o influence.mod: influence.f90 bellhopmod.mod
	$(FC) -c $(FFLAGS) $< 

influence3D.o influence3d.mod: influence3D.f90 bellhopmod.mod
	$(FC) -c $(FFLAGS) $< 

Step.o step.mod: Step.f90 bellhopmod.mod
	$(FC) -c $(FFLAGS) $<

Step3DMod.o step3dmod.mod: Step3DMod.f90 bellhopmod.mod
	$(FC) -c $(FFLAGS) $<

RayNormals.o raynormals.mod: RayNormals.f90 bellhopmod.mod
	$(FC) -c $(FFLAGS) $<

ReadEnvironmentBell.o readenvironmentbell.mod: ReadEnvironmentBell.f90 bellhopmod.mod
	$(FC) -c $(FFLAGS) $< 

bdry3DMod.o bdry3dmod.mod: bdry3DMod.f90 monotonicmod.mod
	$(FC) -c $(FFLAGS) $< 

# Main program objects (depend on all their modules)
bellhop.o: bellhop.f90 arrmod.mod anglemod.mod bdrymod.mod readenvironmentbell.mod bellhopmod.mod sspmod.mod reflectmod.mod writeray.mod raynormals.mod influence.mod step.mod
	$(FC) -c $(FFLAGS) $<

bellhop3D.o: bellhop3D.f90 arrmod.mod anglemod.mod bdry3dmod.mod readenvironmentbell.mod bellhopmod.mod sspmod.mod reflectmod.mod reflect3dmod.mod writeray.mod raynormals.mod influence3d.mod step3dmod.mod
	$(FC) -c $(FFLAGS) $<