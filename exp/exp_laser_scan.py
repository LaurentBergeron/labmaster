"""
Laser scan.
Low power regime: Green 3, Red Open.
"""
from mod.main import *
import time as time_module


def launch(lab, params, fig, data, ID):
    lab.laser.set_current(params.current.v)
    time_module.sleep(params.delay.v)    
    return


def get_data(lab, params, fig, data, ID):
    params.current_meas.set_ith_value(lab.laser.quick_measure("curr"))  
    if USE_WAVEMETER:
        wavenumber = lab.wavemeter.measure()
    else:
        wavenumber = 0
    return lab.lockin.get_X(), wavenumber


def create_plot(lab, params, fig, data, ID):
    plotting.createfig_XY(fig, "Current", "lockin", 1, "--o")
    return 

def update_plot(lab, params, fig, data, ID):
    ax = fig.axes[0]
    if USE_WAVEMETER:
        wavenumber = data[params.current.i,1]
        ax.text(0.5,0.1,"$\lambda$ = %0.3f nm"%wavenumber, transform = ax.transAxes, fontsize=15)
        
    
    plotting.updatefig_XY(fig, params.current_meas.value, data[:,0])
    
    lockin_out = data[:,0]
    nonan = lockin_out[np.logical_not(np.isnan(lockin_out))]
       
    
    curr_min_idx = np.argmin(np.abs(params.current_meas.value - params.curr_estimate_min.v))
    curr_max_idx = np.argmin(np.abs(params.current_meas.value - params.curr_estimate_max.v))
    
    try:
        peak_min = "%0.0f"%np.min(nonan[curr_min_idx:curr_max_idx+1])
        at_curr = " at current %0.6f"%params.current.value[np.argmin(nonan[curr_min_idx:curr_max_idx+1])+curr_min_idx]
        if USE_WAVEMETER:
            at_curr += " and $\lambda$ = %0.3f nm"%wavenumber
    except ValueError:
        peak_min = "unknown"
        at_curr = ""
    fig.suptitle("peak min = "+peak_min+at_curr, fontsize=15)
    
    return at_curr
    
    
def out(lab, params, fig, data, ID):
    return update_plot(fig, params, data)
