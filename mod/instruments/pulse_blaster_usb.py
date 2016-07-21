__author__ =  "Laurent Bergeron <laurent.bergeron4@gmail.com>"

# Base modules
import numpy as np
import visa as vi
import ctypes as ct
import matplotlib.pyplot as plt
import importlib
import time

# Homemade modules
from ..classes import Instrument
from ..units import *
from .. import not_for_user     
nfu = not_for_user 

class Pulse_blaster_usb(Instrument):
    """
    First use procedure: 
    1) Install spinapi drivers. http://www.spincore.com/support/spinapi/SpinAPI_Main.shtml
    if using another pulse_blaster than USB from spincore, write another class because some stuff will not be compatible, pb_inst_pbonly() for instance.
    You should be able to use the same dll wrapper though. Maybe need to add some functions in the wrapper. TODO: Complete the wrapper.
    author : Laurent Bergeron <laurent.bergeron4@gmail.com>
    """

    def __init__(self, name, parent):
        Instrument.__init__(self, name, parent, use_memory=True)
        self.spinapi = importlib.import_module("mod.instruments.wrappers.dll_spinapi27")
        self.verbose = False
        self.adjust_trig_latency = False
        self.slaves = {}
        self.flags = "000000000000000000000000" # channel one is on the right, channel 24 on the left.
        if self.adjust_trig_latency:
            self.trigger_latency = 80e-9
        else:
            self.trigger_latency = 0
        status = self.spinapi.pb_init()  
        self.check_error(status)
        self.ref_freq = 99.999637*1e6
        self.spinapi.pb_core_clock(100) # Recommended to run at 100 MHz
        self.all_slaves_off()
        return 
    
    def abort(self):
        self.all_slaves_off()
        return 
        
    def add_slave(self, name, channel):
        if not (0 < channel < 25):
            raise nfu.LabMasterError, "Pulse blaster slave "+self.name+" channel must be between 1 and 24 (included)"
        self.slaves[name] = channel

    def all_slaves_off(self):
        status = self.spinapi.pb_stop()
        self.check_error(status)
        status = self.spinapi.pb_start_programming(self.spinapi.PULSE_PROGRAM)
        self.check_error(status)
        self.flags = "0"*24
        start = self.spinapi.pb_inst_pbonly(int(self.flags,2), self.spinapi.Inst.CONTINUE, 0, self.spinapi.ms)
        self.check_error(start)
        status = self.spinapi.pb_inst_pbonly(int(self.flags,2), self.spinapi.Inst.BRANCH, start, self.spinapi.ms)
        self.check_error(status)
        status = self.spinapi.pb_stop_programming()
        self.check_error(status)
        status = self.spinapi.pb_reset()
        self.check_error(status)
        status = self.spinapi.pb_start()
        self.check_error(status)
        return
        
    def check_error(self, status):
        if self.verbose:
            print "pb:", status
        if status < 0:
            error = self.spinapi.pb_get_error()
            raise PulseBlasterUSBError, error
        return

    def close(self):
        self.all_slaves_off()
        status = self.spinapi.pb_close()
        self.check_error(status)
        return status

    def get_slave(self, name):
        if isinstance(name, str):
            slave = self.slaves[name]
        else:
            if 0 < name < 25:
                slave = name
            else:
                raise nfu.LabMasterError, "Pulse blaster slave channel must be between 1 and 24 (included)"
        return slave
        
    def load_memory(self):
        time_start = time.time()
        if self.instructions==[]:
            return
        self.instructions.sort() # Sort instructions in time ascending order. sort() takes first column as default.
        status = self.spinapi.pb_stop()
        self.check_error(status)
        status = self.spinapi.pb_start_programming(self.spinapi.PULSE_PROGRAM)
        self.check_error(status)
        
        for flags, opcode, data_field, duration in self.preprocess():
            status = self.spinapi.pb_inst_pbonly(int(flags,2), opcode, data_field, duration*1e9)
        
        self.flags = "0"*24
        start = self.spinapi.pb_inst_pbonly(int(self.flags,2), self.spinapi.Inst.CONTINUE, 0, self.spinapi.ms)
        self.check_error(start)
        status = self.spinapi.pb_inst_pbonly(int(self.flags,2), self.spinapi.Inst.BRANCH, start, self.spinapi.ms)
        self.check_error(status)
        status = self.spinapi.pb_stop_programming()
        self.check_error(status)
        # print "time to load pb:", time.time()-time_start
        return
    
        
    def preprocess(self):
        instructions = sorted([x for x in self.instructions if x[1]!="OPCODE"])
        opcode_instructions = sorted([x for x in self.instructions if x[1]=="OPCODE"])
        # TODO raise an error if more than one OP code at one single time (plus-minus 50 ns)
        times = [x[0]-self.trigger_latency for x in instructions]+[self.lab.total_duration]
        opcode_times = [x[0]-self.trigger_latency for x in opcode_instructions]
        
        result = []
        if times[0] > 0:
            self.flags = "0"*24
            if times[0] in opcode_times:
                opcode = 0 # TODO
                data_field = 0 # TODO
            else:
                opcode = self.spinapi.Inst.CONTINUE
                data_field = 0
            result.append([self.flags, opcode, data_field, times[0]])
        i=0
        while i < len(instructions):
            if times[i] in opcode_times:
                opcode = 0
                data_field = 0
            else:
                opcode = self.spinapi.Inst.CONTINUE
                data_field = 0
            i_saved = i
            while i < len(instructions): 
                duration = times[i+1] - times[i_saved]
                channel = instructions[i][1]
                new_bit = str(instructions[i][2])
                self.flags = self.flags[:24-channel] + new_bit + self.flags[25-channel:]
                if (duration >= 5/float(self.ref_freq)): # minimum pulse length is 5 clock cycles.
                    result.append([self.flags, opcode, data_field, duration])
                    break
                i+=1
            i+=1
        return result
    
    def print_loaded_sequence(self, show_slave="all", ax=None):
        if self.lab.total_duration == 0:
            raise nfu.LabMasterError, "No sequence is loaded."

        if show_slave=="all":
            slaves = self.slaves
        else:
            slaves = {key: self.slaves[key] for key in show_slave}
                
                
        prefix, c = nfu.time_auto_label(self.lab)

        if ax==None:
            fig, axes = plt.subplots(len(slaves), sharex=True)
            axes[-1].set_xlabel("Time ("+prefix+"s)")
            # Span time for all experiment duration
            axes[-1].set_xlim([0, c*(self.lab.total_duration - self.lab.end_buffer)])
        
        preprocess = self.preprocess()
        
        for i, (name, channel) in enumerate(sorted(slaves.items())):
            if ax==None:
                ax_ = axes[i]
            else:
                ax_ = ax
            ax_.yaxis.set_major_locator(plt.NullLocator())
            ax_.set_ylabel(name)
            
            timer=0
            for flags, duration in preprocess:
                print flags, channel, flags[-channel],"\t", timer,"\t", duration
                if flags[-channel]=="1":
                    print "true", c*timer, c*duration
                    ax_.fill_between([c*timer, c*timer+c*duration], 0, [1,1])
                timer+=duration



        plt.show()
        return
        
    def opcode(self, opcode_str, link_to):
        try:
            exec("opcode=self.spinapi.Inst."+opcode_str)
        except AttributeError:
            raise nfu.LabMasterError, "Wrong opcode_str"
        self.instructions.append([self.lab.time_cursor, "OPCODE", opcode, link_to])
        return
        
    def turn_on(self, slave, time_on=None, opcode_str="", ref="", rewind=None):
        slave = self.get_slave(slave)
        if opcode_str!="":
            self.opcode(opcode_str, ref)
        if time_on==None:
            self.instructions.append([self.lab.time_cursor, slave, 1, ref])
            self.lab.update_time_cursor(0., rewind)
        else:
            self.instructions.append([self.lab.time_cursor, slave, 1, ref])
            self.instructions.append([self.lab.time_cursor+time_on, slave, 0, ""])
            self.lab.update_time_cursor(time_on, rewind)
        return
        
    def turn_off(self, slave, time_off=None, opcode_str="", ref="", rewind=None):
        slave = self.get_slave(slave)
        if opcode_str!="":
            self.opcode(opcode_str, ref)
        if time_off==None:
            self.instructions.append([self.lab.time_cursor, slave, 0, ref])
            self.lab.update_time_cursor(0., rewind)
        else:
            self.instructions.append([self.lab.time_cursor, slave, 0, ref])
            self.instructions.append([self.lab.time_cursor+time_off, slave, 1, ""])
            self.lab.update_time_cursor(time_off, rewind)
        return
        
    def start(self):
        status = self.spinapi.pb_reset()
        self.check_error(status)
        status = self.spinapi.pb_start()
        self.check_error(status)
        return


class PulseBlasterUSBError(nfu.LabMasterError):
    pass      
        
