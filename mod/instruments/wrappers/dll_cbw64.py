"""
Python wrapper for cbw64.dll
Required to use MCC USB counter CTR04 drivers.
You can find all the functions from the dll here, however the result/argument types were completed for needed functions only.
Uncompleted functions are commented. Complete them as the need for them arise.
Help file for the dll functions can be downloaded at https://www.mccdaq.com/daq-software/universal-library.aspx.
"""
__author__ =  "Laurent Bergeron <laurent.bergeron4@gmail.com>"

from ctypes import *
import os

## Load cbw64.dll
### IMPORTANT InstalCal must be run at least once for this to work.
dll = WinDLL("C://Program Files (x86)/Measurement Computing/DAQ/cbw64.dll") 

ARRAY = POINTER


def cbDIn(*args):
    """Reads a digital input port."""
    return dll.cbDIn(*args)
dll.cbDIn.restype = c_int #Error code
dll.cbDIn.argtype = (c_int, #BoardNum
                     c_int, #portType
                     POINTER(c_int) #dataValue
                     )

def cbPulseOutStart(*args):
    """
    Starts a timer to generate digital pulses at a specified frequency and duty cycle. 
    Use PulseOutStop() to stop the output. 
    Use this method with counter boards that have a timer-type counter.
    """
    return dll.cbPulseOutStart(*args)
dll.cbPulseOutStart.restype = c_int #Error code
dll.cbPulseOutStart.argtype = (c_int, #boardNum
                               c_int, #timerNum
                               POINTER(c_double), #frequency
                               POINTER(c_double), #duty cycle
                               c_uint, #pulseCount
                               POINTER(c_double), #initial delay
                               c_int, #idleState (Low = 0, High=1)
                               c_int #options (default = 0)
                               )
    
def cbCConfigScan(*args):
    """
    Configures a counter channel. 
    This function only works with counter boards that have counter scan capability.
    """
    return dll.cbCConfigScan(*args)
dll.cbCConfigScan.restype = c_int # Error code
dll.cbCConfigScan.argtype = (c_int, # BoardNum
                             c_int, # CounterNum
                             c_int, # Mode
                             c_int, # DebounceTime
                             c_int, # DebounceMode
                             c_int, # EdgeDetection
                             c_int, # TickSize
                             c_int # MappedChannel
                             )

                                     
def cbCClear(*args):
    """
    Clears a scan counter value (sets it to zero). 
    This function only works with counter boards that have counter scan capability.
    """
    return dll.cbCClear(*args)
dll.cbCClear.restype = c_int # Error code
dll.cbCClear.argtype = (c_int, # BoardNum
                        c_int # CounterNum
                        )

                                
def cbCIn32(*args):
    """Reads the current count from a counter and returns it as a 32-bit integer."""
    return dll.cbCIn32(*args)
dll.cbCIn32.restype = c_int # Error code
dll.cbCIn32.argtype = (c_int, # BoardNum
                       c_int, # CounterNum
                       POINTER(c_ulong) # Count
                       )
                               
                  
def cbGetErrMsg(*args):
    """
    Returns the error message associated with an error code. 
    Each function returns an error code. 
    An error code that is not equal to 0 indicates that an error occurred. 
    Call this function to convert the returned error code to a descriptive error message.
    """
    return dll.cbGetErrMsg(*args)
dll.cbGetErrMsg.restype = c_int
dll.cbGetErrMsg.argtype = (c_int,
                           ARRAY(c_char)
                           )

                                   
# def cbACalibrateData(*args):
    # return dll.cbACalibrateData(*args)
# dll.cbACalibrateData.restype = None
# dll.cbACalibrateData.argtype = (
                                        # )

# def cbAChanInputMode(*args):
    # return dll.cbAChanInputMode(*args)
# dll.cbAChanInputMode.restype = None
# dll.cbAChanInputMode.argtype = (
                                        # )

# def cbAConvertData(*args):
    # return dll.cbAConvertData(*args)
# dll.cbAConvertData.restype = None
# dll.cbAConvertData.argtype = (
                                      # )

