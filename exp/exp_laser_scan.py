"""
Laser scan.
Low power regime: Green 3, Red Open.
"""
import numpy as np 
from mod.main import *
import time as time_module


def launch(lab, params):
    lab.laser.set_current(params.current.v)
    time_module.sleep(500*ms)
    ##something to read and update wavelength, NOT IMPLEMENTED
    return


def get_data(lab, params):
    params.current.set_ith_value(lab.laser.quick_measure("curr"))  
    return lab.lockin.measure()


def create_plot(fig, params, data):
    plotting.createfig_XY(fig, "Current", "lockin", 1, "--o")
    return fig

def update_plot(fig, params, data):
    plotting.updatefig_XY(fig, params.current.value, data)
    
    return
