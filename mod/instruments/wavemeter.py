__authors__ =  "Adam DeAbreu <adeabreu@sfu.ca>, Laurent Bergeron <laurent.bergeron4@gmail.com>"

# Base modules
import numpy as np
import visa as vi
import ctypes as ct
import importlib

# Homemade modules
from ..classes import Instrument
from ..units import *
from .. import not_for_user     
nfu = not_for_user 

class Wavemeter(Instrument):
    """
    """
    def __init__(self, name, parent, com_number):
        Instrument.__init__(self, name, parent)
        self.CLDevIFace = importlib.import_module("mod.instruments.wrappers.dll_CLDevIFace")
        self.com_number = com_number
        self.device_handle = self.CLDevIFace.CLOpenUSBSerialDevice(self.com_number)
        self.lambda_units = "nm"
        return
    
    def abort(self):
        return

    def set_lambda_units(self, lambda_units):
        self.lambda_units = lambda_units
        retval = self.CLDevIFace.CLSetLambdaUnits(self.device_handle, self.lambda_units)
        return retval

    def measure(self):
        wavelength = self.CLDevIFace.CLGetLambdaReading(self.device_handle)
        return wavelength

    def close(self):
        return self.CLDevIFace.CLCloseDevice(self.device_handle)

        
        
