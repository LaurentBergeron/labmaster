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
    

def update_plot(fig, params, data):
    out = None
    ### 2D with phase cycling
    if data.ndim == 3 and params.phase_cycle.size()==2: 
        pass
    ### 1D with phase cycling
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

    if data.ndim == 2 and params.phase_cycle.size()==2:
        if params.phase_cycle.v=="-":
            popt = plotting.update_curve_fit(fig, fit_exp, params.time_axis.value[1:], cyclediff[1:], line_index = 3, nargs = 2, initial_guess=[cyclediff[1], 10])
            if popt is not None:
                fig.suptitle("$T_2$ = "+nfu.auto_unit(popt[1], "s", decimal=3)+"\n $A$ = %3.0f"%popt[0])
                out = popt[0], popt[1]

    return out

    
        
def fit_exp(xdata, A, decay_tau): 
    """ decaying exponential for fitting """
    return A*np.exp(-1.*(xdata)/decay_tau)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
