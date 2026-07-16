# TODO: BELLHOP I/O and interface gaps

Two audits are collected here:

1. **BELLHOP3D I/O gaps** — places where BELLHOP3D's I/O assumes the structure of
   the 2D case, or is otherwise incomplete relative to 2D.
2. **2D BELLHOP Python interface gaps** — Fortran-supported inputs (mostly around
   Cerveny beams) that `aubellhop` cannot express, plus bugs found along the way.

File:line references are to the current `main` branch.

---

# Part 1: BELLHOP3D I/O gaps

Findings from a sweep of `fortran/` (and the `python/aubellhop` wrapper) looking for
places where BELLHOP3D's I/O assumes the structure of the 2D BELLHOP case, or is
otherwise incomplete relative to 2D. Most 2D↔3D branching (env file parsing,
source/receiver positions, run type, ray/arrival/shd file headers) is handled
correctly and was not flagged below — this list is the exceptions.

## Confirmed bugs / gaps

### 1. `.ray` file drops the bearing angle for 3D rays
[fortran/WriteRay.f90](fortran/WriteRay.f90) — `WriteRay3D` (line 63) takes `beta0`
(the ray's launch bearing) as an argument but only ever writes `alpha0` to the ray
file (line 98), identical to the 2D header format. Every 3D ray record loses its
bearing angle; there's no way to tell from the `.ray` file alone which bearing
produced which ray path.

Confirmed downstream: [python/aubellhop/readers.py:1091](python/aubellhop/readers.py:1091)
(`read_rays`) parses a single float per ray as `angle_of_departure` for both 2D and
3D files — there's no bearing column to read even if the Fortran side were fixed
without also widening the reader.

**Fix**: write `alpha0, beta0` in `WriteRay3D`'s per-ray header line (guard by
`ThreeD`/RunType so the 2D `.ray` format is untouched), and update the ray file
format doc + Python reader together.

### 2. 3D bathymetry/altimetry files can't carry spatially-varying geoacoustics
2D `.bty`/`.ati` support a "long format" (`btyType(2:2) == 'L'`) that gives each
range point its own `alphaR, betaR, rho, alphaI, betaI` — see
[fortran/bdryMod.f90:34-40](fortran/bdryMod.f90:34) (`BdryPt` has an `HS` field) and
the `'L'` case in `ReadBTY`/`ReadATI` (lines 100-107, 200-208).

The 3D equivalent, [fortran/bdry3DMod.f90:44-49](fortran/bdry3DMod.f90:44), has no
`HS` field on its `BdryPt` type at all — `ReadATI3D`/`ReadBTY3D` only ever read a
depth grid (`Top(:,iy)%x(3)` / `Bot(:,iy)%x(3)`, lines 134, 278). Confirmed at the
call sites in [fortran/bellhop3D.f90:1072](fortran/bellhop3D.f90:1072) and
`:1107` — `Reflect3D` is always passed the single global `Bdry%Top%HS` /
`Bdry%Bot%HS` from the `.env` file, never anything derived from the bathymetry
file. So a 3D run cannot express "sand here, mud over there" — every reflection
uses the same bottom type everywhere.

This is a known, self-documented gap: the author's own TODO list at the top of
[fortran/bellhop3D.f90:60](fortran/bellhop3D.f90:60) lists "Variable bottom type
vs. lat/long" under "Desired additional features."

**Fix**: extend `bdry3DMod`'s `BdryPt` with an `HS` field, add a long-format grid
read to `ReadATI3D`/`ReadBTY3D`, and thread per-facet HS into `Reflect3D` instead
of the global `Bdry%Top/Bot%HS`.

### 3. SSP types 'P' (PCHIP) and 'Q' (Quad) are accepted for 3D runs but not implemented — ✅ guarded on the Python side
[fortran/ReadEnvironmentBell.f90:263-290](fortran/ReadEnvironmentBell.f90:263)
(`ReadTopOpt`) accepts SSP type `'P'` or `'Q'` unconditionally — there's no
`ThreeD`-specific rejection, and for `'Q'` it happily opens the `.ssp` file.

