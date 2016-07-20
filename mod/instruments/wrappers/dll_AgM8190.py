"""
Python wrapper for AgM8190.dll.
To call a function from AgM8190.dll, import dll_AgM8190.py and use the same function name, but without "AgM8190_" prefix.
To use an attribute from AgM8190.h, import dll_AgM8190.py and use the same attribute name, but without "AGM8190_" prefix.
"""
__author__ =  "Laurent Bergeron <laurent.bergeron4@gmail.com>"
 
# Base modules
from ctypes import *
import CppHeaderParser
import inspect
import os 

# Homemade modules
from visa_types import *


dll = WinDLL("mod/instruments/extern/AgM8190")
header = CppHeaderParser.CppHeader("mod/instruments/extern/AgM8190.h")
        
def clean_args(argtype, *args):  
    l = list(*args)
    parent = inspect.stack()[1][3]
    if hasattr(argtype, "__len__"):
        args_size = len(argtype)
    else: # for some reason when there is only one argtype, it has no __len__ attribute.
        args_size = 1

    if not (args_size == len(l)):
        raise IndexError, "Wrong number of arguments ("+parent+" takes "+str(args_size)+" arguments, not "+str(len(l))+")."
    
    # for i, input in enumerate(l):
        # if not isinstance(input, argtype)

    return tuple(l)

ARRAY = POINTER

### ----------------------------------- Control words ---------------------------------- ###

control = { 
            "CommandFlag" :         0x80000000,
            "EndMarkerSequence" :   0x40000000,
            "EndMarkerScenario" :   0x20000000,
            "InitMarkerSequence" :  0x10000000,
            "MarkerEnable" :        0x01000000,
            "SequAdvModeAuto" :     0x00100000,
            "SequAdvModeCond" :     0x00200000,
            "SequAdvModeReap" :     0x00300000,
            "SequAdvModeSing" :     0x00400000,
            "SegmAdvModeAuto" :     0x00010000,
            "SegmAdvModeCond" :     0x00020000,
            "SegmAdvModeReap" :     0x00030000,
            "SegmAdvModeSing" :     0x00040000,
            "ScaleInit" :           0x00008000,
            "ScaleInc" :            0x00004000,
            "FreqInit" :            0x00002000,
            "FreqInc" :             0x00001000,
            "SegEndOffWholeSegment":0xffffffff,
          }
            
            
            

### ------------------------------------- #DEFINES ------------------------------------- ###
        
for define in (header.defines):
    if define[0]=="_":
        pass
    else:
        define = define.split("/*")[0] # Remove comments from header file
        define = " ".join(define.split())
        define = define.replace(" + ", "+")
        define = define.replace(" ", "=")
        if define[:8]=="AGM8190_":
            define = define[8:]
        exec define

        
### ------------------------------------ PROTOTYPES ------------------------------------ ###


def AbortGeneration(*args):
    """
	If the function generator is in the Output Generation State, this function moves the function generator to the Configuration State. If the function generator is already in the Configuration State, the function does nothing and returns Success. Function AgM8190_ActionSequenceAppend Defines the next step of an action sequence.
    """
    args = clean_args(dll.AgM8190_AbortGeneration.argtype, args)
    return dll.AgM8190_AbortGeneration(*args)