# def cbAConvertPretrigData(*args):
    # return dll.cbAConvertPretrigData(*args)
# dll.cbAConvertPretrigData.restype = None
# dll.cbAConvertPretrigData.argtype = (
                                             # )

# def cbAddBoard(*args):
    # return dll.cbAddBoard(*args)
# dll.cbAddBoard.restype = None
# dll.cbAddBoard.argtype = (
                                  # )

# def cbAddExp(*args):
    # return dll.cbAddExp(*args)
# dll.cbAddExp.restype = None
# dll.cbAddExp.argtype = (
                                # )

# def cbAddMem(*args):
    # return dll.cbAddMem(*args)
# dll.cbAddMem.restype = None
# dll.cbAddMem.argtype = (
                                # )

# def cbAIGetPCMCalCoeffs(*args):
    # return dll.cbAIGetPCMCalCoeffs(*args)
# dll.cbAIGetPCMCalCoeffs.restype = None
# dll.cbAIGetPCMCalCoeffs.argtype = (
                                           # )

# def cbAIn(*args):
    # return dll.cbAIn(*args)
# dll.cbAIn.restype = None
# dll.cbAIn.argtype = (
                             # )

# def cbAIn32(*args):
    # return dll.cbAIn32(*args)
# dll.cbAIn32.restype = None
# dll.cbAIn32.argtype = (
                               # )

# def cbAInputMode(*args):
    # return dll.cbAInputMode(*args)
# dll.cbAInputMode.restype = None
# dll.cbAInputMode.argtype = (
                                    # )

# def cbAInScan(*args):
    # return dll.cbAInScan(*args)
# dll.cbAInScan.restype = None
# dll.cbAInScan.argtype = (
                                 # )

# def cbALoadQueue(*args):
    # return dll.cbALoadQueue(*args)
# dll.cbALoadQueue.restype = None
# dll.cbALoadQueue.argtype = (
                                    # )

# def cbAOut(*args):
    # return dll.cbAOut(*args)
# dll.cbAOut.restype = None
# dll.cbAOut.argtype = (
                              # )

# def cbAOutScan(*args):
    # return dll.cbAOutScan(*args)
# dll.cbAOutScan.restype = None
# dll.cbAOutScan.argtype = (
                                  # )

# def cbAPretrig(*args):
    # return dll.cbAPretrig(*args)
# dll.cbAPretrig.restype = None
# dll.cbAPretrig.argtype = (
                                  # )

# def cbATrig(*args):
    # return dll.cbATrig(*args)
# dll.cbATrig.restype = None
# dll.cbATrig.argtype = (
                               # )

# def cbC7266Config(*args):
    # return dll.cbC7266Config(*args)
# dll.cbC7266Config.restype = None
# dll.cbC7266Config.argtype = (
                                     # )

# def cbC8254Config(*args):
    # return dll.cbC8254Config(*args)
# dll.cbC8254Config.restype = None
# dll.cbC8254Config.argtype = (
                                     # )

# def cbC8536Config(*args):
    # return dll.cbC8536Config(*args)
# dll.cbC8536Config.restype = None
# dll.cbC8536Config.argtype = (
                                     # )

# def cbC8536Init(*args):
    # return dll.cbC8536Init(*args)
# dll.cbC8536Init.restype = None
# dll.cbC8536Init.argtype = (
                                   # )

# def cbC9513Config(*args):
    # return dll.cbC9513Config(*args)
# dll.cbC9513Config.restype = None
# dll.cbC9513Config.argtype = (
                                     # )

# def cbC9513Init(*args):
    # return dll.cbC9513Init(*args)
# dll.cbC9513Init.restype = None
# dll.cbC9513Init.argtype = (
                                   # )



# def cbCFreqIn(*args):
    # return dll.cbCFreqIn(*args)
# dll.cbCFreqIn.restype = None
# dll.cbCFreqIn.argtype = (
                                 # )

# def cbCIn(*args):
    # return dll.cbCIn(*args)
# dll.cbCIn.restype = None
# dll.cbCIn.argtype = (
                             # )


