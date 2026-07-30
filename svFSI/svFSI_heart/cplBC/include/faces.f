!
! Copyright (c) Stanford University, The Regents of the University of
!               California, and others.
!--------------------------------------------------------------------
!     - coronary 11 windkessel outlets (5 - Windkessel) 
!       face(1): x(1), x(2)   (LAD)
!     - aorta 1 windkessel outlet (3 - Windkessel)
!       face(2): x(3)   (aorta_outlet)
!     - Inlet (Heart)
!       face(3): x(4):V_v, x(5):V_a, x(6):Q_ao, x(7):Q_at
!--------------------------------------------------------------------
      face(1)%bGrp  = cplBC_Neu
      face(1)%name  = "LAD"
      face(1)%Xptr  = 1

      face(2)%bGrp  = cplBC_Neu
      face(2)%name  = "aorta_outlet"
      face(2)%Xptr  = 3
      
      face(3)%bGrp = cplBC_Dir
      face(3)%name = "aorta_inlet"
      face(3)%Xptr = 6 ! Q_ao