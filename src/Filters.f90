! Copyright 2019 NREL

! Licensed under the Apache License, Version 2.0 (the "License"); you may not use
! this file except in compliance with the License. You may obtain a copy of the
! License at http://www.apache.org/licenses/LICENSE-2.0

! Unless required by applicable law or agreed to in writing, software distributed
! under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
! CONDITIONS OF ANY KIND, either express or implied. See the License for the
! specific language governing permissions and limitations under the License.
! -------------------------------------------------------------------------------------------
! This module contains all the filters and related subroutines

! Filters:
!       LPFilter: Low-pass filter
!       SecLPFilter: Second order low-pass filter
!       HPFilter: High-pass filter
!       NotchFilter: Notch filter
!       NotchFilterSlopes: Notch Filter with descending slopes
!       PreFilterMeasuredSignals: Pre-filter signals during each run iteration

MODULE Filters
!...............................................................................................................................

IMPLICIT NONE

CONTAINS
!-------------------------------------------------------------------------------------------------------------------------------
    REAL FUNCTION LPFilter(InputSignal, DT, CornerFreq, iStatus, reset, inst)
    ! Discrete time Low-Pass Filter of the form:
    !                           H(z) = (b1z + b0) / (a1*z + a0)
    !
        REAL(4), INTENT(IN)         :: InputSignal
        REAL(4), INTENT(IN)         :: DT                       ! time step [s]
        REAL(4), INTENT(IN)         :: CornerFreq               ! corner frequency [rad/s]
        INTEGER(4), INTENT(IN)      :: iStatus                  ! A status flag set by the simulation as follows: 0 if this is the first call, 1 for all subsequent time steps, -1 if this is the final call at the end of the simulation.
        INTEGER(4), INTENT(INOUT)   :: inst                     ! Instance number. Every instance of this function needs to have an unique instance number to ensure instances don't influence each other.
        LOGICAL(4), INTENT(IN)      :: reset                    ! Reset the filter to the input signal

            ! Local
        REAL(4), SAVE                   :: a1                   ! Denominator coefficient 1
        REAL(4), SAVE                   :: a0                   ! Denominator coefficient 0
        REAL(4), SAVE                   :: b1                    ! Numerator coefficient 1
        REAL(4), SAVE                   :: b0                    ! Numerator coefficient 0 

        REAL(4), DIMENSION(99), SAVE    :: InputSignalLast      ! Input signal the last time this filter was called. Supports 99 separate instances.
        REAL(4), DIMENSION(99), SAVE    :: OutputSignalLast ! Output signal the last time this filter was called. Supports 99 separate instances.

            ! Initialization
        IF ((iStatus == 0) .OR. reset) THEN   
            ! a1 = 
            OutputSignalLast(inst) = InputSignal
            InputSignalLast(inst) = InputSignal
        ENDIF

        ! Define coefficients
        a1 = 2 + CornerFreq*DT
        a0 = CornerFreq*DT - 2
        b1 = CornerFreq*DT
        b0 = CornerFreq*DT

        ! Filter
        LPFilter = 1.0/a1 * (-a0*OutputSignalLast(inst) + b1*InputSignal + b0*InputSignalLast(inst))

        ! Save signals for next time step
        InputSignalLast(inst)  = InputSignal
        OutputSignalLast(inst) = LPFilter
        inst = inst + 1

    END FUNCTION LPFilter