# def cbCIn64(*args):
    # return dll.cbCIn64(*args)
# dll.cbCIn64.restype = None
# dll.cbCIn64.argtype = (
                               # )

# def cbCInScan(*args):
    # return dll.cbCInScan(*args)
# dll.cbCInScan.restype = None
# dll.cbCInScan.argtype = (
                                 # )

# def cbClaimNetworkDevice(*args):
    # return dll.cbClaimNetworkDevice(*args)
# dll.cbClaimNetworkDevice.restype = None
# dll.cbClaimNetworkDevice.argtype = (
                                            # )

# def cbCLoad(*args):
    # return dll.cbCLoad(*args)
# dll.cbCLoad.restype = None
# dll.cbCLoad.argtype = (
                               # )

# def cbCLoad32(*args):
    # return dll.cbCLoad32(*args)
# dll.cbCLoad32.restype = None
# dll.cbCLoad32.argtype = (
                                 # )

# def cbCLoad64(*args):
    # return dll.cbCLoad64(*args)
# dll.cbCLoad64.restype = None
# dll.cbCLoad64.argtype = (
                                 # )

# def cbCreateBoard(*args):
    # return dll.cbCreateBoard(*args)
# dll.cbCreateBoard.restype = None
# dll.cbCreateBoard.argtype = (
                                     # )

# def cbCreateDaqDevice(*args):
    # return dll.cbCreateDaqDevice(*args)
# dll.cbCreateDaqDevice.restype = None
# dll.cbCreateDaqDevice.argtype = (
                                         # )

# def cbCreateDaqDeviceVB(*args):
    # return dll.cbCreateDaqDeviceVB(*args)
# dll.cbCreateDaqDeviceVB.restype = None
# dll.cbCreateDaqDeviceVB.argtype = (
                                           # )

# def cbCStatus(*args):
    # return dll.cbCStatus(*args)
# dll.cbCStatus.restype = None
# dll.cbCStatus.argtype = (
                                 # )

# def cbCStoreOnInt(*args):
    # return dll.cbCStoreOnInt(*args)
# dll.cbCStoreOnInt.restype = None
# dll.cbCStoreOnInt.argtype = (
                                     # )

# def cbDaqInScan(*args):
    # return dll.cbDaqInScan(*args)
# dll.cbDaqInScan.restype = None
# dll.cbDaqInScan.argtype = (
                                   # )

# def cbDaqOutScan(*args):
    # return dll.cbDaqOutScan(*args)
# dll.cbDaqOutScan.restype = None
# dll.cbDaqOutScan.argtype = (
                                    # )

# def cbDaqSetSetpoints(*args):
    # return dll.cbDaqSetSetpoints(*args)
# dll.cbDaqSetSetpoints.restype = None
# dll.cbDaqSetSetpoints.argtype = (
                                         # )

# def cbDaqSetTrigger(*args):
    # return dll.cbDaqSetTrigger(*args)
# dll.cbDaqSetTrigger.restype = None
# dll.cbDaqSetTrigger.argtype = (
                                       # )

# def cbDBitIn(*args):
    # return dll.cbDBitIn(*args)
# dll.cbDBitIn.restype = None
# dll.cbDBitIn.argtype = (
                                # )

# def cbDBitOut(*args):
    # return dll.cbDBitOut(*args)
# dll.cbDBitOut.restype = None
# dll.cbDBitOut.argtype = (
                                 # )

# def cbDClearAlarm(*args):
    # return dll.cbDClearAlarm(*args)
# dll.cbDClearAlarm.restype = None
# dll.cbDClearAlarm.argtype = (
                                     # )

# def cbDConfigBit(*args):
    # return dll.cbDConfigBit(*args)
# dll.cbDConfigBit.restype = None
# dll.cbDConfigBit.argtype = (
                                    # )

# def cbDConfigPort(*args):
    # return dll.cbDConfigPort(*args)
# dll.cbDConfigPort.restype = None
# dll.cbDConfigPort.argtype = (
                                     # )

# def cbDeclareRevision(*args):
    # return dll.cbDeclareRevision(*args)
