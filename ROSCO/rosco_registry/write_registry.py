import yaml
import ROSCO_toolbox
import os
from ROSCO_toolbox.ofTools.util.FileTools import load_yaml

def generate(yfile):
    write_types(yfile)
    write_roscoio(yfile)

def write_types(yfile):
    reg = load_yaml(yfile)
    reg.pop('default_types')
    registry_fname = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'src','ROSCO_Types.f90')
    file = open(registry_fname, 'w')
    file.write('! ROSCO Registry\n')
    file.write('! This file is automatically generated by write_registry.py using ROSCO v{}\n'.format(ROSCO_toolbox.__version__))
    file.write('! For any modification to the registry, please edit the rosco_types.yaml accordingly\n \n')
    file.write('MODULE ROSCO_Types\n') 
    file.write('USE, INTRINSIC :: ISO_C_Binding\n')
    file.write('USE Constants\n')
    file.write('IMPLICIT NONE\n')
    file.write('\n')
    for toptype in reg.keys():
        file.write('TYPE, PUBLIC :: {}\n'.format(toptype))
        for attype in reg[toptype].keys():
            f90type = read_type(reg[toptype][attype])
            atstr  =  check_size(reg[toptype], attype)
            if reg[toptype][attype]['equals']:
                atstr += ' = ' + reg[toptype][attype]['equals']
            file.write('    {:<25s}     :: {:<25s}   ! {}\n'.format(f90type, atstr, reg[toptype][attype]['description']))
        file.write('END TYPE {}\n'.format(toptype))
        file.write('\n')
    file.write('END MODULE ROSCO_Types')
    file.close()

