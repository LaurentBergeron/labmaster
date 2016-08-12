"""
Definition of laser Instrument classes.

Current classes: 
- Laser_ITC4001 
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
        
class Laser_ITC4001(Default_visa):
    """Class allowing to control an ITC4001 infrared laser."""
    def __init__(self, name, parent, visa_ID):
        """
        Inherit from Default_visa and open a VISA device handle.
        - name: Name to give to the instrument.
        - parent: A reference to the lab instance hosting the instrument.
        - visa_ID: Connection address. 
        """
        Default_visa.__init__(self, name, parent, visa_ID) 
        
        self.MAX_CURR = 200*mA
        self.MIN_CURR = 0
        self.MAX_TEMP = 40 ## Celcius
        self.MIN_TEMP = 30 ## Celcius
        print 'connected ITC4001 laser.'
        return 
        
    def check_temperature(self, temp):
        """Check if input temperature satisfies minimum and maximum values."""
        if temp > self.MAX_TEMP:
            self.beep()
            raise LaserITC4001Error, "Can't set temperature higher than "+str(self.MAX_TEMP)+" Celcius."
        elif temp < self.MIN_TEMP:
            self.beep()
            raise LaserITC4001Error, "Can't set temperature lower than "+str(self.MIN_TEMP)+" Celcius."
        return
        
    def check_current(self, curr):
        """Check if input current satisfies minimum and maximum values."""
        if curr > self.MAX_CURR:
            self.beep()
            raise LaserITC4001Error, "Can't set current higher than "+str(self.MAX_CURR*1e3)+" mA."
        elif curr < self.MIN_CURR:
            self.beep()
            raise LaserITC4001Error, "Can't set current lower than "+str(self.MIN_CURR*1e3)+" mA."
        return
    
    def get_temp(self):
        """Read temperature Celcius)."""
        return float(self.device_handle.query("meas:temp?"))
    
    def get_current(self):
        """Read current (A)."""
        return float(self.device_handle.query("meas:curr?"))
    
        
    def set_temp(self, temp):
        """Set temperature (Celcius)."""
        self.check_temperature(temp)
        self.device_handle.write("source2:temp "+str(temp)) ## the suffix 2 is required for ITC4001 instruments.
        return
        
    def set_current(self, curr):
        """Set current (A)."""
        self.check_current(curr)
        self.device_handle.write("source:curr "+str(curr))
        return
        
    def beep(self):
        """Self-explanatory."""
        retval = self.device_handle.write("SYST:BEEP:IMM")
        return "BEEP!"


class LaserITC4001Error(nfu.LabMasterError):
    """Errors raised by the ITC4001 laser."""
    pass
    