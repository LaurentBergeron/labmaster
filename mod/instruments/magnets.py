"""
Definition of magnet Instrument classes.

Current classes: 
- PowerSupplyCS410V
"""
__author__ =  "Laurent Bergeron <laurent.bergeron4@gmail.com>"

# Base modules
import numpy as np
import visa as vi

# Homemade modules
from .default_visa import Default_visa
from ..units import *
from .. import not_for_user     
nfu = not_for_user



class PowerSupplyCS410V(Default_visa):
    """Class allowing to control a CS410V superconducting magnet power supply."""
    
    def __init__(self, name, parent, visa_ID):
        """
        Inherit from Default_visa and open a VISA device handle.
        - name: Name to give to the instrument.
        - parent: A reference to the lab instance hosting the instrument.
        - visa_ID: Connection address. 
        """
        Default_visa.__init__(self, name, parent, visa_ID) 
        self.MIN_CURRENT = 0 ## TODO update
        self.MAX_CURRENT = 1e9 ## TODO update
        print('connected to CS410V superconducting magnet power supply.')
        return
        
    def check_current(self, current):
        """Check if input current satisfies minimum and maximum values."""
        if current > self.MAX_CURRENT:
            raise PowerSupplyCS410VError("Can't set current higher than "+nfu.auto_unit(self.MAX_CURRENT, "A")+".")
        elif current < self.MIN_CURRENT:
            raise PowerSupplyCS410VError("Can't set current lower than "+nfu.auto_unit(self.MIN_CURRENT, "A")+".")
        return
        

    def get_current(self):
        """Read current (A)."""
        retval = self.device_handle.query("source:current:fix?")
        return float(retval)



    def set_current(self, current):
        """Set current (A)."""
        self.check_current(current)
        self.device_handle.write("source:current:fix "+str(current)+"A")
        return



class PowerSupplyCS410VError(nfu.LabMasterError):
    """Errors raised by the CS410V superconducting magnet power supply."""
    pass
    
    
####################################################################################################################################################################################################################
