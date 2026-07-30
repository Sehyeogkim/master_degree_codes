!
! Copyright (c) Stanford University, The Regents of the University of
!               California, and others.
!
!--------------------------------------------------------------------
!     Parameters on outlets
!--------------------------------------------------------------------
      REAL*8, PARAMETER ::
     &  Ra_1  = 12022.31D0,
     &  Ram_1 = 19536.27D0,
     &  Rvm_1 = 3005.58D0,
     &  Rv_1  = 3005.58D0,
     &  Cim_1 = 1.335D-5,
     &  Ca_1  = 1.65D-6,
     &  k_1   = 1.0D0,

     &  Rp_2  = 154.9752D0,
     &  Rd_2  = 1394.7768D0,
     &  C_2  = 5D-4

!--------------------------------------------------------------------
!     Heart Model Parameters on inlet
!     Maximum size for elastance arrays
!--------------------------------------------------------------------
      INTEGER, PARAMETER ::
     &  NMAX_ELAST = 2000

      REAL*8, PARAMETER ::
     &  T_cardiac = 1.0D0,          ! Cardiac cycle period (s) [typically 0.8-1.0]
     &  T_systole = 0.33D0,          ! Time in systole (s) [typically 0.25-0.35]
     &  E_max = 2666.4D0,             ! Maximum ventricular elastance (dynes/cm^5)
     &  E_a   = 200.0D0,              ! Atrial elastance (Pa/mL)
     &  R_v   = 1.0D1,              ! Ventricular resistance (Pa*s/mL)
     &  L_v   = 0.1D1,              ! Ventricular inductance (Pa*s^2/mL)
     &  R_a   = 5.0D0,             ! Atrial resistance (Pa*s/mL)
     &  L_a   = 1.0D0,             ! Atrial inductance (Pa*s^2/mL)
     &  V_v0  = 1.0D2,             ! Initial ventricular volume (mL)
     &  V_a0  = 1.0D2,             ! Initial atrial volume (mL)
     &  Q_venous = -83.3D0         ! Venous flow = Cardiac output (cc/s)
