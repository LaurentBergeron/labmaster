"""
Definition of USB counter Instrument classes.

Current classes: 
- USB_counter_CTR04
"""
__author__ =  "Laurent Bergeron <laurent.bergeron4@gmail.com>"

## Base modules
import inspect
import numpy as np
import visa as vi
import ctypes as ct
import importlib
import time

## Homemade modules
from ..classes import Instrument
from ..units import *
from .. import not_for_user     
nfu = not_for_user 
        

class USB_counter_CTR04(Instrument):
    """
    Class allowing to control an CTR04 USB counter.
    
    First use procedure: 
    1) Install instaCal from Measurement Computing Corporation. http://www.mccdaq.com/daq-software/instacal.aspx
    2) Run inscal32.exe and detect the USB counter device.
    """
    def __init__(self, name, parent, board_num):
        """
        Inherit from Instrument class.
        Import wrapper and initialize driver.
        Configure and clear two counters.
        - name: Name to give to the instrument.
        - parent: A reference to the lab instance hosting the instrument.
        - board_num: Number of the board (0 if only one board is present.)
        """
        ##----------------------------------------------- OPTIONS -----------------------------------------------##
        self.verbose = False
        ##-------------------------------------------------------------------------------------------------------##
        Instrument.__init__(self, name, parent)
        self.cbw64 = importlib.import_module("mod.instruments.wrappers.dll_cbw64")
        self.error_msg = ct.create_string_buffer(1000)
        self.board_num = board_num
        for counter_num in (0,1,2):
            ## counter 0 is bin A
            ## counter 1 is bin B
            ## counter 2 is Count - to use with the timer
            status = self.cbw64.cbCConfigScan(self.board_num, counter_num, 0x10, 16, 0, 0, 0, counter_num)
            self.check_status(status)
            self.clear(counter_num)
        print('connected to USB counter CTR04.')
        return
    
    def abort(self):
        """To be executed when scan raises on error (Ctrl-C included)."""
        return
    
    def check_status(self, status):
        """Get error message if an error was raised by a function from the driver."""
        if self.verbose:
            print("USB_counter:", status)
        if status > 0:
            self.cbw64.cbGetErrMsg(status, self.error_msg)
            raise USBCounterError(self.error_msg.value)
        return
    
    def clear(self, counter_num):
        """Clear count from specified counter."""
        status = self.cbw64.cbCClear(self.board_num, counter_num)
        self.check_status(status)
        return
        
    def close(self):
        """I didn't find a function to close driver."""
        return

    def read(self, counter_num):
        """Read number of counts from specified counter."""
        value = ct.c_ulong()
        status = self.cbw64.cbCIn32(self.board_num, counter_num, ct.byref(value))
        self.check_status(status)
        return value.value
    
    def initiate_timer(self, freq):
        timer_num = 0
        duty_cycle = 0.5
        pulse_count = 1
        initial_delay = 0.
        status = self.cbw64.cbPulseOutStart(self.board_num, timer_num, ct.byref(ct.c_double(freq)), ct.byref(ct.c_double(duty_cycle)), pulse_count, ct.byref(ct.c_double(initial_delay)), 0, 0)
        self.check_status(status)
        return
    
    def timer_is_stopped(self):
        value = ct.c_ulong()
        port = 1 # AuxPort is 1
        status = self.cbw64.cbDIn(self.board_num, port, ct.byref(value))
        self.check_status(status)
        if value.value==0:
            result = True
        else:
            result = False
        return result

class USBCounterError(nfu.LabMasterError):
    """Errors raised by the CTR04 USB counter."""
    pass      
    