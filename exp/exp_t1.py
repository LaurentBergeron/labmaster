""" 
Hahn echo experiment. 
"""

# Base modules
import numpy as np 
import scipy.constants as cst

# Home modules
import _shared_
from mod.main import *
from _sequences_ import *


def sequence(lab, params):
    lab.awg.default_delay["1"] = params.tau.v
    START = params.phase_cycle.v+params.phase_start.v+"/2,"
    END = params.phase_start.v+"/2,"
     
    _shared_.pb_master_trigger(lab)
    _shared_.prepare(lab, params)
    
    lab.free_evolution_time = 0
    
    if DELAY_BEFORE:
        lab.delay(params.tau.v)
    lab.awg.string_sequence(1, START)
    lab.awg.string_sequence(1, END)
    if not DELAY_BEFORE:
        lab.delay(params.tau.v)
    
    params.time_axis.value[params.loops.i*params.tau.size()+params.tau.i] = lab.free_evolution_time
    
    lab.pb.turn_on("scope_trig", time_on=ms, rewind="start")
    _shared_.readout(lab, params)
    return 

from exp_nmr import launch, get_data, create_plot, update_plot, fit_exp
    
    
    
    
    
    
    
    
    
    
    
    
    
