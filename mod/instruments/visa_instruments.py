__author__ =  "Adam DeAbreu <adeabreu@sfu.ca>, Laurent Bergeron <laurent.bergeron4@gmail.com>"

# Base modules
import numpy as np
import visa as vi

# Homemade modules
from ..classes import Instrument
from ..units import *
from .. import not_for_user     
nfu = not_for_user
        
class Default_visa(Instrument):
    """
    """
    def __init__(self, name, parent, visa_ID):
        Instrument.__init__(self, name, parent) 
        rm = vi.ResourceManager()
        self.device_handle = rm.open_resource(visa_ID)
        print self.device_handle.query("*IDN?")
        return
        
    def abort(self):
        return

    def write(self, input):
        return self.device_handle.write(input)

    def query(self, input):
        return self.device_handle.query(input)

    def read(self, input):
        return self.device_handle.query(input)
    
    def close(self):
        return self.device_handle.close()
            
####################################################################################################################################################################################################################

class Laser_ITC4001(Instrument):
    """
    # need things to set the things in the itc
    """
    def __init__(self, name, parent, visa_ID):
        Instrument.__init__(self, name, parent) 
        rm = vi.ResourceManager()
        self.device_handle = rm.open_resource(visa_ID)
        self.temp    = float(self.device_handle.query("source2:temp?"))
        self.curr    = float(self.device_handle.query("source:current?"))
        
        self.MAX_CURR = 200*mA
        self.MIN_CURR = 0
        self.MAX_TEMP = 40 # Celcius
        self.MIN_TEMP = 30 # Celcius
        
        self.meas_mode = "curr"
        return 
        
    def abort(self):
        return
        
    def check_temperature(self, temp):
        if temp > self.MAX_TEMP:
            self.beep()
            raise LaserITC4001Error, "Can't set temperature higher than "+str(self.MAX_TEMP)+" Celcius."
        elif temp < self.MIN_TEMP:
            self.beep()
            raise LaserITC4001Error, "Can't set temperature lower than "+str(self.MIN_TEMP)+" Celcius."
        return
        
    def check_current(self, curr):
        if curr > self.MAX_CURR:
            self.beep()
            raise LaserITC4001Error, "Can't set current higher than "+str(self.MAX_CURR*1e3)+" mA."
        elif curr < self.MIN_CURR:
            self.beep()
            raise LaserITC4001Error, "Can't set current lower than "+str(self.MIN_CURR*1e3)+" mA."
        return
    
    def get_temp(self):
        return float(self.device_handle.query("meas:temp?"))
    
    def get_current(self):
        return float(self.device_handle.query("meas:curr?"))
    
    def measure(self):
        retval = self.device_handle.query("read?")
        return float(retval)
        
    def set_temp(self, temp):
        self.check_temperature(temp)
        self.temp = temp
        self.device_handle.write("source2:temp "+str(temp))
        return
        
    def set_current(self, curr):
        self.check_current(curr)
        self.curr = curr
        self.device_handle.write("source:curr "+str(curr))
        return
        
    def set_meas_mode(self, tomeasure):
        self.device_handle.write("conf:"+tomeasure)
        self.meas_mode = tomeasure
        return
    
    def beep(self):
        retval = self.device_handle.write("SYST:BEEP:IMM")
        return "BEEP!"

    def close(self):
        return self.device_handle.close()

class LaserITC4001Error(nfu.LabMasterError):
    pass
        
####################################################################################################################################################################################################################

class Lockin_5210(Instrument):
    """
    # Need some functions to set all the lockin parameters
    """
    def __init__(self, name, parent, visa_ID):
        Instrument.__init__(self, name, parent) 
        rm = vi.ResourceManager()
        self.device_handle = rm.open_resource(visa_ID)
        self.meas_mode = 'Y'
        return
    
    def abort(self):
        return

    def set_meas_mode(self, meas_mode):
        self.meas_mode = meas_mode
        return

    def measure(self):
        retval = self.device_handle.query(self.meas_mode)
        return float(retval)
        
    def write_arb(self, towrite):
        try:
            retval = self.device_handle.write(towrite)
            retval = retval[1].value
        except vi.VisaIOError:
            retval = -1
        return retval

    def query_arb(self, toquery):
        try:
            retval = self.device_handle.query(toquery)
        except vi.VisaIOError:
            retval = -1
        return retval

    def read_arb(self, toread):
        try:
            retval = self.device_handle.read(toread)
        except vi.VisaIOError:
            retval = -1
        return retval

    def close(self):
        return self.device_handle.close()


class Lockin5210Error(nfu.LabMasterError):
    pass
        
####################################################################################################################################################################################################################

class Sig_gen_E8257D(Instrument):
    """
    authors : Adam DeAbreu <adeabreu@sfu.ca>, Laurent Bergeron <laurent.bergeron4@gmail.com>
    """
    def __init__(self, name, parent, visa_ID):
        Instrument.__init__(self, name, parent) 
        rm = vi.ResourceManager()
        self.device_handle = rm.open_resource(visa_ID)
        return

    def abort(self):
        return

    def get_freq(self):
        retval = self.device_handle.query("source:freq:fix?")
        return float(retval)

    def get_amp(self):
        retval = self.device_handle.query("source:power:alc:level?")
        return float(retval)


    def set_freq(self, freq):
        """ """
        freq = str(freq/1e9)
        self.device_handle.write("source:freq:fix "+freq+"GHZ")
        return

    def set_amp(self, amp):
        amp = str(amp)
        self.device_handle.write("source:power:alc:level "+amp+"DBM")
        return

    def close(self):
        return self.device_handle.close()

class SigGenE8257D(nfu.LabMasterError):
    pass
    
    
####################################################################################################################################################################################################################

class Sig_gen_SRS(Instrument):
    """
    """
    def __init__(self, name, parent, visa_ID):
        Instrument.__init__(self, name, parent)
        rm = vi.ResourceManager()
        self.device_handle = rm.open_resource(visa_ID)
        return

    def abort(self):
        return
        
    def get_freq(self):
        retval = self.device_handle.query("FREQ?")
        return float(retval)

    def set_freq(self, freq):
        freq = str(freq)
        self.device_handle.write("FREQ " + freq)
        return


    def close(self):
        return self.device_handle.close()

class SigGenSRSError(nfu.LabMasterError):
    pass
        
####################################################################################################################################################################################################################
