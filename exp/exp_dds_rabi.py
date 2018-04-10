## Base modules
import numpy as np 

## Home modules
from . import _shared_functions_ 
from mod.main import *
import exp.exp_dds_nmr

launch = exp.exp_dds_nmr.launch
get_data = exp.exp_dds_nmr.get_data

def pre_scan(lab, params, fig, data, ID):
    lab.dds.clear_channel_names()
    lab.dds.add_channel('Xshutter', 10)
    lab.dds.add_channel('Yshutter', 11)
    lab.dds.add_channel('1047shutter', 12)
    lab.dds.add_channel('binA', 7)
    lab.dds.add_channel('binB', 8)
    lab.dds.add_channel('scope_trig', 1)
    
    lab.dds.default_channel = 'RF1'
    lab.dds.set_default_pulse('RF1', amp=params.dds_amp.value, freq=params.dds_freq.value)
    return 
    


def sequence(lab, params, fig, data, ID):
    #_shared_functions_.pb_master_trigger(lab)
    _shared_functions_.prepare(lab, params)
    lab.dds.turn_on('scope_trig', duration=us, rewind=True)

    lab.dds.pulse(length=params.pi_len.v)
        
    _shared_functions_.readout(lab, params)
    
    return     
    
def create_plot(lab, params, fig, data, ID):
    plotting.createfig_XY(fig, '$\pi$', 'data', 1, '--o')
    plotting.add_lines(fig, 1, 'k--')
    return 
    
def update_plot(lab, params, fig, data, ID):
    plotting.updatefig_XY(fig, params.pi_len.value, data, line_index=0)
    popt = out(lab, params, fig, data, ID)
    if popt is not None:
        xdata = params.pi_len.value[1:][np.isfinite(data[1:])]
        ydata = fit_sin(params.pi_len.value[1:], *popt)[np.isfinite(data[1:])]
        plotting.updatefig_XY(fig, xdata, ydata, line_index=1)
        fig.suptitle('$T$ = '+auto_unit(popt[1], 's', decimal=3)+'\n $A$ = %3.0f'%popt[0])

    return

    

    
def fit_sin(xdata, A, period): 
    """ sine for fitting """
    return A*np.sin(2*np.pi*xdata/period)

    
def out(lab, params, fig, data, ID):
    return fitting.fit(fit_sin, params.pi_len.value[1:], data[1:])
    
    
    