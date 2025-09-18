!! Provides an interface for performing an insertion sort on a vector

MODULE SortMod
  !! Provides an interface for performing an insertion sort on a vector

  ! At the Ith step, the first I-1 positions contain a sorted
  ! vector.  We shall insert the Ith value into its place in that
  ! vector shifting up to produce a new vector of length I.

  IMPLICIT NONE
  PUBLIC

  INTEGER, PRIVATE :: ILeft, IMiddle, IRight, I

  INTERFACE Sort
     MODULE PROCEDURE Sort_sngl, Sort_dble, Sort_cmplx
  END INTERFACE Sort

CONTAINS

  SUBROUTINE Sort_sngl( x, N )
    !! Subroutine to perform an insertion sort on a vector (single)

    INTEGER, INTENT( IN ) :: N
    REAL, INTENT( INOUT ) :: x(:)
    REAL    :: xTemp

    IF ( N == 1 ) RETURN

    DO I = 2, N

       xTemp = x( I )

       IF ( xTemp < x( 1 ) ) THEN
          x( 2 : I ) = x( 1 : I - 1 )
          x( 1 )     = xTemp  ! goes in the first position
       ELSE IF ( xTemp < x( I - 1 ) ) THEN ! Binary search for its place

          IRight = I - 1
          ILeft  = 1

          DO WHILE ( IRight > ILeft + 1 )
             IMiddle = ( ILeft + IRight ) / 2
             IF ( xTemp < x( IMiddle ) ) THEN
                IRight = IMiddle
             ELSE
                ILeft  = IMiddle
             ENDIF
          END DO

          ! Shift and insert
          x( IRight + 1 : I ) = x( IRight : I - 1 )
          x( IRight ) = xTemp

       ENDIF

    END DO

  END SUBROUTINE Sort_sngl

  ! ________________________________________________________________________

  SUBROUTINE Sort_dble( x, N )
    !! Subroutine to perform an insertion sort on a vector (double)

    INTEGER, INTENT( IN )          :: N
    REAL (KIND=8), INTENT( INOUT ) :: x(:)
    REAL (KIND=8)                  :: xTemp

    IF ( N == 1 ) RETURN

    DO I = 2, N

       xTemp = x( I )

       IF ( xTemp < x( 1 ) ) THEN
          x( 2 : I ) = x( 1 : I - 1 )
          x( 1 )     = xTemp  ! goes in the first position
       ELSE IF ( xTemp < x( I - 1 ) ) THEN ! Binary search for its place

          IRight = I - 1
          ILeft  = 1

          DO WHILE ( IRight > ILeft + 1 )
             IMiddle = ( ILeft + IRight ) / 2
             IF ( xTemp < x( IMiddle ) ) THEN
                IRight = IMiddle
             ELSE
                ILeft  = IMiddle
             ENDIF
          END DO

          ! Shift and insert
          x( IRight + 1 : I ) = x( IRight : I - 1 )
          x( IRight ) = xTemp

       ENDIF

    END DO

  END SUBROUTINE Sort_dble

  ! ________________________________________________________________________

  SUBROUTINE Sort_cmplx( x, N )
    !! Subroutine to perform an insertion sort on a vector (complex, double)

    ! Based on order of decreasing real part

    INTEGER, INTENT( IN )             :: N
    COMPLEX (KIND=8), INTENT( INOUT ) :: x( N )
    COMPLEX (KIND=8)                  :: xTemp

    IF ( N == 1 ) RETURN

    DO I = 2, N

       xTemp = x( I )

       IF ( REAL( xTemp ) > REAL( x( 1 ) ) ) THEN
          x( 2 : I ) = x( 1 : I - 1 )
          x( 1 )     = xTemp  ! goes in the first position
       ELSE IF ( REAL( xTemp ) > REAL( x( I - 1 ) ) ) THEN ! Binary search for its place

          IRight = I - 1
          ILeft  = 1

          DO WHILE ( IRight > ILeft + 1 )
             IMiddle = ( ILeft + IRight ) / 2

             IF ( REAL( xTemp ) > REAL( x( IMiddle ) ) ) THEN
                IRight = IMiddle
             ELSE
                ILeft  = IMiddle
             END IF
          END DO

          x( IRight + 1 : I ) = x( IRight : I - 1 )
          x( IRight ) = xTemp

       END IF

    END DO

  END SUBROUTINE Sort_cmplx

END MODULE SortMod