But [fortran/sspMod.f90:160-174](fortran/sspMod.f90:160) (`EvaluateSSP3D`'s
`SELECT CASE ( SSP%Type )`) only implements `'N'`, `'C'`, `'S'`, `'H'`, `'A'` — `'P'`
and `'Q'` fall through to `CASE DEFAULT` and `CALL ERROUT(... 'Invalid profile
option')`. A user who sets `'P'` or `'Q'` in a 3D `.env` file gets a clean parse and
then a hard crash the first time the ray tracer asks for a sound speed — the error
is reported nowhere near the actual mistake (the `.env` file's SSP type flag).

Both flags already have a Python interface (`env['soundspeed_interp'] =
'pchip'`/`'quadrilateral'`, mapped in
[constants.py:132-133](python/aubellhop/constants.py:132)), so a Python user could
hit this crash easily. **Fixed**: added an assertion in
[environment.py:`_check_env_ssp`](python/aubellhop/environment.py) that rejects
`soundspeed_interp in ('pchip', 'quadrilateral')` when `dimension == 3`, raising a
clear `ValueError` at `.check()` time instead of letting it reach the Fortran
binary. Verified: 2D+pchip still passes, 3D+linear still passes, 3D+pchip and
3D+quadrilateral both now raise immediately.

The underlying Fortran gap (`EvaluateSSP3D` not implementing `'P'`/`'Q'`) is still
open — this only prevents the crash for users going through the Python wrapper.
Anyone driving `bellhop3d.exe` directly with a hand-written `.env` file can still
hit it. **Remaining fix**: implement `'P'`/`'Q'` in `EvaluateSSP3D` (probably just a
2D-slice delegation like the existing `'N'`/`'C'`/`'S'` cases), or validate
`ThreeD .AND. SSP%Type IN ('P','Q')` at `ReadTopOpt` time in the Fortran itself.

### 4. Reflection coefficient tables have no azimuthal dependence
[fortran/RefCoef.f90](fortran/RefCoef.f90) — `.brc`/`.trc` tables and
`InterpolateReflectionCoefficient` are purely a function of grazing angle
(`theta`). There is no bearing/azimuth axis anywhere in `ReflectionCoef` (line
20-22). Combined with gap #2, this means a 3D run's bottom-loss physics is
identical in every horizontal direction even when the `.env`/`.bty` setup implies a
directionally-varying environment (e.g. a sloped, sediment-graded shelf).

This is a smaller, more architectural item — flagging for awareness rather than a
quick fix, since it would mean extending the `.brc`/`.trc` file format itself.

### 5. Cerveny beams inside BELLHOP3D's Nx2D mode sample the wrong SSP slice
[fortran/influence.f90:228](fortran/influence.f90:228) calls the plain
`EvaluateSSP( ray2D(iS)%x, ... )` — the 2D-signature dispatcher — rather than
`EvaluateSSP2D`, which is the one that knows how to slice a 3D SSP field along the
current radial (see its use elsewhere in bellhop3D.f90, e.g.
[fortran/bellhop3D.f90:770](fortran/bellhop3D.f90:770)). `influence.f90`'s Cerveny
beam path is shared between `bellhop.f90` and the Nx2D path of `bellhop3D.f90`, but
it has no way to pass in the source's (x, y) offset and bearing needed to index
into a 3D SSP.

This is self-documented too — see
[fortran/bellhop3D.f90:50](fortran/bellhop3D.f90:50): "Cerveny beams (rarely
used): influenceC calls SSP; need to select EvaluateSSP2D or EvaluateSSP3D for that
to work in BELLHOP3D." In practice: Cerveny beams (`RunType(2:2)` = `'C'`/`'R'`) in
an Nx2D run with a range/bearing-varying (not just depth-varying) SSP field will
silently use the wrong sound speed profile instead of erroring.

