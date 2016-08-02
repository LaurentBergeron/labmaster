__author__ =  "Laurent Bergeron <laurent.bergeron4@gmail.com>"

# Base modules
import numpy as np
import visa as vi
import ctypes as ct
import matplotlib.pyplot as plt
import importlib
import time
import textwrap

# Homemade modules
from ..classes import Instrument
from ..units import *
from .. import not_for_user     
nfu = not_for_user 

class Pulse_blaster_usb(Instrument):
    """
    Installation procedure: 
    1) Install 32-bit spinapi drivers. http://www.spincore.com/support/spinapi/SpinAPI_Main.shtml
    
    Use of another pulse blaster:
    If using another pulse_blaster than PulseBlasterUSB, this class might not be compatible.
    In this case, write another class in this file. It's strongly suggested to share compatible methods.
    The spinapi Python wrapper is not totally complete, so you might need to add some functions to it.
    """

    def __init__(self, name, parent):
        """Initialize a Pulse_blaster_usb instance with requested options."""
        Instrument.__init__(self, name, parent, use_memory=True)
        ##### OPTIONS #####
        self.verbose = False ## print the result of each dll call. 
        self.adjust_trig_latency = False ## adjust first duration to remove the 8 clock cycles trigger latency.
        self.ref_freq = 99.999637*MHz ## Recommended to run at 100 MHz
        ###################
        self.spinapi = importlib.import_module("mod.instruments.wrappers.dll_spinapi27") ## dll wrapper
        self.slaves = {} ## dict with slave names as keys and their respective channel as values.
        status = self.spinapi.pb_init()
        self.check_error(status)
        self.spinapi.pb_core_clock(self.ref_freq/1e6)
        self.flags = "000000000000000000000000" ## channel one is on the right, channel 24 on the left.
        self.all_slaves_off()
        return 
    
    def abort(self):
        """
        This method is called at the end of the scan function. Make sure it raises no error.
        Turn all channels off.
        """
        self.all_slaves_off()
        return 
        
    def add_slave(self, name, channel):
        """Add a slave to slaves list. Once a slave is added, use turn_on and turn_off to control it."""
        if name in self.available_opcodes():
            raise PulseBlasterUSBError, "Failed to add slave, "+name+" is a reserved name."
        if not (0 < channel < 25):
            raise PulseBlasterUSBError, "Failed to add slave, "+name+" channel must be between 1 and 24."
        for key, channel_ in self.slaves.items():
            if channel==channel_:
                raise PulseBlasterUSBError, "Channel "+str(channel)+" is already assigned to '"+key+"'."
        self.slaves[name] = channel
        return

    def all_slaves_off(self):
        """Turn all channels off."""
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
        
    def available_opcodes(self):
        """A list of all available opcodes, from spinapi.Inst enumeration."""
        return [x for x in dir(self.spinapi.Inst) if not x.startswith("_")]
        
    def branch(self, link_to, duration=0, ref="", rewind=None):
        """
        BRANCH opcode.
        Will branch to the instruction with the same ref as the 'link_to' input. 
        Ex:
        turn_on(..., ref="ilovetobranch!")
        ... useful experiment ...
        branch("ilovetobranch!")
        delay(10*ms)
        
        Careful. The duration starting at the same time as branch IS INCLUDED IN THE BRANCH. To split a delay, use the duration keyword.
        Ex:
        turn_on(..., ref="ilovetobranch!")
        ... useful experiment ...
        branch("ilovetobranch!", duration=us) # This will create a new instruction. This way, 1 us is branched instead of a full 10 ms.
        delay(10*ms)
        
        More info and examples in LabMaster documentation.
        """
        self.opcode("BRANCH", link_to, duration=duration, ref=ref, rewind=rewind)
        return
        
    def check_error(self, status):
        """Check pulse blaster board for errors."""
        if self.verbose:
            print "pb:", status
        if status < 0:
            error = self.spinapi.pb_get_error()
            raise PulseBlasterUSBError, error
        return

    def close(self):
        """Turn off all channels and close pulse blaster spinapi driver."""
        self.all_slaves_off()
        status = self.spinapi.pb_close()
        self.check_error(status)
        return status
    
    def keep_going(self, ref=""):
        """
        Status quo instruction.
        Useful to split delays.
        Useful to insert refs.
        """
        self.instructions.append([self.lab.time_cursor, None, "KEEP_GOING", None, ref])            
    
    def get_ref_freq(self):
        """
        Return current reference frequency.
        """
        ## TODO: Use a function that reads the board to retrieve the actual current frequency, instead of using the one set on __init__. 
        return float(self.ref_freq)
        
    def get_slave(self, name):
        """
        Return slave channel corresponding to name.
        If name is a string, get_slave() will look for slaves added using self.add_slaves() and return the corresponding channel number.
        If name is an int, get_slave() will return it untouched.
        """
        if isinstance(name, str):
            slave = self.slaves[name]
        else:
            if 1 <= name <= 24:
                slave = int(name)
            else:
                raise PulseBlasterUSBError, "Pulse blaster slave channel must be between 1 and 24 (included)"
        return slave
        
        
    def load_memory(self):
        """
        Load PulseBlasterUSB memory using spinapi.pb_inst_pbonly commands.
        The result from self.preprocess() is loaded, then all channels are looped to zero ad infinitum.
        """
        if self.instructions==[]:
            print nfu.warn_msg()+"No instructions for pulse blaster. Set the use_memory attribute to False."
            return
        ### Stop previous generation.
        status = self.spinapi.pb_stop() 
        self.check_error(status)
        ### Start programming memory.
        status = self.spinapi.pb_start_programming(self.spinapi.PULSE_PROGRAM)
        self.check_error(status)
        
        ### Load results from self.preprocess() using spinapi.pb_inst_pbonly commands.
        for flags, opcode, data_field, duration in self.preprocess():
            status = self.spinapi.pb_inst_pbonly(int(flags,2), opcode, data_field, duration*1e9)
        
        ### All channels offs.
        self.flags = "0"*24
        start = self.spinapi.pb_inst_pbonly(int(self.flags,2), self.spinapi.Inst.CONTINUE, 0, self.spinapi.ms)
        self.check_error(start)
        status = self.spinapi.pb_inst_pbonly(int(self.flags,2), self.spinapi.Inst.BRANCH, start, self.spinapi.ms)
        self.check_error(status)
        ### Stop programming memory.
        status = self.spinapi.pb_stop_programming()
        self.check_error(status)
        
        ### Waiting for pb.start() to be called.
        return
    
    def loop_start(self, num_loops, ref, duration=0, rewind=None):
        """
        LOOP opcode.
        Sets where the loop starts, and the number of loops. 
        """
        self.opcode("LOOP", num_loops, duration=duration, ref=ref, rewind=rewind)
        return
        
    def loop_end(self, link_to, duration=0, ref="", rewind=None):
        """
        END_LOOP opcode.
        Sets where the loop ends.
        Will loop to the instruction with the same ref as the 'link_to' input (has to be a LOOP opcode).
        Ex:
        loop_start(10, "looping!")
        ... useful experiment ...
        loop_end("looping!")
        delay(10*ms)

        Careful. The duration starting at the same time as loop_end IS INCLUDED IN THE LOOP. To split a delay, use the duration keyword.
        Ex:
        turn_on(..., ref="looping!")
        ... useful experiment ...
        loop_end("looping!", duration=us) # This will create a new instruction. This way, 1 us is looped instead of a full 10 ms.
        delay(10*ms)
        
        More info and examples in LabMaster documentation.
        """
        self.opcode("END_LOOP", link_to, duration=duration, ref=ref, rewind=rewind)
        return
        
    def preprocess(self):
        """
        Starting with self.intructions list, return a list of arguments ready for spinapi.pb_inst_pbonly().
        Trigger latency can be adjusted with self.adjust_trig_latency option. In this case, a time buffer is needed before first instruction.
        Manages opcodes, data fields and refs (see self.opcode() doc for more info).
        Automatic LONG_DELAY call if needed.
        """
        result = []
        
        ### Unzip instructions
        instructions = [tuple(x) for x in (sorted(self.instructions))] + [(self.lab.total_duration, "", "", "", "")]
        time_list, slave_list, opcode_list, data_field_list, ref_list = zip(*instructions) 
        
        ### Make sure each ref is unique.
        for ref in ref_list:
            if ref != "" and ref_list.count(ref)>1:
                raise PulseBlasterUSBError, "Pulse blaster: each ref must be unique or an empty string."
        
        ### as refs are detected, they will be added to this ref_dict, with ref as the key and the address in pb memory as the value
        ref_dict = {}
        
        ### Set trigger latency if requested in options.
        if self.adjust_trig_latency:
            trigger_latency = 8.0/self.get_ref_freq()
        else:
            trigger_latency = 0
        
        ### First instruction is special.
        ## In any case, if the first instruction doesn't start at time 0, all channels are set to zero until first instruction starts.
        ## If adjust_trig_latency is activated, the first instruction needs to be set after a time buffer (this time buffer needs to be longer than the latency delay).
        ## The duration of this first instruction is cropped by trigger_latency.
        self.flags = "0"*24
        if time_list[0] > trigger_latency:
            duration = time_list[0]-trigger_latency
            if duration != 0:
                opcode = self.spinapi.Inst.CONTINUE
                data_field = 0
                opcode, data_field, duration = self.autolongdelay(opcode, data_field, duration) ## will add a LONG_DELAY opcode if needed.
                result.append([self.flags, opcode, data_field, duration])
                ref_dict["ZERO_TIME"] = len(result)-1 ## to loop/branch to the start, use ZERO_TIME ref.
        else:
            if self.adjust_trig_latency:
                raise PulseBlasterUSBError, "You need to add a time buffer at the start of sequence when adjusting for trigger latency."
                
        ### Go through all the instructions and condense them to spinapi.pb_inst_pbonly() arguments.
        i=0
        while i < len(instructions)-1:
            i_saved = i ## when multiple instructions are assigned during the same 5 clock cycles window, i_saved is needed to remember the time of the earliest instruction. 
            opcode = self.spinapi.Inst.CONTINUE ## by default
            data_field = 0 ## by default
            ref = "" ## by default
            while i < len(instructions)-1:
                ## Check and assign refs
                if ref_list[i] != "": 
                    if ref != "":
                        raise PulseBlasterUSBError, "Two different refs detected at the same time."
                    else:
                        ref = ref_list[i]
                ## Check and assign opcodes/data_field
                if opcode_list[i] in self.available_opcodes():
                    if opcode != self.spinapi.Inst.CONTINUE:
                        raise PulseBlasterUSBError, "Two different opcode instructions detected at the same time."
                    else:
                        opcode = self.spinapi.Inst.__dict__[opcode_list[i]]  ## ready for pulse blaster communication.
                        data_field = data_field_list[i] ## data_field: for BRANCH and END_LOOP opcodes, data_field stays the ref string to link to. 
                                                        ## For all other opcodes, data_field is ready for pulse blaster communication.
                ## Keep going meaning keep channels as they are. Useful to split a delay without using opcodes.
                elif opcode_list[i]=="KEEP_GOING":
                    pass
                ## If no opcode detected, it's a turn_on/turn_off situation.
                else:
                    channel = slave_list[i] ## which channel to change
                    new_bit = str(data_field_list[i]) ## On or off ?
                    self.flags = self.flags[:24-channel] + new_bit + self.flags[25-channel:] ## update flags
                duration = time_list[i+1] - time_list[i_saved] 
                if (duration >= 5.0/self.get_ref_freq()): ## minimum pulse length is 5 clock cycles. If duration is smaller than that, repeat loop without appending result (flags will remain changed).
                    opcode, data_field, duration = self.autolongdelay(opcode, data_field, duration) ## will add a LONG_DELAY opcode if needed.
                    result.append([self.flags, opcode, data_field, duration])
                    if ref!="":
                        ref_dict[ref]=len(result)-1
                    break ## break While statement if a result was appended.
                i+=1
            i+=1

        ### In this final preprocess loop, replace refs for their matching address in pulse_blaster memory.
        final_result = []
        for i, x in enumerate(result):
            flags, opcode, data_field, duration = x
            if x[1]==self.spinapi.Inst.END_LOOP or x[1]==self.spinapi.Inst.BRANCH:
                try:
                    data_field = ref_dict[data_field]
                except KeyError:
                    raise PulseBlasterUSBError, "ref '"+data_field+"' not found."
            final_result.append([flags, opcode, data_field, duration])
        
        return final_result
        
    def autolongdelay(self, opcode, data_field, duration):
        """
        Check if a LONG_DELAY opcode is needed. 
        If needed, opcode, data_field and duration will be modified accordingly.
        If initial opcode is not CONTINUE, nothing will be done.
        """
        max_duration = (2**32-1)/float(self.get_ref_freq()) ## 2^32-1 clock cycles is max duration for CONTINUE
        ultra_max_duration = (2**52-1)/float(self.get_ref_freq()) ## 2^32-1 clock cycles is max duration for LONG_DELAY
        if opcode==self.spinapi.Inst.CONTINUE:
            if duration > ultra_max_duration:
                raise PulseBlasterUSBError, "You asked for a delay longer than %0.0f days."%(ultra_max_duration/60./60./24.)
            elif duration > max_duration:
                opcode = self.spinapi.Inst.LONG_DELAY
                data_field = int(duration//max_duration + 1) ## number of repetition. total duration will be duration*data_field
                duration = duration/float(data_field)
            else:
                pass
        else:
            if duration > max_duration:
                raise PulseBlasterUSBError, "Autolongdelay can't be called because the opcode is already taken."
            else:
                pass
        return opcode, data_field, duration
        
    
    def print_loaded_sequence(self, show_slave="all", ax=None):
        """
        Show the loaded sequence in a matplotlib figure.
        
        Input:
        - show_slave: A list of slaves names to show.
                      If show_slave is "all", all slaves will be shown.
        - ax: Specify an ax on which to plot the loaded sequence. 
              If None, each slave will get its own new ax, on a new figure.
        """
        if self.lab.total_duration == 0:
            raise PulseBlasterUSBError, "No sequence is loaded."

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
        
        
    def opcode(self, opcode_str, data_field, duration=0, ref="", rewind=None):
        """
        Valid entries:
        opcode_str      data_field                  Note
        ------------------------------------------------------
        CONTINUE        Not used                    Use turn_on and turn_off methods instead.
        STOP            Not used                    -
        LOOP            # of loops                  Use loop_start() method instead. WARNING: Time cursor won't update.
        END_LOOP        ref string to loop start    Use loop_end() method instead. WARNING: Time cursor won't update.
        JSR             address of 1st instruction  WARNING: Time cursor won't update.
        RTS             Not used                    WARNING: Time cursor won't update.
        BRANCH          ref string to branch start  Use branch() method instead. WARNING: Time cursor won't update.
        LONG_DELAY      # of repetitions            Automatic when using turn_on and turn_off methods.
        WAIT            Not used                    -
        """
        if opcode not in self.available_opcodes():
            raise PulseBlasterUSBError, "Wrong opcode. \n"+textwrap.dedent(PulseBlasterUSB.opcode.__doc__)
        self.instructions.append([self.lab.time_cursor, None, opcode_str, data_field, ref])
        if duration > 0:
            self.lab.update_time_cursor(duration, rewind)
            self.keep_going()
        return
        
    
    def turn_on(self, slave, time_on=None, opcode_str="", data_field=0, ref="", rewind=None):
        """
        Instruction to turn on specified slave.
        """
        slave = self.get_slave(slave)
        if opcode_str!="":
            self.opcode(opcode_str, data_field)
        if time_on==None:
            self.instructions.append([self.lab.time_cursor, slave, self.spinapi.Inst.CONTINUE, 1, ref])
            self.lab.update_time_cursor(0., rewind)
        else:
            self.instructions.append([self.lab.time_cursor, slave, self.spinapi.Inst.CONTINUE, 1, ref])
            self.instructions.append([self.lab.time_cursor+time_on, slave, self.spinapi.Inst.CONTINUE, 0, ""])
            self.lab.update_time_cursor(time_on, rewind)
        return
        
    def turn_off(self, slave, time_off=None, opcode_str="", ref="", rewind=None):
        """
        Instruction to turn off specified slave.
        """
        slave = self.get_slave(slave)
        if opcode_str!="":
            self.opcode(opcode_str, ref)
        if time_off==None:
            self.instructions.append([self.lab.time_cursor, slave, self.spinapi.Inst.CONTINUE, 0, ref])
            self.lab.update_time_cursor(0., rewind)
        else:
            self.instructions.append([self.lab.time_cursor, slave, self.spinapi.Inst.CONTINUE, 0, ref])
            self.instructions.append([self.lab.time_cursor+time_off, slave, self.spinapi.Inst.CONTINUE, 1, ""])
            self.lab.update_time_cursor(time_off, rewind)
        return
        
    def start(self):
        """Start generation of the loaded sequence."""
        status = self.spinapi.pb_reset()
        self.check_error(status)
        status = self.spinapi.pb_start()
        self.check_error(status)
        return

        

class PulseBlasterUSBError(nfu.LabMasterError):
    """Errors raised by the PulseBlasterUSB class or by the pulse blaster USB board itself."""
    pass      
        
