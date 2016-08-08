""" 
Rabi experiment.
"""

# Base modules
import numpy as np 
import scipy.constants as cst

# Home modules
import _shared_ 
from mod.main import *

from exp_nmr import launch, get_data

def sequence(lab, params, fig, data, ID):
    _shared_.pb_master_trigger(lab)
    _shared_.prepare(lab, params)
    lab.pb.turn_on("scope_trig", time_on=us, rewind="start")

    lab.awg.pulse(length=params.pi_len.v)
        
    _shared_.readout(lab, params)
    
    return     
    
def create_plot(lab, params, fig, data, ID):
    plotting.createfig_XY(fig, "$\pi$", "data", 1, "--o")
    plotting.add_lines(1, "k--")
    return 
    
def update_plot(lab, params, fig, data, ID):
    plotting.updatefig_XY(fig, params.pi_len.value, data, line_index=0)
    out = None
    popt = plotting.update_curve_fit(fig, fit_sin, params.pi_len.value[1:], data[1:], nargs = 2, line_index = 1)
    if popt is not None:
        fig.suptitle("$T$ = "+auto_unit(popt[1], "s", decimal=3)+"\n $A$ = %3.0f"%popt[0])

        out = popt[1]

    return out

    

    
def fit_sin(xdata, A, period): 
    """ sine for fitting """
    return A*np.sin(2*np.pi*xdata/period)

    
def out(lab, params, fig, data, ID):
    return update_plot(fig, params, data)