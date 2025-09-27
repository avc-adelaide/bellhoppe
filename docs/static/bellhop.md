::::::: {.Section1 style="font-family: Helvetica,Arial,sans-serif;"}
# BELLHOP

\

## [Overview](#Overview_)

## [Sample Input](#Sample_Input_Environmental_File:_)

## [Description of Inputs](#Description_of_Inputs_)

### [Source/Receiver Depths and Ranges](#7_-_SOURCERECEIVER_DEPTHS_AND_RANGES) {#sourcereceiver-depths-and-ranges style="margin-left: 40px;"}

### [Run Type](#8_-_RUN_TYPE) {#run-type style="margin-left: 40px;"}

### [Beam Fan](#9_-_BEAM_FAN) {#beam-fan style="margin-left: 40px;"}

### [Numerical Integrator Info](#10_-_NUMERICAL_INTEGRATOR_INFO) {#numerical-integrator-info style="margin-left: 40px;"}

## [Running BELLHOP](#Running_BELLHOP_)

\
\

## []{#Overview_}Overview 

[BELLHOP]{style="font-weight: bold;"} computes acoustic fields in
oceanic environments via beam tracing. The environment treated consists
of an acoustic medium with a sound speed that may depend on range and
depth.\

A theoretical description may be found in:

Michael B. Porter and Homer P. Bucker, \`\`Gaussian beam tracing for
computing ocean acoustic fields,\'\' [J. Acoust. Soc. Amer.
]{style="font-style: italic;"}[82]{style="font-weight: bold;"},
1349\--1359 (1987).

Michael B. Porter and Yong-Chun Liu, "Finite-Element Ray Tracing\'\',
Proceedings of the International Conference on Theoretical and
Computational Acoustics, Eds. D. Lee and M. H. Schultz, pp. 947-956,
World Scientific (1994).

The following programs are used with BELLHOP :

[BELLHOP]{style="font-weight: bold;"}     Main program for doing
Gaussian beam tracing

[PLOTRAY]{style="font-weight: bold;"}     Produces plots of central rays
of beams\

[PLOTARR]{style="font-weight: bold;"}     Produces plots of arrivals
(the echo pattern)

[PLOTATI]{style="font-weight: bold;"}     Produces plots of the
altimetry

[PLOTBTY]{style="font-weight: bold;"}     Produces plots of the
bathymetry\

[ANGLES]{style="font-weight: bold;"}      Given the source and receiver
sound speeds, computes the angle of the limiting ray.

[PLOTSSP]{style="font-weight: bold;"}     Plots the sound speed profile\

[PLOTSSP2D]{style="font-weight: bold;"}   Plots the range-dependent
sound speed profile

BELLHOP produces pressure fields in the NRL standard format and can
therefore be plotted using the MATLAB script, plotshd.m.

The steps in running the program are as follows:

   1. Set up your environmental file and run PLOTSSP to make sure the
SSP looks reasonable.

   2. Do a ray trace.  That is,

      A. Run BELLHOP with the ray trace option to calculate about 50
rays.

      B. Run PLOTRAY to make sure you have the angular coverage you
expect.  Do the rays behave irregularly? If so reduce the step-size and
try again.

   3. Re-run BELLHOP using the coherent, incoherent or semicoherent
option for transmission loss. (Use the default number of beams.)

   4. Run plotshd.m to plot a full range-depth field plot.

   5. Double the number of beams and check convergence.

Files:

        Name           Unit         Description

Input\
        \*.ENV            1       ENVironmental data

Output\
        \*.PRT            6       PRinT file\
        \*.RAY           21       RAY   file\
        \*.SHD           25       SHaDe file

## []{#Sample_Input_Environmental_File:_}Sample Input (Environmental) File:   {#sample-input-environmental-file style="font-family: monospace;"}

\'Munk profile\'        ! TITLE\
50.0                  ! FREQ (Hz)\
1                     ! NMEDIA\
\'SVN\'                 ! SSPOPT (Analytic or C-linear interpolation)\
51  0.0  5000.0       ! DEPTH of bottom (m)\
    0.0  1548.52  /\
  200.0  1530.29  /\
  250.0  1526.69  /\
  400.0  1517.78  /\
  600.0  1509.49  /\
  800.0  1504.30  /\
 1000.0  1501.38  /\
 1200.0  1500.14  /\
 1400.0  1500.12  /\
 1600.0  1501.02  /\
 1800.0  1502.57  /\
 2000.0  1504.62  /\
 2200.0  1507.02  /\
 2400.0  1509.69  /\
 2600.0  1512.55  /\
 2800.0  1515.56  /\
 3000.0  1518.67  /\
 3200.0  1521.85  /\
 3400.0  1525.10  /\
 3600.0  1528.38  /\
 3800.0  1531.70  /\
 4000.0  1535.04  /\
 4200.0  1538.39  /\
 4400.0  1541.76  /\
 4600.0  1545.14  /\
 4800.0  1548.52  /\
 5000.0  1551.91  /\
\'V\'  0.0\
1                       ! NSD\
1000.0 /                ! SD(1:NSD) (m)\
2                       ! NRD\
0.0 5000.0 /            ! RD(1:NRD) (m)\
501                     ! NRR\
0.0  100.0 /            ! RR(1:NR ) (km)\
\'R\'                     ! Run-type: \'R/C/I/S\'\
51                      ! NBEAMS\
-11.0 11.0 /            ! ALPHA(1:NBEAMS) (degrees)\
200.0  5500.0  101.0    ! STEP (m)  ZBOX (m)  RBOX (km)

## []{#Description_of_Inputs_}Description of Inputs {#description-of-inputs-1 style="font-family: monospace;"}

The [first 6 blocks](EnvironmentalFile.html) in the ENVFIL are common to
all the programs in the Acoustics Toolbox. The following blocks should
be appended for BELLHOP:       \

### []{#7_-_SOURCERECEIVER_DEPTHS_AND_RANGES} (7) - SOURCE/RECEIVER DEPTHS AND RANGES {#sourcereceiver-depths-and-ranges-1 style="font-family: monospace;"}

       Syntax:

          [ NSD]{style="font-style: italic;"}\
[           SD(1:NSD)]{style="font-style: italic;"}\
[           NRD]{style="font-style: italic;"}\
[           RD(1:NRD)]{style="font-style: italic;"}\
[           NR]{style="font-style: italic;"}\
[           R(1:NR )]{style="font-style: italic;"}

       Description:

          NSD:  The number of source depths\
          SD(): The source depths (m)\
          NRD:  The number of receiver depths\
          RD(): The receiver depths (m)\
          NR:   The number of receiver ranges\
          R():  The receiver ranges (km)

This data is read in using list-directed I/O you can type it just about
any way you want, e.g. on one line or split onto several lines.  Also if
the depths or ranges are equally spaced then you can type just the first
and last depths followed by a \'/\' and the intermediate depths will be
generated automatically.\

You can specify a receiver at zero range; however, the BELLHOP field is
singular there\-\-- the pressure is returned as zero.\

Some of the subroutines that calculate the beam influence allow an
arbitrary vector of receiver ranges; others require it to be equally
spaced in range. In particular, only the following allow an arbitrary
range vector:

    \'G\' GeoHatCart\
    \'B\' GeoGaussianCart\
    CerveyRayCen\

### []{#8_-_RUN_TYPE} (8) - RUN TYPE {#run-type-1 style="font-family: monospace;"}

       Syntax:

          [ OPTION]{style="font-style: italic;"}

       Description:

          OPTION(1:1): \'R\' generates a ray file\
                       \'E\' generates an eigenray file\
                       \'A\' generates an amplitude-delay file (ascii)\
                       \'a\' generate  an amplitude-delay file (binary)\
                       \'C\' Coherent     TL calculation\
                       \'I  Incoherent   TL calculation\
                       \'S\' Semicoherent TL calculation\
                            (Lloyd mirror source pattern)

          OPTION(2:2): \'G\' Geometric hat beams      in Cartesian
coordinates (default)\
                       \'\^\' Geometric hat beams      in Cartesian
coordinates (same as \'G\' but easier to remember)\
                       \'g\' Geometric hat beams      in ray-centered
coordinates\
                       \'B\' Geometric Gaussian beams in Cartesian
coordinates\
                       \'b\' Geometric Gaussian beams in ray-centered
coordinates\

          OPTION(3:3): \'\*\' read in a source beam pattern file\
                       \'O\' don\'t (omni-directional) (default)

          OPTION(4:4): \'R\' point source (cylindrical coordinates)
(default)\
                       \'X\' line  source (Cartesian coordinates)

          OPTION(5:5): \'R\' rectilinear grid (default)\
                       \'I\' irregular grid

The ray file and eigenray files have the same simple ascii format and
can be plotted using the Matlab script plotray.m.\

The eigenray option seems to generate a lot of questions. The way this
works is that BELLHOP simply writes the trajectories for all the beams
that contribute at a given receiver location. To get a useful picture
you normally want to use a very fine fan, only one receiver location,
and the geometric beam option. See the examples in at/tests.\

The amplitude-delay file can be used with the Matlab script stackarr.m
to \'stack the arrivals\', i.e. to convolve them with the source
spectrum and plot the channel response. stackarr.m can also be used to
simple plot the impulse response. We loosely refer to the amplitudes of
the arrivals or echoes here; however, these values are really complex
numbers that provide the amplitude and phase of each echo.\

For TL calculations, the output is in the shdfil format used by all the
codes in the Acoustics Toolbox and can be plotted using the Matlab
script, plotshd.m. (Use toasc.f to convert the binary shade files to
ascii format for use by plotshd.m or whatever plot package you\'re
using.)\

The pressure field is normally calculated on a rectilinear grid formed
by the receiver ranges and depths. If an irregular grid is selected,
then the receiver ranges and depths are interpreted as a coordinate pair
for the receivers. This option is useful for reverberation calculations
where the receivers need to follow the bottom terrain. This option has
not been used much. The plot routines (plotarr) have not been modified
to accomodate it. There may be some other limitations.\

There are actually several different types of Gaussian beam options
(OPTION(2:2)) implemented in the code. Only the two described above are
fully maintained.

The source beam pattern file has the format

       NSBPPts\
       angle1  power1\
       angle2  power2\
        \...

with angle following the BELLHOP convention, i.e. declination angle in
degrees (so that 90 degrees points to the bottom). The power is in dB.
To match a standard point source calculation one would used anisotropic
source with 0 dB for all angles. (See at/tests/BeamPattern for an
example.)\

### []{#9_-_BEAM_FAN} (9) - BEAM FAN {#beam-fan-1 style="font-family: monospace;"}

       Syntax:

          [ NBEAMS ISINGLE]{style="font-style: italic;"}\
[           ALPHA(1:NBEAMS)]{style="font-style: italic;"}

       Description:

                  [NBEAMS: Number of
beams]{style="font-family: monospace;"}[\
              (use 0 to have the program calculate a value
automatically, but conservatively).]{style="font-family: monospace;"}

[          ISINGLE: If the option to compute a single beam in the fan is
selected (top option)\
              then this selects the index of the beam that is traced.\
]{style="font-family: monospace;"}

          ALPHA(): Beam angles (negative angles toward surface)

For a ray trace you can type in a sequence of angles or you can type the
first and last angles followed by a \'/\'.  For a TL calculation, the
rays must be equally spaced otherwise the results will be incorrect.

### []{#10_-_NUMERICAL_INTEGRATOR_INFO} (10) - NUMERICAL INTEGRATOR INFO {#numerical-integrator-info-1 style="font-family: monospace;"}

       Syntax:

          [STEP ZBOX RBOX]{style="font-style: italic;"}\

       Description:

          STEP:  The step size used for tracing the rays (m). (Use 0 to
let BELLHOP choose the step size.)\
          ZBOX:  The maximum depth to trace a ray        (m).\
          RBOX:  The maximum range to trace a ray       (km).

The required step size depends on many factors.  This includes
frequency, size of features in the SSP (such as surface ducts), range of
receivers, and whether a coherent or incoherent TL calculation is
performed.  If you use STEP=0.0 BELLHOP will use a default step-size and
tell you what it picked.  You should then halve the step size until the
results are convergent to your required accuracy.  To obtain a smooth
ray trace you should use the spline SSP interpolation and a step-size
less than the smallest distance between SSP data points. Rays are traced
until they exit the box ( ZBOX, RBOX ).  By setting ZBOX less than the
water depth you can eliminate bottom reflections. Make ZBOX, RBOX a bit
(say 1%) roomy too make sure rays are not killed the moment they hit the
bottom or are just reaching your furthest receiver.\

The default step size has generally been OK; however, with the paraxial
(Cerven) beams it was too aggressive on one simple test. The paraxial
beams are generally much wider than the geometric beams so a given
receiver gets contributions from beams with much more distance to the
central ray. It is assumed that that increases the sensitivity to the
accuracy of the ray trace (and its normals) which determine the phase of
these distant beams as observed at the receive.\

\

## []{#Running_BELLHOP_}Running BELLHOP

The main issue to be aware of is that ray tracing is very sensitive to
environmental interpolation (both boundary and volume). The Gaussian
beam options reduce that sensitivity significantly; however, one should
still be attentive to this issue. The spline interpolation option to the
SSP should be used with particular caution. In some cases, the spline
fit is very smooth as desired; in other cases, the spline introduces
large wiggles between ssp points, in its effort to produce a smooth
curve. Use PLOTSSP to see how your fit looks.\

BELLHOP numerically integrates the ray equations to trace a ray through
the ocean. To avoid artifacts at discontinuties in the SSP, the step
size is dynamically adjusted to make sure a step always lands on an SSP
point, rather than stepping over it. (The beam curvature needs to be
adjusted at each such point.) It\'s better to not use more points to
describe the SSP than necessary to capture the physics because BELLHOP
will end up using lots of small steps to have each ray land on the SSP
points. Similarly, BELLHOP uses the altimetry and bathymetry points to
define segments in range, and adjusts the step size so that the rays
land on each segment boundary.\

BELLHOP has no direct capability for modeling elastic wave propagation;
however, elastic boundaries can be treated using BOUNCE to generate an
equivalent reflection coefficient.\

You can have BELLHOP use a range-dependent SSP by creating a separate
SSPFIL containing that SSP data in a matrix form. (See [Range-Dependent
SSP File)](RangeDepSSPFile.htm). The range-dependent SSPFIL is read if
you select \'Q\' (quadrilateral) for the SSP interpolation. The depths
for the SSP points are read from the ENVFIL; the ranges are specified in
the SSPFIL. See the example in at/tests/Gulf.\

BELLHOP will produce some artifacts for receivers very close the the
surface or bottom, because a beam is essentially folded onto itself upon
reflection. The zone of overlap (which depends on the fatness of the
beam) is not treated with a lot of care. You can minimize such artifacts
by making the beams narrow, which in turn can often be done by using
lots of rays. If you want to explore some behavior of the field for a
receiver on the bottom, you generally should offset it a little bit.
Alternatively, you can use reciprocity and interchange the role of the
source and the receiver; sources near the bottom are not a problem.\

\

## Frequently Asked Questions

*Why is it that when I do an eigenray run, the rays do not seem to go
through the receiver location?*\

An eigenray is a ray that connects the source and receiver. To find it
precisely requires a root-finding process to identify the launch angle
that generates a ray passing though the receiver location. The receiver
position is a nonlinear and often discontinuous function of the launch
angle, which complicates the root finding. Bellhop adopts a quick and
lazy implementation and simply modifies the ray trace option to write
only the rays that contribute to the receiver. Strictly speaking, these
are not eigenrays. The number of such contributing rays depends on the
type of beam that has been selected in Bellhop. If you use Geometric
Hat-Shaped beams then typically you will get two contributing rays that
bracket the receiver. This is usually the type of beam you would want to
use to get the best picture of the eigenrays. If you use Gaussian beams
then beams further away from the receiver may contribute.\

Regardless of the type of beam, the beam width typically increases with
arclength. To get contributing rays resembling eigenrays you will want
them to have narrow beamwidths. The beam width (for a geometric beam) is
defined by the spacing between adjacent rays. So here finally is the
answer to the question: use a \*LOT\* of rays/beams to get narrow beams.
An eigenray trace is typically very quick because you\'re looking at a
single (or few) receivers. Use at least 1000 rays. Don\'t be afraid to
use 10,000 or even a million rays. Each ray is traced independently so
using a lot of rays does not increase the memory requirements. The run
time will go up, but that is not usually a problem for a single
receiver. Keep in mind that a real channel can produce a lot of
micro-multipath and the idealized view of a high-frequency field being
derived some a simple sum of a few paths is, well, idealized. You will
tend to get less complicated eigenray pictures with smoother profiles,
since each kink in the SSP or bathymetry contributes to the Pachinko
[([パチンコ]{lang="ja"})]{style="caret-color: rgb(34, 34, 34);
          color: rgb(34, 34, 34); font-family: sans-serif; font-size:
          14px; font-style: normal; font-variant-caps: normal;
          font-weight: normal; letter-spacing: normal; orphans: auto;
          text-align: start; text-indent: 0px; text-transform: none;
          white-space: normal; widows: auto; word-spacing: 0px;
          -webkit-text-size-adjust: auto; -webkit-text-stroke-width:
          0px; text-decoration: none;"}[[
]{.Apple-converted-space}]{style="caret-color: rgb(34, 34, 34); color: rgb(34, 34, 34);
          font-family: sans-serif; font-size: 14px; font-style: normal;
          font-variant-caps: normal; font-weight: normal;
          letter-spacing: normal; orphans: auto; text-align: start;
          text-indent: 0px; text-transform: none; white-space: normal;
          widows: auto; word-spacing: 0px; -webkit-text-size-adjust:
          auto; -webkit-text-stroke-width: 0px; background-color:
          rgb(255, 255, 255); text-decoration: none; display: inline
          !important; float: none;"}effect on the rays.\

*\*

*Why is the launch angle in the arrival file not one of the launch
angles selected in the Bellhop input file?*\

Bellhop aggregates arrivals that have similar delay times. This reduces
the storage requirements in both memory and in the output file. It also
reduces the computation required in convolving a source waveform with
the channel impulse response as defined by the arrivals. Finally, it
presents a less confusing plot of the channel impulse response.\

The aggregation is based on a wavelength tolerance. The angles written
in the arrivals file are also an average of contributing rays and
therefore do not necessarily correspond to the launch angles.\

::: {style="color: rgb(0, 0, 0); font-size: 13px;
        font-style: normal; font-variant-caps: normal; font-weight:
        normal; letter-spacing: normal; text-align: start; text-indent:
        0px; text-transform: none; white-space: normal; word-spacing:
        0px; -moz-text-size-adjust: auto; -webkit-text-stroke-width:
        0px; text-decoration: none;"}
`The reason you get multiple arrivals that are all really part of a single arrival is because of:`
:::

::: {style="color: rgb(0, 0, 0); font-size: 13px;
        font-style: normal; font-variant-caps: normal; font-weight:
        normal; letter-spacing: normal; text-align: start; text-indent:
        0px; text-transform: none; white-space: normal; word-spacing:
        0px; -moz-text-size-adjust: auto; -webkit-text-stroke-width:
        0px; text-decoration: none;"}
[` `]{.Apple-tab-span
style="white-space: pre;"}`1) with the geometric beam, it creates an arrival for each of a pair of rays that bracket the receiver.`
:::

::: {style="color: rgb(0, 0, 0); font-size: 13px;
        font-style: normal; font-variant-caps: normal; font-weight:
        normal; letter-spacing: normal; text-align: start; text-indent:
        0px; text-transform: none; white-space: normal; word-spacing:
        0px; -moz-text-size-adjust: auto; -webkit-text-stroke-width:
        0px; text-decoration: none;"}
[` `]{.Apple-tab-span
style="white-space: pre;"}`2) with Gaussian beams you further get contributions from rays that are within a few beam widths of the receiver`
:::

::: {style="color: rgb(0, 0, 0); font-size: 13px;
        font-style: normal; font-variant-caps: normal; font-weight:
        normal; letter-spacing: normal; text-align: start; text-indent:
        0px; text-transform: none; white-space: normal; word-spacing:
        0px; -moz-text-size-adjust: auto; -webkit-text-stroke-width:
        0px; text-decoration: none;"}
[` `]{.Apple-tab-span
style="white-space: pre;"}`3) with more complicated SSPs the ray fan can become unsmooth, producing a sort of micro-multipath.`
:::

\

*Why am I getting a message about there being insufficient storage for
the ray trajectory?*\

Storage is pre-allocated for each ray based on the MaxN parameter in
BellhopMod. (Dynamic allocation is a bit complicated because one
doesn\'t know the number of ray steps needed in advance.) You can easily
change MaxN. Bellhop doesn\'t use a lot of memory so you can make MaxN a
large number. However, in unusual circumstances a ray can outrun the
MaxN limit, using up a lot of CPU time in the process. When that
happens, it usually indicates some kind of problem. So MaxN is a kind of
governor that prevents infinite loops. It rarely happens, but when it
does, it is often when a curvilinaer boundary is used. The curvilinear
option is a bit odd in that it uses a piecewise linear approximation to
adjust ray steps to land on the boundaries. However, it adjusts the
angle of the reflected ray using a higher-order fit to the boundary.
Sometimes that inconsistency causes confusion in the logic that detects
a ray crossing the interface and then Bellhop may make a large number of
infinitesimal steps trying to get the ray back into the water column. If
you get this error, it is a good idea to do a ray trace plot to see if
there is a ray getting stuck at a boundary. You can also look in the ray
file itself and see if there is a ray with a lot of steps that has
gotten stuck.\

*\*

*Why does plotray.m not show the rays at the point where they actually
hit the bottom?*\

When the number of steps in a ray is very large, Bellhop may (depending
on the version) sub-sample the rays so that the file is not too large.
The sub-sampled rays may not include the steps where the ray hits the
bottom. It is trivial to change the routine that writes the rays to turn
that feature on or off. In recent versions, I\'ve tended to disable that
feature to avoid confusion.\

*\*

*What is causing the error message about a ray exiting the box where the
bathymetry, altimetry, or SSP is defined?*\

The ray box (rBox, zBox) is a mask that traps rays that exit that box.
The environment (SSP, bathymetry, altimetry) needs to be defined for any
place where the rays get to. Usually the bathymetry and altimetry are
the key limits in the vertical direction. If, for example, your
bathymetry dips below the lowest tabulated depth for the SSP, you could
have problems. Similarly, if rBox is larger than the greatest range of
the bathymetry, altimetry, or SSP then the ray enters a domain where the
environment is not defined, causing an error.\

The ray box is defined in terms of an absolute value, so the limits of
the ray are z in \[ -zBox, +zBox \] and r in \[ -rBox, +rBox \].\
BELLHOP and BELLHOP3D can trace rays that turn around and go back to the
source. They may then travel to negative ranges. If you did not define
the bathymetry for negative ranges, then you will also get this error
message. These rays, including the negative ranges, are indeed
physical\-\-- you should think of the range slice as a slice through a
3D environment with negative ranges just being along the 180 degree
radial. In this case, make sure your bathymetry covers the domain \[
-rBox, rBox \].\

Of course, this message can also happen when the rBox limit fails to
trap an outgoing ray before it gets past the last bathymetry point. You
would then need to reduce rBox or increase the coverage of your
bathymetry to include larger ranges.\

\

\
:::::::
