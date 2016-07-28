from mod.main import *

def sequence(lab, params):
    return

def launch(lab, params):
    lab.sig_gen.set_freq(params.freq.v)
    time.sleep(100*ms)
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
    return
    
    
    