# dll.cbDeclareRevision.restype = None
# dll.cbDeclareRevision.argtype = (
                                         # )

# def cbDeleteBoard(*args):
    # return dll.cbDeleteBoard(*args)
# dll.cbDeleteBoard.restype = None
# dll.cbDeleteBoard.argtype = (
                                     # )

# def cbDeviceLogin(*args):
    # return dll.cbDeviceLogin(*args)
# dll.cbDeviceLogin.restype = None
# dll.cbDeviceLogin.argtype = (
                                     # )

# def cbDeviceLogout(*args):
    # return dll.cbDeviceLogout(*args)
# dll.cbDeviceLogout.restype = None
# dll.cbDeviceLogout.argtype = (
                                      # )

# def cbDIn(*args):
    # return dll.cbDIn(*args)
# dll.cbDIn.restype = None
# dll.cbDIn.argtype = (
                             # )

# def cbDIn32(*args):
    # return dll.cbDIn32(*args)
# dll.cbDIn32.restype = None
# dll.cbDIn32.argtype = (
                               # )

# def cbDInArray(*args):
    # return dll.cbDInArray(*args)
# dll.cbDInArray.restype = None
# dll.cbDInArray.argtype = (
                                  # )

# def cbDInScan(*args):
    # return dll.cbDInScan(*args)
# dll.cbDInScan.restype = None
# dll.cbDInScan.argtype = (
                                 # )

# def cbDisableEvent(*args):
    # return dll.cbDisableEvent(*args)
# dll.cbDisableEvent.restype = None
# dll.cbDisableEvent.argtype = (
                                      # )

# def cbDOut(*args):
    # return dll.cbDOut(*args)
# dll.cbDOut.restype = None
# dll.cbDOut.argtype = (
                              # )

# def cbDOut32(*args):
    # return dll.cbDOut32(*args)
# dll.cbDOut32.restype = None
# dll.cbDOut32.argtype = (
                                # )

# def cbDOutArray(*args):
    # return dll.cbDOutArray(*args)
# dll.cbDOutArray.restype = None
# dll.cbDOutArray.argtype = (
                                   # )

# def cbDOutScan(*args):
    # return dll.cbDOutScan(*args)
# dll.cbDOutScan.restype = None
# dll.cbDOutScan.argtype = (
                                  # )

# def cbEnableEvent(*args):
    # return dll.cbEnableEvent(*args)
# dll.cbEnableEvent.restype = None
# dll.cbEnableEvent.argtype = (
                                     # )

# def cbErrHandling(*args):
    # return dll.cbErrHandling(*args)
# dll.cbErrHandling.restype = None
# dll.cbErrHandling.argtype = (
                                     # )

# def cbFileAInScan(*args):
    # return dll.cbFileAInScan(*args)
# dll.cbFileAInScan.restype = None
# dll.cbFileAInScan.argtype = (
                                     # )

# def cbFileGetInfo(*args):
    # return dll.cbFileGetInfo(*args)
# dll.cbFileGetInfo.restype = None
# dll.cbFileGetInfo.argtype = (
                                     # )

# def cbFilePretrig(*args):
    # return dll.cbFilePretrig(*args)
# dll.cbFilePretrig.restype = None
# dll.cbFilePretrig.argtype = (
                                     # )

# def cbFileRead(*args):
    # return dll.cbFileRead(*args)
# dll.cbFileRead.restype = None
# dll.cbFileRead.argtype = (
                                  # )

# def cbFlashLED(*args):
    # return dll.cbFlashLED(*args)
# dll.cbFlashLED.restype = None
# dll.cbFlashLED.argtype = (
                                  # )

# def cbFromEngUnits(*args):
    # return dll.cbFromEngUnits(*args)
# dll.cbFromEngUnits.restype = None
# dll.cbFromEngUnits.argtype = (
                                      # )

# def cbGetBoardName(*args):
    # return dll.cbGetBoardName(*args)
# dll.cbGetBoardName.restype = None
# dll.cbGetBoardName.argtype = (
                                      # )

# def cbGetBoardNumber(*args):
    # return dll.cbGetBoardNumber(*args)
