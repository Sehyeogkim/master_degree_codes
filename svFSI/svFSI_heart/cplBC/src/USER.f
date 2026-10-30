!
! Copyright (c) Stanford University, The Regents of the University of
!               California, and others.
!####################################################################
!     Ventricular elastance function
!     This function reads Elastance.dat file on first call and stores data internally
!####################################################################
      SUBROUTINE  ventricular_elastance_at_time(
     &     current_time, E_v, dE_v_dt)
      
      IMPLICIT NONE
      INCLUDE "parameters.f"
      
      REAL(KIND=8), INTENT(IN) :: current_time
      REAL(KIND=8), INTENT(OUT) :: E_v, dE_v_dt
      
      INTEGER :: n_elast
      REAL(KIND=8), DIMENSION(NMAX_ELAST) :: t_norm_arr
      REAL(KIND=8), DIMENSION(NMAX_ELAST) :: e_norm_arr
      LOGICAL :: elastance_loaded
      
      REAL(KIND=8) :: t_within_cycle
      REAL(KIND=8) :: weight, t_elast_lower, t_elast_upper
      INTEGER :: i
      
      SAVE n_elast, t_norm_arr, e_norm_arr, elastance_loaded
      DATA elastance_loaded /.FALSE./

!--------------------------------------------------------------------
!     Read Elastance data from Elastance.dat file (only on first call)
!--------------------------------------------------------------------
      IF (.NOT. elastance_loaded) THEN
         OPEN(98, FILE='Elastance.dat', STATUS='old', ERR=100)
         n_elast = 0
         DO i = 1, NMAX_ELAST
            READ(98, *, END=101, ERR=104) t_norm_arr(i), 
     &           e_norm_arr(i)
            n_elast = i
         END DO
 101     CONTINUE
         CLOSE(98)
         
         IF (n_elast .EQ. 0) THEN
            WRITE(*,*) 'ERROR: No elastance data read from ',
     &                 'Elastance.dat'
            STOP
         END IF

         elastance_loaded = .TRUE.
         GOTO 105
 100     WRITE(*,*) 'ERROR: Elastance.dat not found.'
         STOP
 104     WRITE(*,*) 'ERROR: Error reading Elastance.dat at line ', i
         WRITE(*,*) 'Successfully read ', n_elast, ' data points.'
         CLOSE(98)
         STOP
 105     CONTINUE
      END IF

!--------------------------------------------------------------------
!     Calculate elastance at specific time t
!--------------------------------------------------------------------
      t_within_cycle = current_time - 
     &     FLOOR(current_time / T_cardiac) * T_cardiac
            
!     Initialize elastance value
      dE_v_dt = 0D0
      E_v = 0D0
      
!     Find the correct interval and interpolate
      DO i = 1, n_elast - 1
         t_elast_lower = t_norm_arr(i) * T_systole
         t_elast_upper = t_norm_arr(i+1) * T_systole

         IF (t_within_cycle .GE. t_elast_lower .AND.
     &       t_within_cycle .LT. t_elast_upper) THEN
            weight = (t_within_cycle - t_elast_lower) / 
     &               (t_elast_upper - t_elast_lower)
            E_v = E_max * 
     &           (e_norm_arr(i) * (1D0 - weight) + 
     &            e_norm_arr(i+1) * weight)
            
            dE_v_dt = E_max * (e_norm_arr(i+1) - e_norm_arr(i)) / 
     &               (t_elast_upper - t_elast_lower)
            RETURN
         END IF
      END DO
      
      RETURN
      END SUBROUTINE



!####################################################################
!     Initialize the coupled boundary conditions
!####################################################################
      SUBROUTINE cplBC_INI(nFaces, nTimeSteps, qConv, pConv, face)
      IMPLICIT NONE
      INCLUDE "cplBC.h"

      INTEGER, INTENT(IN) :: nFaces
      INTEGER, INTENT(OUT) :: nTimeSteps
      REAL(KIND=8), INTENT(OUT) :: pConv, qConv
      TYPE(cplFaceType), INTENT(OUT) :: face(nFaces)

!--------------------------------------------------------------------
!     Unit conversions and number of time steps
!--------------------------------------------------------------------
      pConv = 1D0
      qConv = 1D0
      nTimeSteps = 100

!--------------------------------------------------------------------
!     List of all coupled faces, BC groups and Xptr is specified here
!--------------------------------------------------------------------
      INCLUDE "faces.f"
      END SUBROUTINE cplBC_INI

!####################################################################
!     Here you should find the f_i = dx_i/dt
!####################################################################
      SUBROUTINE cplBC_FINDF(t, nFaces, nX, X, f, Q, P, offst, nW, Xw)
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: nFaces, nX, nW
      REAL(KIND=8), INTENT(IN) :: t
      REAL(KIND=8), INTENT(IN) :: Q(nFaces), P(nFaces)
      REAL(KIND=8), INTENT(OUT) :: f(nX), offst(nFaces)
      REAL(KIND=8), INTENT(INOUT) :: x(nX), Xw(nW)

