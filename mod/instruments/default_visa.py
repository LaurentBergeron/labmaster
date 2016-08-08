"""
Definition of the Default_visa class, a quick way to connect and control a classless VISA instrument.
"""

__author__ =  "Adam DeAbreu <adeabreu@sfu.ca>, Laurent Bergeron <laurent.bergeron4@gmail.com>"

## Base modules
import numpy as np
import visa as vi

## Homemade modules
from ..classes import Instrument
from ..units import *
from .. import not_for_user     
nfu = not_for_user
        
class Default_visa(Instrument):
    """A generic Instrument class for VISA communication protocol."""
    def __init__(self, name, parent, visa_ID):
        """
        Inherit from Instrument and open a VISA device handle.
        - name: Name to give to the instrument.
        - parent: A reference to the lab instance hosting the instrument.
        - visa_ID: Connection address. 
        """
        Instrument.__init__(self, name, parent) 
        rm = vi.ResourceManager()
        self.device_handle = rm.open_resource(visa_ID)
        print self.device_handle.query("*IDN?")
        return
        
    def abort(self):
        """To be executed when scan raises on error (Ctrl-C included)."""
        return

    def write(self, towrite):
        """Default VISA write. Refer to the instrument manual for possible inputs."""
        try:
            retval = self.device_handle.write(towrite)
            retval = retval[1].value
        except vi.VisaIOError:
            retval = -1
        return retval

    def query(self, toquery):
        """Default VISA query. Refer to the instrument manual for possible inputs."""
        try:
            retval = self.device_handle.query(toquery)
        except vi.VisaIOError:
            retval = -1
        return retval

    def read(self, toread):
        """Default VISA read. Refer to the instrument manual for possible inputs."""
        try:
            retval = self.device_handle.read(toread)
        except vi.VisaIOError:
            retval = -1
        return retval
    
    def close(self):
        """Close the device handle."""
        return self.device_handle.close()

    
class DefaultVISAError(nfu.LabMasterError):
    """Errors raised by a default VISA class."""
    pass