**Fix**: give `influence.f90`'s Cerveny path an `EvaluateSSP2D`-aware call when
invoked from BELLHOP3D (needs `xs_3D`/`tradial` threaded in), or explicitly
restrict Cerveny beams to depth-only 3D SSPs and validate at input time.

## Other gaps the author already flagged (not independently re-verified in depth)

Straight from the "Loose ends" / "Desired additional features" header comment in
[fortran/bellhop3D.f90:41-63](fortran/bellhop3D.f90:41) — listed here because they
bear directly on 3D I/O correctness and are easy to lose track of:

- Nx2D mode doesn't handle jumps in `cx`, `cy` (in `Step2D`).
- Can't specify `isingle(2)` (single-beam debug selection) for alpha *and* beta
  simultaneously.
- Trilinear (hexahedral) SSP interpolation ignores `cxy` cross-derivative terms.
- If the lower halfspace is much deeper than the SSP's max depth, the step size
  selection can be too large and the ray exits the ray box.
- `Influence3DGeoHat` writes no eigenray info when `NR == 1` (single receiver
  range) — see the `'E'` case around
  [fortran/influence3D.f90:813](fortran/influence3D.f90:813).
- No check for `Sz` (source depth) being below the bottom when a `.bty` file is in
  use — 2D's `ReadSzRz` clamps against `zMin`/`zMax` from the *nominal* SSP depths,
  not the actual (possibly shallower) bathymetry at the source's x,y.
- No "terrain following" option for receiver depth.

## Python wrapper (`python/aubellhop`): read/write asymmetry mirrors the Fortran gaps

The wrapper already has 3D-aware *readers* — `read_ssp_3d`
([readers.py:489](python/aubellhop/readers.py:489)) and `read_ati_3d`/`read_bty_3d`
([readers.py:666-707](python/aubellhop/readers.py:666)) both know the 3D grid file
formats. But the *writer* side does not:

- [writers.py:287](python/aubellhop/writers.py:287) (`_create_bty_ati_file`) always
  emits the 2D range/depth `S`/`L` format, for both 2D and 3D `Environment`s (called
  unconditionally at lines 89 and 93). There is no code path that emits BELLHOP3D's
  grid format (`'R'`/`'C'` type line, NX + x-vector, NY + y-vector, NY rows of NX
  depths — see `ReadATI3D`/`ReadBTY3D` above). **A 3D `Environment` with
  `bottom_interp` set cannot currently produce a bathymetry file BELLHOP3D can
  read** — it'll get a 2D-shaped file instead.
- [writers.py:317](python/aubellhop/writers.py:317) (`_create_ssp_quad_file`) only
  writes the 2D quad `.ssp` grid (range × depth). There's no writer for the 3D
  hexahedral `.ssp` grid (x × y × z) that `sspMod.f90`'s `Hexahedral` reader
  expects, even though `read_ssp_3d` can parse one back.

These two are probably the highest-leverage items if the goal is genuinely
usable BELLHOP3D support from Python, since right now there's no way to author a
non-flat 3D environment from the wrapper at all, regardless of whether the Fortran
side is fixed.

---

# Part 2: 2D BELLHOP — missing Python interfaces (Cerveny beams and friends)

Findings from a systematic comparison of every input `bellhop.exe` reads (via
`ReadEnvironmentBell.f90`, `angleMod.f90`, `RefCoef.f90`, `bdryMod.f90`) against
what `environment.py`/`writers.py`/`readers.py` can express. The bulk of the gaps
cluster around the Cerveny beam options, confirming the vague recollection that
prompted this audit.

## Fortran bug found along the way (fork regression — fix first)

