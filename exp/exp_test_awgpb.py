## Base modules
import numpy as np 
import scipy.constants as cst

## Home modules
import _shared_
from mod.main import *


def sequence(lab, params, fig, data, ID):
   
    lab.pb.turn_on("master_trig", time_on=20*us)
    
    lab.free_evolution_time = 0
    
    lab.pb.turn_on(10, time_on=0.5*us, rewind="start")
    lab.delay(75*ns)
    lab.pb.turn_on("Xshutter", time_on=0.81*us, rewind="start")
    lab.delay(30*ns)
    
    lab.awg.pulse(length=150*ns, freq=100*MHz)
    lab.delay(75*ns)
    lab.awg.pulse(length=75*ns)
    lab.delay(75*ns)
    lab.awg.pulse(length=150*ns, amp=0.5)
    lab.delay(35*ns)
    lab.awg.pulse(length=200*ns, shape="gauss")
    
    return 

    
def launch(lab, params, fig, data, ID):
    lab.awg.initiate_generation(1)
    lab.pb.start()
    return

    
    
    
    
    
    
    
    
    
    
