from mod.main import *

def sequence(lab, params, fig, data, ID):
    return

def launch(lab, params, fig, data, ID):
    lab.sig_gen.set_freq(params.freq.v)
    time.sleep(params.delay.v)
    return


def get_data(lab, params, fig, data, ID):  
    return lab.lockin.get_X()

    
def create_plot(lab, params, fig, data, ID):
    if len(fig.axes) == 0: 
        ## If the figure is empty.
        plotting.createfig_XY(fig, "sig_gen frequency", "lock-in", 1, "--o")
    else: 
        ## If using a figure which already contains a plot.
        plotting.add_lines(fig, 1, "-")
    return
    
def update_plot(lab, params, fig, data, ID):
    ax = fig.axes[0]
    plotting.updatefig_XY(fig, params.freq.value, data, line_index=len(ax.lines)-1)
    
    peak_min, at_freq = out(lab, params, fig, data, ID)
    fig.suptitle("peak min = "+peak_min+at_freq, fontsize=15)
    return
    
    
def out(lab, params, fig, data, ID):
    nonan = data[np.logical_not(np.isnan(data))]
    freq_min_idx = np.argmin(np.abs(params.freq.value - params.freq_estimate_min.v))
    freq_max_idx = np.argmin(np.abs(params.freq.value - params.freq_estimate_max.v))
    try:
        peak_min = "%0.0f"%np.min(nonan[freq_min_idx:freq_max_idx+1])
        at_freq = " at freq "+auto_unit(params.freq.value[np.argmin(nonan[freq_min_idx:freq_max_idx+1])+freq_min_idx], "Hz", decimal=6)
    except ValueError:
        peak_min = "unknown"
        at_freq = ""
    return peak_min, at_freq
    
