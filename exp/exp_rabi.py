## Base modules
import numpy as np 

## Home modules
import _shared_ 
from mod.main import *

from exp_nmr import launch, get_data

def start(lab, params, fig, data, ID):
    lab.pb.add_channel('master_trig', 1)
    lab.pb.add_channel('Xshutter', 2)
    lab.pb.add_channel('binA', 10)
    lab.pb.add_channel('binB', 11)
    lab.pb.add_channel('scope_trig', 17)
    
    lab.awg.default_channel = '1'
    lab.awg.set_default_pulse(amp=params.awg_amp.value, freq=params.awg_freq.value)
    lab.awg.set_sample_rate(params.awg_sample_rate.value)
    lab.awg.set_trigger_mode('trig')
    return 
    


def sequence(lab, params, fig, data, ID):
    _shared_.pb_master_trigger(lab)
    _shared_.prepare(lab, params)
    lab.pb.turn_on('scope_trig', duration=us, rewind=True)

    lab.awg.pulse(length=params.pi_len.v)
        
    _shared_.readout(lab, params)
    
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
    
    
    