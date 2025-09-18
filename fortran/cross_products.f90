!! Provides a standard 3D cross product function

MODULE cross_products
!! Provides a 3D cross product function for both single and double reals

  IMPLICIT NONE
  PUBLIC

  INTERFACE cross_product
     MODULE PROCEDURE cross_product_sngl, cross_product_dble
  END INTERFACE cross_product

CONTAINS

  FUNCTION cross_product_sngl( a, b )
    !! Computes 3D cross product of single precision vectors

    REAL (KIND=4), DIMENSION( 3 ) :: cross_product_sngl
    REAL (KIND=4), DIMENSION( 3 ), INTENT(  IN ) :: a, b

    cross_product_sngl( 1 ) = a( 2 ) * b( 3 ) - a( 3 ) * b( 2 )
    cross_product_sngl( 2 ) = a( 3 ) * b( 1 ) - a( 1 ) * b( 3 )
    cross_product_sngl( 3 ) = a( 1 ) * b( 2 ) - a( 2 ) * b( 1 )

  END FUNCTION cross_product_sngl

  FUNCTION cross_product_dble( a, b )
    !! Computes 3D cross product of double precision vectors

    REAL (KIND=8), DIMENSION( 3 ) :: cross_product_dble
    REAL (KIND=8), DIMENSION( 3 ), INTENT(  IN ) :: a, b

    cross_product_dble( 1 ) = a( 2 ) * b( 3 ) - a( 3 ) * b( 2 )
    cross_product_dble( 2 ) = a( 3 ) * b( 1 ) - a( 1 ) * b( 3 )
    cross_product_dble( 3 ) = a( 1 ) * b( 2 ) - a( 2 ) * b( 1 )

  END FUNCTION cross_product_dble

END MODULE cross_products
