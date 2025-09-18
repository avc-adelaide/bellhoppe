!! Monotonicity testing utilities for input validation

MODULE monotonicMod
  !! Provides interface to test whether an input vector is strictly monotonically increasing

  IMPLICIT NONE
  PUBLIC

  INTERFACE monotonic
     MODULE PROCEDURE monotonic_sngl, monotonic_dble
  END INTERFACE monotonic

CONTAINS

  FUNCTION monotonic_sngl( x, N )
    !! Tests if single precision vector is monotonically increasing

    LOGICAL :: monotonic_sngl
    INTEGER,                       INTENT( IN ) :: N
    REAL (KIND=4), DIMENSION( N ), INTENT( IN ) :: x

    monotonic_sngl = .TRUE.
    IF ( N == 1 ) RETURN
    IF ( ANY( x( 2 : N ) <= x( 1 : N - 1 ) ) ) monotonic_sngl = .FALSE.

  END FUNCTION monotonic_sngl

  FUNCTION monotonic_dble( x, N )
    !! Tests if double precision vector is monotonically increasing

    LOGICAL :: monotonic_dble
    INTEGER,                       INTENT( IN ) :: N
    REAL (KIND=8), DIMENSION( N ), INTENT( IN ) :: x

    monotonic_dble = .TRUE.
    IF ( N == 1 ) RETURN
    IF ( ANY( x( 2 : N ) <= x( 1 : N - 1 ) ) ) monotonic_dble = .FALSE.

  END FUNCTION monotonic_dble

END MODULE monotonicMod
