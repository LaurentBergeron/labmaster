## Base modules
import numpy as np 
import scipy.constants as cst

## Home modules
import _shared_


def sequence(lab, params, fig, data, ID):
    lab.awg.set_default_params(delay=params.tau.v)
    
    lab.pb.turn_on("master_trig", time_on=20*us)
    
    lab.free_evolution_time = 0
    
    for _ in np.arange(params.loops.v):
        lab.awg.string_sequence(1, LOADED_SEQUENCE)
    
    lab.pb.turn_on("Xshutter", time_on=100*ms, rewind="start")
    return 

    
def launch(lab, params, fig, data, ID):
    lab.awg.initiate_generation(1)
    lab.pb.start()
    return

    
    
    
    
    
    
    
    
    
    
