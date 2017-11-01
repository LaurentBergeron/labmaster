## Base modules
import numpy as np 
import scipy.constants as cst

## Home modules
from . import _shared_
from mod.main import *
from ._sequences_ import *

from .exp_nmr import launch, get_data, create_plot, fit_exp, out
from . import exp_nmr

def pre_scan(lab, params, fig, data, ID):
    lab.pb.add_channel('master_trig', 1)
    lab.pb.add_channel('Xshutter', 2)
    lab.pb.add_channel('binA', 10)
    lab.pb.add_channel('binB', 11)
    lab.pb.add_channel('scope_trig', 17)
    
    exp_nmr.PHASE_CYCLING = PHASE_CYCLING ## global variable needs to be shared with nmr.py to use its functions.
    
    lab.awg.default_channel = '1'
    lab.awg.set_default_pulse(length=params.pi_len.v, amp=params.awg_amp.v, freq=params.awg_freq.v)
    lab.awg.set_sample_rate(params.awg_sample_rate.v)
    lab.awg.set_trigger_mode('trig')

    if PHASE_CYCLING:
        params.phase_cycle.sweep_dim = params.get_dimension() + 1
        params.phase_cycle.value = ['','-']
    else:
        params.phase_cycle.value = ''
    
    params.time_axis.sweep_dim = 0
    params.time_axis.value = np.zeros(params.tau.get_size())
    return

def sequence(lab, params, fig, data, ID):
    lab.awg.set_default_pulse(delay=params.tau.v)
    START = params.phase_cycle.v+params.phase_start.v+'/2,'
    END = params.phase_start.v+'/2,'
     
    _shared_.pb_master_trigger(lab)
    _shared_.prepare(lab, params)
    
    lab.free_evolution_time = 0
    
    if DELAY_BEFORE_PULSE:
        lab.delay(params.tau.v)
    lab.awg.string_sequence(START)
    lab.awg.string_sequence(END)
    if not DELAY_BEFORE_PULSE:
        lab.delay(params.tau.v)
    
    params.time_axis.value[params.tau.i] = lab.free_evolution_time
    
    lab.pb.turn_on('scope_trig', duration=ms, rewind=True)
    _shared_.readout(lab, params)
    return 


def update_plot(lab, params, fig, data, ID):
    saved = time.time()
    ##------------------------- 2D with phase cycling ----------------------------##
    if data.ndim == 3 and PHASE_CYCLING: 
        pass
    ##------------------------- 1D with phase cycling ----------------------------##
    elif data.ndim == 2 and PHASE_CYCLING: 
        cycle1 = data[:,0]
        cycle2 = data[:,1]
        cyclediff = cycle1-cycle2
        plotting.updatefig_XY(fig, params.time_axis.value, cycle1, line_index=0)
        plotting.updatefig_XY(fig, params.time_axis.value, cycle2, line_index=1)
        plotting.updatefig_XY(fig, params.time_axis.value, cyclediff, line_index=2)
        
        popt = out(lab, params, fig, data, ID)
        if popt is not None:
            xdata = params.time_axis.value[1:][np.isfinite(cyclediff[1:])]
            ydata = fit_exp(params.time_axis.value[1:], *popt)[np.isfinite(cyclediff[1:])]
            plotting.updatefig_XY(fig, xdata, ydata, line_index=3)
            fig.suptitle('$T_1$ = '+auto_unit(popt[1], 's', decimal=3)+'\n $A$ = %3.0f'%popt[0])
    ##------------------------- no phase cycling ----------------------------##
    else: 
        plotting.updatefig_XY(fig, params.time_axis.value, data, line_index=0)
        popt = out(lab, params, fig, data, ID)
        if popt != None:
            xdata = params.time_axis.value[1:][np.isfinite(data[1:])]
            ydata = fit_exp(params.time_axis.value[1:], *popt)[np.isfinite(data[1:])]
            plotting.updatefig_XY(fig, xdata, ydata, line_index=1)
            fig.suptitle('$T_1$ = '+auto_unit(popt[1], 's', decimal=3)+'\t\t $A$ = %3.0f'%popt[0], fontsize=20)

    print((time.time()-saved))
    return
    
    
    
    
    
    
    
    
    
