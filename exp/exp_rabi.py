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
    
from exp_nmr import launch, get_data
    
def create_plot(fig, params, data):
    plotting.createfig_XY(fig, "$\pi$", "data", 1, "--o")
    return 
    
def update_plot(fig, params, data):
    plotting.updatefig_XY(fig, params.pi_len.value, data, line_index=0)
    return

    
