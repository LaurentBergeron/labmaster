""" 
Hahn echo experiment.
"""

# Base modules
import numpy as np 
import scipy.constants as cst

# Home modules
import _shared_
from mod.main import *

bcfwd = "tau, X/2, tau, Y, tau, -Y/2, tau, Y, tau, X/2, tau,"
bcrev = "tau, -X/2, tau, -Y, tau, Y/2, tau, -Y, tau, -X/2, tau,"
bclvl0 = bcfwd + bcrev
XYXY = "X, tau, Y, tau, X, tau, Y,"
YXYX = "Y, tau, X, tau, Y, tau, X,"
minusXYXY = "-X, tau, -Y, tau, -X, tau, -Y,"
minusYXYX = "-Y, tau, -X, tau, -Y, tau, -X,"

RAMSEY = "tau,"
HAHN = "tau, X, tau," # Hahn echo
PIBY2 = "tau, X/2, tau," 
XY16 = "tau/2,"+XYXY+"tau,"+YXYX+"tau,"+minusXYXY+"tau,"+minusYXYX+"tau/2,"
ACPMG_XSTART = "tau/2, Y, tau, -Y, tau/2,"
ACPMG_YSTART = "tau/2, X, tau, -X, tau/2,"
bclvl1 = bcfwd + bcfwd + bcrev + bcrev
bclvl2 = bcfwd + bclvl1 + bcfwd + bclvl1 + bcrev + bclvl1 + bcrev


def sequence(lab, params):
    lab.awg.default_delay["1"] = params.tau.v
    START = params.phase_cycle.v+params.phase_start.v+"/2,"
    END = params.phase_start.v+"/2,"
     
    _shared_.pb_master_trigger(lab)
    _shared_.prepare(lab, params)
    lab.free_evolution_time = 0
    lab.pb.turn_on("scope_trig", time_on=10*ms, rewind="start") 
    lab.awg.string_sequence(1, START)
    saved_time = lab.time_cursor
    lab.awg.string_sequence(1, HAHN, loops=1)#params.loops.v)
    one_loop_duration = lab.time_cursor - saved_time
    lab.awg.string_sequence(1, END)
    lab.delay(one_loop_duration*(params.loops.v-1))
    params.time_axis.value[params.loops.i*params.tau.size()+params.tau.i] = lab.free_evolution_time
    
    _shared_.readout(lab, params)
    raw_input("seq")
    return 

    
def launch(lab, params):
    lab.usb_counter.clear(0)
    lab.usb_counter.clear(1)
    lab.awg.initiate_generation(1)
    lab.pb.start()
    # lab.awg.print_loaded_sequence(1)
    return


def get_data(lab, params):     
    A = lab.usb_counter.read(0) 
    B = lab.usb_counter.read(1)
    # print "A:", A, "\tB:", B, "\tB-A:", B-A
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
        
    # fig.axes[0].plot([], 'k--')
    return
    
def update_plot(fig, params, data):
    ### 2D with phase cycling
    if data.ndim == 3 and params.phase_cycle.size()==2: 
        pass
    ### 1D with phase cycling
    elif data.ndim == 2 and params.phase_cycle.size()==2: 
        if params.phase_cycle.v=="-":
            plotting.updatefig_XY(fig, params.time_axis.value, data[:,0], line_index=0)
            plotting.updatefig_XY(fig, params.time_axis.value, data[:,1], line_index=1)
            plotting.updatefig_XY(fig, params.time_axis.value, data[:,0]-data[:,1], line_index=2)
    ### no phase cycling
    else: 
        plotting.updatefig_XY(fig, params.time_axis.value, data, line_index=0)
    
    # def fit_exp(xdata, A, decay_tau): ##decaying exponential
        # return A*np.exp(-1.*(xdata)/decay_tau)
    
    # plotting.update_curve_fit(fig, fit_exp, params.time_axis.value, data[:,0]-data[:,1], line_index = 3, nargs = 2)
    return

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
