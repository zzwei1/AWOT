      SUBROUTINE D2DX2_3D(A,
     $MAXX_IN,MAXY_IN,MAXZ_IN,NX,NY,NZ,
     $DELX,
     $BADDATA,
     $MAXX_OUT,MAXY_OUT,MAXZ_OUT,
     $D2DX2_A)

C  Thomas Matejka NOAA/NSSL 9 May 1997

C  This subroutine calculates the partial second derivative with respect
C  to the first dimension of a three-dimensional data field.

C  Input:

C  A is a three-dimensional real array.  A(I,J,K) specifies the value,
C  at the Ith grid point in the first dimension, the Jth grid point in
C  the second dimension, and the Kth grid point in the third dimension,
C  of the data field whose derivative is sought.  If it is missing, it
C  should equal BADDATA.

C  MAXX_IN is an integer variable that specifies the first dimension of
C  A in the calling program.

C  MAXY_IN is an integer variable that specifies the second dimension of
C  A in the calling program.

C  MAXZ_IN is an integer variable that specifies the third dimension of
C  A in the calling program.

C  NX is an integer variable that specifies the number of grid points in
C  the first dimension for A and D2DX2_A.

C  NY is an integer variable that specifies the number of grid points in
C  the second dimension for A and D2DX2_A.

C  NZ is an integer variable that specifies the number of grid points in
C  the third dimension for A and D2DX2_A.

C  DELX is a real variable that specifies the grid spacing in the first
C  dimension for A and D2DX2_A.

C  BADDATA is a real variable that specifies the value used to indicate
C  a missing value as described.

C  MAXX_OUT is an integer variable that specifies the first dimension of
C  D2DX2_A in the calling program.

C  MAXY_OUT is an integer variable that specifies the second dimension
C  of D2DX2_A in the calling program.

C  MAXZ_OUT is an integer variable that specifies the third dimension of
C  D2DX2_A in the calling program.

C  Output:

C  D2DX2_A is a three-dimensional real array.  D2DX2_A(I,J,K) returns
C  the value, at the Ith grid point in the first dimension, the Jth grid
C  point in the second dimension, and the Kth grid point in the third
C  dimension, of the partial second derivative of A with respect to the
C  first dimension.  If it is missing, it is returned as BADDATA.

      IMPLICIT NONE
      INTEGER MAXX_IN,MAXY_IN,MAXZ_IN,MAXX_OUT,MAXY_OUT,MAXZ_OUT,NX,NY,
     $NZ,IX,IY,IZ
      REAL DELX,BADDATA
      REAL A(MAXX_IN,MAXY_IN,MAXZ_IN)
      REAL D2DX2_A(MAXX_OUT,MAXY_OUT,MAXZ_OUT)

      DO IZ=1,NZ
         DO IY=1,NY
            DO IX=1,NX
               IF(IX.GT.1.AND.
     $         IX.LT.NX.AND.
     $         A(IX-1,IY,IZ).NE.BADDATA.AND.
     $         A(IX,IY,IZ).NE.BADDATA.AND.
     $         A(IX+1,IY,IZ).NE.BADDATA)THEN
                  D2DX2_A(IX,IY,IZ)=
     $            (A(IX-1,IY,IZ)+A(IX+1,IY,IZ)-2.*A(IX,IY,IZ))/DELX**2
               ELSE
                  D2DX2_A(IX,IY,IZ)=BADDATA
               ENDIF
            ENDDO
         ENDDO
      ENDDO
      END              