def write_roscoio(yfile):
    reg = load_yaml(yfile)
    reg.pop('default_types')
    registry_fname = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'src','ROSCO_IO.f90')
    file = open(registry_fname, 'w')
    file.write('! ROSCO IO\n')
    file.write('! This file is automatically generated by write_registry.py using ROSCO v{}\n'.format(ROSCO_toolbox.__version__))
    file.write('! For any modification to the registry, please edit the rosco_types.yaml accordingly\n \n')
    file.write('MODULE ROSCO_IO\n') 
    file.write('    USE, INTRINSIC :: ISO_C_Binding\n')
    file.write('    USE ROSCO_Types\n')
    file.write('    USE ReadSetParameters\n')
    file.write('    USE Constants\n')
    file.write('IMPLICIT NONE\n\n')
    file.write('CONTAINS\n\n')
    file.write('SUBROUTINE WriteRestartFile(LocalVar, CntrPar, objInst, RootName, size_avcOUTNAME)\n')
    file.write("    TYPE(LocalVariables), INTENT(IN)                :: LocalVar\n")
    file.write("    TYPE(ControlParameters), INTENT(INOUT)          :: CntrPar\n")
    file.write("    TYPE(ObjectInstances), INTENT(INOUT)            :: objInst\n")
    file.write("    INTEGER(IntKi), INTENT(IN)                      :: size_avcOUTNAME\n")
    file.write("    CHARACTER(size_avcOUTNAME-1), INTENT(IN)        :: RootName \n")
    file.write("    \n")
    file.write("    INTEGER(IntKi), PARAMETER    :: Un = 87             ! I/O unit for pack/unpack (checkpoint & restart)\n")
    file.write("    INTEGER(IntKi)               :: I                   ! Generic index.\n")
    file.write("    CHARACTER(128)               :: InFile              ! Input checkpoint file\n")
    file.write("    INTEGER(IntKi)               :: ErrStat\n")
    file.write("    CHARACTER(128)               :: ErrMsg              \n")
    file.write("    CHARACTER(128)               :: n_t_global          ! timestep number as a string\n")
    file.write("\n")
    file.write("    WRITE(n_t_global, '(I0.0)' ) NINT(LocalVar%Time/LocalVar%DT)\n")
    file.write("    InFile = RootName(1:size_avcOUTNAME-5)//TRIM( n_t_global )//'.RO.chkp'\n")
    file.write("    OPEN(unit=Un, FILE=TRIM(InFile), STATUS='UNKNOWN', FORM='UNFORMATTED' , ACCESS='STREAM', IOSTAT=ErrStat, ACTION='WRITE' )\n")
    file.write("\n")
    file.write("    IF ( ErrStat /= 0 ) THEN\n")
    file.write("        ErrMsg  = 'Cannot open file "'//TRIM( InFile )//'". Another program may have locked it for writing.'\n")
    file.write("\n")
    file.write("    ELSE\n")
    for var in reg['LocalVariables']:
        if reg['LocalVariables'][var]['type'] == 'derived_type':
            for dvar in reg[reg['LocalVariables'][var]['id']]:
                file.write('        WRITE( Un, IOSTAT=ErrStat) LocalVar%{}%{}\n'.format(var,dvar))
        elif reg['LocalVariables'][var]['size'] > 0:
            for i in range(reg['LocalVariables'][var]['size']):
                file.write('        WRITE( Un, IOSTAT=ErrStat) LocalVar%{}({})\n'.format(var, i+1))
        else:
            file.write('        WRITE( Un, IOSTAT=ErrStat) LocalVar%{}\n'.format(var))
    for var in reg['ObjectInstances']:
        file.write('        WRITE( Un, IOSTAT=ErrStat) objInst%{}\n'.format(var))
    file.write('        Close ( Un )\n')
    file.write('    ENDIF\n')
    file.write('END SUBROUTINE WriteRestartFile\n')
    file.write('\n \n')
    file.write('SUBROUTINE ReadRestartFile(avrSWAP, LocalVar, CntrPar, objInst, PerfData, RootName, size_avcOUTNAME, ErrVar)\n')
    # file.write('    USE ROSCO_Types, ONLY: LocalVariables, ControlParameters, ObjectInstances, PerformanceData, ErrorVariables\n')
    file.write("    TYPE(LocalVariables), INTENT(INOUT)             :: LocalVar\n")
    file.write("    TYPE(ControlParameters), INTENT(INOUT)          :: CntrPar\n")
    file.write("    TYPE(ObjectInstances), INTENT(INOUT)            :: objInst\n")
    file.write("    TYPE(PerformanceData), INTENT(INOUT)            :: PerfData\n")
    file.write("    TYPE(ErrorVariables), INTENT(INOUT)             :: ErrVar\n")
    file.write("    REAL(C_FLOAT), INTENT(IN)                       :: avrSWAP(*)\n")
    file.write("    INTEGER(IntKi), INTENT(IN)                      :: size_avcOUTNAME\n")
    file.write("    CHARACTER(size_avcOUTNAME-1), INTENT(IN)        :: RootName \n")
    file.write("    \n")
    file.write("    INTEGER(IntKi), PARAMETER    :: Un = 87             ! I/O unit for pack/unpack (checkpoint & restart)\n")
    file.write("    INTEGER(IntKi)               :: I                   ! Generic index.\n")
    file.write("    CHARACTER(128)               :: InFile              ! Input checkpoint file\n")
    file.write("    INTEGER(IntKi)               :: ErrStat\n")
    file.write("    CHARACTER(128)               :: ErrMsg              \n")
    file.write("    CHARACTER(128)               :: n_t_global          ! timestep number as a string\n")
    file.write("\n")
    file.write("    WRITE(n_t_global, '(I0.0)' ) NINT(avrSWAP(2)/avrSWAP(3))\n")
    file.write("    InFile = RootName(1:size_avcOUTNAME-5)//TRIM( n_t_global )//'.RO.chkp'\n")
    file.write("    OPEN(unit=Un, FILE=TRIM(InFile), STATUS='UNKNOWN', FORM='UNFORMATTED' , ACCESS='STREAM', IOSTAT=ErrStat, ACTION='READ' )\n")
    file.write("\n")
    file.write("    IF ( ErrStat /= 0 ) THEN\n")
    file.write("        ErrMsg  = 'Cannot open file "'//TRIM( InFile )//'". Another program may have locked it for writing.'\n")
    file.write("\n")
    file.write("    ELSE\n")
    for var in reg['LocalVariables']:
        if reg['LocalVariables'][var]['type'] == 'derived_type':
            for dvar in reg[reg['LocalVariables'][var]['id']]:
                file.write('        READ( Un, IOSTAT=ErrStat) LocalVar%{}%{}\n'.format(var, dvar))
        elif reg['LocalVariables'][var]['size'] > 0:
            for i in range(reg['LocalVariables'][var]['size']):
                file.write('        READ( Un, IOSTAT=ErrStat) LocalVar%{}({})\n'.format(var, i+1))
        else:
            file.write('        READ( Un, IOSTAT=ErrStat) LocalVar%{}\n'.format(var))
            if var == 'ACC_INFILE_SIZE':
                file.write('        ALLOCATE(LocalVar%ACC_INFILE(LocalVar%ACC_INFILE_SIZE))\n')
    for var in reg['ObjectInstances']:
        file.write('        READ( Un, IOSTAT=ErrStat) objInst%{}\n'.format(var))
    file.write('        Close ( Un )\n')
    file.write('    ENDIF\n')
    file.write('    ! Read Parameter files\n')
    file.write('    CALL ReadControlParameterFileSub(CntrPar, LocalVar%ACC_INFILE, LocalVar%ACC_INFILE_SIZE, ErrVar)\n')
    file.write('    IF (CntrPar%WE_Mode > 0) THEN\n')
    file.write('        CALL READCpFile(CntrPar, PerfData, ErrVar)\n')
    file.write('    ENDIF\n')
    file.write('END SUBROUTINE ReadRestartFile\n')
    file.write('\n \n')
    file.write('SUBROUTINE Debug(LocalVar, CntrPar, DebugVar, avrSWAP, RootName, size_avcOUTNAME)\n')
    file.write('! Debug routine, defines what gets printed to DEBUG.dbg if LoggingLevel = 1\n')
    file.write('\n')
    file.write('    TYPE(ControlParameters), INTENT(IN) :: CntrPar\n')
    file.write('    TYPE(LocalVariables), INTENT(IN) :: LocalVar\n')
    file.write('    TYPE(DebugVariables), INTENT(IN) :: DebugVar\n')
    file.write('\n')
    file.write('    INTEGER(IntKi), INTENT(IN)      :: size_avcOUTNAME\n')
    file.write('    INTEGER(IntKi)                  :: I , nDebugOuts, nLocalVars   ! Generic index.\n')
    file.write('    CHARACTER(1), PARAMETER         :: Tab = CHAR(9)                ! The tab character.\n')
    file.write('    CHARACTER(29), PARAMETER        :: FmtDat = "(F20.5,TR5,99(ES20.5E2,TR5:))"   ! The format of the debugging data\n')
    file.write('    INTEGER(IntKi), PARAMETER       :: UnDb = 85                    ! I/O unit for the debugging information\n')
    file.write('    INTEGER(IntKi), PARAMETER       :: UnDb2 = 86                   ! I/O unit for the debugging information, avrSWAP\n')
    file.write('    INTEGER(IntKi), PARAMETER       :: UnDb3 = 87                   ! I/O unit for the debugging information, avrSWAP\n')
    file.write('    REAL(ReKi), INTENT(INOUT)       :: avrSWAP(*)                   ! The swap array, used to pass data to, and receive data from, the DLL controller.\n')
    file.write('    CHARACTER(size_avcOUTNAME-1), INTENT(IN) :: RootName            ! a Fortran version of the input C string (not considered an array here)    [subtract 1 for the C null-character]\n')
    file.write('    CHARACTER(200)                  :: Version                      ! git version of ROSCO\n')
    file.write('    CHARACTER(15), ALLOCATABLE      :: DebugOutStrings(:), DebugOutUnits(:)\n')
    file.write('    REAL(DbKi), ALLOCATABLE         :: DebugOutData(:)\n \n')
    file.write('    CHARACTER(15), ALLOCATABLE      :: LocalVarOutStrings(:)\n')
    file.write('    REAL(DbKi), ALLOCATABLE         :: LocalVarOutData(:)\n \n')
    file.write('    nDebugOuts = {}\n'.format(len(reg['DebugVariables'].keys())))
    file.write('    Allocate(DebugOutData(nDebugOuts))\n')
    file.write('    Allocate(DebugOutStrings(nDebugOuts))\n')
    file.write('    Allocate(DebugOutUnits(nDebugOuts))\n')
    dbg_strings = []
    dbg_units   = []
    for dbg_idx, dbgvar in enumerate(reg['DebugVariables']):
        dbg_strings.append(dbgvar)
        desc = reg['DebugVariables'][dbgvar]['description']
        dbg_units.append(desc[desc.find('['):desc.find(']')+1])
        file.write('    DebugOutData({}) = DebugVar%{}\n'.format(dbg_idx+1,dbgvar))
    file.write('    DebugOutStrings = [CHARACTER(15) :: ')
    counter = 0
    for string in dbg_strings:
        counter += 1
        if counter == len(dbg_strings):
            file.write(" '{}'".format(string))
        else:
            file.write(" '{}',".format(string))
        if (counter % 5 == 0):
            file.write(' & \n                                     ')
    file.write(']\n')
    file.write('    DebugOutUnits = [CHARACTER(15) :: ')
    counter = 0
    for unit in dbg_units:
        counter += 1
        if counter == len(dbg_units):
            file.write(" '{}'".format(unit))
        else:
            file.write(" '{}',".format(unit))
        if (counter % 5 == 0):
            file.write(' & \n                                     ')
    file.write(']\n')
    lv_strings = []
    for lv_idx, localvar in enumerate(reg['LocalVariables']):
        if reg['LocalVariables'][localvar]['type'] in ['integer', 'real']:
            lv_strings.append(localvar)
    file.write('    nLocalVars = {}\n'.format(len(lv_strings)))
    file.write('    Allocate(LocalVarOutData(nLocalVars))\n')
    file.write('    Allocate(LocalVarOutStrings(nLocalVars))\n')
    for lv_idx, localvar in enumerate(reg['LocalVariables']):
        if reg['LocalVariables'][localvar]['type'] in ['integer', 'real']:
            if reg['LocalVariables'][localvar]['size'] > 0:
                file.write('    LocalVarOutData({}) = LocalVar%{}(1)\n'.format(lv_idx+1, localvar))
            else:
                file.write('    LocalVarOutData({}) = LocalVar%{}\n'.format(lv_idx+1, localvar))
    file.write('    LocalVarOutStrings = [CHARACTER(15) :: ')
    counter = 0
    for string in lv_strings:
        counter += 1
        if counter == len(lv_strings):
            file.write(" '{}'".format(string))
        else:
            file.write(" '{}',".format(string))
        if (counter % 5 == 0):
            file.write(' & \n                                     ')
    file.write(']\n')
    
    file.write("    ! Initialize debug file\n")
    file.write("    IF ((LocalVar%iStatus == 0) .OR. (LocalVar%iStatus == -9))  THEN ! .TRUE. if we're on the first call to the DLL\n")
    file.write("    ! If we're debugging, open the debug file and write the header:\n")
    file.write("    ! Note that the headers will be Truncated to 10 characters!!\n")
    file.write("        IF (CntrPar%LoggingLevel > 0) THEN\n")
    file.write("            OPEN(unit=UnDb, FILE=RootName(1: size_avcOUTNAME-5)//'RO.dbg')\n")
    file.write("            WRITE(UnDb, *)  'Generated on '//CurDate()//' at '//CurTime()//' using ROSCO-'//TRIM(rosco_version)\n")
    file.write("            WRITE(UnDb, '(99(a20,TR5:))') 'Time',   DebugOutStrings\n")
    file.write("            WRITE(UnDb, '(99(a20,TR5:))') '(sec)',  DebugOutUnits\n")
    file.write("        END IF\n")
    file.write("\n")
    file.write("        IF (CntrPar%LoggingLevel > 1) THEN\n")
    file.write("            OPEN(unit=UnDb2, FILE=RootName(1: size_avcOUTNAME-5)//'RO.dbg2')\n")
    file.write("            WRITE(UnDb2, *)  'Generated on '//CurDate()//' at '//CurTime()//' using ROSCO-'//TRIM(rosco_version)\n")
    file.write("            WRITE(UnDb2, '(99(a20,TR5:))') 'Time',   LocalVarOutStrings\n")
    file.write("            WRITE(UnDb2, '(99(a20,TR5:))')\n")
    file.write("        END IF\n")
    file.write("\n")
    file.write("        IF (CntrPar%LoggingLevel > 2) THEN\n")
    file.write("            OPEN(unit=UnDb3, FILE=RootName(1: size_avcOUTNAME-5)//'RO.dbg3')\n")
    file.write("            WRITE(UnDb3,'(/////)')\n")
    file.write("            WRITE(UnDb3,'"+'(A,85("'+"'//Tab//'"+'AvrSWAP("'+',I2,")"'+"))')  'LocalVar%Time ', (i,i=1, 85)\n")
    file.write("            WRITE(UnDb3,'"+'(A,85("'+"'//Tab//'"+'(-)"'+"))')  '(s)'"+'\n')
    file.write("        END IF\n")
    file.write("    ELSE\n")
    file.write("        ! Print simulation status, every 10 seconds\n")
    file.write("        IF (MODULO(LocalVar%Time, 10.0_DbKi) == 0) THEN\n")
    file.write("            WRITE(*, 100) LocalVar%GenSpeedF*RPS2RPM, LocalVar%BlPitch(1)*R2D, avrSWAP(15)/1000.0, LocalVar%WE_Vw\n")
    file.write("            100 FORMAT('Generator speed: ', f6.1, ' RPM, Pitch angle: ', f5.1, ' deg, Power: ', f7.1, ' kW, Est. wind Speed: ', f5.1, ' m/s')\n")
    file.write("        END IF\n")
    file.write("\n")
    file.write("        ! Write debug files\n")
    file.write("        IF(CntrPar%LoggingLevel > 0) THEN\n")
    file.write("            WRITE (UnDb, FmtDat)  LocalVar%Time, DebugOutData\n")
    file.write("        END IF\n")
    file.write("\n")
    file.write("        IF(CntrPar%LoggingLevel > 1) THEN\n")
    file.write("            WRITE (UnDb2, FmtDat)  LocalVar%Time, LocalVarOutData\n")
    file.write("        END IF\n")
    file.write("\n")
    file.write("        IF(CntrPar%LoggingLevel > 2) THEN\n")
    file.write("            WRITE (UnDb3, FmtDat)    LocalVar%Time, avrSWAP(1: 85)\n")
    file.write("        END IF\n")
    file.write("    END IF\n")
    file.write("\n")
    file.write("END SUBROUTINE Debug\n")
    file.write("\n")
    file.write("END MODULE ROSCO_IO")
    file.close()

