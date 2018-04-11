"""
Default parameters shared among experiments.
"""

from mod.units import *

dds_freq = MHz
dds_amp = 1.0

awg_sample_rate = 976*MHz
awg_freq = 50*MHz
awg_amp = 200*mV

pi_len = 31.5*us/2
bin_len = 150*ms
amp_sensitivity = 1e-7
ND_filters = '3.0'
ND_filters_1047 = '2.04'

laser_current = 0.146205
sig_gen_freq = 1.61042*GHz

mag_field = 0