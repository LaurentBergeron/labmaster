## Base modules
import numpy as np 
import scipy.constants as cst

## Home modules
from . import _shared_
from mod.main import *
import exp._sequences_ as _sequences_



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

    if PHASE_CYCLING:
        params.phase_cycle.sweep_dim = params.get_dimension() + 1
        params.phase_cycle.value = ['','-']
    else:
        params.phase_cycle.value = ''

    params.time_axis.sweep_dim = 0
    params.time_axis.value = np.zeros(params.tau.get_size()*params.loops.get_size())
    return

def sequence(lab, params, fig, data, ID):
    lab.dds.reset_registers() ## makes sure that only one frequency is used (a different frequency on delays will shift the phase)
    lab.dds.set_default_pulse(delay=params.tau.v)
    START = params.phase_cycle.v+params.phase_start.v+'/2,'
    END = params.phase_start.v+'/2,'
    
    lab.delay(10*us)
    # _shared_.pb_master_trigger(lab)
    _shared_.prepare(lab, params)
    
    lab.free_evolution_time = 0
    
    lab.dds.turn_on('scope_trig', duration=us, rewind=True)
    lab.dds.string_sequence(START)
    for _ in np.arange(params.loops.v):
        lab.dds.string_sequence(params.sequence.v)
    lab.dds.string_sequence(END)
    params.time_axis.value[params.loops.i*params.tau.get_size()+params.tau.i] = lab.free_evolution_time

    _shared_.readout(lab, params)
    return 

    
def launch(lab, params, fig, data, ID):
    lab.usb_counter.clear(0)
    lab.usb_counter.clear(1)
    lab.dds.start()
    input()
    return


def get_data(lab, params, fig, data, ID):     
    A = lab.usb_counter.read(0) 
    B = lab.usb_counter.read(1)
    return B-A
    

    
def create_plot(lab, params, fig, data, ID):
    ##------------------------- 2D with phase cycling ----------------------------##
    if data.ndim == 3 and PHASE_CYCLING: 
        pass
    ##------------------------- 1D with phase cycling ----------------------------##
    elif data.ndim == 2 and PHASE_CYCLING: 
        plotting.createfig_XY(fig, 'Free evolution time (s)', 'countB - countA', 3, '--o')
        plotting.add_lines(fig, 1, 'k--')
    ##--------------------------- no phase cycling -------------------------------##
    else: 
        plotting.createfig_XY(fig, 'Free evolution time (s)', 'countB - countA', 1, '--o')
        plotting.add_lines(fig, 1, 'k--')

    return
    
def update_plot(lab, params, fig, data, ID):
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
            fig.suptitle('$T_2$ = '+auto_unit(popt[1], 's', decimal=3)+'\t\t $A$ = %3.0f'%popt[0], fontsize=20)
            
    ##--------------------------- no phase cycling -------------------------------##
    else: 
        plotting.updatefig_XY(fig, params.time_axis.value, data, line_index=0)
        
        popt = out(lab, params, fig, data, ID)
        if popt is not None:
            xdata = params.time_axis.value[1:][np.isfinite(data[1:])]
            ydata = fit_exp(params.time_axis.value[1:], *popt)[np.isfinite(data[1:])]
            plotting.updatefig_XY(fig, xdata, ydata, line_index=1)
            fig.suptitle('$T_2$ = '+auto_unit(popt[1], 's', decimal=3)+'\t\t $A$ = %3.0f'%popt[0], fontsize=20)
    input()
    return 

    
        
def fit_exp(xdata, A, decay_tau): 
    """ decaying exponential for fitting """
    return A*np.exp(-1.*(xdata)/decay_tau)
    
    
    
    
    
def out(lab, params, fig, data, ID):
    ##------------------------- 2D with phase cycling ----------------------------##
    if data.ndim == 3 and PHASE_CYCLING: 
        pass
    ##------------------------- 1D with phase cycling ----------------------------##
    elif data.ndim == 2 and PHASE_CYCLING: 
        cycle1 = data[:,0]
        cycle2 = data[:,1]
        fitdata = cycle1-cycle2
    ##--------------------------- no phase cycling -------------------------------##
    else: 
        fitdata = data
    return fitting.fit(fit_exp, params.time_axis.value[1:], fitdata[1:], initial_guess=[fitdata[1], 10])
    
    
    
    
    
    
    
    
    
    