!-------------------------------------------------------------------------------------------------------------------------------
    REAL FUNCTION SecLPFilter(InputSignal, DT, CornerFreq, Damp, iStatus, reset, inst)
    ! Discrete time Low-Pass Filter of the form:
    !                           H(z) = (b2z^2 + b1z + b0) / (a2z^2 + a1*z + a0)
        IMPLICIT NONE
        REAL(4), INTENT(IN)         :: InputSignal
        REAL(4), INTENT(IN)         :: DT                       ! time step [s]
        REAL(4), INTENT(IN)         :: CornerFreq               ! corner frequency [rad/s]
        REAL(4), INTENT(IN)         :: Damp                     ! Dampening constant
        INTEGER(4), INTENT(IN)      :: iStatus                  ! A status flag set by the simulation as follows: 0 if this is the first call, 1 for all subsequent time steps, -1 if this is the final call at the end of the simulation.
        INTEGER(4), INTENT(INOUT)   :: inst                     ! Instance number. Every instance of this function needs to have an unique instance number to ensure instances don't influence each other.
        LOGICAL(4), INTENT(IN)      :: reset                    ! Reset the filter to the input signal

        ! Local
        REAL(4), SAVE                   :: a2                   ! Denominator coefficient 2
        REAL(4), SAVE                   :: a1                   ! Denominator coefficient 1
        REAL(4), SAVE                   :: a0                   ! Denominator coefficient 0
        REAL(4), SAVE                   :: b2                    ! Numerator coefficient 2
        REAL(4), SAVE                   :: b1                    ! Numerator coefficient 1
        REAL(4), SAVE                   :: b0                    ! Numerator coefficient 0 
        REAL(4), DIMENSION(99), SAVE :: InputSignalLast1    ! Input signal the last time this filter was called. Supports 99 separate instances.
        REAL(4), DIMENSION(99), SAVE :: InputSignalLast2    ! Input signal the next to last time this filter was called. Supports 99 separate instances.
        REAL(4), DIMENSION(99), SAVE :: OutputSignalLast1   ! Output signal the last time this filter was called. Supports 99 separate instances.
        REAL(4), DIMENSION(99), SAVE :: OutputSignalLast2   ! Output signal the next to last time this filter was called. Supports 99 separate instances.

        ! Initialization
        IF ((iStatus == 0) .OR. reset )  THEN
            OutputSignalLast1(inst)  = InputSignal
            OutputSignalLast2(inst)  = InputSignal
            InputSignalLast1(inst)   = InputSignal
            InputSignalLast2(inst)   = InputSignal
        ENDIF

        ! Coefficients
        a2 = DT**2*CornerFreq**2 + 4 + 4*Damp*CornerFreq*DT
        a1 = 2*DT**2*CornerFreq**2 - 8
        a0 = DT**2*CornerFreq**2 + 4 - 4*Damp*CornerFreq*DT
        b2 = DT**2*CornerFreq**2 
        b1 = 2*DT**2*CornerFreq**2 
        b0 = DT**2*CornerFreq**2 
        
        SecLPFilter = 1.0/a2* (-a1*OutputSignalLast1(inst) - a0*OutputSignalLast2(inst) + b2*InputSignal &
                                + b1*InputSignalLast1(inst) + b0*InputSignalLast2(inst))

        ! Save signals for next time step
        InputSignalLast2(inst)   = InputSignalLast1(inst)
        InputSignalLast1(inst)   = InputSignal
        OutputSignalLast2(inst)  = OutputSignalLast1(inst)
        OutputSignalLast1(inst)  = SecLPFilter
        inst = inst + 1

    END FUNCTION SecLPFilter
!-------------------------------------------------------------------------------------------------------------------------------
    REAL FUNCTION HPFilter( InputSignal, DT, CornerFreq, iStatus, reset, inst)
    ! Discrete time High-Pass Filter

        REAL(4), INTENT(IN)     :: InputSignal
        REAL(4), INTENT(IN)     :: DT                       ! time step [s]
        REAL(4), INTENT(IN)     :: CornerFreq               ! corner frequency [rad/s]
        INTEGER, INTENT(IN)     :: iStatus                  ! A status flag set by the simulation as follows: 0 if this is the first call, 1 for all subsequent time steps, -1 if this is the final call at the end of the simulation.
        INTEGER, INTENT(INOUT)  :: inst                     ! Instance number. Every instance of this function needs to have an unique instance number to ensure instances don't influence each other.
        LOGICAL(4), INTENT(IN)  :: reset                    ! Reset the filter to the input signal
        ! Local
        REAL(4)                         :: K                        ! Constant gain
        REAL(4), DIMENSION(99), SAVE    :: InputSignalLast      ! Input signal the last time this filter was called. Supports 99 separate instances.
        REAL(4), DIMENSION(99), SAVE    :: OutputSignalLast ! Output signal the last time this filter was called. Supports 99 separate instances.

        ! Initialization
        IF ((iStatus == 0) .OR. reset)  THEN
            OutputSignalLast(inst) = InputSignal
            InputSignalLast(inst) = InputSignal
        ENDIF
        K = 2.0 / DT

        ! Body
        HPFilter = K/(CornerFreq + K)*InputSignal - K/(CornerFreq + K)*InputSignalLast(inst) - (CornerFreq - K)/(CornerFreq + K)*OutputSignalLast(inst)

        ! Save signals for next time step
        InputSignalLast(inst)   = InputSignal
        OutputSignalLast(inst)  = HPFilter
        inst = inst + 1

    END FUNCTION HPFilter
