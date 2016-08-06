""" 
Pulse blaster test. 
"""

import numpy as np 
from mod.main import *

def sequence(lab, params, fig, data, ID):
    lab.pb.turn_on(1, time_on=5)
    lab.pb.delay(60)
    lab.pb.turn_on(2, time_on=5)
    lab.pb.turn_on(3, time_on=5)
    lab.pb.turn_on(4, time_on=5)
    
    return
    
 

    
def launch(lab, params, fig, data, ID):
    lab.pb.start()
    return


def get_data(lab, params, fig, data, ID):  
    import random
    return random.random()

