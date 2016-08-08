"""
Definition of lock-in amplifier Instrument classes.

Current classes: 
- Lockin_5210 
"""
__author__ =  "Adam DeAbreu <adeabreu@sfu.ca>, Laurent Bergeron <laurent.bergeron4@gmail.com>"

## Base modules
import numpy as np
import visa as vi

## Homemade modules
from default_visa import Default_visa
from ..units import *
from .. import not_for_user     
nfu = not_for_user
        
class Lockin_5210(Default_visa):
    """Class allowing to control a model 5210 lock-in amplifier."""
    def __init__(self, name, parent, visa_ID):
        """
        Inherit from Default_visa and open a VISA device handle.
        - name: Name to give to the instrument.
        - parent: A reference to the lab instance hosting the instrument.
        - visa_ID: Connection address. 
        """
        Default_visa.__init__(self, name, parent) 
        rm = vi.ResourceManager()
        self.device_handle = rm.open_resource(visa_ID)
        return
    
        
    def auto_phase(self):
        """TODO"""
        self.device_handle.write('AQN')
        return

    def get_X(self):
        """Read X component (V)."""
        retval = self.device_handle.query('X')
        return float(retval)
        
    def get_Y(self):
        """Read Y component (V)."""
        retval = self.device_handle.query('Y')
        return float(retval)
        
    def get_XY(self):
        """Read voltage from both X and Y at the same time."""
        X, Y = self.device_handle.query('XY').split(",")
        return float(X), float(Y)
        
    def get_magnitude(self):
        """Read voltage magnitude (V)."""
        retval = self.device_handle.query('MAG')
        return float(retval)
        
    def get_phase(self):
        """Read phase (deg)."""
        retval = self.device_handle.query('PHA')
        return float(retval)
        
    def get_magnitude_and_phase(self):
        """Read both voltage magnitude and phase at the same time."""
        mag, phase = self.device_handle.query('MP').split(",")
        return float(mag), float(phase)/1000.0

    def get_time_constant(self):
        """Read currently selected time_constant."""
        code = self.device_handle.query('TC')
        return self.time_cst_chart.get(str(int(code)), "failed")

    def get_sensitivity(self):
        """Read currently selected sensitivity."""
        code = self.device_handle.query('SEN')
        return self.sensitivity_chart.get(str(int(code)), "failed")
        
    def set_time_constant(self, time_cst):
        """Set time constant. Input the requested time constant in seconds."""
        code = None
        for key, value in self.time_cst_chart.items():
            if value==time_cst:
                code = key
        if code==None:
            raise Lockin5210Error, "Requested time constant not available."
        return self.device_handle.write('TC '+code)

    def set_sensitivity(self, sensitivity):
        """Set sensitivity. Input the requested sensitivity in volts."""
        code = None
        for key, value in self.sensitivity_chart.items():
            if value==sensitivity:
                code = key
        if code==None:
            raise Lockin5210Error, "Requested sensitivity not available."
        return self.device_handle.write('SEN '+code)
        
        

    ## Dictionary of sensitivity codes.
    sensitivity_chart = {"0":100*nV,
                         "1":300*nV,
                         "2":uV,
                         "3":3*uV,
                         "4":10*uV,
                         "5":30*uV,
                         "6":100*uV,
                         "7":300*uV,
                         "8":mV,
                         "9":3*mV,
                         "10":10*mV,
                         "11":30*mV,
                         "12":100*mV,
                         "13":300*mV,
                         "14":1,
                         "15":3}

    ## Dictionary of time constant codes.
    time_cst_chart = {"0":ms,
                      "1":3*ms,
                      "2":10*ms,
                      "3":30*ms,
                      "4":100*ms,
                      "5":300*ms,
                      "6":1,
                      "7":3,
                      "8":10,
                      "9":30,
                      "10":100,
                      "11":300,
                      "12":1000,
                      "13":3000}
        
class Lockin5210Error(nfu.LabMasterError):
    """Errors raised by the model 5210 lock-in amplifier."""
    pass
        