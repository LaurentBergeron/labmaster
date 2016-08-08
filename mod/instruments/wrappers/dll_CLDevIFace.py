"""
Python wrapper for CLDevIFace.dll
Required to use Bristol 621 Wavelength Meter drivers.
Wrapper base taken from Charlie CHen <cchen@zygo.com>.
"""
__author__ =  "Adam DeAbreu <adeabreu@sfu.ca>, Charlie CHen <cchen@zygo.com>"
__version__ = "1.1"

from ctypes import *
import os

## Load CLDevIFace.dll
dll = CDLL("mod/instruments/extern/CLDevIFace.dll")



class BristolWaveLengthMeterWrapperException(Exception):
    """
    class BristolWaveLengthMeterWrapperException
    @Purpose:
        raise specialized exception for wavelength meter
    @Inputs:
        expr = expression where excpetion occurs
        msg = exception message
    """
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg
    
    def __str__(self):
        return "ERROR: BristolWaveLengthMeterWrapperException; expression = %s; %s\n" % \
                (repr(self.expr), self.msg)

c_int_p = POINTER(c_int)
c_int8_p = POINTER(c_int8)
c_ubyte_p = POINTER(c_ubyte)
c_float_p = POINTER(c_float)
c_double_p = POINTER(c_double)
c_void_p_p = POINTER(c_void_p)
c_short_p = POINTER(c_short)


def CLOpenUSBSerialDevice(ComNumber):
    """
    @Purpose:
        Open the device using a USB Serial Port Interface
    @Inputs:
        ComNumber: the windows COM port number where the USB driver is installed
    @Outputs:
        A valid CLDevice handle number, or -1 on failure. This device handle will
        be used with all commands to identify the port.
    """
    funct = dll.CLOpenUSBSerialDevice
    funct.restype = c_int
    funct.argtypes = [c_int]

    if not isinstance(ComNumber, c_int):
        ComNumber = c_int(ComNumber)
    
    retval = funct(ComNumber)
    if retval == -1:
        raise BristolWaveLengthMeterWrapperException('CLOpenUSBSerialDevice(%s)' % ComNumber,
                'ERROR: CLOpenUSBSerialDevice(%s) failed with status -1' % ComNumber)
    return retval

def CLCloseDevice(DeviceHandle):
    """
    Purpose:
        Close connection to the device
    Inputs:
        Device Handle of device to close
    Outputs:
        0 if successful
    """
    funct = dll.CLCloseDevice
    funct.restype = c_int
    funct.argtype = [c_int]

    if not isinstance(DeviceHandle, c_int):
        DeviceHandle = c_int(DeviceHandle)

    retval = funct(DeviceHandle)

    if retval != 0:
        raise BristolWaveLengthMeterWrapperException('CLCloseDevice(%s)' % (DeviceHandle),
                "ERROR: CLCloseDevice(%s) failed." % (DeviceHandle))
    return retval


def CLSetMeasHBCallback(DeviceHandle, ProcessMeasHBData):
    """
    THIS FUNCTION IS NOT IMPLEMENTED, YET.
    @Purpose:
        Set a user defined callback function to receive measurement information from
        the instrument when it is available
    @Inputs:
        DeviceHandle: a valid CLDevice handle.
        ProcessMeasHBData: user supplied callback funciton.
    """
    funct = dll.CLSetMeasHBCallback
    funct.restype = c_int
    pass
    # TO BE IMPLEMENTED.
    
def CLGetMeasurementData(DeviceHandle, data):
    """
    THIS FUNCTION IS NOT IMPLEMENTED, YET.
    @Purpose:
        Set a user defined callback function to receive measurement information
        from the instrument when it is available.
    @Inputs:
        DeviceHandle: a valid CLDevice handle.
        Data: pointer to locaiton to write data of type tsMeasurementDataType.
    """
    funct = dll.CLGetMeasurementData
    funct.restype = c_int
    pass
    # TO BE INPLEMENTED.
    