!-------------------------------------------------------------------------------------------------------------------------------
    REAL FUNCTION NotchFilterSlopes(InputSignal, DT, CornerFreq, Damp, iStatus, reset, inst)
    ! Discrete time inverted Notch Filter with descending slopes, G = CornerFreq*s/(Damp*s^2+CornerFreq*s+Damp*CornerFreq^2)

        REAL(4), INTENT(IN)     :: InputSignal
        REAL(4), INTENT(IN)     :: DT                       ! time step [s]
        REAL(4), INTENT(IN)     :: CornerFreq               ! corner frequency [rad/s]
        REAL(4), INTENT(IN)     :: Damp                     ! Dampening constant
        INTEGER, INTENT(IN)     :: iStatus                  ! A status flag set by the simulation as follows: 0 if this is the first call, 1 for all subsequent time steps, -1 if this is the final call at the end of the simulation.
        INTEGER, INTENT(INOUT)  :: inst                     ! Instance number. Every instance of this function needs to have an unique instance number to ensure instances don't influence each other.
        LOGICAL(4), INTENT(IN)  :: reset                    ! Reset the filter to the input signal
        ! Local
        REAL(4), DIMENSION(99), SAVE :: InputSignalLast1    ! Input signal the last time this filter was called. Supports 99 separate instances.
        REAL(4), DIMENSION(99), SAVE :: InputSignalLast2    ! Input signal the next to last time this filter was called. Supports 99 separate instances.
        REAL(4), DIMENSION(99), SAVE :: OutputSignalLast1   ! Output signal the last time this filter was called. Supports 99 separate instances.
        REAL(4), DIMENSION(99), SAVE :: OutputSignalLast2   ! Output signal the next to last time this filter was called. Supports 99 separate instances.
        
        ! Initialization
        IF ((iStatus == 0) .OR. reset) THEN
            OutputSignalLast1(inst)  = InputSignal
            OutputSignalLast2(inst)  = InputSignal
            InputSignalLast1(inst)   = InputSignal
            InputSignalLast2(inst)   = InputSignal
        ENDIF

        ! Body
        NotchFilterSlopes = 1.0/(4.0+2.0*DT*Damp*CornerFreq+DT**2.0*CornerFreq**2.0) * ( (8.0-2.0*DT**2.0*CornerFreq**2.0)*OutputSignalLast1(inst) &
                        + (-4.0+2.0*DT*Damp*CornerFreq-DT**2.0*CornerFreq**2.0)*OutputSignalLast2(inst) + &
                            (2.0*DT*Damp*CornerFreq)*InputSignal + (-2.0*DT*Damp*CornerFreq)*InputSignalLast2(inst) )

        ! Save signals for next time step
        InputSignalLast2(inst)   = InputSignalLast1(inst)
        InputSignalLast1(inst)   = InputSignal          !Save input signal for next time step
        OutputSignalLast2(inst)  = OutputSignalLast1(inst)      !Save input signal for next time step
        OutputSignalLast1(inst)  = NotchFilterSlopes
        inst = inst + 1

    END FUNCTION NotchFilterSlopes
!-------------------------------------------------------------------------------------------------------------------------------
    REAL FUNCTION NotchFilter(InputSignal, DT, omega, betaNum, betaDen, iStatus, reset, inst)
    ! Discrete time Notch Filter, G = (s^2 + 2*omega*betaNum*s + omega^2)/(s^2 + 2*omega*betaDen*s + omega^2)

        REAL(4), INTENT(IN)     :: InputSignal
        REAL(4), INTENT(IN)     :: DT                       ! time step [s]
        REAL(4), INTENT(IN)     :: omega                    ! corner frequency [rad/s]
        REAL(4), INTENT(IN)     :: betaNum                  ! Dampening constant in numerator of filter transfer function
        REAL(4), INTENT(IN)     :: betaDen                  ! Dampening constant in denominator of filter transfer function
        INTEGER, INTENT(IN)     :: iStatus                  ! A status flag set by the simulation as follows: 0 if this is the first call, 1 for all subsequent time steps, -1 if this is the final call at the end of the simulation.
        INTEGER, INTENT(INOUT)  :: inst                     ! Instance number. Every instance of this function needs to have an unique instance number to ensure instances don't influence each other.
        LOGICAL(4), INTENT(IN)  :: reset                    ! Reset the filter to the input signal
        ! Local
        REAL(4)                         :: K, P1, P2, P3, P4, P5    ! Constant gain
        REAL(4), DIMENSION(99), SAVE    :: InputSignalLast1         ! Input signal the last time this filter was called. Supports 99 separate instances.
        REAL(4), DIMENSION(99), SAVE    :: InputSignalLast2         ! Input signal the next to last time this filter was called. Supports 99 separate instances.
        REAL(4), DIMENSION(99), SAVE    :: OutputSignalLast1        ! Output signal the last time this filter was called. Supports 99 separate instances.
        REAL(4), DIMENSION(99), SAVE    :: OutputSignalLast2        ! Output signal the next to last time this filter was called. Supports 99 separate instances.

        ! Initialization
        IF ((iStatus == 0) .OR. reset) THEN
            OutputSignalLast1(inst)  = InputSignal
            OutputSignalLast2(inst)  = InputSignal
            InputSignalLast1(inst)   = InputSignal
            InputSignalLast2(inst)   = InputSignal
        ENDIF
        K = 2/DT
        P1 = (K**2 + 2*omega*BetaNum*K + omega**2)/(K**2 + 2*omega*BetaDen*K + omega**2)
        P2 = (2*omega**2 - 2*K**2)  / (K**2 + 2*omega*BetaDen*K + omega**2);
        P3 = (K**2 - 2*omega*BetaNum*K + omega**2) / (K**2 + 2*omega*BetaDen*K + omega**2)
        P4 = (2*omega**2 - 2*K**2)  / (K**2 + 2*omega*BetaDen*K + omega**2)
        P5 = (K**2 - 2*omega*BetaDen*K + omega**2)/ (K**2 + 2*omega*BetaDen*K + omega**2)
        
        ! Body
        NotchFilter = P1*InputSignal + P2*InputSignalLast1(inst) + P3*InputSignalLast2(inst) - P4*OutputSignalLast1(inst) - P5*OutputSignalLast2(inst)

        ! Save signals for next time step
        InputSignalLast2(inst)   = InputSignalLast1(inst)
        InputSignalLast1(inst)   = InputSignal          !Save input signal for next time step
        OutputSignalLast2(inst)  = OutputSignalLast1(inst)      !Save input signal for next time step
        OutputSignalLast1(inst)  = NotchFilter
        inst = inst + 1

    END FUNCTION NotchFilter
