"""
Laser scan.
Low power regime: Green 3, Red Open.
"""
from mod.main import *

def start(lab, params, fig, data, ID):
    lab.laser.set_current(params.current.value[0])
    time.sleep(200*ms)
    
    params.current_meas.value = np.zeros(params.current.get_size())
    return
    
    
def launch(lab, params, fig, data, ID):
    lab.laser.set_current(params.current.v)
    time.sleep(params.delay.v)    
    return
    
    
def get_data(lab, params, fig, data, ID):
    params.current_meas.set_ith_value(lab.laser.get_current())  
    if USE_WAVEMETER:
        wavelength = lab.wavemeter.measure()
    else:
        wavelength = 0
    return lab.lockin.get_X(), wavelength


def create_plot(lab, params, fig, data, ID):
    plotting.createfig_XY(fig, 'Current', 'lockin', 1, '--o')
    return 

def update_plot(lab, params, fig, data, ID):
    ax = fig.axes[0]
    if USE_WAVEMETER:
        wavelength = data[params.current.i,1]
        ax.text(0.5,0.1,'$\lambda$ = %0.3f nm'%wavelength, transform = ax.transAxes, fontsize=15)
    plotting.updatefig_XY(fig, params.current_meas.value, data[:,0])
    peak_min, at_curr = out(lab, params, fig, data, ID)
    if peak_min != None:
        title = 'peak min = %0.0f'%peak_min
        title += ' at '+auto_unit(at_curr, 'A', decimal=3)
    else:
        title = 'peak min = unknown'
    
    if USE_WAVEMETER:
        title+='\n$\lambda$ = %0.3f nm'%wavelength
    fig.suptitle(title, fontsize=15-3*USE_WAVEMETER)
    return 
    
    
def out(lab, params, fig, data, ID):
    lockin_data = data[:,0]
    lockin_nonan = remove_nan(lockin_data)    
    curr_min_idx = np.argmin(np.abs(params.current.value - params.curr_estimate_min.v))
    curr_max_idx = np.argmin(np.abs(params.current.value - params.curr_estimate_max.v))
    try:
        peak_min = np.min(lockin_nonan[curr_min_idx:curr_max_idx+1])
        at_curr = params.current.value[np.argmin(lockin_nonan[curr_min_idx:curr_max_idx+1])+curr_min_idx]
    except ValueError:
        peak_min = None
        at_curr = None
    return peak_min, at_curr
