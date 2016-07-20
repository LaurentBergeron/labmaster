""" 
Pulse blaster test. 
"""

import numpy as np 
from mod.main import *

def sequence(lab, params):
    
    lab.pb.turn_on("binA")
    for _ in np.arange(params.countA.v):
        lab.pb.turn_on("send_count", time_on=us)
        lab.delay(us)
    lab.pb.turn_off("binA")
    
    lab.pb.turn_on("binB")
    for _ in np.arange(params.countB.v):
        lab.pb.turn_on("send_count", time_on=us)
        lab.delay(us)
    lab.pb.turn_off("binB")
    
    
    return
 

    
def launch(lab, params):
    lab.usb_counter.clear(0)
    lab.usb_counter.clear(1)
    lab.pb.start()
    return


def get_data(lab, params):      
    A = lab.usb_counter.read(0)
    B = lab.usb_counter.read(1)
    return A, B, B-A


def start(lab, params):
    return
    
    
    
def end(lab, params):
    return
    
    
    