!-------------------------------------------------------------------------------------------------------------------------------
    SUBROUTINE PreFilterMeasuredSignals(CntrPar, LocalVar, objInst)
    ! Prefilter measured wind turbine signals to separate the filtering from the actual control actions

        USE ROSCO_Types, ONLY : ControlParameters, LocalVariables, ObjectInstances
        
        TYPE(ControlParameters), INTENT(INOUT)  :: CntrPar
        TYPE(LocalVariables), INTENT(INOUT)     :: LocalVar
        TYPE(ObjectInstances), INTENT(INOUT)    :: objInst

        ! Filter the HSS (generator) speed measurement:
        ! Apply Low-Pass Filter (choice between first- and second-order low-pass filter)
        IF (CntrPar%F_LPFType == 1) THEN
            LocalVar%GenSpeedF = LPFilter(LocalVar%GenSpeed, LocalVar%DT, CntrPar%F_LPFCornerFreq, LocalVar%iStatus, .FALSE., objInst%instLPF)
        ELSEIF (CntrPar%F_LPFType == 2) THEN   
            LocalVar%GenSpeedF = SecLPFilter(LocalVar%GenSpeed, LocalVar%DT, CntrPar%F_LPFCornerFreq, CntrPar%F_LPFDamping, LocalVar%iStatus, .FALSE., objInst%instSecLPF) ! Second-order low-pass filter on generator speed
        END IF
        
        IF (CntrPar%F_NotchType == 1) THEN
            LocalVar%GenSpeedF = NotchFilter(LocalVar%GenSpeedF, LocalVar%DT, CntrPar%F_NotchCornerFreq, CntrPar%F_NotchBetaNumDen(1), CntrPar%F_NotchBetaNumDen(2), LocalVar%iStatus, .FALSE., objInst%instNotch)
        END IF
        
        ! Filtering the tower fore-aft acceleration signal 
        IF ((LocalVar%iStatus == 0)) THEN
            LocalVar%NACIMU_FA_AccF = SecLPFilter(0.0, LocalVar%DT, 0.1, 0.7, LocalVar%iStatus, .TRUE., objInst%instSecLPF) ! Initialize at 0.0 acceleration. NJA: seems to be more stable
            ! LocalVar%NACIMU_FA_AccF = SecLPFilter(LocalVar%NacIMU_FA_Acc, LocalVar%DT, 0.1, 0.7, LocalVar%iStatus, .TRUE., objInst%instSecLPF)
        ELSE
            LocalVar%NACIMU_FA_AccF = SecLPFilter(LocalVar%NacIMU_FA_Acc, LocalVar%DT, 0.075, 0.7, LocalVar%iStatus, .FALSE., objInst%instSecLPF) ! Fixed Damping
        ENDIF
        LocalVar%FA_AccHPF = HPFilter(LocalVar%FA_Acc, LocalVar%DT, CntrPar%FA_HPFCornerFreq, LocalVar%iStatus, .FALSE., objInst%instHPF)
        
    END SUBROUTINE PreFilterMeasuredSignals
    END MODULE Filters
