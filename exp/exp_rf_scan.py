from mod.main import *

def sequence(lab, params):
    return

def launch(lab, params):
    lab.sig_gen.set_freq(params.freq.v)
    time.sleep(params.delay.v)
    return


def get_data(lab, params):  
    return lab.lockin.measure()

    
def create_plot(fig, params, data):
    if len(fig.axes) == 0:
        plotting.createfig_XY(fig, "sig_gen frequency", "lock-in", 1, "--o")
    else:
        fig.axes[0].plot([], "-")
    return
    
def update_plot(fig, params, data):
    ax = fig.axes[0]
    plotting.updatefig_XY(fig, params.freq.value, data, line_index=len(ax.lines)-1)
    
    nonan = data[np.logical_not(np.isnan(data))]
    
    freq_min_idx = np.argmin(np.abs(params.freq.value - params.freq_estimate_min.v))
    freq_max_idx = np.argmin(np.abs(params.freq.value - params.freq_estimate_max.v))
    
    try:
        peak_min = "%0.0f"%np.min(nonan[curr_min_idx:curr_max_idx+1])
        at_freq = " at freq "+auto_unit(params.current.value[np.argmin(nonan[curr_min_idx:curr_max_idx+1])+curr_min_idx], "Hz", decimal=6)
    except ValueError:
        peak_min = "unknown"
        at_freq = ""
        
    fig.suptitle("peak min = "+peak_min+at_freq, fontsize=15)
        

    return
    
    
    
