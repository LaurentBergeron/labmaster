"""
Functions shared among experiments.
"""

# Base modules
import numpy as np 
import scipy.constants as cst

# Home modules
from mod.main import *

def pb_master_trigger(lab):
    lab.pb.turn_on("master_trig", time_on=us, rewind="start")
    lab.delay(20*us) ## Start buffer to allow correction of trigger latency.

def prepare(lab, params):    
    """ Preparation for a RMN experiment. """
    lab.pb.turn_on("Xshutter", time_on=100*ms)
    lab.delay(4*ms)
    return

def readout(lab, params):
    """ Readout of a RMN experiment. """    
    lab.delay(2*ms)
    lab.pb.turn_on("Xshutter")
    lab.delay(5*ms)
    lab.pb.turn_on("binA", time_on=params.bin_length.v)
    lab.pb.turn_on("binB", time_on=params.bin_length.v)
    lab.delay(5*ms)
    lab.pb.turn_off("Xshutter")
    return