def check_size(main_attribute, sub_attribute):
    if main_attribute[sub_attribute]['type'] == 'derived_type':
        atstr = sub_attribute
    else:
        size = int(main_attribute[sub_attribute]['size'])
        if size == 0:
            atstr = sub_attribute
        else:
            atstr = sub_attribute + '({})'.format(size)
    return atstr

def read_type(param):
    if param['type'] == 'integer':
        f90type = 'INTEGER(IntKi)'
        if param['allocatable']:
            f90type += ', DIMENSION(:), ALLOCATABLE'
    elif param['type'] == 'real':
        f90type = 'REAL(DbKi)'
        if param['allocatable']:
            if param['dimension']:
                f90type += ', DIMENSION{}, ALLOCATABLE'.format(param['dimension'])
            else:
                f90type += ', DIMENSION(:), ALLOCATABLE'
        elif param['dimension']:
            f90type += ', DIMENSION{}'.format(param['dimension'])
    elif param['type'] == 'character':
        f90type = 'CHARACTER'
        if param['length']:
            f90type += '({})'.format(param['length'])
        if param['allocatable']:
            if param['dimension']:
                f90type += ', DIMENSION{}, ALLOCATABLE'.format(param['dimension'])
            else:
                f90type = 'CHARACTER(:), ALLOCATABLE'
    elif param['type'] == 'logical':
        f90type = 'LOGICAL'
    elif param['type'] == 'c_integer':
        f90type = 'INTEGER(C_INT)'
    elif param['type'] == 'c_pointer':
        f90type = 'TYPE(C_PTR)'
    elif param['type'] == 'c_intptr_t':
        f90type = 'INTEGER(C_INTPTR_T)'
    elif param['type'] == 'c_funptr':
        f90type = 'TYPE(C_FUNPTR)'
    elif param['type'] == 'derived_type':
        f90type = 'TYPE({})'.format(param['id'])
    else:
        raise AttributeError('{} does not have a recognizable type'.format(param['type']))


    return f90type

if __name__ == '__main__':
    fname = os.path.join(os.path.dirname(os.path.abspath(__file__)),'rosco_types.yaml')
    generate(fname)

