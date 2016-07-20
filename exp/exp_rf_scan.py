import numpy as np 
from mod.main import *
import time as time_module

def sequence(lab, params):
    return

def launch(lab, params):
    lab.sig_gen_srs.set_freq(params.freq.v)
    time_module.sleep(100*ms)
    return


def get_data(lab, params):  
    return lab.lockin.measure()

    
def create_plot(params, data):
    fig = plotting.createfig_XY("RF frequency", "lock-in", 1, "--o")
    return fig
    
def update_plot(fig, params, data):
    plotting.updatefig_XY(fig, params.freq.value, data)
    ax = fig.axes[0]
    ax.text(0.6, 0.2, "$freq$: "+str(params.freq.v),transform = ax.transAxes, fontsize=15)
    return
    
    
    