# dll.cbGetBoardNumber.restype = None
# dll.cbGetBoardNumber.argtype = (
                                        # )

# def cbGetBoardNumberVB(*args):
    # return dll.cbGetBoardNumberVB(*args)
# dll.cbGetBoardNumberVB.restype = None
# dll.cbGetBoardNumberVB.argtype = (
                                          # )

# def cbGetCalCoeff(*args):
    # return dll.cbGetCalCoeff(*args)
# dll.cbGetCalCoeff.restype = None
# dll.cbGetCalCoeff.argtype = (
                                     # )

# def cbGetConfig(*args):
    # return dll.cbGetConfig(*args)
# dll.cbGetConfig.restype = None
# dll.cbGetConfig.argtype = (
                                   # )

# def cbGetConfigString(*args):
    # return dll.cbGetConfigString(*args)
# dll.cbGetConfigString.restype = None
# dll.cbGetConfigString.argtype = (
                                         # )

# def cbGetDaqDeviceInventory(*args):
    # return dll.cbGetDaqDeviceInventory(*args)
# dll.cbGetDaqDeviceInventory.restype = None
# dll.cbGetDaqDeviceInventory.argtype = (
                                               # )

# def cbGetDaqDeviceInventory_daqami(*args):
    # return dll.cbGetDaqDeviceInventory_daqami(*args)
# dll.cbGetDaqDeviceInventory_daqami.restype = None
# dll.cbGetDaqDeviceInventory_daqami.argtype = (
                                                      # )


# def cbGetIOStatus(*args):
    # return dll.cbGetIOStatus(*args)
# dll.cbGetIOStatus.restype = None
# dll.cbGetIOStatus.argtype = (
                                     # )

# def cbGetNetDeviceDescriptor(*args):
    # return dll.cbGetNetDeviceDescriptor(*args)
# dll.cbGetNetDeviceDescriptor.restype = None
# dll.cbGetNetDeviceDescriptor.argtype = (
                                                # )

# def cbGetRevision(*args):
    # return dll.cbGetRevision(*args)
# dll.cbGetRevision.restype = None
# dll.cbGetRevision.argtype = (
                                     # )

# def cbGetSignal(*args):
    # return dll.cbGetSignal(*args)
# dll.cbGetSignal.restype = None
# dll.cbGetSignal.argtype = (
                                   # )

# def cbGetStatus(*args):
    # return dll.cbGetStatus(*args)
# dll.cbGetStatus.restype = None
# dll.cbGetStatus.argtype = (
                                   # )

# def cbGetTCValues(*args):
    # return dll.cbGetTCValues(*args)
# dll.cbGetTCValues.restype = None
# dll.cbGetTCValues.argtype = (
                                     # )

# def cbIgnoreInstaCal(*args):
    # return dll.cbIgnoreInstaCal(*args)
# dll.cbIgnoreInstaCal.restype = None
# dll.cbIgnoreInstaCal.argtype = (
                                        # )

# def cbInByte(*args):
    # return dll.cbInByte(*args)
# dll.cbInByte.restype = None
# dll.cbInByte.argtype = (
                                # )

# def cbInDoubleWord(*args):
    # return dll.cbInDoubleWord(*args)
# dll.cbInDoubleWord.restype = None
# dll.cbInDoubleWord.argtype = (
                                      # )

# def cbInWord(*args):
    # return dll.cbInWord(*args)
# dll.cbInWord.restype = None
# dll.cbInWord.argtype = (
                                # )

# def cbLoadConfig(*args):
    # return dll.cbLoadConfig(*args)
# dll.cbLoadConfig.restype = None
# dll.cbLoadConfig.argtype = (
                                    # )

# def cbLogConvertFile(*args):
    # return dll.cbLogConvertFile(*args)
# dll.cbLogConvertFile.restype = None
# dll.cbLogConvertFile.argtype = (
                                        # )

# def cbLogGetAIChannelCount(*args):
    # return dll.cbLogGetAIChannelCount(*args)
