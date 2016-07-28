"""
Laser scan.
Low power regime: Green 3, Red Open.
"""
from mod.main import *
import time as time_module


def launch(lab, params):
    lab.laser.set_current(params.current.v)
    time_module.sleep(500*ms)
    
    return


def get_data(lab, params):
    params.current.set_ith_value(lab.laser.quick_measure("curr"))  
    return lab.lockin.measure(), lab.wavemeter.measure()


def create_plot(fig, params, data):
    plotting.createfig_XY(fig, "Current", "lockin", 1, "--o")
    return fig

def update_plot(fig, params, data):
    wavemeter = data[params.current.i,1]
    ax = fig.axes[0]
    plotting.updatefig_XY(fig, params.current.value, data[:,0])
    ax.text(0.5,0.1,"$k$ = "+str(wavemeter), transform = ax.transAxes, fontsize=15)
    
    lockin_out = data[:,0]
    nonan = lockin_out[np.logical_not(np.isnan(lockin_out))]
    
    ### where is your peak? ###
    curr_min = 0.146
    curr_max = 0.149
    ###########################
    
    
    curr_min_idx = np.argmin(np.abs(params.current.value - curr_min))
    curr_max_idx = np.argmin(np.abs(params.current.value - curr_max))
    
    try:
        peak_min = np.min(nonan[curr_min_idx:curr_max_idx+1])
        at_curr = " at current "+str(params.current.value[np.argmin(nonan[curr_min_idx:curr_max_idx+1])+curr_min_idx])
        at_curr += " and $k$ = "+str(wavemeter)
    except ValueError:
        peak_min = "unknown"
        at_curr = ""
    fig.suptitle("peak min = "+str(peak_min)+at_curr, fontsize=15)
    
    return
