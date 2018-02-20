from mod.main import *

def pre_scan(lab, params, fig, data, ID):
    time.sleep(200*ms) 
    return

def sequence(lab, params, fig, data, ID):
    return
    
def launch(lab, params, fig, data, ID):
    lab.sig_gen_srs.set_freq(params.freq.v)
    time.sleep(params.delay.v)
    return


def get_data(lab, params, fig, data, ID):  
    print('getdata')
    return lab.lockin.get_X()

    
def create_plot(lab, params, fig, data, ID):
    if len(fig.axes) == 0: 
        ## If the figure is empty.
        plotting.createfig_XY(fig, 'sig_gen frequency', 'lock-in', 1, '--o')
    else: 
        ## If using a figure which already contains a plot.
        plotting.add_lines(fig, 1, '-')
    return
    
def update_plot(lab, params, fig, data, ID):
    ax = fig.axes[0] 
    plotting.updatefig_XY(fig, params.freq.value, data, line_index=len(ax.lines)-1)
    
    peak_min, at_freq = out(lab, params, fig, data, ID)
    if peak_min != None:
        title = 'peak min = %0.0f'%peak_min
        title += ' at '+auto_unit(at_freq, 'Hz', decimal=6)
    else:
        title = 'peak_min = unknown'
    fig.suptitle(title, fontsize=15)
    return
    
    
def out(lab, params, fig, data, ID):
    data_nonan = remove_nan(data)
    freq_min_idx = np.argmin(np.abs(params.freq.value - params.freq_estimate_min.v))
    freq_max_idx = np.argmin(np.abs(params.freq.value - params.freq_estimate_max.v))
    try:
        peak_min = np.min(data_nonan[freq_min_idx:freq_max_idx+1])
        at_freq = params.freq.value[np.argmin(data_nonan[freq_min_idx:freq_max_idx+1])+freq_min_idx]
    except ValueError:
        peak_min = None
        at_freq = None
    return peak_min, at_freq
    
