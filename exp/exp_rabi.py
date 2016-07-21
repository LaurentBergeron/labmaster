""" 
Rabi experiment.
"""

# Base modules
import numpy as np 
import scipy.constants as cst

# Home modules
import _shared_ 
from mod.main import *


def sequence(lab, params):

    _shared_.pb_master_trigger(lab)
    _shared_.prepare(lab, params)
    lab.pb.turn_on("scope_trig", time_on=us, rewind="start")

    lab.awg.pulse(1, length=params.pi_len.v)
        
    _shared_.readout(lab, params)
    
    return 
    
def launch(lab, params):
    lab.usb_counter.clear(0)
    lab.usb_counter.clear(1)
    lab.awg.initiate_generation(1)
    lab.pb.start()
    return

def get_data(lab, params):      
    A = lab.usb_counter.read(0)
    B = lab.usb_counter.read(1)
    return B-A
    
def create_plot(fig, params, data):
    plotting.createfig_XY("$\pi$", "data", 1, "--o")
    return 
    
def update_plot(fig, params, data):
    plotting.updatefig_XY(fig, params.pi_len.value, data, line_index=0)
    return

    