# dll.cbLogGetAIChannelCount.restype = None
# dll.cbLogGetAIChannelCount.argtype = (
                                              # )

# def cbLogGetAIInfo(*args):
    # return dll.cbLogGetAIInfo(*args)
# dll.cbLogGetAIInfo.restype = None
# dll.cbLogGetAIInfo.argtype = (
                                      # )

# def cbLogGetCJCInfo(*args):
    # return dll.cbLogGetCJCInfo(*args)
# dll.cbLogGetCJCInfo.restype = None
# dll.cbLogGetCJCInfo.argtype = (
                                       # )

# def cbLogGetDIOInfo(*args):
    # return dll.cbLogGetDIOInfo(*args)
# dll.cbLogGetDIOInfo.restype = None
# dll.cbLogGetDIOInfo.argtype = (
                                       # )

# def cbLogGetFileInfo(*args):
    # return dll.cbLogGetFileInfo(*args)
# dll.cbLogGetFileInfo.restype = None
# dll.cbLogGetFileInfo.argtype = (
                                        # )

# def cbLogGetFileName(*args):
    # return dll.cbLogGetFileName(*args)
# dll.cbLogGetFileName.restype = None
# dll.cbLogGetFileName.argtype = (
                                        # )

# def cbLogGetPreferences(*args):
    # return dll.cbLogGetPreferences(*args)
# dll.cbLogGetPreferences.restype = None
# dll.cbLogGetPreferences.argtype = (
                                           # )

# def cbLogGetSampleInfo(*args):
    # return dll.cbLogGetSampleInfo(*args)
# dll.cbLogGetSampleInfo.restype = None
# dll.cbLogGetSampleInfo.argtype = (
                                          # )

# def cbLogReadAIChannels(*args):
    # return dll.cbLogReadAIChannels(*args)
# dll.cbLogReadAIChannels.restype = None
# dll.cbLogReadAIChannels.argtype = (
                                           # )

# def cbLogReadCJCChannels(*args):
    # return dll.cbLogReadCJCChannels(*args)
# dll.cbLogReadCJCChannels.restype = None
# dll.cbLogReadCJCChannels.argtype = (
                                            # )

# def cbLogReadDIOChannels(*args):
    # return dll.cbLogReadDIOChannels(*args)
# dll.cbLogReadDIOChannels.restype = None
# dll.cbLogReadDIOChannels.argtype = (
                                            # )

# def cbLogReadTimeTags(*args):
    # return dll.cbLogReadTimeTags(*args)
# dll.cbLogReadTimeTags.restype = None
# dll.cbLogReadTimeTags.argtype = (
                                         # )

# def cbLogSetPreferences(*args):
    # return dll.cbLogSetPreferences(*args)
# dll.cbLogSetPreferences.restype = None
# dll.cbLogSetPreferences.argtype = (
                                           # )

# def cbMemRead(*args):
    # return dll.cbMemRead(*args)
# dll.cbMemRead.restype = None
# dll.cbMemRead.argtype = (
                                 # )

# def cbMemReadPretrig(*args):
    # return dll.cbMemReadPretrig(*args)
# dll.cbMemReadPretrig.restype = None
# dll.cbMemReadPretrig.argtype = (
                                        # )

# def cbMemReset(*args):
    # return dll.cbMemReset(*args)
# dll.cbMemReset.restype = None
# dll.cbMemReset.argtype = (
                                  # )

# def cbMemWrite(*args):
    # return dll.cbMemWrite(*args)
# dll.cbMemWrite.restype = None
# dll.cbMemWrite.argtype = (
                                  # )

# def cbOutByte(*args):
    # return dll.cbOutByte(*args)
# dll.cbOutByte.restype = None
# dll.cbOutByte.argtype = (
                                 # )

# def cbOutDoubleWord(*args):
    # return dll.cbOutDoubleWord(*args)
# dll.cbOutDoubleWord.restype = None
# dll.cbOutDoubleWord.argtype = (
                                       # )

# def cbOutWord(*args):
    # return dll.cbOutWord(*args)
# dll.cbOutWord.restype = None
# dll.cbOutWord.argtype = (
                                 # )

