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

from exp.exp_nmr import sequence, launch, get_data, create_plot
import exp.exp_nmr
exp.exp_nmr.LOADED_SEQUENCE = RAMSEY

def update_plot(lab, params, fig, data, ID):
    out = None
    ### with phase cycling
    if data.ndim == 2 and params.phase_cycle.size()==2: 
        cycle1 = data[:,0]
        cycle2 = data[:,1]
        cyclediff = cycle1-cycle2
        plotting.updatefig_XY(fig, params.time_axis.value, cycle1, line_index=0)
        plotting.updatefig_XY(fig, params.time_axis.value, cycle2, line_index=1)
        plotting.updatefig_XY(fig, params.time_axis.value, cyclediff, line_index=2)
        
    ### no phase cycling
    else: 
        plotting.updatefig_XY(fig, params.time_axis.value, data, line_index=0)
        
        popt = plotting.update_curve_fit(fig, fit_sin, params.time_axis.value[1:], data[1:], nargs = 2, line_index = 1)
        if popt is not None:
            fig.suptitle("$T$ = "+auto_unit(popt[1], "s", decimal=3)+"\n $A$ = %3.0f"%popt[0])

            out = popt[1]

    return out

    
def fit_sin(xdata, A, period): 
    """ sine for fitting """
    return A*np.sin(2*np.pi*xdata/period)
        
    
    
def out(lab, params, fig, data, ID):
    return update_plot(fig, params, data)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
