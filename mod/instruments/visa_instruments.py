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
        return
    
    def abort(self):
        return
        
    def auto_phase(self):
        self.device_handle.write('AQN')
        return

    def get_X(self):
        retval = self.device_handle.query('X')
        return float(retval)
        
    def get_Y(self):
        retval = self.device_handle.query('Y')
        return float(retval)
        
    def get_XY(self):
        X, Y = self.device_handle.query('XY').split(",")
        return float(X), float(Y)
        
    def get_magnitude(self):
        retval = self.device_handle.query('MAG')
        return float(retval)
        
    def get_phase(self):
        retval = self.device_handle.query('PHA')
        return float(retval)
        
    def get_magnitude_and_phase(self):
        mag, phase = self.device_handle.query('MP').split(",")
        return float(mag), float(phase)/1000.0

    def get_time_constant(self):
        code = self.device_handle.query('TC')
        return self.time_cst_chart.get(str(int(code)), "failed")

    def get_sensitivity(self):
        code = self.device_handle.query('SEN')
        return self.sensitivity_chart.get(str(int(code)), "failed")
        
    def set_time_constant(self, time_cst):
        code = None
        for key, value in self.time_cst_chart.items():
            if value==time_cst:
                code = key
        if code==None:
            raise Lockin5210Error, "Requested time constant not available."
        return self.device_handle.write('TC '+code)

    def set_sensitivity(self, sensitivity):
        code = None
        for key, value in self.sensitivity_chart.items():
            if value==sensitivity:
                code = key
        if code==None:
            raise Lockin5210Error, "Requested sensitivity not available."
        return self.device_handle.write('SEN '+code)
        
        
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
        self.MIN_FREQ = 100*kHz
        self.MAX_FREQ = 50*GHz
        self.MIN_AMP = -20 ##dBm
        self.MAX_AMP = 12 ##dBm
        return

    def abort(self):
        return
        
    def check_freq(self, freq):
        if freq > self.MAX_FREQ:
            raise SigGenE8257DError, "Can't set freq higher than "+nfu.auto_unit(self.MAX_FREQ, "Hz")+"."
        elif freq < self.MIN_FREQ:
            raise SigGenE8257DError, "Can't set freq lower than "+nfu.auto_unit(self.MIN_FREQ, "Hz")+"."
        return
        
    def check_amp(self, amp):
        if amp > self.MAX_AMP:
            raise SigGenE8257DError, "Can't set amp higher than "+nfu.auto_unit(self.MAX_AMP, "dBm")+"."
        elif amp < self.MIN_AMP:
            raise SigGenE8257DError, "Can't set amp lower than "+nfu.auto_unit(self.MIN_AMP, "dBm")+"."
        return

    def get_freq(self):
        retval = self.device_handle.query("source:freq:fix?")
        return float(retval)

    def get_amp(self):
        retval = self.device_handle.query("source:power:alc:level?")
        return float(retval)


    def set_freq(self, freq):
        self.check_freq(freq)
        self.device_handle.write("source:freq:fix "+str(freq/1e9)+"GHZ")
        return

    def set_amp(self, amp):
        self.check_amp(amp)
        self.device_handle.write("source:power:alc:level "+str(amp)+"DBM")
        return

    def close(self):
        return self.device_handle.close()

class SigGenE8257DError(nfu.LabMasterError):
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