# def cbPulseOutStart(*args):
    # return dll.cbPulseOutStart(*args)
# dll.cbPulseOutStart.restype = None
# dll.cbPulseOutStart.argtype = (
                                       # )

# def cbPulseOutStop(*args):
    # return dll.cbPulseOutStop(*args)
# dll.cbPulseOutStop.restype = None
# dll.cbPulseOutStop.argtype = (
                                      # )

# def cbReadMem(*args):
    # return dll.cbReadMem(*args)
# dll.cbReadMem.restype = None
# dll.cbReadMem.argtype = (
                                 # )

# def cbReleaseDaqDevice(*args):
    # return dll.cbReleaseDaqDevice(*args)
# dll.cbReleaseDaqDevice.restype = None
# dll.cbReleaseDaqDevice.argtype = (
                                          # )

# def cbResetDevice(*args):
    # return dll.cbResetDevice(*args)
# dll.cbResetDevice.restype = None
# dll.cbResetDevice.argtype = (
                                     # )

# def cbRS485(*args):
    # return dll.cbRS485(*args)
# dll.cbRS485.restype = None
# dll.cbRS485.argtype = (
                               # )

# def cbSaveConfig(*args):
    # return dll.cbSaveConfig(*args)
# dll.cbSaveConfig.restype = None
# dll.cbSaveConfig.argtype = (
                                    # )

# def cbScaledWinArrayToBuf(*args):
    # return dll.cbScaledWinArrayToBuf(*args)
# dll.cbScaledWinArrayToBuf.restype = None
# dll.cbScaledWinArrayToBuf.argtype = (
                                             # )

# def cbScaledWinBufAlloc(*args):
    # return dll.cbScaledWinBufAlloc(*args)
# dll.cbScaledWinBufAlloc.restype = None
# dll.cbScaledWinBufAlloc.argtype = (
                                           # )

# def cbScaledWinBufToArray(*args):
    # return dll.cbScaledWinBufToArray(*args)
# dll.cbScaledWinBufToArray.restype = None
# dll.cbScaledWinBufToArray.argtype = (
                                             # )

# def cbSelectSignal(*args):
    # return dll.cbSelectSignal(*args)
# dll.cbSelectSignal.restype = None
# dll.cbSelectSignal.argtype = (
                                      # )

# def cbSetCalCoeff(*args):
    # return dll.cbSetCalCoeff(*args)
# dll.cbSetCalCoeff.restype = None
# dll.cbSetCalCoeff.argtype = (
                                     # )

# def cbSetConfig(*args):
    # return dll.cbSetConfig(*args)
# dll.cbSetConfig.restype = None
# dll.cbSetConfig.argtype = (
                                   # )

# def cbSetConfigString(*args):
    # return dll.cbSetConfigString(*args)
# dll.cbSetConfigString.restype = None
# dll.cbSetConfigString.argtype = (
                                         # )

# def cbSetTrigger(*args):
    # return dll.cbSetTrigger(*args)
# dll.cbSetTrigger.restype = None
# dll.cbSetTrigger.argtype = (
                                    # )

# def cbStopBackground(*args):
    # return dll.cbStopBackground(*args)
# dll.cbStopBackground.restype = None
# dll.cbStopBackground.argtype = (
                                        # )

# def cbStopIOBackground(*args):
    # return dll.cbStopIOBackground(*args)
# dll.cbStopIOBackground.restype = None
# dll.cbStopIOBackground.argtype = (
                                          # )

# def cbTEDSRead(*args):
    # return dll.cbTEDSRead(*args)
# dll.cbTEDSRead.restype = None
# dll.cbTEDSRead.argtype = (
                                  # )

# def cbTimerOutStart(*args):
    # return dll.cbTimerOutStart(*args)
# dll.cbTimerOutStart.restype = None
# dll.cbTimerOutStart.argtype = (
                                       # )

# def cbTimerOutStop(*args):
    # return dll.cbTimerOutStop(*args)
# dll.cbTimerOutStop.restype = None
# dll.cbTimerOutStop.argtype = (
                                      # )

