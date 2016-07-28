""" 
Pulse blaster test. 
"""

import numpy as np 
from mod.main import *

def sequence(lab, params):
    lab.pb.turn_on("slave", time_on=100*ms)
    lab.pb.delay(params.tau1.v)
    lab.pb.turn_on("slave", time_on=100*ms)
    lab.pb.delay(params.tau2.v)
    lab.pb.turn_on("slave", time_on=100*ms)
    lab.pb.delay(1)
    return
    
 

    
def launch(lab, params):
    lab.pb.start()
    return


def get_data(lab, params):  
    import random
    return random.random()


def start(lab, params):
    return
    
    
    
def end(lab, params):
    return
    
    
    
