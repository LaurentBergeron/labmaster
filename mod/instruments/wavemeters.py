"""
Definition of wavemeter Instrument classes.

Current classes: 
- Wavemeter_Bristol621
"""
__authors__ =  "Adam DeAbreu <adeabreu@sfu.ca>, Laurent Bergeron <laurent.bergeron4@gmail.com>"

## Base modules
import numpy as np
import visa as vi
import ctypes as ct
import importlib

## Homemade modules
from ..classes import Instrument
from ..units import *
from .. import not_for_user     
nfu = not_for_user 

class Wavemeter_Bristol621(Instrument):
    """Class allowing to control a Bristol 621 wavemeter."""
    def __init__(self, name, parent, com_number):
        """
        Inherit from Instrument class.
        Import wrapper and initialize device handle.
        - name: Name to give to the instrument.
        - parent: A reference to the lab instance hosting the instrument.
        - com_number: Serial port connection number.
        """
        Instrument.__init__(self, name, parent)
        self.CLDevIFace = importlib.import_module("mod.instruments.wrappers.dll_CLDevIFace")
        self.com_number = com_number
        self.device_handle = self.CLDevIFace.CLOpenUSBSerialDevice(self.com_number)
        self.lambda_units = "nm"
        print('connected to Bristol 621 wavemeter.')
        return
    
    def abort(self):
        """To be executed when scan raises on error (Ctrl-C included)."""
        return

    def set_lambda_units(self, lambda_units):
        """Choose if the reading if given in wavenumber or nanometer ('GHz', '1/cm' or 'nm')."""
        self.lambda_units = lambda_units
        retval = self.CLDevIFace.CLSetLambdaUnits(self.device_handle, self.lambda_units)
        return retval

    def measure(self):
        """
        Read the wavemeter.
        The result will be in the units given by self.lambda_units.
        """
        wavelength = self.CLDevIFace.CLGetLambdaReading(self.device_handle)
        return wavelength

    def close(self):
        """Close the device handle."""
        return self.CLDevIFace.CLCloseDevice(self.device_handle)

        