# def cbTIn(*args):
    # return dll.cbTIn(*args)
# dll.cbTIn.restype = None
# dll.cbTIn.argtype = (
                             # )

# def cbTInScan(*args):
    # return dll.cbTInScan(*args)
# dll.cbTInScan.restype = None
# dll.cbTInScan.argtype = (
                                 # )

# def cbToEngUnits(*args):
    # return dll.cbToEngUnits(*args)
# dll.cbToEngUnits.restype = None
# dll.cbToEngUnits.argtype = (
                                    # )

# def cbToEngUnits32(*args):
    # return dll.cbToEngUnits32(*args)
# dll.cbToEngUnits32.restype = None
# dll.cbToEngUnits32.argtype = (
                                      # )

# def cbVIn(*args):
    # return dll.cbVIn(*args)
# dll.cbVIn.restype = None
# dll.cbVIn.argtype = (
                             # )

# def cbVIn32(*args):
    # return dll.cbVIn32(*args)
# dll.cbVIn32.restype = None
# dll.cbVIn32.argtype = (
                               # )

# def cbVOut(*args):
    # return dll.cbVOut(*args)
# dll.cbVOut.restype = None
# dll.cbVOut.argtype = (
                              # )

# def cbWinArrayToBuf(*args):
    # return dll.cbWinArrayToBuf(*args)
# dll.cbWinArrayToBuf.restype = None
# dll.cbWinArrayToBuf.argtype = (
                                       # )

# def cbWinArrayToBuf32(*args):
    # return dll.cbWinArrayToBuf32(*args)
# dll.cbWinArrayToBuf32.restype = None
# dll.cbWinArrayToBuf32.argtype = (
                                         # )

# def cbWinBufAlloc(*args):
    # return dll.cbWinBufAlloc(*args)
# dll.cbWinBufAlloc.restype = None
# dll.cbWinBufAlloc.argtype = (
                                     # )

# def cbWinBufAlloc32(*args):
    # return dll.cbWinBufAlloc32(*args)
# dll.cbWinBufAlloc32.restype = None
# dll.cbWinBufAlloc32.argtype = (
                                       # )

# def cbWinBufAlloc64(*args):
    # return dll.cbWinBufAlloc64(*args)
# dll.cbWinBufAlloc64.restype = None
# dll.cbWinBufAlloc64.argtype = (
                                       # )

# def cbWinBufFree(*args):
    # return dll.cbWinBufFree(*args)
# dll.cbWinBufFree.restype = None
# dll.cbWinBufFree.argtype = (
                                    # )

# def cbWinBufFromEngUnits(*args):
    # return dll.cbWinBufFromEngUnits(*args)
# dll.cbWinBufFromEngUnits.restype = None
# dll.cbWinBufFromEngUnits.argtype = (
                                            # )

# def cbWinBufToArray(*args):
    # return dll.cbWinBufToArray(*args)
# dll.cbWinBufToArray.restype = None
# dll.cbWinBufToArray.argtype = (
                                       # )

# def cbWinBufToArray32(*args):
    # return dll.cbWinBufToArray32(*args)
# dll.cbWinBufToArray32.restype = None
# dll.cbWinBufToArray32.argtype = (
                                         # )

# def cbWinBufToArray64(*args):
    # return dll.cbWinBufToArray64(*args)
# dll.cbWinBufToArray64.restype = None
# dll.cbWinBufToArray64.argtype = (
                                         # )

# def cbWinBufToEngUnits(*args):
    # return dll.cbWinBufToEngUnits(*args)
# dll.cbWinBufToEngUnits.restype = None
# dll.cbWinBufToEngUnits.argtype = (
                                          # )

# def cbWriteMem(*args):
    # return dll.cbWriteMem(*args)
# dll.cbWriteMem.restype = None
# dll.cbWriteMem.argtype = (
                                  # )

# def lvPromptInstaCAL(*args):
    # return dll.lvPromptInstaCAL(*args)
# dll.lvPromptInstaCAL.restype = None
# dll.lvPromptInstaCAL.argtype = (
                                        # )

