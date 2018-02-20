## Base modules
import numpy as np 

## Home modules
from . import _shared_ 
from mod.main import *


def pre_scan(lab, params, fig, data, ID):
    lab.dds.add_channel('scope_trig', 4)
    
    lab.dds.default_rf_channel = 'RF1'
    lab.dds.set_default_pulse('RF1', amp=params.amp.value, freq=params.freq.value)
    lab.dds.reset_registers()
    return 
    


def sequence(lab, params, fig, data, ID):
    lab.dds.turn_on('scope_trig', duration=us, rewind=True)
    lab.dds.pulse(length=.5*params.pi_len.v)
    lab.delay(params.pi_len.v)
    lab.dds.pulse(length=params.pi_len.v)
    lab.delay(params.pi_len.v)
    lab.dds.pulse(length=.5*params.pi_len.v)
    return     
    
    
    
    
    
def launch(lab, params, fig, data, ID):
    lab.dds.start()
    return
    
def get_data(lab, params, fig, data, ID):
    # print('get_data')
    return