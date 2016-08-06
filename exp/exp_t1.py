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


from exp_nmr import launch, get_data, create_plot, fit_exp

def sequence(lab, params, fig, data, ID):
    lab.awg.default_delay["1"] = params.tau.v
    START = params.phase_cycle.v+params.phase_start.v+"/2,"
    END = params.phase_start.v+"/2,"
     
    _shared_.pb_master_trigger(lab)
    _shared_.prepare(lab, params)
    
    lab.free_evolution_time = 0
    
    if DELAY_BEFORE_PULSE:
        lab.delay(params.tau.v)
    lab.awg.string_sequence(1, START)
    lab.awg.string_sequence(1, END)
    if not DELAY_BEFORE_PULSE:
        lab.delay(params.tau.v)
    
    params.time_axis.value[params.loops.i*params.tau.size()+params.tau.i] = lab.free_evolution_time
    
    lab.pb.turn_on("scope_trig", time_on=ms, rewind="start")
    _shared_.readout(lab, params)
    return 


def update_plot(lab, params, fig, data, ID):
    out = None
    ### phase cycling
    elif data.ndim == 2 and params.phase_cycle.size()==2: 
        if params.phase_cycle.v=="-":
            cycle1 = data[:,0]
            cycle2 = data[:,1]
            cyclediff = cycle1-cycle2
            plotting.updatefig_XY(fig, params.time_axis.value, cycle1, line_index=0)
            plotting.updatefig_XY(fig, params.time_axis.value, cycle2, line_index=1)
            plotting.updatefig_XY(fig, params.time_axis.value, cyclediff, line_index=2)
    ### no phase cycling
    else: 
        plotting.updatefig_XY(fig, params.time_axis.value, data, line_index=0)

    if params.phase_cycle.size()==2:
        if params.phase_cycle.v=="-":
            popt = plotting.update_curve_fit(fig, fit_exp, params.time_axis.value[1:], cyclediff[1:], line_index = 3, nargs = 2, initial_guess=[cyclediff[1], 10])
            if popt is not None:
                fig.suptitle("$T_1$ = "+auto_unit(popt[1], "s", decimal=3)+"\n $A$ = %3.0f"%popt[0])
                out = popt[0], popt[1]

    return out
    
def out(lab, params, fig, data, ID):
    return update_plot(fig, params, data)
    
    
    
    
    
    
    
    
    
    
    
