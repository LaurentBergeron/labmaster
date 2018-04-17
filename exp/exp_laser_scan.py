"""
laser scan.
"""
from mod.main import *

def pre_scan(lab, params, fig, data, ID):
        
    lab.laser.set_current(params.current.value[0])
    time.sleep(200*ms)
    
    params.current_meas.value = np.zeros(params.current.get_size())
    # params.wavelength.value = np.zeros(params.current.get_size())
    return
    
    
def launch(lab, params, fig, data, ID):
    lab.laser.set_current(params.current.v)
    time.sleep(params.delay.v)
    if DETECTOR=='COUNTER':
        lab.counter.clear(2)
    return
    
    
def get_data(lab, params, fig, data, ID):
    if USE_WAVEMETER:
        wavelength = lab.wavemeter.measure()
    else:
        wavelength = 0
    params.current_meas.set_ith_value(lab.laser.get_current())  
    # params.wavelength.set_ith_value(wavelength)
    
    if DETECTOR=='LOCKIN':
        result = lab.lockin.get_Y()
    elif DETECTOR=='COUNTER':
        lab.counter.initiate_timer(params.delay.value)
        while not lab.counter.timer_is_stopped():   
            pass
        result = lab.counter.read(2)
    return result


def create_plot(lab, params, fig, data, ID):
    plotting.createfig_XY(fig, 'Current', 'lockin', 1, '--o')
    return 

def update_plot(lab, params, fig, data, ID):
    title = ''
    if USE_FIT:
        peak_min, at_curr = out(lab, params, fig, data, ID)
        if peak_min != None:
            title += 'peak min = %0.0f'%peak_min
            title += ' at '+auto_unit(at_curr, 'A', decimal=3)
        else:
            title += 'peak min = unknown'
    if USE_WAVEMETER:
        wavelength = params.wavelength.value[i]
        fig.axes[0].text(0.5,0.1,'$\lambda$ = %0.3f nm'%wavelength, transform = ax.transAxes, fontsize=15)
        title+='\n$\lambda$ = %0.3f nm'%wavelength
        
    plotting.updatefig_XY(fig, params.current_meas.value, data)
    
    fig.suptitle(title, fontsize=15-3*USE_WAVEMETER)
    
    return 
    
    
def out(lab, params, fig, data, ID):
    peak_min = None
    at_curr = None
    try:
        lockin_data = data
        lockin_nonan = remove_nan(lockin_data)    
        curr_min_idx = np.argmin(np.abs(params.current.value - params.curr_estimate_min.v))
        curr_max_idx = np.argmin(np.abs(params.current.value - params.curr_estimate_max.v))
        peak_min = np.min(lockin_nonan[curr_min_idx:curr_max_idx+1])
        at_curr = params.current.value[np.argmin(lockin_nonan[curr_min_idx:curr_max_idx+1])+curr_min_idx]
    except:
        print("Couldn't calculate current at peak minimum.")
        
    return peak_min, at_curr
