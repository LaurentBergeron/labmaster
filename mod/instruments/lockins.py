"""
Definition of lock-in amplifier Instrument classes.

Current classes: 
- Lockin_SR844
- Lockin_5210 
"""
__author__ =  "Adam DeAbreu <adeabreu@sfu.ca>, Laurent Bergeron <laurent.bergeron4@gmail.com>"

## Base modules
import numpy as np
import visa as vi

## Homemade modules
from .default_visa import Default_visa
from ..units import *
from .. import not_for_user     
nfu = not_for_user
        
        
class Lockin_SR844(Default_visa):
    """Class allowing to control a model 5210 lock-in amplifier."""
    def __init__(self, name, parent, visa_ID):
        """
        Inherit from Default_visa and open a VISA device handle.
        - name: Name to give to the instrument.
        - parent: A reference to the lab instance hosting the instrument.
        - visa_ID: Connection address. 
        """
        Default_visa.__init__(self, name, parent, visa_ID) 
        print('connected to lock-in model SR844.')
        return
    
        
    def auto_phase(self):
        """Change the phase to maximise X signal."""
        self.device_handle.write('APHS')
        return

    def get_X(self):
        """Read X component (volts if self.convert_reading=True)."""
        X = float(self.device_handle.query('OUTP?1'))
        return X
        
    def get_Y(self):
        """Read Y component (volts if self.convert_reading=True)."""
        Y = float(self.device_handle.query('OUTP?2'))
        return Y
        
    def get_XY(self):
        """Read voltage from both X and Y at the same time."""
        X, Y = self.device_handle.query('SNAP?1,2').split(",")
        X, Y = float(X), float(Y)
        return X, Y
        
    def get_magnitude(self):
        """Read voltage magnitude (volts if self.convert_reading=True)."""
        mag = float(self.device_handle.query('OUTP?3'))
        return mag
        
    def get_phase(self):
        """Read phase (deg if self.convert_reading=True)."""
        phase = float(self.device_handle.query('OUTP?5'))
        return phase
        
    def get_magnitude_and_phase(self):
        """Read both voltage magnitude and phase at the same time."""
        mag, phase = self.device_handle.query('SNAP?3,5').split(",")
        mag, phase = float(mag), float(phase)
        return mag, phase

    def get_time_constant(self):
        """Read currently selected time_constant."""
        code = self.device_handle.query('OFLT?').rstrip()
        return self.time_cst_chart.get(str(int(code)), "failed")

    def get_sensitivity(self):
        """Read currently selected sensitivity."""
        code = self.device_handle.query('SENS?').rstrip()
        return self.sensitivity_chart.get(str(int(code)), "failed")
        
    def set_time_constant(self, time_cst):
        """Set time constant. Input the requested time constant in seconds."""
        code = None
        for key, value in list(self.time_cst_chart.items()):
            if value==time_cst:
                code = key
        if code==None:
            raise Lockin5210Error("Requested time constant not available.")
        return self.device_handle.write('OFLT'+code)

    def set_sensitivity(self, sensitivity):
        """Set sensitivity. Input the requested sensitivity in volts."""
        code = None
        for key, value in list(self.sensitivity_chart.items()):
            if value==sensitivity:
                code = key
        if code==None:
            raise Lockin5210Error("Requested sensitivity not available.")
        return self.device_handle.write('SENS'+code)
        
        

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
                         "14":1}

    ## Dictionary of time constant codes.
    time_cst_chart = {"0":100*us,
                      "1":300*us,
                      "2":ms,
                      "3":3*ms,
                      "4":10*ms,
                      "5":30*ms,
                      "6":100*ms,
                      "7":300*ms,
                      "8":1,
                      "9":3,
                      "10":10,
                      "11":30,
                      "12":100,
                      "13":300,
                      "14":1000,
                      "15":3000,
                      "16":10000,
                      "17":30000}
        
        
        
class Lockin_5210(Default_visa):
    """Class allowing to control a model 5210 lock-in amplifier."""
    def __init__(self, name, parent, visa_ID):
        """
        Inherit from Default_visa and open a VISA device handle.
        - name: Name to give to the instrument.
        - parent: A reference to the lab instance hosting the instrument.
        - visa_ID: Connection address. 
        """
        Default_visa.__init__(self, name, parent, visa_ID) 
        ### Options ###
        self.convert_reading = False ## True is not fully tested.
        print('connected to lock-in model 5210.')
        return
    
        
    def auto_phase(self):
        """Change the phase to maximise X signal."""
        self.device_handle.write('AQN')
        return

    def get_X(self):
        """Read X component (volts if self.convert_reading=True)."""
        X = float(self.device_handle.query('X'))
        if self.convert_reading:
            X *= self.get_sensitivity()/10000.0
        return X
        
    def get_Y(self):
        """Read Y component (volts if self.convert_reading=True)."""
        Y = float(self.device_handle.query('Y'))
        if self.convert_reading:
            Y *= self.get_sensitivity()/10000.0
        return Y
        
    def get_XY(self):
        """Read voltage from both X and Y at the same time."""
        X, Y = self.device_handle.query('XY').split(",")
        X, Y = float(X), float(Y)
        if self.convert_reading:
            X *= self.get_sensitivity()/10000.0
            Y *= self.get_sensitivity()/10000.0
        return X, Y
        
    def get_magnitude(self):
        """Read voltage magnitude (volts if self.convert_reading=True)."""
        mag = float(self.device_handle.query('MAG'))
        if self.convert_reading:
            mag *= self.get_sensitivity()/10000.0
        return mag
        
    def get_phase(self):
        """Read phase (deg if self.convert_reading=True)."""
        phase = float(self.device_handle.query('PHA'))
        if self.convert_reading:
            mag *= self.get_sensitivity()/10000.0
            phase /= 1000.0
        return phase
        
    def get_magnitude_and_phase(self):
        """Read both voltage magnitude and phase at the same time."""
        mag, phase = self.device_handle.query('MP').split(",")
        mag, phase = float(mag), float(phase)
        if self.convert_reading:
            phase /= 1000.0
        return mag, phase

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
        for key, value in list(self.time_cst_chart.items()):
            if value==time_cst:
                code = key
        if code==None:
            raise Lockin5210Error("Requested time constant not available.")
        return self.device_handle.write('TC '+code)

    def set_sensitivity(self, sensitivity):
        """Set sensitivity. Input the requested sensitivity in volts."""
        code = None
        for key, value in list(self.sensitivity_chart.items()):
            if value==sensitivity:
                code = key
        if code==None:
            raise Lockin5210Error("Requested sensitivity not available.")
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
        