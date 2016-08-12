"""
Default parameters shared among experiments.
"""

from mod.units import *

awg_sample_rate = 976*MHz
awg_freq = 50*MHz
pi_len = 31.5*us
awg_amp = 200*mV
bin_len = 150*ms
amp_sensitivity = 1e-7
ND_filters = 'Red Open, Green 3'

laser_current = 0.146205
sig_gen_freq = 1.61042*GHz