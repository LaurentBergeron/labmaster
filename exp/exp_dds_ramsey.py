## Base modules
import numpy as np 
import scipy.constants as cst
import pdb

## Home modules
from . import _shared_
from mod.main import *
from . import _sequences_
import exp.exp_dds_nmr

sequence = exp.exp_dds_nmr.sequence
launch = exp.exp_dds_nmr.launch
get_data = exp.exp_dds_nmr.get_data
create_plot = exp.exp_dds_nmr.create_plot


def pre_scan(lab, params, fig, data, ID):
    lab.dds.clear_channel_names()
    lab.dds.add_channel('Xshutter', 10)
    lab.dds.add_channel('Yshutter', 11)
    lab.dds.add_channel('1047shutter', 12)
    lab.dds.add_channel('binA', 7)
    lab.dds.add_channel('binB', 8)
    lab.dds.add_channel('scope_trig', 1)

    lab.dds.default_channel = 'RF1'
    lab.dds.set_default_pulse('RF1', length=params.pi_len.v, amp=params.dds_amp.v, freq=params.dds_freq.v)
    
    exp.exp_dds_nmr.PHASE_CYCLING = PHASE_CYCLING ## global variable needs to be shared with nmr.py to use its functions.

    if PHASE_CYCLING:
        params.phase_cycle.sweep_dim = params.get_dimension() + 1
        params.phase_cycle.value = ['','-']
    else:
        params.phase_cycle.value = ''

    params.sequence.value = _sequences_.RAMSEY

    params.loops.value = 1 ## required to share the same sequence as exp_nmr.py
    
    params.time_axis.sweep_dim = 0
    params.time_axis.value = np.zeros(params.tau.get_size())

    return

    
    
    
def update_plot(lab, params, fig, data, ID):
    ##------------------------- with phase cycling ----------------------------##
    if data.ndim == 2 and PHASE_CYCLING: 
        cycle1 = data[:,0]
        cycle2 = data[:,1]
        cyclediff = cycle1-cycle2
        plotting.updatefig_XY(fig, params.time_axis.value, cycle1, line_index=0)
        plotting.updatefig_XY(fig, params.time_axis.value, cycle2, line_index=1)
        plotting.updatefig_XY(fig, params.time_axis.value, cyclediff, line_index=2)
        
    ##------------------------- no phase cycling ------------------------------##
    else: 
        plotting.updatefig_XY(fig, params.time_axis.value, data, line_index=0)
        popt = out(lab, params, fig, data, ID)
        if popt is not None:
            xdata = params.time_axis.value[1:][np.isfinite(data[1:])]
            ydata = fit_sin(params.time_axis.value[1:], *popt)[np.isfinite(data[1:])]
            plotting.updatefig_XY(fig, xdata, ydata, line_index=1)
            fig.suptitle('$T$ = '+auto_unit(popt[1], 's', decimal=3)+'\n $A$ = %3.0f'%popt[0])

    return

    
def fit_sin(xdata, A, period): 
    """ sine for fitting """
    return A*np.sin(2*np.pi*xdata/period)
        
    
    
def out(lab, params, fig, data, ID):
    if PHASE_CYCLING: 
        cycle1 = data[:,0]
        cycle2 = data[:,1]
        fitdata = cycle1-cycle2
    ##--------------------------- no phase cycling -------------------------------##
    else: 
        fitdata = data
    return fitting.fit(fit_sin, params.time_axis.value[1:], fitdata[1:])
    
    
    
    
    
    
    
    
    
    
    
    
    
    
