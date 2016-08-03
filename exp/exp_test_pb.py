""" 
Pulse blaster test. 
"""

import numpy as np 
from mod.main import *

def sequence(lab, params):
    lab.pb.turn_on(1, time_on=50*us)
    lab.pb.loop_start(2, ref="loop")
    lab.pb.delay(50*us)
    lab.pb.turn_on(2, time_on=50*us, rewind=25*us, ref="b")
    lab.pb.turn_on(3, time_on=50*us)
    lab.pb.loop_end("loop", duration = 50*us)
    lab.pb.delay(50*us)
    lab.pb.turn_on(4, time_on=50*us)
    lab.pb.branch("b", duration = 25*us)
    
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
    
    
    
