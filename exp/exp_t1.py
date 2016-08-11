"""
T1.
"""

## Base modules
import numpy as np 
import scipy.constants as cst

## Home modules
import _shared_
from mod.main import *
from _sequences_ import *

from exp_nmr import launch, get_data, create_plot, fit_exp

def sequence(lab, params, fig, data, ID):
    lab.awg.set_default_params(delay=params.tau.v)
    START = params.phase_cycle.v+params.phase_start.v+"/2,"
    END = params.phase_start.v+"/2,"
     
    _shared_.pb_master_trigger(lab)
    _shared_.prepare(lab, params)
    
    lab.free_evolution_time = 0
    
    if DELAY_BEFORE_PULSE:
        lab.delay(params.tau.v)
    lab.awg.string_sequence(START)
    lab.awg.string_sequence(END)
    if not DELAY_BEFORE_PULSE:
        lab.delay(params.tau.v)
    
    params.time_axis.value[params.loops.i*params.tau.size()+params.tau.i] = lab.free_evolution_time
    
    lab.pb.turn_on("scope_trig", time_on=ms, rewind="start")
    _shared_.readout(lab, params)
    return 


def update_plot(lab, params, fig, data, ID):
    ##------------------------- 2D with phase cycling ----------------------------##
    if data.ndim == 3 and params.phase_cycle.get_size()==2: 
        pass
    ##------------------------- 1D with phase cycling ----------------------------##
    elif data.ndim == 2 and params.phase_cycle.get_size()==2: 
        cycle1 = data[:,0]
        cycle2 = data[:,1]
        cyclediff = cycle1-cycle2
        plotting.updatefig_XY(fig, params.time_axis.value, cycle1, line_index=0)
        plotting.updatefig_XY(fig, params.time_axis.value, cycle2, line_index=1)
        plotting.updatefig_XY(fig, params.time_axis.value, cyclediff, line_index=2)
        
        popt = out(lab, params, fig, data, ID)
        if popt is not None:
            plotting.updatefig_XY(fig, params.time_axis.value[1:], fit_exp(params.time_axis.value[1:], *popt), line_index=3)
            fig.suptitle("$T_1$ = "+auto_unit(popt[1], "s", decimal=3)+"\n $A$ = %3.0f"%popt[0])
    ##------------------------- no phase cycling ----------------------------##
    else: 
        plotting.updatefig_XY(fig, params.time_axis.value, data, line_index=0)


    return
    
def out(lab, params, fig, data, ID):
    cycle1 = data[:,0]
    cycle2 = data[:,1]
    cyclediff = cycle1-cycle2
    return fitting.fit(fit_exp, params.time_axis.value[1:], cyclediff[1:], initial_guess=[cyclediff[1], 10])
    
    
    
    
    
    
    
    
    
    
    