### 2.1 Cerveny ray-centered beams crash on coherent TL runs — ✅ FIXED
[fortran/influence.f90:161-167](fortran/influence.f90:161) — `InfluenceCervenyRayCen`'s
`SELECT CASE ( Beam%RunType( 1 : 1 ) )` handles `'I', 'S'` (squares the
contribution) and ERROUTs with "Unknown RunType" on everything else — including
`'C'` (coherent), which in the original code was a deliberate pass-through (the
`SELECT` replaced an `IF I-or-S` with no else-branch). Introduced by commit
`a320828` ("add error handling to fortran code"), which added a `CASE DEFAULT`
error to an intentionally non-exhaustive select.

Compare [fortran/influence.f90:313-321](fortran/influence.f90:313) —
`InfluenceCervenyCart` has the correct three-way form (`'C'` → scale, `'I','S'` →
abs², DEFAULT → error).

**Effect**: any coherent TL run with `RunType(2:2) = 'R'` (Cerveny ray-centered
beams) dies mid-run. **Fixed** by adding a no-op `CASE ( 'C' )` to the select in
`InfluenceCervenyRayCen`; regression test `tests/test_cerveny.py` runs
`tests/Cerveny/CervenyR_Coh.env` end-to-end.

## Python bugs

### 2.2 Env reader gates the Cerveny lines on the wrong beam type — ✅ FIXED
[python/aubellhop/readers.py:360](python/aubellhop/readers.py:360) —
`_read_gaussian_params` bails unless `beam_type in (gaussian_simple, ray)`. The
Fortran reads the two extra beam lines for `RunType(2:2)` in `('R', 'C')` =
`(ray, cartesian)` — and the *writer*
([writers.py:230](python/aubellhop/writers.py:230)) uses the correct pair.
Consequences:
- reading an env file with Cerveny **Cartesian** beams silently drops the two
  Cerveny parameter lines (round-trip loses `beam_width_type` etc.);
- reading an env file with **simple Gaussian** beams (`'S'`) tries to consume two
  lines that don't exist in the file.

**Fixed** by changing the reader's condition to
`(BHStrings.cartesian, BHStrings.ray)`; covered by the read tests in
`tests/test_cerveny.py` (Cartesian params parsed, SGB trailing lines skipped).

## Missing interfaces / dead Environment fields

### 2.3 `beam_reflection_curvature_change` is declared but never wired up
[environment.py:178](python/aubellhop/environment.py:178) declares it; nothing in
`writers.py`/`readers.py` touches it. The Fortran reads beam width and curvature
change as a single two-char token `Beam%Type(2:3)` — width `F/M/W` + curvature
`D/S/Z` ([ReadEnvironmentBell.f90:202-216](fortran/ReadEnvironmentBell.f90:202)).
The writer emits only `beam_width_type`
([writers.py:233](python/aubellhop/writers.py:233)), so unless the user knows to
smuggle both chars into one field (`beam_width_type='FD'`), the curvature char is
blank and the Fortran ERROUTs at parse time ("Unknown curvature condition").
Same crash if `beam_width_type` is left at its default `None` for a Cerveny run
(the line is written as bare `/`, leaving `Beam%Type(2:3) = '  '`).

**Fix**: writer concatenates `beam_width_type + beam_reflection_curvature_change`
(with sensible defaults, e.g. `'F'`+`'D'`); reader splits the token back into the
two fields; validate values (`F/M/W`, `D/S/Z`) in `Environment.check()`.

### 2.4 `beam_reflection_shift` is declared but never wired up — RunType char 7 unwritable
[environment.py:179](python/aubellhop/environment.py:179) declares it; never used.
The Fortran maps `RunType(7:7)` → `Beam%Type(4:4)`; `'S'` enables beam
displacement & width change on boundary reflection ("Seongil's version",
[bellhop.f90:798](fortran/bellhop.f90:798)). But `_write_env_task`
([writers.py:213](python/aubellhop/writers.py:213)) only emits RunType chars 1–5,
and `_parse_task` ([readers.py:304](python/aubellhop/readers.py:304)) only parses
chars 1–6. The beam-shift physics is unreachable from Python.

