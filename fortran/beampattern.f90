!! Source beam pattern loading and processing

MODULE beampattern
  !! Source beam pattern handling including loading, interpolation, and angular weighting

  USE FatalError
  USE monotonicMod

  IMPLICIT NONE
  PUBLIC
  SAVE

  INTEGER, PARAMETER         :: SBPFile = 50
  INTEGER                    :: NSBPPts          ! Number of source beam-pattern points
  REAL (KIND=8), ALLOCATABLE :: SrcBmPat( :, : )
  CHARACTER (LEN=1)          :: SBPFlag          ! '*' or 'O' to indicate a directional or omni pattern

CONTAINS

  SUBROUTINE ReadPat( FileRoot, PRTFile )
    !!    Reads a source beam pattern file (`.sbp`) based on `FileRoot``.
    !!    Reports status messages to the print/log file connected to `PRTFile``.

    IMPLICIT NONE

    ! Arguments
    CHARACTER (LEN=80), INTENT( IN ) :: FileRoot
        !! Source beampattern filename *without* `.sbp` extension
    INTEGER,            INTENT( IN ) :: PRTFile
        !! I/O Unit for print file

    ! Local variables
    INTEGER :: I, IAllocStat, IOStat

    IF ( SBPFlag == '*' ) THEN
       WRITE( PRTFile, * )
       WRITE( PRTFile, * ) '______________________________'
       WRITE( PRTFile, * ) 'Using source beam pattern file'

       OPEN( UNIT = SBPFile,   FILE = TRIM( FileRoot ) // '.sbp', STATUS = 'OLD', IOSTAT = IOStat, ACTION = 'READ' )
       IF ( IOstat /= 0 ) THEN
          WRITE( PRTFile, * ) 'SBPFile = ', TRIM( FileRoot ) // '.sbp'
          CALL ERROUT( 'BELLHOP-ReadPat', 'Unable to open source beampattern file' )
       END IF

       READ(  SBPFile, * ) NSBPPts
       WRITE( PRTFile, * ) 'Number of source beam pattern points', NSBPPts

       ALLOCATE( SrcBmPat( NSBPPts, 2 ), Stat = IAllocStat )
       IF ( IAllocStat /= 0 ) &
            CALL ERROUT( 'BELLHOP-ReadPat', 'Insufficient memory for source beam pattern data: reduce # SBP points' )

       WRITE( PRTFile, * )
       WRITE( PRTFile, * ) ' Angle (degrees)  Power (dB)'

       DO I = 1, NSBPPts
          READ(  SBPFile, * ) SrcBmPat( I, : )
          WRITE( PRTFile, FMT = "( 2G11.3 )" ) SrcBmPat( I, : )
       END DO

    ELSE   ! no pattern given, use omni source pattern
       NSBPPts = 2
       ALLOCATE( SrcBmPat( 2, 2 ), Stat = IAllocStat )
       IF ( IAllocStat /= 0 ) CALL ERROUT( 'BELLHOP-ReadPat', 'Insufficient memory'  )
       SrcBmPat( 1, : ) = [ -180.0, 0.0 ]
       SrcBmPat( 2, : ) = [  180.0, 0.0 ]
    ENDIF

    IF ( .NOT. monotonic( SrcBmPat( :, 1 ) , NSBPPts ) ) &
       CALL ERROUT( 'beampattern : ReadPat', 'Source beam-pattern angles are not monotonic' )

    SrcBmPat( :, 2 ) = 10 ** ( SrcBmPat( :, 2 ) / 20 )  ! convert dB to linear scale

  END SUBROUTINE ReadPat

END MODULE beampattern
