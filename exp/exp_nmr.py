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
    
    lab.awg.string_sequence(1, START)
    for _ in np.arange(params.loops.v):
        lab.awg.string_sequence(1, LOADED_SEQUENCE)
    lab.awg.string_sequence(1, END)
    params.time_axis.value[params.loops.i*params.tau.size()+params.tau.i] = lab.free_evolution_time
    
    lab.pb.turn_on("scope_trig", time_on=ms, rewind="start")
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
    ### 2D with phase cycling
    if data.ndim == 3 and params.phase_cycle.size()==2: 
        pass
    ### 1D with phase cycling
    elif data.ndim == 2 and params.phase_cycle.size()==2: 
        plotting.createfig_XY(fig, "Free evolution time (s)", "countB - countA", 3, "--o")
    ### no phase cycling
    else: 
        plotting.createfig_XY(fig, "Free evolution time (s)", "countB - countA", 1, "--o")
        
    fig.axes[0].plot([], 'k--')
    return
    
def update_plot(fig, params, data):
    out = None, None
    ### 2D with phase cycling
    if data.ndim == 3 and params.phase_cycle.size()==2: 
        pass
    ### 1D with phase cycling
    elif data.ndim == 2 and params.phase_cycle.size()==2: 
        cycle1 = data[:,0]
        cycle2 = data[:,1]
        cyclediff = cycle1-cycle2
        plotting.updatefig_XY(fig, params.time_axis.value, cycle1, line_index=0)
        plotting.updatefig_XY(fig, params.time_axis.value, cycle2, line_index=1)
        plotting.updatefig_XY(fig, params.time_axis.value, cyclediff, line_index=2)
        
        popt = plotting.update_curve_fit(fig, fit_exp, params.time_axis.value[1:], cyclediff[1:], line_index = 3, nargs = 2, initial_guess=[cyclediff[1], 10])
        if popt is not None:
            fig.suptitle("$T_2$ = "+auto_unit(popt[1], "s", decimal=3)+"\n $A$ = %3.0f"%popt[0])
            out = popt[0], popt[1]
            
    ### no phase cycling
    else: 
        plotting.updatefig_XY(fig, params.time_axis.value, data, line_index=0)


    return out

    
        
def fit_exp(xdata, A, decay_tau): 
    """ decaying exponential for fitting """
    return A*np.exp(-1.*(xdata)/decay_tau)
    
    
    
    
    
def out(fig, lab, params):
    return update_plot(fig, params, data)
    
    
    
    
    
    
    
    
    
    
    