### 2.5 Analytic SSP (`'A'`) has no Python mapping
`FlagMaps.soundspeed_interp`
([constants.py:129-137](python/aubellhop/constants.py:129)) covers
`S/C/Q/P/H/N` but not `'A'`, which 2D BELLHOP supports
([ReadEnvironmentBell.f90:286](fortran/ReadEnvironmentBell.f90:286),
`Analytic`/`AnalyticCosh` in sspMod.f90). Reading an env file that uses it raises
"option not available"; writing one is impossible.

### 2.6 Boundary conditions `'W'`/`'P'` (IRC) missing from both BC maps
`TopBot` accepts `V/R/A/G/F/W/P`
([ReadEnvironmentBell.f90:456-473](fortran/ReadEnvironmentBell.f90:456)).
`FlagMaps.bottom_boundary_condition` has `V/A/R/G/F`;
`surface_boundary_condition` has `V/A/R/F` (also missing `'G'`). In particular
`'P'` is a real feature: bottom BC `'P'` makes `ReadReflectionCoefficient` read a
precalculated internal reflection coefficient from a `.irc` file
([RefCoef.f90:108-125](fortran/RefCoef.f90:108)) — typically produced by BOUNCE.
No way to select it from Python. (`'W'` looks vestigial in BELLHOP itself — no
IRC-writing code exists in `bellhop.f90` — verify before exposing.)

## Missing guards (valid Python input → guaranteed Fortran ERROUT)

Same category as the 3D pchip/quad guard added to `_check_env_ssp` — the wrapper
accepts these and the crash happens in Fortran with no pointer back to the
offending setting:

### 2.7 `beam_type='gaussian-ray'` (`'b'`) is not implemented in 2D BELLHOP
`PickEpsilon` hard-errors: "Geo Gaussian beams in ray-centered coords. not
implemented in BELLHOP" ([bellhop.f90:438-439](fortran/bellhop.f90:438)). The
FlagMap happily maps it ([constants.py:211](python/aubellhop/constants.py:211)).
Should raise at `check()` time for 2D environments.

### 2.8 Cerveny beams don't support eigenray or arrival runs
Both Cerveny influence routines ERROUT: "Cerveny influence does not support
eigenrays or arrivals" ([influence.f90:42](fortran/influence.f90:42), `:201`).
Python allows `beam_type` `cartesian`/`ray` combined with tasks
`eigenrays`/`arrivals`/`arrivals-binary`. Should raise at `check()` time.

### 2.9 No validation of Cerveny numeric/char params
- `beam_images_num` must be 1–3
  ([influence.f90:107-108](fortran/influence.f90:107));
- `beam_component` must be `P`/`V`/`H`
  ([influence.f90:140-153](fortran/influence.f90:140)) — also exposed as a raw
  Fortran char rather than a readable string, unlike the rest of the interface.

## Adjacent finding (3D, discovered in passing)

### 2.10 Writer never emits RunType char 6 — full-3D runs unreachable from Python
`_write_env_task` writes RunType chars 1–5 only; `ReadRunType` defaults char 6 to
`'2'` = Nx2D ([ReadEnvironmentBell.f90:433-440](fortran/ReadEnvironmentBell.f90:433)).
So even with `dimension='3D'`, a Python-written env file always runs bellhop3d in
Nx2D mode; full 3D (`'3'`) cannot be produced. (The *reader* does parse char 6,
so this is write-side only.) Belongs with Part 1 priorities.

## Fortran curiosity (no Python action needed)

The broadband machinery (`ReadfreqVec`,
[SourceReceiverPositions.f90:53-91](fortran/SourceReceiverPositions.f90:53),
keyed on `TopOpt(6:6) == 'B'`) is unreachable: `ReadTopOpt` rejects anything but
`'I'` or `' '` in position 6
([ReadEnvironmentBell.f90:347-353](fortran/ReadEnvironmentBell.f90:347)). Dead
code inherited from upstream; nothing to interface to until the Fortran accepts
`'B'` again.