!--------------------------------------------------------------------
!     Load parameters from parameters.f FIRST (before declaring variables)
!--------------------------------------------------------------------
      INCLUDE "parameters.f"

!--------------------------------------------------------------------
!     Variable declarations (all after IMPLICIT NONE and INCLUDE)
!--------------------------------------------------------------------
!     Variables heart model ODE
      REAL(KIND=8) :: E_v, dE_v_dt, flow_diff_ao, flow_diff_at
      LOGICAL :: aortic_open, mitral_open

!     Variables for dP_dt
      REAL(KIND=8) :: dP_v_dt, P_v, P_a
!--------------------------------------------------------------------
!     Eq 3 and 5: Calculate elastance and pressures
!--------------------------------------------------------------------
      CALL ventricular_elastance_at_time(t, E_v, dE_v_dt)
      P_a = E_a * x(5)
      P_v = E_v * x(4)

!--------------------------------------------------------------------
!     Eq4: Aortic valve (using predicted pressure)
!     When OPEN: dQ_ao/dt = (1/L_v) * [P_aor - P_v - R_v*Q_ao]
!     When CLOSED: Q_ao = 0
!--------------------------------------------------------------------
      aortic_open = (P_v .GE. P(3)) .OR. (x(6) .LT. 0D0)
      IF (aortic_open) THEN
         flow_diff_ao = P(3) - P_v - R_v * x(6)
         f(6) = flow_diff_ao / L_v
      ELSE
         f(6) = -x(6) / (0.001D0)
      END IF

!--------------------------------------------------------------------
!     Eq6: Mitral valve (using predicted pressures)
!     When OPEN: dQ_at/dt = (1/L_a) * [P_v - P_a - R_a*Q_at]
!     When CLOSED: Q_at = 0
!--------------------------------------------------------------------
      mitral_open = (P_a .GE. P_v) .OR. (x(7) .LT. 0D0)
      IF (mitral_open) THEN
         flow_diff_at = P_v - P_a - R_a * x(7)
         f(7) = flow_diff_at / L_a
      ELSE
         f(7) = -x(7) / (0.001D0)
      END IF

!--------------------------------------------------------------------
!     Eq7: derivative of ventricular pressure
!--------------------------------------------------------------------
!-------------------------------------------------------------------
!     Eq2: dV_v/dt = Q_ao - Q_at (Q < 0 is the right direction, since inlet require negative Q)
!     Eq1: dV_a/dt = Q_at - Q_venous
      f(4) = x(6) - x(7)
      f(5) = x(7) - Q_venous
      dP_v_dt = E_v * (x(6) - x(7)) + x(4) * dE_v_dt

!--------------------------------------------------------------------
!     Eq8: Outlet BCs (Coronary Windkessel)
!        dp_a/dt = Q/Ca - (p_a - p_v)/(Ca*Ram)
!                 = (Q - (p_a - p_v)/Ram) / Ca
!-------------------------------------------
            f(1) = ( Q(1) - 
     &                    ( x(1) - x(2) ) / 
     &                    Ram_1 ) / Ca_1

!-------------------------------------------
!        Eq9: dp_v/dt
!        dp_v/dt = dPim/dt + 1/Cim * [ (p_a - p_v)/Ram
!                                      - p_v/(Rvm + Rv) ]
!-------------------------------------------
            f(2) = k_1 * dP_v_dt +
     &                  ( ( x(1) - x(2) ) / 
     &                    Ram_1 -
     &                    x(2) / (Rvm_1 + Rv_1) ) / 
     &                  Cim_1

!-------------------------------------------
!        Assign outlet pressure offset
!        P_outlet = p_a + Ra * Q = x(idx_pa) + offst(i_outlet)
!-------------------------------------------
      offst(1) = Ra_1 * Q(1)

!-------------------------------------------
!      Eq 10: wind kessel RCR BC at the face1 - aortic outlet.
!-------------------------------------------
      f(3)= (1D0/C_2) * (Q(2) - x(3)/Rd_2)
      offst(2) = Q(2) * Rp_2

!-------------------------------------------
!     output data: t, outlet pressures, inlet variables
!-------------------------------------------
      Xw(1) = t
      Xw(2) = P_v       ! P_v - ventricular pressure (left ventricular pressure)
      Xw(3) = E_v       ! E_v - ventricular elastance
      IF (aortic_open) THEN
         Xw(4) = 1.0D0
      ELSE
         Xw(4) = 0.0D0
      END IF
      IF (mitral_open) THEN
         Xw(5) = 1.0D0
      ELSE
         Xw(5) = 0.0D0
      END IF
      RETURN
      END SUBROUTINE cplBC_FINDF