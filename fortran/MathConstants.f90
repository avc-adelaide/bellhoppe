!! Provides maths constants such as `pi` and `i`

MODULE MathConstants
  !! Provides maths constants such as `pi` and `i`

  IMPLICIT NONE
  PUBLIC
  SAVE

  REAL    (KIND=8), PARAMETER :: pi = 3.1415926535897932D0
  REAL    (KIND=8), PARAMETER :: RadDeg = 180.0D0 / pi, DegRad = pi / 180.0D0
  COMPLEX (KIND=8), PARAMETER :: i  = ( 0.0D0, 1.0D0 )

END MODULE MathConstants