dll.AgM8190_AbortGeneration.restype = ViStatus
dll.AgM8190_AbortGeneration.argtype = (
                                       ViSession # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                       )

def ActionSequenceAppend(*args):
    """
	Defines the next step of an action sequence.
    """
    args = clean_args(dll.AgM8190_ActionSequenceAppend.argtype, args)
    return dll.AgM8190_ActionSequenceAppend(*args)
dll.AgM8190_ActionSequenceAppend.restype = ViStatus
dll.AgM8190_ActionSequenceAppend.argtype = (
                                            ViSession, # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                            ViConstString, # Channel: The physical or virtual repeated capability identifier. Pass VI_NULL if the operation does not apply to a repeated capability. You can also pass VI_NULL if the device only has a single channel.For valid values, see the Channel repeated capability. 
                                            ViInt32, # SequenceID: The action sequence ID.
                                            ViInt32, # Action: The action identifier.
                                            ViReal64, # Value1: The first value for the selected action.
                                            ViReal64 # Value2: The second value for the selected action.
                                            )

def ActionSequenceCreate(*args):
    """
	Creates a new empty action sequence and returns a sequence ID.
    """
    args = clean_args(dll.AgM8190_ActionSequenceCreate.argtype, args)
    return dll.AgM8190_ActionSequenceCreate(*args)
dll.AgM8190_ActionSequenceCreate.restype = ViStatus
dll.AgM8190_ActionSequenceCreate.argtype = (
                                            ViSession, # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                            ViConstString, # Channel: The physical or virtual repeated capability identifier. Pass VI_NULL if the operation does not apply to a repeated capability. You can also pass VI_NULL if the device only has a single channel.For valid values, see the Channel repeated capability. 
                                            POINTER(ViInt32) # Val: Sequence ID.
                                            )

def ActionSequenceDelete(*args):
    """
	Deletes an action sequence.
    """
    args = clean_args(dll.AgM8190_ActionSequenceDelete.argtype, args)
    return dll.AgM8190_ActionSequenceDelete(*args)
dll.AgM8190_ActionSequenceDelete.restype = ViStatus
dll.AgM8190_ActionSequenceDelete.argtype = (
                                            ViSession, # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                            ViConstString, # Channel: The physical or virtual repeated capability identifier. Pass VI_NULL if the operation does not apply to a repeated capability. You can also pass VI_NULL if the device only has a single channel.For valid values, see the Channel repeated capability. 
                                            ViInt32 # Val: The sequence ID of the sequence to be deleted.
                                            )

def ActionSequenceDeleteAll(*args):
    """
	Deletes the complete action table.
    """
    args = clean_args(dll.AgM8190_ActionSequenceDeleteAll.argtype, args)
    return dll.AgM8190_ActionSequenceDeleteAll(*args)
dll.AgM8190_ActionSequenceDeleteAll.restype = ViStatus
dll.AgM8190_ActionSequenceDeleteAll.argtype = (
                                               ViSession, # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                               ViConstString # Channel: The physical or virtual repeated capability identifier. Pass VI_NULL if the operation does not apply to a repeated capability. You can also pass VI_NULL if the device only has a single channel.For valid values, see the Channel repeated capability. 
                                               )

def AmplitudeTableGetData(*args):
    args = clean_args(dll.AgM8190_AmplitudeTableGetData.argtype, args)
    """
	Reads amplitude table entries starting at the index specified.
    """
    return dll.AgM8190_AmplitudeTableGetData(*args)
dll.AgM8190_AmplitudeTableGetData.restype = ViStatus
dll.AgM8190_AmplitudeTableGetData.argtype = (
                                             ViSession, # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                             ViConstString, # Channel: The physical or virtual repeated capability identifier. Pass VI_NULL if the operation does not apply to a repeated capability. You can also pass VI_NULL if the device only has a single channel.For valid values, see the Channel repeated capability. 
                                             ViInt32, # TableIndex: An index in the amplitude table.
                                             ViInt32, # Length: The number of entries to be read.
                                             ViInt32, # DataBufferSize: Number of elements in Data.
                                             ARRAY(ViReal64), # Data: The amplitude table data that is returned.
                                             POINTER(ViInt32) # DataActualSize: Actual number of elements in Data.
                                             )

def AmplitudeTableReset(*args):
    """
	Resets all amplitude table entries to default values.
    """
    args = clean_args(dll.AgM8190_AmplitudeTableReset.argtype, args)
    return dll.AgM8190_AmplitudeTableReset(*args)
dll.AgM8190_AmplitudeTableReset.restype = ViStatus
dll.AgM8190_AmplitudeTableReset.argtype = (
                                           ViSession, # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                           ViConstString # Channel: The physical or virtual repeated capability identifier. Pass VI_NULL if the operation does not apply to a repeated capability. You can also pass VI_NULL if the device only has a single channel.For valid values, see the Channel repeated capability. 
                                           )

def AmplitudeTableSetData(*args):
    """ 
	Writes one or multiple amplitude table entries starting at the index specified by the TableIndex parameter.args = clean_args(dll.AgM8190_AmplitudeTableSetData.argtype, args)
    """
    return dll.AgM8190_AmplitudeTableSetData(*args)
dll.AgM8190_AmplitudeTableSetData.restype = ViStatus
dll.AgM8190_AmplitudeTableSetData.argtype = (
                                             ViSession, # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                             ViConstString, # Channel: The physical or virtual repeated capability identifier. Pass VI_NULL if the operation does not apply to a repeated capability. You can also pass VI_NULL if the device only has a single channel.For valid values, see the Channel repeated capability. 
                                             ViInt32, # TableIndex: An index in the Amplitude table. 
                                             ViInt32, # DataBufferSize: Number of elements in Data.
                                             ARRAY(ViReal64) # Data: The amplitude data. Valid range: [0.0, 1.0].
                                             )

def ArbitraryClearMemory(*args):
    """
	Removes all previously created arbitrary waveforms and sequences from the function generator's memory and invalidates all waveform and sequence handles.
    """
    args = clean_args(dll.AgM8190_ArbitraryClearMemory.argtype, args)
    return dll.AgM8190_ArbitraryClearMemory(*args)
dll.AgM8190_ArbitraryClearMemory.restype = ViStatus
dll.AgM8190_ArbitraryClearMemory.argtype = (
                                            ViSession # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                            )

def ArbitraryConfigureAC(*args):
    """
	Configures the attributes of the arbitrary waveform the function generator produces for the AC output path.
    """
    args = clean_args(dll.AgM8190_ArbitraryConfigureAC.argtype, args)
    return dll.AgM8190_ArbitraryConfigureAC(*args)
dll.AgM8190_ArbitraryConfigureAC.restype = ViStatus
dll.AgM8190_ArbitraryConfigureAC.argtype = (
                                            ViSession, # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                            ViConstString, # Channel: The physical or virtual repeated capability identifier. Pass VI_NULL if the operation does not apply to a repeated capability. You can also pass VI_NULL if the device only has a single channel.For valid values, see the Channel repeated capability. 
                                            ViReal64, # Amplitude: The amplitude of the arbitrary waveform the function generator produces in the AC output path. The units are volts.
                                            ViInt32 # Format: Specifies the format mode in AC output path.
                                            )

def ArbitraryConfigureDAC(*args):
    """
	Configures the attributes of the arbitrary waveform the function generator produces for the DAC output path.
    """
    args = clean_args(dll.AgM8190_ArbitraryConfigureDAC.argtype, args)
    return dll.AgM8190_ArbitraryConfigureDAC(*args)
dll.AgM8190_ArbitraryConfigureDAC.restype = ViStatus
dll.AgM8190_ArbitraryConfigureDAC.argtype = (
                                             ViSession, # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                             ViConstString, # Channel: The physical or virtual repeated capability identifier. Pass VI_NULL if the operation does not apply to a repeated capability. You can also pass VI_NULL if the device only has a single channel.For valid values, see the Channel repeated capability. 
                                             ViReal64, # Amplitude: The amplitude of the arbitrary waveform the function generator produces in the DAC output path. The units are volts.
                                             ViInt32, # Format: Specifies the format mode in DAC output path.
                                             ViReal64 # Offset: The offset of the arbitrary waveform the function generator produces in the DAC output path. The units are volts.
                                             )

def ArbitraryConfigureDC(*args):
    """
	Configures the attributes of the arbitrary waveform the function generator produces for the DC output path.
    """
    args = clean_args(dll.AgM8190_ArbitraryConfigureDC.argtype, args)
    return dll.AgM8190_ArbitraryConfigureDC(*args)
dll.AgM8190_ArbitraryConfigureDC.restype = ViStatus
dll.AgM8190_ArbitraryConfigureDC.argtype = (
                                            ViSession, # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                            ViConstString, # Channel: The physical or virtual repeated capability identifier. Pass VI_NULL if the operation does not apply to a repeated capability. You can also pass VI_NULL if the device only has a single channel.For valid values, see the Channel repeated capability. 
                                            ViReal64, # Amplitude: The amplitude of the arbitrary waveform the function generator produces in the DC output path. The units are volts. 
                                            ViInt32, # Format: Specifies the format mode in DC output path.
                                            ViReal64 # Offset: The offset of the arbitrary waveform the function generator produces in the DC output path. The units are volts.
                                            )

def ChannelAbortGeneration(*args):
    """
	If the function generator is in the Output Generation State, this function moves the function generator to the Configuration State. If the function generator is already in the Configuration State, the function does nothing and returns Success.
    """
    args = clean_args(dll.AgM8190_ChannelAbortGeneration.argtype, args)
    return dll.AgM8190_ChannelAbortGeneration(*args)
dll.AgM8190_ChannelAbortGeneration.restype = ViStatus
dll.AgM8190_ChannelAbortGeneration.argtype = (
                                              ViSession, # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                              ViConstString # Channel: The physical or virtual repeated capability identifier. Pass VI_NULL if the operation does not apply to a repeated capability. You can also pass VI_NULL if the device only has a single channel.For valid values, see the Channel repeated capability. 
                                              )

def ChannelInitiateGeneration(*args):
    """
	If the function generator is in the Configuration State, this function moves the function generator to the Output Generation State. If the function generator is already in the Output Generation State, this function does nothing and returns Success.
    """
    args = clean_args(dll.AgM8190_ChannelInitiateGeneration.argtype, args)
    return dll.AgM8190_ChannelInitiateGeneration(*args)
dll.AgM8190_ChannelInitiateGeneration.restype = ViStatus
dll.AgM8190_ChannelInitiateGeneration.argtype = (
                                                 ViSession, # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                                 ViConstString # Channel: The physical or virtual repeated capability identifier. Pass VI_NULL if the operation does not apply to a repeated capability. You can also pass VI_NULL if the device only has a single channel.For valid values, see the Channel repeated capability. 
                                                 )

def ClearArbMemory(*args):
    """
	Removes all previously created arbitrary waveforms and sequences from the function generator's memory and invalidates all waveform and sequence handles.
    """
    args = clean_args(dll.AgM8190_ClearArbMemory.argtype, args)
    return dll.AgM8190_ClearArbMemory(*args)
dll.AgM8190_ClearArbMemory.restype = ViStatus
dll.AgM8190_ClearArbMemory.argtype = (
                                      ViSession # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                      )

def ClearArbSequence(*args):
    """
	Removes a previously created arbitrary sequence from the function generator's memory and invalidates the sequence's handle.
    """
    args = clean_args(dll.AgM8190_ClearArbSequence.argtype, args)
    return dll.AgM8190_ClearArbSequence(*args)
dll.AgM8190_ClearArbSequence.restype = ViStatus
dll.AgM8190_ClearArbSequence.argtype = (
                                        ViSession, # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                        ViInt32 # Handle: Specifies the handle that identifies the arbitrary sequence to clear.
                                        )

def ClearArbWaveform(*args):
    """
	Removes a previously created arbitrary waveform from the function generator's memory and invalidates the waveform's handle.
    """
    args = clean_args(dll.AgM8190_ClearArbWaveform.argtype, args)
    return dll.AgM8190_ClearArbWaveform(*args)
dll.AgM8190_ClearArbWaveform.restype = ViStatus
dll.AgM8190_ClearArbWaveform.argtype = (
                                        ViSession, # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                        ViInt32 # Handle: Specifies the handle that identifies the arbitrary waveform to clear.
                                        )

def ClearError(*args):
    """
	This function clears the error code and error description for the current execution thread and for the IVI session. If the user specifies a valid IVI session for the Vi parameter, this function clears the error information for the session. If the user passes VI_NULL for the Vi parameter, this function clears the error information for the current execution thread. If the Vi parameter is an invalid session, the function does nothing and returns an error.
    """
    args = clean_args(dll.AgM8190_ClearError.argtype, args)
    return dll.AgM8190_ClearError(*args)
dll.AgM8190_ClearError.restype = ViStatus
dll.AgM8190_ClearError.argtype = (
                                  ViSession # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                  )

def ClearInterchangeWarnings(*args):
    """
	Not Supported - Clears the list of interchangeability warnings that the IVI specific driver maintains.
    """
    args = clean_args(dll.AgM8190_ClearInterchangeWarnings.argtype, args)
    return dll.AgM8190_ClearInterchangeWarnings(*args)
dll.AgM8190_ClearInterchangeWarnings.restype = ViStatus
dll.AgM8190_ClearInterchangeWarnings.argtype = (
                                                ViSession # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                                )

def close(*args):
    """
	Closes the I/O session to the instrument. Driver methods and properties that access the instrument are not accessible after Close is called.
    """
    args = clean_args(dll.AgM8190_close.argtype, args)
    return dll.AgM8190_close(*args)
dll.AgM8190_close.restype = ViStatus
dll.AgM8190_close.argtype = (
                             ViSession # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                             )

def ConfigureArbSequence(*args):
    """
	Configures the attributes of the function generator that affect arbitrary sequence generation.
    """
    args = clean_args(dll.AgM8190_ConfigureArbSequence.argtype, args)
    return dll.AgM8190_ConfigureArbSequence(*args)
dll.AgM8190_ConfigureArbSequence.restype = ViStatus
dll.AgM8190_ConfigureArbSequence.argtype = (
                                            ViSession, # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                            ViConstString, # ChannelName: The ChannelName parameter may be a string defined by the driver or supplied as a virtual name in the configuration store. For single output instruments, the driver may define the empty string as valid ChannelName.For valid values, see the Channel repeated capability. 
                                            ViInt32, # Handle: Specifies the handle that identifies the arbitrary sequence to produce. This value sets the Arbitrary Sequence Handle property.
                                            ViReal64, # Gain: Specifies the arbitrary waveform gain. This value sets the Arbitrary Gain property.
                                            ViReal64 # Offset: Specifies the arbitrary waveform offset. This value sets the Arbitrary Offset property.
                                            )

def ConfigureArbWaveform(*args):
    """
	Configures the attributes of the function generator that affect arbitrary waveform generation.
    """
    args = clean_args(dll.AgM8190_ConfigureArbWaveform.argtype, args)
    return dll.AgM8190_ConfigureArbWaveform(*args)
dll.AgM8190_ConfigureArbWaveform.restype = ViStatus
dll.AgM8190_ConfigureArbWaveform.argtype = (
                                            ViSession, # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                            ViConstString, # ChannelName: The ChannelName parameter may be a string defined by the driver or supplied as a virtual name in the configuration store. For single output instruments, the driver may define the empty string as valid ChannelName.For valid values, see the Channel repeated capability. 
                                            ViInt32, # Handle: Specifies the handle that identifies the arbitrary waveform to produce. This value sets the Arbitrary Waveform Handle attribute.
                                            ViReal64, # Gain: Specifies the arbitrary waveform gain. This value sets the Arbitrary Gain attribute.
                                            ViReal64 # Offset: Specifies the arbitrary waveform offset. This value sets the Arbitrary Offset attribute.
                                            )

def ConfigureInternalTriggerRate(*args):
    """
	Configures the function generator's internal trigger rate.
    """
    args = clean_args(dll.AgM8190_ConfigureInternalTriggerRate.argtype, args)
    return dll.AgM8190_ConfigureInternalTriggerRate(*args)
dll.AgM8190_ConfigureInternalTriggerRate.restype = ViStatus
dll.AgM8190_ConfigureInternalTriggerRate.argtype = (
                                                    ViSession, # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                                    ViReal64 # Rate: Specifies the rate at which the function generator's internal trigger source produces triggers. The driver uses this value to set the Internal Trigger Rate attribute. See the attribute description for more details
                                                    )

def ConfigureOutputEnabled(*args):
    """
	Configures whether the signal the function generator produces appears at a channel's output connector.
    """
    args = clean_args(dll.AgM8190_ConfigureOutputEnabled.argtype, args)
    return dll.AgM8190_ConfigureOutputEnabled(*args)
dll.AgM8190_ConfigureOutputEnabled.restype = ViStatus
dll.AgM8190_ConfigureOutputEnabled.argtype = (
                                              ViSession, # Vi: The ViSession handle that you obtain from the IviFgen_init or IviFgen_InitWithOptions function. The handle identifies a particular instrument session
                                              ViConstString, # ChannelName: The name of the channel to enable or disable.For valid values, see the Channel repeated capability.  
                                              ViBoolean # Enabled: Specifies whether the signal the function generator produces appears at the channel's output connector. The driver uses this value to set the Output Enabled Attribute. See the attribute description for more details
                                              )

def ConfigureOutputMode(*args):
    """
	Configures the output mode of the function generator. The output mode determines how the function generator produces waveforms.
    """
    args = clean_args(dll.AgM8190_ConfigureOutputMode.argtype, args)
    return dll.AgM8190_ConfigureOutputMode(*args)
dll.AgM8190_ConfigureOutputMode.restype = ViStatus
dll.AgM8190_ConfigureOutputMode.argtype = (
                                           ViSession,  
                                           ViInt32
                                           )

def ConfigureRefClockSource(*args):
    """
	Sets the source of the function generator's reference clock. The function generator uses the reference clock to derive frequencies and sample rates when generating output.
    """
    args = clean_args(dll.AgM8190_ConfigureRefClockSource.argtype, args)
    return dll.AgM8190_ConfigureRefClockSource(*args)
dll.AgM8190_ConfigureRefClockSource.restype = ViStatus
dll.AgM8190_ConfigureRefClockSource.argtype = (
                                               ViSession,
                                               ViInt32
                                               )

def ConfigureSampleRate(*args):
    """
	Configures the function generator's sample rate.
	"""
    args = clean_args(dll.AgM8190_ConfigureSampleRate.argtype, args)
    return dll.AgM8190_ConfigureSampleRate(*args)
dll.AgM8190_ConfigureSampleRate.restype = ViStatus
dll.AgM8190_ConfigureSampleRate.argtype = (
                                           ViSession,
                                           ViReal64
                                           )

def ConfigureTriggerSource(*args):
    """
	Configures the function generator's trigger source attribute.
	"""
    args = clean_args(dll.AgM8190_ConfigureTriggerSource.argtype, args)
    return dll.AgM8190_ConfigureTriggerSource(*args)
dll.AgM8190_ConfigureTriggerSource.restype = ViStatus
dll.AgM8190_ConfigureTriggerSource.argtype = (
                                              ViSession,
                                              ViConstString,
                                              ViInt32
                                              )

def CreateArbSequence(*args):
    """
	Creates an arbitrary waveform sequence from an array of waveform handles and a corresponding array of loop counts, and returns a handle that identifies the sequence. The handle is used by the Configure, and Clear methods.
	"""
    args = clean_args(dll.AgM8190_CreateArbSequence.argtype, args)
    return dll.AgM8190_CreateArbSequence(*args)
dll.AgM8190_CreateArbSequence.restype = ViStatus
dll.AgM8190_CreateArbSequence.argtype = (
                                         ViSession,
                                         ViInt32,
                                         ARRAY(ViInt32),
                                         ARRAY(ViInt32),
                                         POINTER(ViInt32)
                                         )

def CreateArbWaveform(*args):
    """
	Creates an arbitrary waveform and returns a handle to it. The handle is used by the Configure, Clear, and ArbitrarySequence.Create methods.
	"""
    args = clean_args(dll.AgM8190_CreateArbWaveform.argtype, args)
    return dll.AgM8190_CreateArbWaveform(*args)
dll.AgM8190_CreateArbWaveform.restype = ViStatus
dll.AgM8190_CreateArbWaveform.argtype = (
                                         ViSession,
                                         ViInt32,
                                         ARRAY(ViReal64),
                                         POINTER(ViInt32)
                                         )

def CreateChannelIQWaveformWithInit(*args):
    """
	Defines the size of a waveform memory segment and initializes all sample values in the segment.
	"""
    args = clean_args(dll.AgM8190_CreateChannelIQWaveformWithInit.argtype, args)
    return dll.AgM8190_CreateChannelIQWaveformWithInit(*args)
dll.AgM8190_CreateChannelIQWaveformWithInit.restype = ViStatus
dll.AgM8190_CreateChannelIQWaveformWithInit.argtype = (
                                                       ViSession,
                                                       ViConstString,
                                                       ViInt32,
                                                       ViInt16,
                                                       ViInt16,
                                                       POINTER(ViInt32)
                                                       )

def DigitalUpConversionGetCarrierFrequency(*args):
    """
	Returns the carrier frequency used for interpolated modes.
	"""
    args = clean_args(dll.AgM8190_DigitalUpConversionGetCarrierFrequency.argtype, args)
    return dll.AgM8190_DigitalUpConversionGetCarrierFrequency(*args)
dll.AgM8190_DigitalUpConversionGetCarrierFrequency.restype = ViStatus
dll.AgM8190_DigitalUpConversionGetCarrierFrequency.argtype = (
                                                              ViSession,
                                                              ViConstString,
                                                              POINTER(ViReal64),
                                                              POINTER(ViReal64)
                                                              )

def DigitalUpConversionGetCarrierFrequencyMax(*args):
    """
	Returns the maximum value of the carrier frequency used for interpolated modes.
	"""
    args = clean_args(dll.AgM8190_DigitalUpConversionGetCarrierFrequencyMax.argtype, args)
    return dll.AgM8190_DigitalUpConversionGetCarrierFrequencyMax(*args)
dll.AgM8190_DigitalUpConversionGetCarrierFrequencyMax.restype = ViStatus
dll.AgM8190_DigitalUpConversionGetCarrierFrequencyMax.argtype = (
                                                                 ViSession,
                                                                 ViConstString,
                                                                 POINTER(ViReal64),
                                                                 POINTER(ViReal64)
                                                                 )

def DigitalUpConversionGetCarrierFrequencyMin(*args):
    """
	Returns the minimum value of the carrier frequency used for interpolated modes.
	"""
    args = clean_args(dll.AgM8190_DigitalUpConversionGetCarrierFrequencyMin.argtype, args)
    return dll.AgM8190_DigitalUpConversionGetCarrierFrequencyMin(*args)
dll.AgM8190_DigitalUpConversionGetCarrierFrequencyMin.restype = ViStatus
dll.AgM8190_DigitalUpConversionGetCarrierFrequencyMin.argtype = (
                                                                 ViSession,
                                                                 ViConstString,
                                                                 POINTER(ViReal64),
                                                                 POINTER(ViReal64)
                                                                 )

def DigitalUpConversionSetCarrierFrequency(*args):
    """
	Sets the carrier frequency used for interpolated modes.
	"""
    args = clean_args(dll.AgM8190_DigitalUpConversionSetCarrierFrequency.argtype, args)
    return dll.AgM8190_DigitalUpConversionSetCarrierFrequency(*args)
dll.AgM8190_DigitalUpConversionSetCarrierFrequency.restype = ViStatus
dll.AgM8190_DigitalUpConversionSetCarrierFrequency.argtype = (
                                                              ViSession,
                                                              ViConstString,
                                                              ViReal64,
                                                              ViReal64
                                                              )

def Disable(*args):
    """
	Quickly places the instrument in a state where it has no, or minimal, effect on the external system to which it is connected. This state is not necessarily a known state.
	"""
    args = clean_args(dll.AgM8190_Disable.argtype, args)
    return dll.AgM8190_Disable(*args)
dll.AgM8190_Disable.restype = ViStatus
dll.AgM8190_Disable.argtype = (
                               ViSession
                               )

def error_message(*args):
    """
	Translates the error return value from an IVI driver function to a user-readable string. The user should pass a buffer with at least 256 bytes for the ErrorMessage parameter.
	"""
    args = clean_args(dll.AgM8190_error_message.argtype, args)
    return dll.AgM8190_error_message(*args)
dll.AgM8190_error_message.restype = ViStatus
dll.AgM8190_error_message.argtype = (
                                     ViSession,
                                     ViStatus,
                                     ARRAY(ViChar)
                                     )

def error_query(*args):
    """
	Queries the instrument and returns instrument specific error information. This function can be used when QueryInstrumentStatus is True to retrieve error details when the driver detects an instrument error.
	"""
    args = clean_args(dll.AgM8190_error_query.argtype, args)
    return dll.AgM8190_error_query(*args)
dll.AgM8190_error_query.restype = ViStatus
dll.AgM8190_error_query.argtype = (
                                   ViSession,
                                   POINTER(ViInt32),
                                   ARRAY(ViChar)
                                   )

def FrequencyTableGetData(*args):
    """
	Reads frequency table entries starting at the index specified.
	"""
    args = clean_args(dll.AgM8190_FrequencyTableGetData.argtype, args)
    return dll.AgM8190_FrequencyTableGetData(*args)
dll.AgM8190_FrequencyTableGetData.restype = ViStatus
dll.AgM8190_FrequencyTableGetData.argtype = (
                                             ViSession,
                                             ViConstString,
                                             ViReal64,
                                             ViInt32,
                                             ViInt32,
                                             ARRAY(ViReal64),
                                             POINTER(ViInt32)
                                             )

def FrequencyTableReset(*args):
    """
	Resets all frequency table entries to default values.
	"""
    args = clean_args(dll.AgM8190_FrequencyTableReset.argtype, args)
    return dll.AgM8190_FrequencyTableReset(*args)
dll.AgM8190_FrequencyTableReset.restype = ViStatus
dll.AgM8190_FrequencyTableReset.argtype = (
                                           ViSession,
                                           ViConstString
                                           )

def FrequencyTableSetData(*args):
    """
	Writes one or multiple frequency table entries starting at the index specified by the TableIndex parameter.
	"""
    args = clean_args(dll.AgM8190_FrequencyTableSetData.argtype, args)
    return dll.AgM8190_FrequencyTableSetData(*args)
dll.AgM8190_FrequencyTableSetData.restype = ViStatus
dll.AgM8190_FrequencyTableSetData.argtype = (
                                             ViSession,
                                             ViConstString,
                                             ViReal64,
                                             ViInt32,
                                             ARRAY(ViReal64)
                                             )

def GetAttributeViBoolean(*args):
    """
	This routine is used to access low-level settings of the instrument. See the attributeID parameter for a link to all attributes of the instrument.
	"""
    args = clean_args(dll.AgM8190_GetAttributeViBoolean.argtype, args)
    return dll.AgM8190_GetAttributeViBoolean(*args)
dll.AgM8190_GetAttributeViBoolean.restype = ViStatus
dll.AgM8190_GetAttributeViBoolean.argtype = (
                                             ViSession,
                                             ViConstString,
                                             ViAttr,
                                             POINTER(ViBoolean)
                                             )

def GetAttributeViInt32(*args):
    """
	This routine is used to access low-level settings of the instrument. See the attributeID parameter for a link to all attributes of the instrument.
	"""
    args = clean_args(dll.AgM8190_GetAttributeViInt32.argtype, args)
    return dll.AgM8190_GetAttributeViInt32(*args)
dll.AgM8190_GetAttributeViInt32.restype = ViStatus
dll.AgM8190_GetAttributeViInt32.argtype = (
                                           ViSession,
                                           ViConstString,
                                           ViAttr,
                                           POINTER(ViInt32)
                                           )

def GetAttributeViInt64(*args):
    """
	This routine is used to access low-level settings of the instrument. See the attributeID parameter for a link to all attributes of the instrument.
	"""
    args = clean_args(dll.AgM8190_GetAttributeViInt64.argtype, args)
    return dll.AgM8190_GetAttributeViInt64(*args)
dll.AgM8190_GetAttributeViInt64.restype = ViStatus
dll.AgM8190_GetAttributeViInt64.argtype = (
                                           ViSession,
                                           ViConstString,
                                           ViInt32,
                                           POINTER(ViInt64)
                                           )

def GetAttributeViReal64(*args):
    """
	This routine is used to access low-level settings of the instrument. See the attributeID parameter for a link to all attributes of the instrument.
	"""
    args = clean_args(dll.AgM8190_GetAttributeViReal64.argtype, args)
    return dll.AgM8190_GetAttributeViReal64(*args)
dll.AgM8190_GetAttributeViReal64.restype = ViStatus
dll.AgM8190_GetAttributeViReal64.argtype = (
                                            ViSession,
                                            ViConstString,
                                            ViAttr,
                                            POINTER(ViReal64)
                                            )

def GetAttributeViSession(*args):
    """
	This routine is used to access low-level settings of the instrument. See the attributeID parameter for a link to all attributes of the instrument.
	"""
    args = clean_args(dll.AgM8190_GetAttributeViSession.argtype, args)
    return dll.AgM8190_GetAttributeViSession(*args)
dll.AgM8190_GetAttributeViSession.restype = ViStatus
dll.AgM8190_GetAttributeViSession.argtype = (
                                             ViSession,
                                             ViConstString,
                                             ViAttr,
                                             POINTER(ViSession)
                                             )

def GetAttributeViString(*args):
    """
	This routine is used to access low-level settings of the instrument. See the attributeID parameter for a link to all attributes of the instrument.
	"""
    args = clean_args(dll.AgM8190_GetAttributeViString.argtype, args)
    return dll.AgM8190_GetAttributeViString(*args)
dll.AgM8190_GetAttributeViString.restype = ViStatus
dll.AgM8190_GetAttributeViString.argtype = (
                                            ViSession,  
                                            ViConstString, # RepCapIndentifier: If the attribute applies to a repeated capability, the user passes a physical or virtual repeated capability identifier. Otherwise, the user passes VI_NULL or an empty string. For attributes requiring nested repeated capabilities, enter the names separated by a colon as in: "Window1:Trace2".
                                            ViAttr, # AttributeID: The ID of the attribute. The valid values for this parameter can be found in the driver header file.
                                            ViInt32, # AttributeValueBufferSize: The number of bytes in the ViChar array that the user specifies for the AttributeValue parameter.
                                            ARRAY(ViChar) # AttributeValue: The buffer in which the function returns the current value of the attribute. Can be VI_NULL if AttributeValueBufferSize is 0.
                                            )

def GetChannelName(*args):
    """
	This function returns the physical name defined by the specific driver for the output channel that corresponds to the 1-based index that the user specifies. If the value that the user passes for the ChannelIndex parameter is less than one or greater than the value of the Channel Count, the function returns an empty string in the ChannelName parameter and returns an error.
	"""
    args = clean_args(dll.AgM8190_GetChannelName.argtype, args)
    return dll.AgM8190_GetChannelName(*args)
dll.AgM8190_GetChannelName.restype = ViStatus
dll.AgM8190_GetChannelName.argtype = (
                                      ViSession,
                                      ViInt32,
                                      ViInt32,
                                      ARRAY(ViChar)
                                      )

def GetError(*args):
    """
	This function retrieves and then clears the IVI error information for the session or the current execution thread. If the user specifies a valid IVI session for the Vi parameter, Get Error retrieves and then clears the error information for the session. If the user passes VI_NULL for the Vi parameter, Get Error retrieves and then clears the error information for the current execution thread. If the Vi parameter is an invalid session, the function does nothing and returns an error. Normally, the error information describes the first error that occurred since the user last called the Get Error or Clear Error function.
	"""
    args = clean_args(dll.AgM8190_GetError.argtype, args)
    return dll.AgM8190_GetError(*args)
dll.AgM8190_GetError.restype = ViStatus
dll.AgM8190_GetError.argtype = (
                                ViSession,  
                                POINTER(ViStatus), # ErrorCode: Returns the error code. Zero indicates that no error occurred. A positive value indicates a warning. A negative value indicates an error. The user can pass VI_NULL if the user does not want to retrieve this value.
                                ViInt32, # ErrorDescriptionBufferSize: The number of bytes in the ViChar array that the user specifies for the ErrorDescription parameter.
                                ARRAY(ViChar) # ErrorDescription: Buffer into which the function copies the full formatted error string. The string describes the error code and any extra information regarding the error or warning condition. The buffer shall contain at least as many bytes as the user specifies in the ErrorDescriptionBufferSize parameter. The user can pass VI_NULL if the ErrorDescriptionBufferSize parameter is zero.
                                )

def GetNextCoercionRecord(*args):
    """
	Not Supported - Returns the oldest record from the coercion record list. Records are only added to the list if RecordCoercions is True.
	"""
    args = clean_args(dll.AgM8190_GetNextCoercionRecord.argtype, args)
    return dll.AgM8190_GetNextCoercionRecord(*args)
dll.AgM8190_GetNextCoercionRecord.restype = ViStatus
dll.AgM8190_GetNextCoercionRecord.argtype = (
                                             ViSession,
                                             ViInt32,
                                             ARRAY(ViChar)
                                             )

def GetNextInterchangeWarning(*args):
    """
	Not Supported - Returns the oldest warning from the interchange warning list. Records are only added to the list if InterchangeCheck is True.
	"""
    args = clean_args(dll.AgM8190_GetNextInterchangeWarning.argtype, args)
    return dll.AgM8190_GetNextInterchangeWarning(*args)
dll.AgM8190_GetNextInterchangeWarning.restype = ViStatus
dll.AgM8190_GetNextInterchangeWarning.argtype = (
                                                 ViSession,
                                                 ViInt32,
                                                 ARRAY(ViChar)
                                                 )

def GetReferenceClockSourceSupported(*args):
    """
	Read Only - This property is used to query, if a reference clock source is available on the current hardware revision.
	"""
    args = clean_args(dll.AgM8190_GetReferenceClockSourceSupported.argtype, args)
    return dll.AgM8190_GetReferenceClockSourceSupported(*args)
dll.AgM8190_GetReferenceClockSourceSupported.restype = ViStatus
dll.AgM8190_GetReferenceClockSourceSupported.argtype = (
                                                        ViSession,
                                                        ViInt32,
                                                        POINTER(ViBoolean)
                                                        )

def GetStatusAmplitudeClipped(*args):
    """
	Read Only - This property reads the amplitude clipped status per channel. "True" means that the amplitude for the selected channel has been clipped to the highest possible DAC value.
	"""
    args = clean_args(dll.AgM8190_GetStatusAmplitudeClipped.argtype, args)
    return dll.AgM8190_GetStatusAmplitudeClipped(*args)
dll.AgM8190_GetStatusAmplitudeClipped.restype = ViStatus
dll.AgM8190_GetStatusAmplitudeClipped.argtype = (
                                                 ViSession,
                                                 ViConstString,
                                                 POINTER(ViBoolean)
                                                 )

def ImportIQToFile(*args):
    """
	This method is intended to be used by the Soft Front Panel only.
	"""
    args = clean_args(dll.AgM8190_ImportIQToFile.argtype, args)
    return dll.AgM8190_ImportIQToFile(*args)
dll.AgM8190_ImportIQToFile.restype = ViStatus
dll.AgM8190_ImportIQToFile.argtype = (
                                      ViSession,
                                      ViConstString,
                                      ViInt32,
                                      ViBoolean
                                      )

def init(*args):
    """
	Opens the I/O session to the instrument. Driver methods and properties that access the instrument are only accessible after Initialize is called. Initialize optionally performs a Reset and queries the instrument to validate the instrument model.
	"""
    args = clean_args(dll.AgM8190_init.argtype, args)
    return dll.AgM8190_init(*args)
dll.AgM8190_init.restype = ViStatus
dll.AgM8190_init.argtype = (
                            ViRsrc,
                            ViBoolean,
                            ViBoolean,
                            POINTER(ViSession)
                            )

def InitiateGeneration(*args):
    """
	If the function generator is in the Configuration State, this function moves the function generator to the Output Generation State. If the function generator is already in the Output Generation State, this function does nothing and returns Success.
	"""
    args = clean_args(dll.AgM8190_InitiateGeneration.argtype, args)
    return dll.AgM8190_InitiateGeneration(*args)
dll.AgM8190_InitiateGeneration.restype = ViStatus
dll.AgM8190_InitiateGeneration.argtype = (
                                          ViSession
                                          )

def InitWithOptions(*args):
    """
	Opens the I/O session to the instrument. Driver methods and properties that access the instrument are only accessible after Initialize is called. Initialize optionally performs a Reset and queries the instrument to validate the instrument model.
	"""
    args = clean_args(dll.AgM8190_InitWithOptions.argtype, args)
    return dll.AgM8190_InitWithOptions(*args)
dll.AgM8190_InitWithOptions.restype = ViStatus
dll.AgM8190_InitWithOptions.argtype = (
                                       ViRsrc, # ResourceName: An IVI logical name or an instrument specific string that identifies the address of the instrument, such as a VISA resource descriptor string.
                                       ViBoolean, # IdQuery: Specifies whether to verify the ID of the instrument.
                                       ViBoolean, # Reset: Specifies whether to reset the instrument.
                                       ViConstString, # OptionsString: The user can use the OptionsString parameter to specify the initial values of certain IVI inherent attributes for the session. The format of an assignment in the OptionsString parameter is "Name=Value", where Name is one of: RangeCheck, QuerytInstrStatus, Cache, Simulate, RecordCoercions, InterchangeCheck,or DriverSetup. Value is either true or false except for DriverSetup. If the Options String parameter contains an assignment for the Driver Setup attribute, the Initialize function assumes that everything following "DriverSetup=" is part of the assignment.
                                       POINTER(ViSession) # Vi: Unique identifier for an IVI session
                                       )

def InvalidateAllAttributes(*args):
    """
	Not Supported - Invalidates all of the driver's cached values.
	"""
    args = clean_args(dll.AgM8190_InvalidateAllAttributes.argtype, args)
    return dll.AgM8190_InvalidateAllAttributes(*args)
dll.AgM8190_InvalidateAllAttributes.restype = ViStatus
dll.AgM8190_InvalidateAllAttributes.argtype = (
                                               ViSession
                                               )

def LockSession(*args):
    """
	Obtains a multithread lock on the driver after waiting until all other execution threads have released their locks on the instrument session.
	"""
    args = clean_args(dll.AgM8190_LockSession.argtype, args)
    return dll.AgM8190_LockSession(*args)
dll.AgM8190_LockSession.restype = ViStatus
dll.AgM8190_LockSession.argtype = (
                                   ViSession,
                                   POINTER(ViBoolean)
                                   )

def MarkerConfigure(*args):
    """
	Configures the marker amplitude and offset for the specified marker type (Sample/Sync) on the selected channel.
	"""
    args = clean_args(dll.AgM8190_MarkerConfigure.argtype, args)
    return dll.AgM8190_MarkerConfigure(*args)
dll.AgM8190_MarkerConfigure.restype = ViStatus
dll.AgM8190_MarkerConfigure.argtype = (
                                       ViSession,
                                       ViConstString,
                                       ViInt32,
                                       ViReal64,
                                       ViReal64
                                       )

def MemoryCopy(*args):
    """
	Copies an existing file to a new file or an existing directory to a new directory.
	"""
    args = clean_args(dll.AgM8190_MemoryCopy.argtype, args)
    return dll.AgM8190_MemoryCopy(*args)
dll.AgM8190_MemoryCopy.restype = ViStatus
dll.AgM8190_MemoryCopy.argtype = (
                                  ViSession,
                                  ViInt32,
                                  ViConstString,
                                  ViInt32,
                                  ViConstString
                                  )

def MemoryCreateFolder(*args):
    """
	Creates a new directory.
	"""
    args = clean_args(dll.AgM8190_MemoryCreateFolder.argtype, args)
    return dll.AgM8190_MemoryCreateFolder(*args)
dll.AgM8190_MemoryCreateFolder.restype = ViStatus
dll.AgM8190_MemoryCreateFolder.argtype = (
                                          ViSession,
                                          ViConstString
                                          )

def MemoryDelete(*args):
    """
	Removes a file from the specified directory.
	"""
    args = clean_args(dll.AgM8190_MemoryDelete.argtype, args)
    return dll.AgM8190_MemoryDelete(*args)
dll.AgM8190_MemoryDelete.restype = ViStatus
dll.AgM8190_MemoryDelete.argtype = (
                                    ViSession,
                                    ViConstString,
                                    ViConstString
                                    )

def MemoryDeleteFolder(*args):
    """
	Removes a directory. All files and directories under the specified directory are also removed.
	"""
    args = clean_args(dll.AgM8190_MemoryDeleteFolder.argtype, args)
    return dll.AgM8190_MemoryDeleteFolder(*args)
dll.AgM8190_MemoryDeleteFolder.restype = ViStatus
dll.AgM8190_MemoryDeleteFolder.argtype = (
                                          ViSession,
                                          ViConstString
                                          )

def MemoryLoadData(*args):
    """
	Loads data from the specified file.
	"""
    args = clean_args(dll.AgM8190_MemoryLoadData.argtype, args)
    return dll.AgM8190_MemoryLoadData(*args)
dll.AgM8190_MemoryLoadData.restype = ViStatus
dll.AgM8190_MemoryLoadData.argtype = (
                                      ViSession,
                                      ViConstString,
                                      ViInt32,
                                      ARRAY(ViChar),
                                      POINTER(ViInt32)
                                      )

def MemoryMove(*args):
    """
	Moves an existing file to a new file or an existing directory to a new directory.
	"""
    args = clean_args(dll.AgM8190_MemoryMove.argtype, args)
    return dll.AgM8190_MemoryMove(*args)
dll.AgM8190_MemoryMove.restype = ViStatus
dll.AgM8190_MemoryMove.argtype = (
                                  ViSession,
                                  ViInt32,
                                  ViConstString,
                                  ViInt32,
                                  ViConstString
                                  )

def MemoryQueryCatalog(*args):
    """
	Queries disk usage information (drive capacity, free space available) and obtain a list of files and directories in a specified directory.
	"""
    args = clean_args(dll.AgM8190_MemoryQueryCatalog.argtype, args)
    return dll.AgM8190_MemoryQueryCatalog(*args)
dll.AgM8190_MemoryQueryCatalog.restype = ViStatus
dll.AgM8190_MemoryQueryCatalog.argtype = (
                                          ViSession,
                                          POINTER(ViInt64),
                                          POINTER(ViInt64),
                                          ViInt32,
                                          ARRAY(ViChar)
                                          )

def MemoryStoreData(*args):
    """
	Stores data into the specified file.
	"""
    args = clean_args(dll.AgM8190_MemoryStoreData.argtype, args)
    return dll.AgM8190_MemoryStoreData(*args)
dll.AgM8190_MemoryStoreData.restype = ViStatus
dll.AgM8190_MemoryStoreData.argtype = (
                                       ViSession,
                                       ViConstString,
                                       ViInt32,
                                       ARRAY(ViChar)
                                       )

def OutputConfigureDelay(*args):
    """
	Configures the delay and different offset attributes.
	"""
    args = clean_args(dll.AgM8190_OutputConfigureDelay.argtype, args)
    return dll.AgM8190_OutputConfigureDelay(*args)
dll.AgM8190_OutputConfigureDelay.restype = ViStatus
dll.AgM8190_OutputConfigureDelay.argtype = (
                                            ViSession,
                                            ViConstString,
                                            ViReal64,
                                            ViReal64,
                                            ViReal64
                                            )

def QueryArbSeqCapabilities(*args):
    """
	Returns the attributes of the function generator that are related to creating arbitrary sequences. These attributes are the maximum number of sequences, minimum sequence length, maximum sequence length, and maximum loop count.
	"""
    args = clean_args(dll.AgM8190_QueryArbSeqCapabilities.argtype, args)
    return dll.AgM8190_QueryArbSeqCapabilities(*args)
dll.AgM8190_QueryArbSeqCapabilities.restype = ViStatus
dll.AgM8190_QueryArbSeqCapabilities.argtype = (
                                               ViSession,
                                               POINTER(ViInt32),
                                               POINTER(ViInt32),
                                               POINTER(ViInt32),
                                               POINTER(ViInt32)
                                               )

def QueryArbWfmCapabilities(*args):
    """
	Returns the attributes of the function generator that are related to creating arbitrary waveforms. These attributes are the maximum number of waveforms, waveform quantum, minimum waveform size, and maximum waveform size.
	"""
    args = clean_args(dll.AgM8190_QueryArbWfmCapabilities.argtype, args)
    return dll.AgM8190_QueryArbWfmCapabilities(*args)
dll.AgM8190_QueryArbWfmCapabilities.restype = ViStatus
dll.AgM8190_QueryArbWfmCapabilities.argtype = (
                                               ViSession,
                                               POINTER(ViInt32),
                                               POINTER(ViInt32),
                                               POINTER(ViInt32),
                                               POINTER(ViInt32)
                                               )

def reset(*args):
    """
	Places the instrument in a known state and configures instrument options on which the IVI specific driver depends (for example, enabling/disabling headers). For an IEEE 488.2 instrument, Reset sends the command string *RST to the instrument.
	"""
    args = clean_args(dll.AgM8190_reset.argtype, args)
    return dll.AgM8190_reset(*args)
dll.AgM8190_reset.restype = ViStatus
dll.AgM8190_reset.argtype = (
                             ViSession
                             )

def ResetInterchangeCheck(*args):
    """
	Not Supported - Resets the interchangeability checking algorithms of the driver so that methods and properties that executed prior to calling this function have no affect on whether future calls to the driver generate interchangeability warnings.
	"""
    args = clean_args(dll.AgM8190_ResetInterchangeCheck.argtype, args)
    return dll.AgM8190_ResetInterchangeCheck(*args)
dll.AgM8190_ResetInterchangeCheck.restype = ViStatus
dll.AgM8190_ResetInterchangeCheck.argtype = (
                                             ViSession
                                             )

def ResetWithDefaults(*args):
    """
	Does the equivalent of Reset and then, (1) disables class extension capability groups, (2) sets attributes to initial values defined by class specs, and (3) configures the driver to option string settings used when Initialize was last executed.
	"""
    args = clean_args(dll.AgM8190_ResetWithDefaults.argtype, args)
    return dll.AgM8190_ResetWithDefaults(*args)
dll.AgM8190_ResetWithDefaults.restype = ViStatus
dll.AgM8190_ResetWithDefaults.argtype = (
                                         ViSession
                                         )

def revision_query(*args):
    """
	Retrieves revision information from the instrument.
	"""
    args = clean_args(dll.AgM8190_revision_query.argtype, args)
    return dll.AgM8190_revision_query(*args)
dll.AgM8190_revision_query.restype = ViStatus
dll.AgM8190_revision_query.argtype = (
                                      ViSession,
                                      ARRAY(ViChar),
                                      ARRAY(ViChar)
                                      )

def SampleClockConfigure(*args):
    """
	Configures the sample clock output and source attributes.
	"""
    args = clean_args(dll.AgM8190_SampleClockConfigure.argtype, args)
    return dll.AgM8190_SampleClockConfigure(*args)
dll.AgM8190_SampleClockConfigure.restype = ViStatus
dll.AgM8190_SampleClockConfigure.argtype = (
                                            ViSession,
                                            ViConstString,
                                            ViInt32,
                                            ViInt32
                                            )

def SampleClockGetSampleClockSource(*args):
    """
	Specifies the clock used for the waveform generation. Note that when using an external sample clock, the Arbitrary Sample Rate External attribute must be set to the corresponding frequency of the external sample clock.
	"""
    args = clean_args(dll.AgM8190_SampleClockGetSampleClockSource.argtype, args)
    return dll.AgM8190_SampleClockGetSampleClockSource(*args)
dll.AgM8190_SampleClockGetSampleClockSource.restype = ViStatus
dll.AgM8190_SampleClockGetSampleClockSource.argtype = (
                                                       ViSession,
                                                       ViConstString,
                                                       POINTER(ViInt32)
                                                       )

def SampleClockSetSampleClockSource(*args):
    """
	Specifies the clock used for the waveform generation. Note that when using an external sample clock, the Arbitrary Sample Rate External attribute must be set to the corresponding frequency of the external sample clock.
	"""
    args = clean_args(dll.AgM8190_SampleClockSetSampleClockSource.argtype, args)
    return dll.AgM8190_SampleClockSetSampleClockSource(*args)
dll.AgM8190_SampleClockSetSampleClockSource.restype = ViStatus
dll.AgM8190_SampleClockSetSampleClockSource.argtype = (
                                                       ViSession,
                                                       ViConstString,
                                                       ViInt32
                                                       )

def self_test(*args):
    """
	Performs an instrument self test, waits for the instrument to complete the test, and queries the instrument for the results. If the instrument passes the test, TestResult is zero and TestMessage is 'Self test passed'.
	"""
    args = clean_args(dll.AgM8190_self_test.argtype, args)
    return dll.AgM8190_self_test(*args)
dll.AgM8190_self_test.restype = ViStatus
dll.AgM8190_self_test.argtype = (
                                 ViSession,
                                 POINTER(ViInt16),
                                 ARRAY(ViChar)
                                 )

def SendSoftwareTrigger(*args):
    """
	Sends a software trigger, which will cause the function generator to generate output.
	"""
    args = clean_args(dll.AgM8190_SendSoftwareTrigger.argtype, args)
    return dll.AgM8190_SendSoftwareTrigger(*args)
dll.AgM8190_SendSoftwareTrigger.restype = ViStatus
dll.AgM8190_SendSoftwareTrigger.argtype = (
                                           ViSession
                                           )

def SequenceClear(*args):
    """
	Allows you to delete an arbitrary sequence from the specified channel.
	"""
    args = clean_args(dll.AgM8190_SequenceClear.argtype, args)
    return dll.AgM8190_SequenceClear(*args)
dll.AgM8190_SequenceClear.restype = ViStatus
dll.AgM8190_SequenceClear.argtype = (
                                     ViSession,
                                     ViConstString,
                                     ViInt32
                                     )

def SequenceClearAll(*args):
    """
	Allows you to delete all arbitrary sequences from the specified channel.
	"""
    args = clean_args(dll.AgM8190_SequenceClearAll.argtype, args)
    return dll.AgM8190_SequenceClearAll(*args)
dll.AgM8190_SequenceClearAll.restype = ViStatus
dll.AgM8190_SequenceClearAll.argtype = (
                                        ViSession,
                                        ViConstString
                                        )

def SequenceConfigure(*args):
    """
	Configures the attributes of the function generator that affect arbitrary sequence generation.
	"""
    args = clean_args(dll.AgM8190_SequenceConfigure.argtype, args)
    return dll.AgM8190_SequenceConfigure(*args)
dll.AgM8190_SequenceConfigure.restype = ViStatus
dll.AgM8190_SequenceConfigure.argtype = (
                                         ViSession,
                                         ViConstString,
                                         ViInt32,
                                         ViReal64,
                                         ViReal64
                                         )

def SequenceCreate(*args):
    """
	Creates an arbitrary waveform sequence from an array of waveform handles and a corresponding array of loop counts, and returns a handle that identifies the sequence.
	"""
    args = clean_args(dll.AgM8190_SequenceCreate.argtype, args)
    return dll.AgM8190_SequenceCreate(*args)
dll.AgM8190_SequenceCreate.restype = ViStatus
dll.AgM8190_SequenceCreate.argtype = (
                                      ViSession,
                                      ViConstString,
                                      ViInt32,
                                      ARRAY(ViInt32),
                                      ViInt32,
                                      ARRAY(ViInt32),
                                      POINTER(ViInt32)
                                      )

def SequenceGetAdvancementMode(*args):
    """
	Specifies the advancement mode between iterations of a sequence.
	"""
    args = clean_args(dll.AgM8190_SequenceGetAdvancementMode.argtype, args)
    return dll.AgM8190_SequenceGetAdvancementMode(*args)
dll.AgM8190_SequenceGetAdvancementMode.restype = ViStatus
dll.AgM8190_SequenceGetAdvancementMode.argtype = (
                                                  ViSession,
                                                  ViConstString,
                                                  ViInt32,
                                                  POINTER(ViInt32)
                                                  )

def SequenceGetComment(*args):
    """
	Specifies the comment associated with an arbitrary sequence.
	"""
    args = clean_args(dll.AgM8190_SequenceGetComment.argtype, args)
    return dll.AgM8190_SequenceGetComment(*args)
dll.AgM8190_SequenceGetComment.restype = ViStatus
dll.AgM8190_SequenceGetComment.argtype = (
                                          ViSession,
                                          ViConstString,
                                          ViInt32,
                                          ViInt32,
                                          ARRAY(ViChar)
                                          )

def SequenceGetData(*args):
    """
	Returns the sequence data for a given sequence-id and step.
	"""
    args = clean_args(dll.AgM8190_SequenceGetData.argtype, args)
    return dll.AgM8190_SequenceGetData(*args)
dll.AgM8190_SequenceGetData.restype = ViStatus
dll.AgM8190_SequenceGetData.argtype = (
                                       ViSession,
                                       ViConstString,
                                       ViInt32,
                                       ViInt32,
                                       ViInt32,
                                       ViInt32,
                                       ARRAY(ViInt32),
                                       POINTER(ViInt32)
                                       )

def SequenceGetLoopCount(*args):
    """
	Specifies the number of iterations of a sequence. Valid range: 1 to 4294967295.
	"""
    args = clean_args(dll.AgM8190_SequenceGetLoopCount.argtype, args)
    return dll.AgM8190_SequenceGetLoopCount(*args)
dll.AgM8190_SequenceGetLoopCount.restype = ViStatus
dll.AgM8190_SequenceGetLoopCount.argtype = (
                                            ViSession,
                                            ViConstString,
                                            ViInt32,
                                            POINTER(ViInt64)
                                            )

def SequenceGetName(*args):
    """
	Specifies the name associated with an arbitrary sequence.
	"""
    args = clean_args(dll.AgM8190_SequenceGetName.argtype, args)
    return dll.AgM8190_SequenceGetName(*args)
dll.AgM8190_SequenceGetName.restype = ViStatus
dll.AgM8190_SequenceGetName.argtype = (
                                       ViSession,
                                       ViConstString,
                                       ViInt32,
                                       ViInt32,
                                       ARRAY(ViChar)
                                       )

def SequenceQueryFreeMemory(*args):
    """
	Returns the number of free sequence entries.
	"""
    args = clean_args(dll.AgM8190_SequenceQueryFreeMemory.argtype, args)
    return dll.AgM8190_SequenceQueryFreeMemory(*args)
dll.AgM8190_SequenceQueryFreeMemory.restype = ViStatus
dll.AgM8190_SequenceQueryFreeMemory.argtype = (
                                               ViSession,
                                               ViConstString,
                                               POINTER(ViInt32),
                                               POINTER(ViInt32),
                                               POINTER(ViInt32)
                                               )

def SequenceSetAdvancementMode(*args):
    """
	Specifies the advancement mode between iterations of a sequence.
	"""
    args = clean_args(dll.AgM8190_SequenceSetAdvancementMode.argtype, args)
    return dll.AgM8190_SequenceSetAdvancementMode(*args)
dll.AgM8190_SequenceSetAdvancementMode.restype = ViStatus
dll.AgM8190_SequenceSetAdvancementMode.argtype = (
                                                  ViSession,
                                                  ViConstString,
                                                  ViInt32,
                                                  ViInt32
                                                  )

def SequenceSetComment(*args):
    """
	Specifies the comment associated with an arbitrary sequence.
	"""
    args = clean_args(dll.AgM8190_SequenceSetComment.argtype, args)
    return dll.AgM8190_SequenceSetComment(*args)
dll.AgM8190_SequenceSetComment.restype = ViStatus
dll.AgM8190_SequenceSetComment.argtype = (
                                          ViSession,
                                          ViConstString,
                                          ViInt32,
                                          ViConstString
                                          )

def SequenceSetData(*args):
    """
	Allows you to write one or multiple sequence steps for the specified sequence id (handle).
	"""
    args = clean_args(dll.AgM8190_SequenceSetData.argtype, args)
    return dll.AgM8190_SequenceSetData(*args)
dll.AgM8190_SequenceSetData.restype = ViStatus
dll.AgM8190_SequenceSetData.argtype = (
                                       ViSession,
                                       ViConstString,
                                       ViInt32,
                                       ViInt32,
                                       ViInt32,
                                       ARRAY(ViInt32)
                                       )

def SequenceSetLoopCount(*args):
    """
	Specifies the number of iterations of a sequence. Valid range: 1 to 4294967295.
	"""
    args = clean_args(dll.AgM8190_SequenceSetLoopCount.argtype, args)
    return dll.AgM8190_SequenceSetLoopCount(*args)
dll.AgM8190_SequenceSetLoopCount.restype = ViStatus
dll.AgM8190_SequenceSetLoopCount.argtype = (
                                            ViSession, 
                                            ViConstString,
                                            ViInt32,
                                            ViInt64
                                            )

def SequenceSetName(*args):
    """
	Specifies the name associated with an arbitrary sequence.
	"""
    args = clean_args(dll.AgM8190_SequenceSetName.argtype, args)
    return dll.AgM8190_SequenceSetName(*args)
dll.AgM8190_SequenceSetName.restype = ViStatus
dll.AgM8190_SequenceSetName.argtype = (
                                       ViSession,
                                       ViConstString,
                                       ViInt32,
                                       ViConstString
                                       )

def SequenceTableGetData(*args):
    """
	Read Only - Reads data from the sequencer memory, if all segments are read-write. An error is returned, if at least one write-only segment in the waveform memory exists.
	"""
    args = clean_args(dll.AgM8190_SequenceTableGetData.argtype, args)
    return dll.AgM8190_SequenceTableGetData(*args)
dll.AgM8190_SequenceTableGetData.restype = ViStatus
dll.AgM8190_SequenceTableGetData.argtype = (
                                            ViSession,
                                            ViConstString,
                                            ViInt32,
                                            ViInt32,
                                            ViInt32,
                                            ARRAY(ViInt32),
                                            POINTER(ViInt32)
                                            )

def SequenceTableReset(*args):
    """
	Read Only - Reset all sequence table entries to default values.
	"""
    args = clean_args(dll.AgM8190_SequenceTableReset.argtype, args)
    return dll.AgM8190_SequenceTableReset(*args)
dll.AgM8190_SequenceTableReset.restype = ViStatus
dll.AgM8190_SequenceTableReset.argtype = (
                                          ViSession,
                                          ViConstString
                                          )

def SequenceTableSetData(*args):
    """
	Allows you to write directly to the sequencer memory.
	"""
    args = clean_args(dll.AgM8190_SequenceTableSetData.argtype, args)
    return dll.AgM8190_SequenceTableSetData(*args)
dll.AgM8190_SequenceTableSetData.restype = ViStatus
dll.AgM8190_SequenceTableSetData.argtype = (
                                            ViSession,
                                            ViConstString,
                                            ViInt32,
                                            ViInt32,
                                            ARRAY(ViInt32)
                                            )

def SetAttributeViBoolean(*args):
    """
	This routine is used to access low-level settings of the instrument. See the attributeID parameter for a link to all attributes of the instrument.
	"""
    args = clean_args(dll.AgM8190_SetAttributeViBoolean.argtype, args)
    return dll.AgM8190_SetAttributeViBoolean(*args)
dll.AgM8190_SetAttributeViBoolean.restype = ViStatus
dll.AgM8190_SetAttributeViBoolean.argtype = (
                                             ViSession,
                                             ViConstString,
                                             ViAttr,
                                             ViBoolean
                                             )

def SetAttributeViInt32(*args):
    """
	This routine is used to access low-level settings of the instrument. See the attributeID parameter for a link to all attributes of the instrument.
	"""
    args = clean_args(dll.AgM8190_SetAttributeViInt32.argtype, args)
    return dll.AgM8190_SetAttributeViInt32(*args)
dll.AgM8190_SetAttributeViInt32.restype = ViStatus
dll.AgM8190_SetAttributeViInt32.argtype = (
                                           ViSession,
                                           ViConstString,
                                           ViAttr,
                                           ViInt32
                                           )

def SetAttributeViInt64(*args):
    """
	This routine is used to access low-level settings of the instrument. See the attributeID parameter for a link to all attributes of the instrument.
	"""
    args = clean_args(dll.AgM8190_SetAttributeViInt64.argtype, args)
    return dll.AgM8190_SetAttributeViInt64(*args)
dll.AgM8190_SetAttributeViInt64.restype = ViStatus
dll.AgM8190_SetAttributeViInt64.argtype = (
                                           ViSession,
                                           ViConstString,
                                           ViInt32,
                                           ViInt64
                                           )

def SetAttributeViReal64(*args):
    """
	This routine is used to access low-level settings of the instrument. See the attributeID parameter for a link to all attributes of the instrument.
	"""
    args = clean_args(dll.AgM8190_SetAttributeViReal64.argtype, args)
    return dll.AgM8190_SetAttributeViReal64(*args)
dll.AgM8190_SetAttributeViReal64.restype = ViStatus
dll.AgM8190_SetAttributeViReal64.argtype = (
                                            ViSession,
                                            ViConstString,
                                            ViAttr,
                                            ViReal64
                                            )

def SetAttributeViSession(*args):
    """
	This routine is used to access low-level settings of the instrument. See the attributeID parameter for a link to all attributes of the instrument.
	"""
    args = clean_args(dll.AgM8190_SetAttributeViSession.argtype, args)
    return dll.AgM8190_SetAttributeViSession(*args)
dll.AgM8190_SetAttributeViSession.restype = ViStatus
dll.AgM8190_SetAttributeViSession.argtype = (
                                             ViSession,
                                             ViConstString,
                                             ViAttr,
                                             ViSession
                                             )

def SetAttributeViString(*args):
    """
	This routine is used to access low-level settings of the instrument. See the attributeID parameter for a link to all attributes of the instrument.
	"""
    args = clean_args(dll.AgM8190_SetAttributeViString.argtype, args)
    return dll.AgM8190_SetAttributeViString(*args)
dll.AgM8190_SetAttributeViString.restype = ViStatus
dll.AgM8190_SetAttributeViString.argtype = (
                                            ViSession,
                                            ViConstString,
                                            ViAttr,
                                            ViConstString
                                            )

def StatusClear(*args):
    """
	Clears all event registers and error queue. The enable registers are unaffected.
	"""
    args = clean_args(dll.AgM8190_StatusClear.argtype, args)
    return dll.AgM8190_StatusClear(*args)
dll.AgM8190_StatusClear.restype = ViStatus
dll.AgM8190_StatusClear.argtype = (
                                   ViSession
                                   )

def StatusConfigureServiceRequest(*args):
    """
	Clears all the enable registers. It then sets the appropriate transition filters and enable registers so when the specified event(s) occur(s) the instrument requests service. All other events are disabled from generating a service request.
	"""
    args = clean_args(dll.AgM8190_StatusConfigureServiceRequest.argtype, args)
    return dll.AgM8190_StatusConfigureServiceRequest(*args)
dll.AgM8190_StatusConfigureServiceRequest.restype = ViStatus
dll.AgM8190_StatusConfigureServiceRequest.argtype = (
                                                     ViSession,
                                                     ViInt32
                                                     )

def StatusGetFrequencyStable(*args):
    """
	Read Only - This property returns a boolean value for the selected channel's frequency status. If the frequency status is stable, the attribute value is true, otherwise false.
	"""
    args = clean_args(dll.AgM8190_StatusGetFrequencyStable.argtype, args)
    return dll.AgM8190_StatusGetFrequencyStable(*args)
dll.AgM8190_StatusGetFrequencyStable.restype = ViStatus
dll.AgM8190_StatusGetFrequencyStable.argtype = (
                                                ViSession,
                                                ViConstString,
                                                POINTER(ViBoolean)
                                                )

def StatusGetGenerating(*args):
    """
	Read Only - If the function generator is in the Output Generation State, the attribute value is true, otherwise false.
	"""
    args = clean_args(dll.AgM8190_StatusGetGenerating.argtype, args)
    return dll.AgM8190_StatusGetGenerating(*args)
dll.AgM8190_StatusGetGenerating.restype = ViStatus
dll.AgM8190_StatusGetGenerating.argtype = (
                                           ViSession,
                                           ViConstString,
                                           POINTER(ViBoolean)
                                           )

def StatusGetOutputVoltageOK(*args):
    """
	Read Only - This property reads the output protection state per channel. "False" means Output has switched off (to protect itself).
	"""
    args = clean_args(dll.AgM8190_StatusGetOutputVoltageOK.argtype, args)
    return dll.AgM8190_StatusGetOutputVoltageOK(*args)
dll.AgM8190_StatusGetOutputVoltageOK.restype = ViStatus
dll.AgM8190_StatusGetOutputVoltageOK.argtype = (
                                                ViSession,
                                                ViConstString,
                                                POINTER(ViBoolean)
                                                )

def StatusGetRegister(*args):
    """
	Instrument status registers.
	"""
    args = clean_args(dll.AgM8190_StatusGetRegister.argtype, args)
    return dll.AgM8190_StatusGetRegister(*args)
dll.AgM8190_StatusGetRegister.restype = ViStatus
dll.AgM8190_StatusGetRegister.argtype = (
                                         ViSession,
                                         ViInt32,
                                         ViInt32,
                                         POINTER(ViInt32)
                                         )

def StatusSetRegister(*args):
    """
	Instrument status registers.
	"""
    args = clean_args(dll.AgM8190_StatusSetRegister.argtype, args)
    return dll.AgM8190_StatusSetRegister(*args)
dll.AgM8190_StatusSetRegister.restype = ViStatus
dll.AgM8190_StatusSetRegister.argtype = (
                                         ViSession,
                                         ViInt32,
                                         ViInt32,
                                         ViInt32
                                         )

def SystemIoRead(*args):
    """
	This function provides direct read access to the underlying instrument I/O interface.
	"""
    args = clean_args(dll.AgM8190_SystemIoRead.argtype, args)
    return dll.AgM8190_SystemIoRead(*args)
dll.AgM8190_SystemIoRead.restype = ViStatus
dll.AgM8190_SystemIoRead.argtype = (
                                    ViSession,
                                    ViInt32,
                                    ARRAY(ViChar),
                                    POINTER(ViInt32)
                                    )

def SystemIoWrite(*args):
    """
	This function provides direct write access to the underlying instrument I/O interface.
	"""
    args = clean_args(dll.AgM8190_SystemIoWrite.argtype, args)
    return dll.AgM8190_SystemIoWrite(*args)
dll.AgM8190_SystemIoWrite.restype = ViStatus
dll.AgM8190_SystemIoWrite.argtype = (
                                     ViSession,
                                     ViConstString
                                     )

def SystemLoadConfiguration(*args):
    """
	This function configures the function generator to the state stored in current file.
	"""
    args = clean_args(dll.AgM8190_SystemLoadConfiguration.argtype, args)
    return dll.AgM8190_SystemLoadConfiguration(*args)
dll.AgM8190_SystemLoadConfiguration.restype = ViStatus
dll.AgM8190_SystemLoadConfiguration.argtype = (
                                               ViSession,
                                               ViConstString
                                               )

def SystemPowerOnSelfTest(*args):
    """
	Returns the results of the power on self-tests.
	"""
    args = clean_args(dll.AgM8190_SystemPowerOnSelfTest.argtype, args)
    return dll.AgM8190_SystemPowerOnSelfTest(*args)
dll.AgM8190_SystemPowerOnSelfTest.restype = ViStatus
dll.AgM8190_SystemPowerOnSelfTest.argtype = (
                                             ViSession,
                                             ViInt32,
                                             ARRAY(ViChar)
                                             )

def SystemStoreConfiguration(*args):
    """
	This function saves the current configuration of the function generator to the current file.
	"""
    args = clean_args(dll.AgM8190_SystemStoreConfiguration.argtype, args)
    return dll.AgM8190_SystemStoreConfiguration(*args)
dll.AgM8190_SystemStoreConfiguration.restype = ViStatus
dll.AgM8190_SystemStoreConfiguration.argtype = (
                                                ViSession,
                                                ViConstString
                                                )

def SystemWaitForOperationComplete(*args):
    """
	Does not return until previously started operations complete or more MaxTimeMilliseconds milliseconds of time have expired.
	"""
    args = clean_args(dll.AgM8190_SystemWaitForOperationComplete.argtype, args)
    return dll.AgM8190_SystemWaitForOperationComplete(*args)
dll.AgM8190_SystemWaitForOperationComplete.restype = ViStatus
dll.AgM8190_SystemWaitForOperationComplete.argtype = (
                                                      ViSession,
                                                      ViInt32
                                                      )

def TriggerConfigureEvent(*args):
    """
	Configures the event impedance, slope and threshold attributes.
	"""
    args = clean_args(dll.AgM8190_TriggerConfigureEvent.argtype, args)
    return dll.AgM8190_TriggerConfigureEvent(*args)
dll.AgM8190_TriggerConfigureEvent.restype = ViStatus
dll.AgM8190_TriggerConfigureEvent.argtype = (
                                             ViSession,
                                             ViInt32,
                                             ViInt32,
                                             ViReal64
                                             )

def TriggerConfigureMode(*args):
    """
	Configures the arming mode, the gate mode and the trigger mode for the specified channel.
	"""
    args = clean_args(dll.AgM8190_TriggerConfigureMode.argtype, args)
    return dll.AgM8190_TriggerConfigureMode(*args)
dll.AgM8190_TriggerConfigureMode.restype = ViStatus
dll.AgM8190_TriggerConfigureMode.argtype = (
                                            ViSession,
                                            ViConstString,
                                            ViInt32,
                                            ViInt32,
                                            ViInt32
                                            )

def TriggerConfigureTrigger(*args):
    """
	Configures the trigger impedance, slope and threshold attributes.
	"""
    args = clean_args(dll.AgM8190_TriggerConfigureTrigger.argtype, args)
    return dll.AgM8190_TriggerConfigureTrigger(*args)
dll.AgM8190_TriggerConfigureTrigger.restype = ViStatus
dll.AgM8190_TriggerConfigureTrigger.argtype = (
                                               ViSession,
                                               ViInt32,
                                               ViInt32,
                                               ViReal64
                                               )

def TriggerSendSoftwareEnable(*args):
    """
	This method sends the enable event to the specified channel of the function generator.
	"""
    args = clean_args(dll.AgM8190_TriggerSendSoftwareEnable.argtype, args)
    return dll.AgM8190_TriggerSendSoftwareEnable(*args)
dll.AgM8190_TriggerSendSoftwareEnable.restype = ViStatus
dll.AgM8190_TriggerSendSoftwareEnable.argtype = (
                                                 ViSession,
                                                 ViConstString
                                                 )

def TriggerSendSoftwareEvent(*args):
    """
	This method sends the advancement event to the specified channel of the function generator.
	"""
    args = clean_args(dll.AgM8190_TriggerSendSoftwareEvent.argtype, args)
    return dll.AgM8190_TriggerSendSoftwareEvent(*args)
dll.AgM8190_TriggerSendSoftwareEvent.restype = ViStatus
dll.AgM8190_TriggerSendSoftwareEvent.argtype = (
                                                ViSession,
                                                ViConstString
                                                )

def TriggerSendSoftwareTrigger(*args):
    """
	This method sends the trigger event to the specified channel of the function generator.
	"""
    args = clean_args(dll.AgM8190_TriggerSendSoftwareTrigger.argtype, args)
    return dll.AgM8190_TriggerSendSoftwareTrigger(*args)
dll.AgM8190_TriggerSendSoftwareTrigger.restype = ViStatus
dll.AgM8190_TriggerSendSoftwareTrigger.argtype = (
                                                  ViSession,
                                                  ViConstString
                                                  )

def UnlockSession(*args):
    """
	Releases a previously obtained mutlithread lock.
	"""
    args = clean_args(dll.AgM8190_UnlockSession.argtype, args)
    return dll.AgM8190_UnlockSession(*args)
dll.AgM8190_UnlockSession.restype = ViStatus
dll.AgM8190_UnlockSession.argtype = (
                                     ViSession,
                                     POINTER(ViBoolean)
                                     )

def WaveformClear(*args):
    """
	Deletes a segment from the specified channel.
	"""
    args = clean_args(dll.AgM8190_WaveformClear.argtype, args)
    return dll.AgM8190_WaveformClear(*args)
dll.AgM8190_WaveformClear.restype = ViStatus
dll.AgM8190_WaveformClear.argtype = (
                                     ViSession,
                                     ViConstString,
                                     ViInt32
                                     )

def WaveformClearAll(*args):
    """
	Delete all segments from the specified channel.
	"""
    args = clean_args(dll.AgM8190_WaveformClearAll.argtype, args)
    return dll.AgM8190_WaveformClearAll(*args)
dll.AgM8190_WaveformClearAll.restype = ViStatus
dll.AgM8190_WaveformClearAll.argtype = (
                                        ViSession,
                                        ViConstString
                                        )

def WaveformConfigure(*args):
    """
	Configures the attributes of the function generator that affect arbitrary waveform generation.
	"""
    args = clean_args(dll.AgM8190_WaveformConfigure.argtype, args)
    return dll.AgM8190_WaveformConfigure(*args)
dll.AgM8190_WaveformConfigure.restype = ViStatus
dll.AgM8190_WaveformConfigure.argtype = (
                                         ViSession,
                                         ViConstString,
                                         ViInt32,
                                         ViReal64,
                                         ViReal64
                                         )

def WaveformCreateChannelWaveform(*args):
    """
	Creates a channel-specific arbitrary waveform and returns a handle to it. The handle is used by the Configure, Clear, and ArbitrarySequence.Create methods.
	"""
    args = clean_args(dll.AgM8190_WaveformCreateChannelWaveform.argtype, args)
    return dll.AgM8190_WaveformCreateChannelWaveform(*args)
dll.AgM8190_WaveformCreateChannelWaveform.restype = ViStatus
dll.AgM8190_WaveformCreateChannelWaveform.argtype = (
                                                     ViSession,
                                                     ViConstString,
                                                     ViInt32,
                                                     ARRAY(ViReal64),
                                                     POINTER(ViInt32)
                                                     )

def WaveformCreateChannelWaveformChunkInt16(*args):
    """
	Use this method to create an arbitrary waveform by transferring the waveform data in chunks.
	"""
    args = clean_args(dll.AgM8190_WaveformCreateChannelWaveformChunkInt16.argtype, args)
    return dll.AgM8190_WaveformCreateChannelWaveformChunkInt16(*args)
dll.AgM8190_WaveformCreateChannelWaveformChunkInt16.restype = ViStatus
dll.AgM8190_WaveformCreateChannelWaveformChunkInt16.argtype = (
                                                               ViSession,
                                                               ViConstString,
                                                               ViInt32,
                                                               ViInt32,
                                                               ViInt32,
                                                               ViInt32,
                                                               ARRAY(ViInt16),
                                                               POINTER(ViInt32)
                                                               )

def WaveformCreateChannelWaveformChunkInt16WithInit(*args):
    """
	Use this method to create an arbitrary waveform by transferring the waveform data in chunks and to preinitialize the allocated memory.
	"""
    args = clean_args(dll.AgM8190_WaveformCreateChannelWaveformChunkInt16WithInit.argtype, args)
    return dll.AgM8190_WaveformCreateChannelWaveformChunkInt16WithInit(*args)
dll.AgM8190_WaveformCreateChannelWaveformChunkInt16WithInit.restype = ViStatus
dll.AgM8190_WaveformCreateChannelWaveformChunkInt16WithInit.argtype = (
                                                                       ViSession,
                                                                       ViConstString,
                                                                       ViInt32,
                                                                       ViInt32,
                                                                       ViInt32,
                                                                       ViInt32,
                                                                       ARRAY(ViInt16),
                                                                       ViInt16,
                                                                       POINTER(ViInt32)
                                                                       )

def WaveformCreateChannelWaveformInt16(*args):
    """
	Creates a channel-specific arbitrary waveform and returns a handle to it. The handle is used by the Configure, Clear, and ArbitrarySequence.Create methods.
	"""
    args = clean_args(dll.AgM8190_WaveformCreateChannelWaveformInt16.argtype, args)
    return dll.AgM8190_WaveformCreateChannelWaveformInt16(*args)
dll.AgM8190_WaveformCreateChannelWaveformInt16.restype = ViStatus
dll.AgM8190_WaveformCreateChannelWaveformInt16.argtype = (
                                                          ViSession,
                                                          ViConstString,
                                                          ViInt32,
                                                          ARRAY(ViInt16),
                                                          POINTER(ViInt32)
                                                          )

def WaveformCreateChannelWaveformInt16WriteOnly(*args):
    """
	Creates a channel-specific arbitrary waveform and returns a handle to it. The waveform is write-only and cannot be read back from memory.
	"""
    args = clean_args(dll.AgM8190_WaveformCreateChannelWaveformInt16WriteOnly.argtype, args)
    return dll.AgM8190_WaveformCreateChannelWaveformInt16WriteOnly(*args)
dll.AgM8190_WaveformCreateChannelWaveformInt16WriteOnly.restype = ViStatus
dll.AgM8190_WaveformCreateChannelWaveformInt16WriteOnly.argtype = (
                                                                   ViSession,
                                                                   ViConstString,
                                                                   ViInt32,
                                                                   ARRAY(ViInt16),
                                                                   POINTER(ViInt32)
                                                                   )

def WaveformGetComment(*args):
    """
	Specifies the comment associated with a segment.
	"""
    args = clean_args(dll.AgM8190_WaveformGetComment.argtype, args)
    return dll.AgM8190_WaveformGetComment(*args)
dll.AgM8190_WaveformGetComment.restype = ViStatus
dll.AgM8190_WaveformGetComment.argtype = (
                                          ViSession,
                                          ViConstString,
                                          ViInt32,
                                          ViInt32,
                                          ARRAY(ViChar)
                                          )

def WaveformGetName(*args):
    """
	Specifies the name associated with a segment.
	"""
    args = clean_args(dll.AgM8190_WaveformGetName.argtype, args)
    return dll.AgM8190_WaveformGetName(*args)
dll.AgM8190_WaveformGetName.restype = ViStatus
dll.AgM8190_WaveformGetName.argtype = (
                                       ViSession,
                                       ViConstString,
                                       ViInt32,
                                       ViInt32,
                                       ARRAY(ViChar)
                                       )

def WaveformImport(*args):
    """
	Imports segment data from a file. Different file formats are supported.
	"""
    args = clean_args(dll.AgM8190_WaveformImport.argtype, args)
    return dll.AgM8190_WaveformImport(*args)
dll.AgM8190_WaveformImport.restype = ViStatus
dll.AgM8190_WaveformImport.argtype = (
                                      ViSession,
                                      ViConstString,
                                      ViInt32,
                                      ViConstString,
                                      ViInt32,
                                      ViInt32
                                      )

def WaveformImportIQ(*args):
    """
	Imports segment data from a file. Different file formats are supported. An already existing segment can be filled, or a new segment can be created.
	"""
    args = clean_args(dll.AgM8190_WaveformImportIQ.argtype, args)
    return dll.AgM8190_WaveformImportIQ(*args)
dll.AgM8190_WaveformImportIQ.restype = ViStatus
dll.AgM8190_WaveformImportIQ.argtype = (
                                        ViSession,
                                        ViConstString,
                                        ViInt32,
                                        ViConstString,
                                        ViInt32,
                                        ViInt32,
                                        ViBoolean,
                                        ViInt32
                                        )

def WaveformQueryFreeMemory(*args):
    """
	Returns the amount of memory space available for waveform data.
	"""
    args = clean_args(dll.AgM8190_WaveformQueryFreeMemory.argtype, args)
    return dll.AgM8190_WaveformQueryFreeMemory(*args)
dll.AgM8190_WaveformQueryFreeMemory.restype = ViStatus
dll.AgM8190_WaveformQueryFreeMemory.argtype = (
                                               ViSession,
                                               ViConstString,
                                               POINTER(ViInt64),
                                               POINTER(ViInt64),
                                               POINTER(ViInt64)
                                               )

def WaveformSetComment(*args):
    """
	Specifies the comment associated with a segment.
	"""
    args = clean_args(dll.AgM8190_WaveformSetComment.argtype, args)
    return dll.AgM8190_WaveformSetComment(*args)
dll.AgM8190_WaveformSetComment.restype = ViStatus
dll.AgM8190_WaveformSetComment.argtype = (
                                          ViSession,
                                          ViConstString,
                                          ViInt32,
                                          ViConstString
                                          )

def WaveformSetName(*args):
    """
	Specifies the name associated with a segment.
	"""
    args = clean_args(dll.AgM8190_WaveformSetName.argtype, args)
    return dll.AgM8190_WaveformSetName(*args)
dll.AgM8190_WaveformSetName.restype = ViStatus
dll.AgM8190_WaveformSetName.argtype = (
                                       ViSession,
                                       ViConstString,
                                       ViInt32,
                                       ViConstString
                                       )

