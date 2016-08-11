"""
Definition of Pulse Blaster Instrument classes.

Current classes: 
- Pulse_blaster_USB
"""
__author__ =  "Laurent Bergeron <laurent.bergeron4@gmail.com>"

## Base modules
import numpy as np
import visa as vi
import ctypes as ct
import matplotlib.pyplot as plt
import importlib
import time
import textwrap

## Homemade modules
from ..classes import Instrument
from ..units import *
from .. import not_for_user     
nfu = not_for_user 

class Pulse_blaster_USB(Instrument):
    """
    Class allowing to control an SpinCore PulseBlasterUSB! instrument.
    
    Installation procedure: 
    1) Install 32-bit spinapi drivers. http://www.spincore.com/support/spinapi/SpinAPI_Main.shtml
    """

    def __init__(self, name, parent):
        """
        Inherit from Instrument. 
        Import wrapper and initialize instrument drivers.
        Set all channels to 0 V.
        - name: Name to give to the instrument.
        - parent: A reference to the lab instance hosting the instrument.
        """
        ##-------------------------------------------- OPTIONS --------------------------------------------##
        self.verbose = False                    ## Print the status of each driver function call.
        self.adjust_trig_latency = False        ## Adjust first duration to remove the 8 clock cycles trigger latency (needs a time buffer at the start of sequence).
        self.ref_freq = 99.999637*MHz           ## Recommended to run at 100 MHz
        ##-------------------------------------------------------------------------------------------------##
        ## Inherit from Instrument
        Instrument.__init__(self, name, parent, use_memory=True)
        ## Reset show_warning attributes to True.
        self.reset_warnings()
        ## spinapi wrapper
        self.spinapi = importlib.import_module("mod.instruments.wrappers.dll_spinapi27") ## dll wrapper
        ## Dictionary with channel names as keys and their respective channel as values.
        self.channels = {} 
        ## States of the channels. Channel one is on the right, channel 24 on the left.
        self.flags = "000000000000000000000000"
        ## Initialize drivers.
        status = self.spinapi.pb_init()
        self.check_error(status)
        ## Set clock frequency.
        self.spinapi.pb_core_clock(self.ref_freq/1e6)
        ## Turn all channels off.
        self.all_channels_off()
        return 
    
    def abort(self):
        """
        To be executed when scan raises on error (Ctrl-C included).
        Set all channels to 0V.
        """
        self.all_channels_off()
        return 
        
    def add_channel(self, name, channel):
        """
        Add a channel to channels dictionary.
        - name: New name.
        - channel: This channel number can now be refered with the name.
        """
        if name in self.available_opcodes():
            raise PulseBlasterUSBError, "Failed to add channel, "+name+" is a reserved name."
        if not (0 < channel < 25):
            raise PulseBlasterUSBError, "Failed to add channel, "+name+" must be between 1 and 24."
        for key, channel_ in self.channels.items():
            if channel==channel_ and key!=name:
                raise PulseBlasterUSBError, "Channel "+str(channel)+" is already assigned to '"+key+"'."
        self.channels[name] = channel
        return

    def all_channels_off(self):
        """Set all channels to 0V."""
        ## Stop generation (states of the channels will stay the same as when they stopped).
        status = self.spinapi.pb_stop()
        self.check_error(status)
        ## Start a PULSE_PROGRAM (usual stuff).
        status = self.spinapi.pb_start_programming(self.spinapi.PULSE_PROGRAM)
        self.check_error(status)
        ## Branch two instructions to loop zeros.
        self.flags = "0"*24
        start = self.spinapi.pb_inst_pbonly(int(self.flags,2), self.spinapi.Inst.CONTINUE, 0, self.spinapi.ms)
        self.check_error(start)
        status = self.spinapi.pb_inst_pbonly(int(self.flags,2), self.spinapi.Inst.BRANCH, start, self.spinapi.ms)
        self.check_error(status)
        ## Stop programming.
        status = self.spinapi.pb_stop_programming()
        self.check_error(status)
        ## Start generation.
        self.start()
        return
        
    def available_opcodes(self):
        """A list of all available opcodes, from spinapi.Inst enumeration."""
        return [x for x in dir(self.spinapi.Inst) if not x.startswith("_") and x!="CONTINUE"]
        
    def branch(self, link_to, duration=0, ref=""):
        """
        BRANCH opcode.
        
        - link_to: Reference string of the instruction to branch to.
        - ref: A reference string for eventual opcode (optional).
        - duration: Duration of the instruction (recommended). Channel states will stay the same.
        
        WARNING: Time cursor won't update. Do not use in combinaison with other instruments if timing is important.
        The duration argument is recommended. If not specified, the branch instruction will merge with the next instruction.
        More info and examples in LabMaster documentation.
        """
        self.opcode("BRANCH", link_to, duration=duration, ref=ref)
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
        self.all_channels_off()
        status = self.spinapi.pb_close()
        self.check_error(status)
        return status
    
    def JSR(self, link_to, duration=0, ref=""):
        """
        JSR opcode. Not tested.
        
        - link_to: Reference string of the instruction to link to.
        - ref: A reference string for eventual opcode (optional).
        - duration: Duration of the instruction (recommended). Channel states will stay the same.
        
        WARNING: Time cursor won't update. Do not use in combinaison with other instruments if timing is important.
        The duration argument is recommended. If not specified, the JSR instruction will merge with the next instruction.
        """
        self.opcode("JSR", link_to, duration=duration, ref=ref)
        return
    
    def keep_going(self, ref=""):
        """
        Status quo instruction. Nothing happens.
        Useful to split delays.
        Useful to insert refs.
        """
        self.instructions.append([self.lab.time_cursor, None, "KEEP_GOING", None, ref])            
    
    def get_ref_freq(self):
        """
        Return reference frequency from the self.ref_freq attribute.
        It would be best to use a get_frequency() function for the Pulse Blaster, but I didn't find one.
        """
        return float(self.ref_freq)
        
        
        
    def load_memory(self):
        """
        Call self.preprocess() which translates instructions to Pulse Blaster language.
        Load PulseBlasterUSB memory using the spinapi.pb_inst_pbonly() function.
        After the programmed sequence, all channels are looped to zero ad infinitum.
        """
        if self.instructions==[]:
            if self.show_warning_no_inst:
                print nfu.warn_msg()+"No instructions for pulse blaster. Set the use_memory attribute to False."
                self.show_warning_no_inst = False
            return
        ## Stop previous generation.
        status = self.spinapi.pb_stop() 
        self.check_error(status)
        ## Start programming memory.
        status = self.spinapi.pb_start_programming(self.spinapi.PULSE_PROGRAM)
        self.check_error(status)
        
        ## Load results from self.preprocess() using spinapi.pb_inst_pbonly commands.
        for flags, opcode, data_field, duration in self.preprocess():
            print flags, opcode, data_field, duration
            status = self.spinapi.pb_inst_pbonly(int(flags,2), opcode, data_field, duration*1e9)
        print ""
        ## All channels offs.
        self.flags = "0"*24
        start = self.spinapi.pb_inst_pbonly(int(self.flags,2), self.spinapi.Inst.CONTINUE, 0, self.spinapi.ms)
        self.check_error(start)
        status = self.spinapi.pb_inst_pbonly(int(self.flags,2), self.spinapi.Inst.BRANCH, start, self.spinapi.ms)
        self.check_error(status)
        ## Stop programming memory.
        status = self.spinapi.pb_stop_programming()
        self.check_error(status)
        
        ## Waiting for pb.start() to be called.
        return
    
    def loop_start(self, num_loops, ref, duration=0):
        """
        LOOP opcode.
        Selects the start emplacement of the loop.
        
        - num_loops: Number of loops.
        - ref: A reference string for loop_end() (required).
        - duration: Duration of the instruction (recommended). Channel states will stay the same.
        
        WARNING: Time cursor won't update. Do not use in combinaison with other instruments if timing is important.
        The duration argument is recommended. If not specified, the branch instruction will merge with the next instruction.
        """
        self.opcode("LOOP", num_loops, duration=duration, ref=ref)
        return
        
    def loop_end(self, link_to, duration=0, ref=""):
        """
        END_LOOP opcode.
        Sets where the loop ends.

        - link_to: Reference string of the instruction to loop to.
        - ref: A reference string for eventual opcode (optional).
        - duration: Duration of the instruction (recommended). Channel states will stay the same.
        
        WARNING: Time cursor won't update. Do not use in combinaison with other instruments if timing is important.
        The duration argument is recommended. If not specified, the JSR instruction will merge with the next instruction.
        More info and examples in LabMaster documentation.
        """
        self.opcode("END_LOOP", link_to, duration=duration, ref=ref)
        return
        
    def preprocess(self):
        """
        Translate self.intructions list to a list of arguments ready for spinapi.pb_inst_pbonly().
        Trigger latency can be adjusted with self.adjust_trig_latency option. In this case, a time buffer is needed before first instruction.
        Will support opcodes, data fields and refs (see self.opcode() doc for more info).
        Automatic LONG_DELAY when needed.
        """
        result = []
        
        ## Unzip instructions
        instructions = [tuple(x) for x in (sorted(self.instructions))] + [(self.lab.total_duration, "", "", "", "")]
        time_list, channel_list, opcode_list, data_field_list, ref_list = zip(*instructions) 
        
        ## Make sure each ref is unique.
        for ref in ref_list:
            if ref != "" and ref_list.count(ref)>1:
                raise PulseBlasterUSBError, "Pulse blaster: each ref must be unique or an empty string."
        
        ## as refs are detected, they will be added to this ref_dict, with ref as the key and the address in pb memory as the value
        ref_dict = {}
        
        ## Set trigger latency if requested in options.
        if self.adjust_trig_latency:
            trigger_latency = 8.0/self.get_ref_freq()
        else:
            trigger_latency = 0
        
        ## First instruction is special.
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
                
        ## Go through all the instructions and condense them to spinapi.pb_inst_pbonly() arguments.
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
                    channel = channel_list[i] ## which channel to change
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

        ## In this final preprocess loop, replace refs for their matching address in pulse_blaster memory.
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
        
    
    def plot_loaded_sequence(self, show_channel="all", ax=None):
        """
        Show the sequence computed from the preprocess in a matplotlib figure. WARNING: opcodes are not implemented.
        
        
        - show_channel: A list of channels names to show.
                        If show_channel is "all", all channels in self.instructions will be used.
        - ax: Specify an ax on which to plot the loaded sequence. 
              If None, each channel will get its own new ax, on a new figure.
        """
            
        ## Select channels to plot.
        if show_channel=="all":
            channels = {}
            channel_values = list(set([inst[1] for inst in self.instructions if inst[1] != None]))
            for chan in channel_values:
                name = 'channel '+str(chan)
                for key, v in self.channels.items():
                    if chan==v:
                        name = key
                channels.update({name: chan})
                        
        else:
            channels = {key: self.channels[key] for key in show_channel}
                
        ## For a nicer looking time axis (x axis).
        prefix, c = nfu.plot_loaded_sequence_auto_label(self.lab)

        ## If ax is not specified, create a figure.
        if ax==None:
            fig, axes = plt.subplots(len(channels), sharex=True)
            if len(channels)==1:
                ax_ = axes
            else:
                ax_ = axes[-1]
            ax_.set_xlabel("Time ("+prefix+"s)")
            ## Span time for all experiment duration
            ax_.set_xlim([0, c*(self.lab.total_duration - self.lab.end_buffer)])
        
        ## Compute preprocess
        preprocess_result = self.preprocess()
        ## Plot each channel one by one.
        for i, (name, channel) in enumerate(sorted(channels.items())):
            if ax==None:
                ## Select ax corresponding to current channel.
                ax_ = axes[i]
            else:
                ## If an ax was specified, always use the specified ax.
                ax_ = ax
            
            ## Ax formatting
            ax_.yaxis.set_major_locator(plt.NullLocator())
            ax_.set_ylabel(name)
            
            ## Fill the plot for times when the channel is ON.
            timer=0
            for flags, opcode, _, duration in preprocess_result:
                if opcode != 0:
                    print "Opcode effects are not considered in the plot."
                    continue
                if flags[-channel]=="1":
                    ax_.fill_between([c*timer, c*timer+c*duration], 0, [1,1])
                timer+=duration

        plt.show()
        return
        
        
    def opcode(self, opcode_str, data_field, duration=0, ref=""):
        """
        Valid entries:
        opcode_str      data_field                  Note
        ------------------------------------------------------
        STOP            Not used                    -
        LOOP            # of loops                  Use loop_start() method instead.  -> SEE *WARNING*
        END_LOOP        ref string to loop start    Use loop_end() method instead.    -> SEE *WARNING*
        JSR             ref string to subroutine    Not tested.                       -> SEE *WARNING*
        RTS             Not used                    Not tested.                       -> SEE *WARNING*
        BRANCH          ref string to branch start  Use branch() method instead.      -> SEE *WARNING*
        LONG_DELAY      # of repetitions            Automatic in preprocess.
        WAIT            Not used                    -
        
        - ref: A reference string for eventual opcode (required for 'LOOP' and 'RTS').
        - duration: Duration of the instruction (recommended). Channel states will stay the same.
                  
        *WARNING*: Time cursor won't update. Do not use in combinaison with other instruments if timing is important.
        """
        if opcode_str not in self.available_opcodes():
            raise PulseBlasterUSBError, "Wrong opcode. \n"+textwrap.dedent(Pulse_blaster_USB.opcode.__doc__)
        self.keep_going()
        self.instructions.append([self.lab.time_cursor, None, opcode_str, data_field, ref])
        if duration > 0:
            self.lab.update_time_cursor(duration, None)
            self.keep_going()
        return
    
    def reset_warnings(self):
        """ 
        Reset show_warnings attributes to True. 
        Is called at the beginning of the scan function.
        """
        self.show_warning_no_inst = True
        return
    
    def RTS(self, ref, duration=0):
        """
        RTS opcode. Not tested.
        
        - ref: A reference string for the JSR opcode (required).
        - duration: Duration of the instruction (recommended). Channel states will stay the same.
        
        WARNING: Time cursor won't update. Do not use in combinaison with other instruments if timing is important.
        The duration argument is recommended. If not specified, the JSR instruction will merge with the next instruction.
        """
        self.opcode("RTS", 0, duration=duration, ref=ref)
        return
    
    def turn_on(self, channel, duration=None, opcode_str="", data_field=0, ref="", rewind=None):
        """
        Instruction to turn on specified channel.
        
        - duration: Duration of the instruction. If not specified, channel will stay ON indefinitely.
        - opcode_str: add an opcode to the instruction.
        - data_field: The data field used by the opcode, if opcode_str was specified.
        - ref: A reference string for eventual opcode (optional).
        - rewind: After updating time_cursor, go back in time by 'rewind' seconds.
                  If rewind is "start", go back to initial time cursor position. This will update self.total_duration but keep self.time_cursor the same.
        """
        channel = self.channel_format(channel)
        if opcode_str!="":
            self.opcode(opcode_str, data_field)
        if duration==None:
            self.instructions.append([self.lab.time_cursor, channel, self.spinapi.Inst.CONTINUE, 1, ref])
            self.lab.update_time_cursor(0., rewind)
        else:
            self.instructions.append([self.lab.time_cursor, channel, self.spinapi.Inst.CONTINUE, 1, ref])
            self.instructions.append([self.lab.time_cursor+duration, channel, self.spinapi.Inst.CONTINUE, 0, ""])
            self.lab.update_time_cursor(duration, rewind)
        return
        
    def turn_off(self, channel, duration=None, opcode_str="", ref="", rewind=None):
        """
        Instruction to turn off specified channel.
        
        - duration: Duration of the instruction. If not specified, channel will stay OFF indefinitely.
        - opcode_str: add an opcode to the instruction.
        - data_field: The data field used by the opcode, if opcode_str was specified.
        - ref: A reference string for eventual opcode (optional).
        - rewind: After updating time_cursor, go back in time by 'rewind' seconds.
                  If rewind is "start", go back to initial time cursor position. This will update self.total_duration but keep self.time_cursor the same.
        """
        channel = self.channel_format(channel)
        if opcode_str!="":
            self.opcode(opcode_str, ref)
        if duration==None:
            self.instructions.append([self.lab.time_cursor, channel, self.spinapi.Inst.CONTINUE, 0, ref])
            self.lab.update_time_cursor(0., rewind)
        else:
            self.instructions.append([self.lab.time_cursor, channel, self.spinapi.Inst.CONTINUE, 0, ref])
            self.instructions.append([self.lab.time_cursor+duration, channel, self.spinapi.Inst.CONTINUE, 1, ""])
            self.lab.update_time_cursor(duration, rewind)
        return
        
    def channel_format(self, name):
        """
        Return channel corresponding to name.
        If name is a string, channel_format() will look for channels added using self.add_channels() and return the corresponding channel number.
        If name is an int, channel_format() will return it untouched.
        """
        if isinstance(name, str):
            channel = self.channels[name]
        else: 
            if 1 <= name <= 24:
                channel = int(name)
            else:
                raise PulseBlasterUSBError, "Pulse blaster channel channel must be between 1 and 24 (included)"
        return channel
        
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
        
