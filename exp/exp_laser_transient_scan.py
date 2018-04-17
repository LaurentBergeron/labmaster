"""
laser scan with transients.
"""
from mod.main import *

def pre_scan(lab, params, fig, data, ID):
    lab.dds.clear_channel_names()
    lab.dds.add_channel('eblana', 10)
    lab.dds.add_channel('japan', 11)
    lab.dds.add_channel('1047', 12)
    lab.dds.add_channel('scope_trig', 1)
        
    lab.laser_japan.set_current(params.current.value[0])
    time.sleep(200*ms)
    
    return
    
    
def launch(lab, params, fig, data, ID):
    lab.laser_japan.set_current(params.current.v)
    time.sleep(params.delay.v)
    if DETECTOR=='COUNTER':
        lab.counter.clear(2)
    return
    
def sequence(lab, params, fig, data, ID):
    lab.dds.turn_on(duration=1*ms)
    return
    
    
def get_data(lab, params, fig, data, ID):
    
    if DETECTOR=='LOCKIN':
        result = lab.lockin.get_Y()
    elif DETECTOR=='COUNTER':
        lab.counter.initiate_timer(params.delay.value)
        while not lab.counter.timer_is_stopped():
            pass
        result = lab.counter.read(2)
    return result


def create_plot(lab, params, fig, data, ID):
    plotting.createfig_XY(fig, 'Current', 'lockin', 1, '--o')
    return 

def update_plot(lab, params, fig, data, ID):
        
    plotting.updatefig_XY(fig, params.current.value, data)
    
    
    return 
    