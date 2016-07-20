__author__ =  "Laurent Bergeron <laurent.bergeron4@gmail.com>"

# Base modules
import inspect
import numpy as np
import visa as vi
import ctypes as ct
import importlib
import time

# Homemade modules
from ..classes import Instrument
from ..units import *
from .. import not_for_user     
nfu = not_for_user 
        

class Usb_counter(Instrument):
    """
    First use procedure: 
    1) Install instaCal from Measurement Computing Corporation. http://www.mccdaq.com/daq-software/instacal.aspx
    2) Run inscal32.exe and detect the USB counter device.
    
    TODO: Complete the wrapper.
    """
    def __init__(self, name, parent, board_num):
        Instrument.__init__(self, name, parent)
        self.is_ping_pong
        self.cbw32 = importlib.import_module("mod.instruments.wrappers.dll_cbw32")
        self.verbose = False
        self.error_msg = ct.create_string_buffer(1000)
        self.board_num = board_num
        self.saved = {}
        for counter_num in (0,1):
            status = self.cbw32.cbCConfigScan(self.board_num, counter_num, 0x10, 16, 0, 0, 0, counter_num)
            self.check_status(status)
            self.clear(counter_num)
            self.saved[str(counter_num)] = 0
        return
    
    def abort(self):
        return
    
    def check_status(self, status):
        if self.verbose:
            print "USB_counter:", status
        if status > 0:
            self.cbw32.cbGetErrMsg(status, self.error_msg)
            raise USBCounterError, self.error_msg.value
        return
    
    def clear(self, counter_num):
        status = self.cbw32.cbCClear(self.board_num, counter_num)
        self.check_status(status)
        return
        
    def close(self):
        return

    def read(self, counter_num):
        value = ct.c_ulong()
        status = self.cbw32.cbCIn32(self.board_num, counter_num, ct.byref(value))
        self.check_status(status)
        self.saved[str(counter_num)] = value.value
        return value.value

class USBCounterError(nfu.LabMasterError):
    pass      
    