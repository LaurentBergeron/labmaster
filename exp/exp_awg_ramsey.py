## Base modules
import numpy as np 
import scipy.constants as cst

## Home modules
from . import _shared_
from mod.main import *
from . import _sequences_

from exp.exp_nmr import sequence, launch, get_data, create_plot


def pre_scan(lab, params, fig, data, ID):
    lab.pb.add_channel('master_trig', 1)
    lab.pb.add_channel('Xshutter', 2)
    lab.pb.add_channel('binA', 10)
    lab.pb.add_channel('binB', 11)
    lab.pb.add_channel('scope_trig', 17)

    lab.awg.default_channel = '1'
    lab.awg.set_default_pulse(length=params.pi_len.v, amp=params.awg_amp.v, freq=params.awg_freq.v)
    lab.awg.set_sample_rate(params.awg_sample_rate.v)
    lab.awg.set_trigger_mode('trig')

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
            print(xdata)
            print(ydata)
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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
