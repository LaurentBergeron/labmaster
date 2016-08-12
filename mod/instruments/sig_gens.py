"""
Definition of signal generator Instrument classes.

Current classes: 
- Sig_gen_E8257D 
- Sig_gen_SRS
"""
__author__ =  "Adam DeAbreu <adeabreu@sfu.ca>, Laurent Bergeron <laurent.bergeron4@gmail.com>"

# Base modules
import numpy as np
import visa as vi

# Homemade modules
from default_visa import Default_visa
from ..units import *
from .. import not_for_user     
nfu = not_for_user



class Sig_gen_E8257D(Default_visa):
    """Class allowing to control a E8257D signal generator."""
    
    def __init__(self, name, parent, visa_ID):
        """
        Inherit from Default_visa and open a VISA device handle.
        - name: Name to give to the instrument.
        - parent: A reference to the lab instance hosting the instrument.
        - visa_ID: Connection address. 
        """
        Default_visa.__init__(self, name, parent, visa_ID) 
        self.MIN_FREQ = 100*kHz
        self.MAX_FREQ = 50*GHz
        self.MIN_AMP = -20 ##dBm
        self.MAX_AMP = 12 ##dBm
        print 'connected to E8257D signal generator.'
        return
        
    def check_freq(self, freq):
        """Check if input frequency satisfies minimum and maximum values."""
        if freq > self.MAX_FREQ:
            raise SigGenE8257DError, "Can't set freq higher than "+nfu.auto_unit(self.MAX_FREQ, "Hz")+"."
        elif freq < self.MIN_FREQ:
            raise SigGenE8257DError, "Can't set freq lower than "+nfu.auto_unit(self.MIN_FREQ, "Hz")+"."
        return
        
    def check_amp(self, amp):
        """Check if input amplitude satisfies minimum and maximum values."""
        if amp > self.MAX_AMP:
            raise SigGenE8257DError, "Can't set amp higher than "+nfu.auto_unit(self.MAX_AMP, "dBm")+"."
        elif amp < self.MIN_AMP:
            raise SigGenE8257DError, "Can't set amp lower than "+nfu.auto_unit(self.MIN_AMP, "dBm")+"."
        return

    def get_freq(self):
        """Read frequency (Hz)."""
        retval = self.device_handle.query("source:freq:fix?")
        return float(retval)

    def get_amp(self):
        """Read amplitude (dBm)."""
        retval = self.device_handle.query("source:power:alc:level?")
        return float(retval)


    def set_freq(self, freq):
        """Set signal frequency (Hz)."""
        self.check_freq(freq)
        self.device_handle.write("source:freq:fix "+str(freq/1e9)+"GHZ")
        return

    def set_amp(self, amp):
        """Set signal amplitude (dBm)."""
        self.check_amp(amp)
        self.device_handle.write("source:power:alc:level "+str(amp)+"DBM")
        return


class SigGenE8257DError(nfu.LabMasterError):
    """Errors raised by the E8257D signal generator."""
    pass
    
    
####################################################################################################################################################################################################################

class Sig_gen_SRS(Default_visa):
    """Class allowing to control a SRS signal generator."""
    
    def __init__(self, name, parent, visa_ID):
        """
        Inherit from Default_visa and open a VISA device handle.
        - name: Name to give to the instrument.
        - parent: A reference to the lab instance hosting the instrument.
        - visa_ID: Connection address. 
        """
        Default_visa.__init__(self, name, parent, visa_ID) 
        print 'connected to SRS signal generator.'
        return
        
    def get_freq(self):
        """Read signal frequency (Hz)."""
        retval = self.device_handle.query("FREQ?")
        return float(retval)

    def set_freq(self, freq):
        """Set signal frequency (Hz)."""
        freq = str(freq)
        self.device_handle.write("FREQ " + freq)
        return


class SigGenSRSError(nfu.LabMasterError):
    """Errors raised by the SRS signal generator."""
    pass
        
####################################################################################################################################################################################################################