def CLSetLambdaUnits(DeviceHandle, LambdaUnits):
    """
    @Purpose:
        Set the units returned from the CLGetLambdaReading.
    @Inputs:
        DeviceHandle: a valid CLDevice handle.
        LambdaUnits: 'nm' = nanometers
                     'GHz' = gigahertz
                     '1/cm' = inverse centimeters
    """
    funct = dll.CLSetLambdaUnits
    funct.restype = c_int
    funct.argtypes = [c_int, c_uint]
    
    if not isinstance(DeviceHandle, c_int):
        DeviceHandle = c_int(DeviceHandle)
    
    if LambdaUnits == 'nm':
        retval = funct(DeviceHandle, c_uint(0))
    elif LambdaUnits == 'GHz':
        retval = funct(DeviceHandle, c_uint(1))
    elif LambdaUnits == '1/cm':
        retval = funct(DeviceHandle, c_uint(2))
    else:
        raise BristolWaveLengthMeterWrapperException('LambdaUnits = %s' % LambdaUnits,
                "ERROR: LambdaUnits must be either 'nm', 'GHz', or '1/cm', and case matters!")
    
    if retval != 0:
        raise BristolWaveLengthMeterWrapperException('CLSetLambdaUnits(%s, %s)' % (DeviceHandle, LambdaUnits),
                "ERROR: CLSetLambdaUnits(%s, %s) failed." % (DeviceHandle, LambdaUnits))
                
def CLSetPowerUnits(DeviceHandle, PowerUnits):
    """
    @Purpose:
        Set the units returned from the CLGetPowerReading.
    @Inputs:
        DeviceHandle: a valid CLDevice handle.
        PowerUnits: 'mw' = miliwatts
                    'dB' = decibels
    """
    funct = dll.CLSetPowerUnits
    funct.restype = c_int
    funct.argtypes = [c_int, c_uint]
    
    if not isinstance(DeviceHandle, c_int):
        DeviceHandle = c_int(DeviceHandle)

    if PowerUnits == 'mw':
        retval = funct(DeviceHandle, c_uint(0))
    elif PowerUnits == 'dB':
        retval = funct(DeviceHandle, c_uint(1))
    else:
        raise BristolWaveLengthMeterWrapperException('PowerUnits = %s' % PowerUnits,
            "ERROR: PowerUnits must be either 'mw' or 'dB', and case matters!")
    
    if retval != 0:
        raise BristolWaveLengthMeterWrapperException('CLSetPowerUnits(%s, %s)' % (DeviceHandle, PowerUnits),
                "ERROR: CLSetPowerUnits(%s, %s) failed." % (DeviceHandle, PowerUnits))

def CLGetLambdaReading(DeviceHandle):
    """
    @Purpose:
        Get the current wavelength reading in units set by CLSetLambdaUnits.
    @Inputs:
        DeviceHandle: a valid CLDevice handle.
    @Outputs:
        64 bit floating point wavelength reading in units set by CLSetLambdaUnits.
    """
    funct = dll.CLGetLambdaReading
    funct.restype = c_double
    funct.argtypes = [c_int]
    
    if not isinstance(DeviceHandle, c_int):
        DeviceHandle = c_int(DeviceHandle)

    return funct(DeviceHandle)
    
def CLGetPowerReading(DeviceHandle):
    """
    @Purpose:
        Get the current power reading in units set by CLSetPowerUnits.
    @Inputs:
        DeviceHandle: a valid CLDevice handle.
    @Outputs:
        32 bit floating point value of the power in units set by CLSetPowerUnits.
    """
    funct = dll.CLGetPowerReading
    funct.restype = c_float
    funct.argtypes = [c_int]
    
    if not isinstance(DeviceHandle, c_int):
        DeviceHandle = c_int(DeviceHandle)

    return funct(DeviceHandle)
    
def CLSetMedium(DeviceHandle, medium):
    """
    @Purpose:
        Use to set the current medium for the CLGetLambdaReading function.
    @Inputs:
        DeviceHandle: a valid CLDevice handle.
        medium: 'vacuum' or 'air'
    """
    funct = dll.CLSetMedium
    funct.restype = c_int
    funct.argtypes = [c_int, c_uint]

    if not isinstance(DeviceHandle, c_int):
        DeviceHandle = c_int(DeviceHandle)
    
    if medium == 'vacuum':
        retval = funct(DeviceHandle, c_uint(0))
    elif medium == 'air':
        retval = funct(DeviceHandle, c_uint(1))
    else:
        raise BristolWaveLengthMeterWrapperException('medium = %s' % medium,
            "ERROR: medium must be either 'vacuum' or 'air', and case matters!")
    
    if retval != 0:
        raise BristolWaveLengthMeterWrapperException('CLSetMedium(%s, %s)' % (DeviceHandle, medium),
                "ERROR: CLSetMedium(%s, %s) failed." % (DeviceHandle, medium))
