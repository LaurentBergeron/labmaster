"""
Definition of Pulse Blaster Instrument classes.

Current classes: 
- Pulse_blaster_DDSII300
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

class Pulse_blaster_DDSII300(Instrument):
    """
    Class allowing to control an SpinCore PulseBlasterDDS-II-300 instrument.
    
    Installation procedure: 
    1) Install 64-bit spinapi drivers. http://www.spincore.com/support/spinapi/SpinAPI_Main.shtml
    """

    def __init__(self, name, parent):
        """
        Inherit from Instrument. 
        Import wrapper and initialize instrument drivers.
        Set all channels to 0 V.
        Set a default pulse and initialize pulse registers to those values.
        - name: Name to give to the instrument.
        - parent: A reference to the lab instance hosting the instrument.
        """
        ##-------------------------------------------- OPTIONS --------------------------------------------##
        self.verbose = False                    ## Print the status of each driver function call.
        self.adjust_trig_latency = False        ## Adjust first duration to remove the 8 clock cycles trigger latency (needs a time buffer at the start of sequence).
        self.ref_freq = 75*MHz                  ## Recommended to run at 75 MHz
        ##-------------------------------------------------------------------------------------------------##
        ## Inherit from Instrument
        Instrument.__init__(self, name, parent, use_memory=True)
        ## Reset show_warning attributes to True.
        self.reset_warnings()
        ## spinapi wrapper
        self.spinapi = importlib.import_module("mod.instruments.wrappers.dll_spinapi") ## dll wrapper
        ## Dictionary with channel names as keys and their respective channel as values.
        self.channels = {}
        ## Dictionary with registers for RF1 (DDS0) and RF2 (DDS1) (leave empty at this point)
        self.registers = {'RF1':{'freq':[], 'phase':[], 'amp':[]}, 'RF2':{'freq':[], 'phase':[], 'amp':[]}}
        ## Set default rf_channel (to use when rf_channel is not specified in a function call).
        self.default_rf_channel = 'RF1'
        ## Default values are dictionaries with values defined below in set_default_pulse. Key of the dictionary is the channel.
        self.default_delay = {}
        self.default_length = {}
        self.default_freq = {}
        self.default_phase = {}
        self.default_amp = {}
        self.set_default_pulse('RF1', delay=ms, length=us, freq=MHz, phase=0, amp=1.)
        self.set_default_pulse('RF2', delay=ms, length=us, freq=MHz, phase=0, amp=1.)
        ## States of the channels. Channel one is on the right, channel 12 on the left. 
        self.flags = "000000000000"
        ## Initialize drivers.
        status = self.spinapi.pb_init()
        self.check_error(status)
        ## Set clock frequency.
        self.spinapi.pb_core_clock(self.ref_freq/1e6)
        ## Clear registers and add default pulses to registers.
        self.reset_registers()
        ## Turn all channels off.
        self.all_channels_off()
        print('connected to PulseBlasterDDSII300.')
        return 
    
    def rf_channel_format(self, rf_channel):
        """
        returns correct formatting for rf_channel. 
        if input is None, default_rf_channel is used.
        """
        if rf_channel==None:
            rf_channel = self.default_rf_channel
        if rf_channel in (1,2):
            rf_channel = 'RF'+str(rf_channel)            
        if not (rf_channel in ('RF1','RF2')):
            raise PulseBlasterDDSII300Error("Wrong format for rf_channel input. Should be 'RF1' or 'RF2'")
        return rf_channel
        
    def rf_channel_str2int(self, rf_channel_str):
        """
        From 'RF1', 'RF2' to 1, 2
        """
        rf_channel_str = self.rf_channel_format(rf_channel_str)
        return int(rf_channel_str[-1:])
    
    def set_default_pulse(self, rf_channel=None, delay=None, length=None, freq=None, phase=None, amp=None, offset=None, shape=None):
        """
        Changes many parameters of a pulse at the same time.
        Does not load the parameters into the board memory. Using self.load_memory() or self.cw() will automatically load them into the registers.
        Calling self.reset_registers() will clear registers and then load the default pulse into the registers.
        """
        rf_channel = self.rf_channel_format(rf_channel)
        if delay!=None:
            self.default_delay[rf_channel] = delay
        if length!=None:
            self.default_length[rf_channel] = length
        if freq!=None:
            self.default_freq[rf_channel] = freq
        if phase!=None:
            self.default_phase[rf_channel] = phase
        if amp!=None:
            self.default_amp[rf_channel] = amp
        if shape!=None:
            self.default_shape[rf_channel] = shape
        return
        
    def string_sequence(self, string, BB1=False, pulse_factor="length", rf_channel=None):
        """ 
        Input pulse sequence instructions as a string. Separe options shown below by comas in a string.
        Not sensitive to spaces, tabs ('\\t') and returns ('\\r' or '\\n').
        Is based on default pulse parameters (delay, length, amplitude, frequency, phase and shape).
        Example of valid string input: 'tau, X/2, tau*3, -Y, tau'.
        
        'X', '-X', 'Y' or '-Y' will select the phase (respectively 0, 180, 90 and 270 degrees). This phase is added to self.default_phase.
        
        'tau' or 't' is for a delay. 
        The duration of tau is the default delay.
        
        A factor can be applied to both pulses and delays. 
        The factor can be multipled using '*' or divided using '/'.
        The factor has to follow the command. For example, 'tau*2' is valid but not '2*tau'.
        
        - pulse_factor: By default, the factor applies to the pulse length. Input pulse_factor='amp' to apply the factor to the pulse amplitude.
                        For delays, the factor always applies on duration.
        - BB1: Convert all pulses to their BB1 equivalent. If this option is activated, the only available factor is 0.5.
        """
        rf_channel = self.rf_channel_format(rf_channel)
        clean_string = (string.replace(" ", "").replace("\n", "").replace("\t", "").replace("\r", ""))
        for tok, token in enumerate(clean_string.split(",")):
            phase = self.default_phase[rf_channel]
            length = self.default_length[rf_channel]
            tau = self.default_delay[rf_channel]
            amp = self.default_amp[rf_channel]

            try:
                if ("t"==token.split("/")[0].split("*")[0]) or ("tau"==token.split("/")[0].split("*")[0]):
                    if "/" in token:
                        factor = 1/float(token.split("/")[-1])
                    elif "*" in token:
                        factor = float(token.split("*")[-1])
                    else:
                        factor = 1
                    self.lab.delay(tau*factor)
                elif ("X" in token) or ("Y" in token):
                    ## Phase to add to default
                    if "-X" in token:
                        phase+=180
                    elif "-Y" in token:
                        phase+=270
                    elif "X" in token:
                        phase+=0
                    elif "Y" in token:
                        phase+=90
                    ## Pulse length (or amp) divider/multiplier
                    if "/" in token:
                        factor = 1/float(token.split("/")[-1])
                    elif "*" in token:
                        factor = float(token.split("*")[-1])
                    else:
                        factor = 1
                    if pulse_factor=="length":
                        length*=factor
                    elif pulse_factor=="amp":
                        amp*=factor
                    ## BB1 option
                    if BB1:
                        if factor==1:
                            self.pulse_BB1_pi(channel=channel, pi_len=self.default_length[channel], phase=phase, pi_amp=amp)
                        elif factor==0.5:
                            self.pulse_BB1_piby2(channel=channel, pi_len=self.default_length[channel], piby2_len=length, phase=phase, pi_amp=self.default_amp[channel],  piby2_amp=amp)
                        else:
                            raise PulseBlasterDDSII300Error("BB1 option is valid for pi or pi/2 pulses only.")
                    else:
                        self.pulse(rf_channel=rf_channel, length=length, phase=phase, amp=amp)

                elif token=="":
                    pass
                else:
                    raise ValueError
            except ValueError:
                raise PulseBlasterDDSII300Error("Token '"+str(token)+"' for "+self.__class__.__name__+"."+str(inspect.stack()[0][3])+" was not recognized. \n\n"+self.__class__.__name__+"."+str(inspect.stack()[0][3])+" docstring:\n"+textwrap.dedent(PulseBlasterDDSII300.string_sequence.__doc__)+"\n")
        return
        
    
    def clear_freq_register(self, rf_channel=None):
        """
        Empties the frequency register of specified rf channel.
        """
        rf_channel = self.rf_channel_format(rf_channel)
        status = self.spinapi.pb_select_dds(self.rf_channel_str2int(rf_channel)-1)
        self.check_error(status)
        self.registers[rf_channel]['freq'] = []
        status = self.spinapi.pb_start_programming(self.spinapi.FREQ_REGS)
        self.check_error(status)
        status = self.spinapi.pb_stop_programming()
        self.check_error(status)
        return
        
    def clear_phase_register(self, rf_channel=None):
        """
        Empties the phase register of specified rf channel.
        """
        rf_channel = self.rf_channel_format(rf_channel)
        status = self.spinapi.pb_select_dds(self.rf_channel_str2int(rf_channel)-1)
        self.check_error(status)
        self.registers[rf_channel]['phase'] = []
        status = self.spinapi.pb_start_programming(self.spinapi.TX_PHASE_REGS)
        self.check_error(status)
        status = self.spinapi.pb_stop_programming()
        self.check_error(status)
        return
        
    def clear_amp_register(self, rf_channel=None):
        """
        Empties the amplitude register of specified rf channel.
        Actually doesn't clear anything on the board (amplitude register works differently than phase and frequency registers), but makes LabMaster think it's empty, so it's equivalent.
        """
        rf_channel = self.rf_channel_format(rf_channel)
        status = self.spinapi.pb_select_dds(self.rf_channel_str2int(rf_channel)-1)
        self.check_error(status)
        self.registers[rf_channel]['amp'] = []
        return
    
    def clear_registers(self):
        """
        Clear all registers.
        """
        for rf_channel in ('RF1','RF2'):
            self.clear_freq_register(rf_channel)
            self.clear_phase_register(rf_channel)
            self.clear_amp_register(rf_channel)
        return
        
    def reset_registers(self):
        """
        Clear registers and add default pulses to registers.
        """
        self.clear_registers()
        for rf_channel in ('RF1','RF2'):
            self.add_freq_to_register(rf_channel, self.default_freq[rf_channel])
            self.add_phase_to_register(rf_channel, self.default_phase[rf_channel])
            self.add_amp_to_register(rf_channel, self.default_amp[rf_channel])
        return
    
    def add_freq_to_register(self, rf_channel, freq_to_add):
        """
        Add input frequency to the next register on the specified rf channel.
        freq_to_add: from 5 kHz to 100 MHz (specify in Hz)
        """
        rf_channel = self.rf_channel_format(rf_channel)
        if not (5*kHz <= freq_to_add <= 100*MHz): 
            raise PulseBlasterDDSII300Error('Frequency added to register should be between 5 kHz and 100 MHz.')
        if len(self.registers[rf_channel]['freq']) > 15:
            raise PulseBlasterDDSII300Error('Maximum number of frequency registers reached ('+rf_channel+').')
        ## Select RF channel for programming registers
        self.spinapi.pb_select_dds(self.rf_channel_str2int(rf_channel)-1)
        ## Update registers dictionary
        self.registers[rf_channel]['freq'].append(freq_to_add)
        ## Program frequency register
        status = self.spinapi.pb_start_programming(self.spinapi.FREQ_REGS)
        self.check_error(status)
        for freq in self.registers[rf_channel]['freq']:
            ## pb_set_freq uses MHz
            status = self.spinapi.pb_set_freq(freq*1e-6)
            self.check_error(status)
        status = self.spinapi.pb_stop_programming()
        self.check_error(status)
        return
   
    def add_phase_to_register(self, rf_channel, phase_to_add):
        """
        Add input phase to the next register on the specified rf channel.
        phase_to_add: from 0 to 360 (in degrees)
        """
        rf_channel = self.rf_channel_format(rf_channel)
        if not (0 <= phase_to_add < 360): 
            raise PulseBlasterDDSII300Error('Phase added to register should be between 0 and 360.')
        if len(self.registers[rf_channel]['phase']) > 7:
            raise PulseBlasterDDSII300Error('Maximum number of phase registers reached ('+rf_channel+').')
        ## Select RF channel for programming registers
        self.spinapi.pb_select_dds(self.rf_channel_str2int(rf_channel)-1)
        ## Update registers dictionary
        self.registers[rf_channel]['phase'].append(phase_to_add)
        status = self.spinapi.pb_start_programming(self.spinapi.TX_PHASE_REGS)
        ## Program phase register
        self.check_error(status)
        for phase in self.registers[rf_channel]['phase']:
            ## pb_set_phase uses degrees
            status = self.spinapi.pb_set_phase(phase)
            self.check_error(status)
        status = self.spinapi.pb_stop_programming()
        self.check_error(status)
        return
        
    def add_amp_to_register(self, rf_channel, amp_to_add):
        """
        Add input amplitude to the next register on the specified rf channel.
        amp_to_add: from 0.0 to 1.0
        """
        rf_channel = self.rf_channel_format(rf_channel)
        if not (0. <= amp_to_add <= 1.): 
            raise PulseBlasterDDSII300Error('Amplitude added to register should be between 0.0 and 1.0.')
        if len(self.registers[rf_channel]['amp']) > 3:
            raise PulseBlasterDDSII300Error('Maximum number of amplitude registers reached ('+rf_channel+').')
        ## Select RF channel for programming registers
        self.spinapi.pb_select_dds(self.rf_channel_str2int(rf_channel)-1)
        ## Update registers dictionary
        self.registers[rf_channel]['amp'].append(amp_to_add)
        ## Program frequency register. For some reason it works differently than frequency and phase programming (there is no need for pb_start_programming and pb_stop_programming function calls.
        register_address = len(self.registers[rf_channel]['amp']) - 1
        status = self.spinapi.pb_set_amp(amp_to_add, register_address)
        self.check_error(status)
        return
    
    def clear_channel_names(self):
        """
        Clear channel name aliases
        """
        self.channels = {}
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
            raise PulseBlasterDDSII300Error("Failed to add channel, "+name+" is a reserved name.")
        if not (0 < channel < 13):
            raise PulseBlasterDDSII300Error("Failed to add channel, "+name+" must be between 1 and 12.")
        for key, channel_ in list(self.channels.items()):
            if channel==channel_ and key!=name:
                raise PulseBlasterDDSII300Error("Channel "+str(channel)+" is already assigned to '"+key+"'.")
        self.channels[name] = channel
        return

    def all_channels_on(self):
        """Set all channels on."""
        ## Stop generation (states of the channels will stay the same as when they stopped).
        status = self.spinapi.pb_stop()
        self.check_error(status)
        ## Start a PULSE_PROGRAM (usual stuff).
        status = self.spinapi.pb_start_programming(self.spinapi.PULSE_PROGRAM)
        self.check_error(status)
        ## Branch two instructions to loop zeros.
        self.flags = "1"*12
        start = self.spinapi.pb_inst_dds2(0, 0, 0, self.spinapi.TX_DISABLE, self.spinapi.NO_PHASE_RESET, \
                                          0, 0, 0, self.spinapi.TX_DISABLE, self.spinapi.NO_PHASE_RESET, \
                                          int(self.flags,2), self.spinapi.Inst.CONTINUE, 0, self.spinapi.ms)
        self.check_error(start)
        start = self.spinapi.pb_inst_dds2(0, 0, 0, self.spinapi.TX_DISABLE, self.spinapi.NO_PHASE_RESET, \
                                          0, 0, 0, self.spinapi.TX_DISABLE, self.spinapi.NO_PHASE_RESET, \
                                          int(self.flags,2), self.spinapi.Inst.BRANCH, start, self.spinapi.ms)
        self.check_error(status)
        ## Stop programming.
        status = self.spinapi.pb_stop_programming()
        self.check_error(status)
        ## Start generation.
        self.start()
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
        self.flags = "0"*12
        start = self.spinapi.pb_inst_dds2(0, 0, 0, self.spinapi.TX_DISABLE, self.spinapi.NO_PHASE_RESET, \
                                          0, 0, 0, self.spinapi.TX_DISABLE, self.spinapi.NO_PHASE_RESET, \
                                          int(self.flags,2), self.spinapi.Inst.CONTINUE, 0, self.spinapi.ms)
        self.check_error(start)
        start = self.spinapi.pb_inst_dds2(0, 0, 0, self.spinapi.TX_DISABLE, self.spinapi.NO_PHASE_RESET, \
                                          0, 0, 0, self.spinapi.TX_DISABLE, self.spinapi.NO_PHASE_RESET, \
                                          int(self.flags,2), self.spinapi.Inst.BRANCH, start, self.spinapi.ms)
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
            print("pb:", status)
        if status == -1:
            raise PulseBlasterDDSII300Error('Unknown error.')
        if status < -1:
            error = self.spinapi.pb_get_error()
            raise PulseBlasterDDSII300Error(error)
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
        Load PulseBlasterUSB memory using the spinapi.pb_inst_dds2() function.
        After the programmed sequence, all channels are looped to zero ad infinitum.
        
        TODO: Add frequencies
        """
        if self.instructions==[]:
            if self.show_warning_no_inst:
                print("PulseBlasterDDS-II-300: No instructions detected. self.load_memory() skipped.")
                self.show_warning_no_inst = False
            return
        ## Stop previous generation.
        status = self.spinapi.pb_stop() 
        self.check_error(status)
        ## Start programming memory.
        status = self.spinapi.pb_start_programming(self.spinapi.PULSE_PROGRAM)
        self.check_error(status)
        
        ## Load results from self.preprocess() using spinapi.pb_inst_dds2 commands.
        for TTL_params, RF1_params, RF2_params in self.preprocess():
            flags, opcode, data_field, duration = TTL_params
            status = self.spinapi.pb_inst_dds2(*RF1_params, \
                                               *RF2_params, \
                                               int(flags,2), opcode, data_field, duration*1e9)
            self.check_error(status)

        ## All channels offs.
        self.flags = "0"*12
        start = self.spinapi.pb_inst_dds2(0, 0, 0, self.spinapi.TX_DISABLE, self.spinapi.NO_PHASE_RESET, \
                                          0, 0, 0, self.spinapi.TX_DISABLE, self.spinapi.NO_PHASE_RESET, \
                                          int(self.flags,2), self.spinapi.Inst.CONTINUE, 0, self.spinapi.ms)
        self.check_error(start)
        status = self.spinapi.pb_inst_dds2(0, 0, 0, self.spinapi.TX_DISABLE, self.spinapi.NO_PHASE_RESET, \
                                          0, 0, 0, self.spinapi.TX_DISABLE, self.spinapi.NO_PHASE_RESET, \
                                          int(self.flags,2), self.spinapi.Inst.BRANCH, start, self.spinapi.ms)
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
        Translate self.intructions list to a list of arguments ready for spinapi.pb_inst_dds2().
        Trigger latency can be adjusted with self.adjust_trig_latency option. In this case, a time buffer is needed before first instruction.
        Supports opcodes, data fields and refs (see self.opcode() doc for more info).
        Supports pulse instructions given by self.pulse()
        Automatic LONG_DELAY when needed (not sure how it works if RF is enabled during a long delay - there might be phase issues?)
        """
        result = []
        
        ## Unzip instructions
        instructions = [tuple(x) for x in (sorted(self.instructions, key=lambda x: x[0]))] + [(self.lab.total_duration, "", "", "", "", ())]
        time_list, channel_list, opcode_list, data_field_list, ref_list = list(zip(*instructions)) 
        
        ## Make sure each ref is unique.
        for ref in ref_list:
            if ref != "" and ref_list.count(ref)>1:
                raise PulseBlasterDDSII300Error("Pulse blaster: each ref must be unique or an empty string.")
        
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
        self.flags = "0"*12
        if time_list[0] > trigger_latency:
            duration = time_list[0]-trigger_latency
            if duration != 0:
                opcode = self.spinapi.Inst.CONTINUE
                data_field = 0
                opcode, data_field, duration = self.autolongdelay(opcode, data_field, duration) ## will add a LONG_DELAY opcode if needed.
                TTL_params = (self.flags, opcode, data_field, duration)
                RF1_params = (0,0,0,self.spinapi.TX_DISABLE, self.spinapi.NO_PHASE_RESET)
                RF2_params = (0,0,0,self.spinapi.TX_DISABLE, self.spinapi.NO_PHASE_RESET)
                result.append([TTL_params, RF1_params, RF2_params])
        else:
            if self.adjust_trig_latency:
                raise PulseBlasterDDSII300Error("You need to add a time buffer at the start of sequence when adjusting for trigger latency.")
                
        ref_dict["ZERO_TIME"] = 0 ## to loop/branch to the start, use ZERO_TIME ref.
        
        ## Go through all the instructions and condense them to spinapi.pb_inst_dds2() arguments.
        RF1_params = (0,0,0,self.spinapi.TX_DISABLE, self.spinapi.NO_PHASE_RESET) ## just for the start. will change when a pulse instruction is detected.
        RF2_params = (0,0,0,self.spinapi.TX_DISABLE, self.spinapi.NO_PHASE_RESET) ## just for the start. will change when a pulse instruction is detected.
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
                        raise PulseBlasterDDSII300Error("Two different refs detected for the same time.")
                    else:
                        ref = ref_list[i]
                ## Check and assign opcodes/data_field
                if opcode_list[i] in self.available_opcodes():
                    if opcode != self.spinapi.Inst.CONTINUE:
                        raise PulseBlasterDDSII300Error("Two different opcode instructions detected at the same time.")
                    else:
                        opcode = self.spinapi.Inst.__dict__[opcode_list[i]]  ## ready for pulse blaster communication.
                        data_field = data_field_list[i] ## data_field: for BRANCH and END_LOOP opcodes, data_field stays the ref string to link to. 
                                                        ## For all other opcodes, data_field is ready for pulse blaster communication.
                ## Keep going meaning keep channels as they are. Useful to split a delay without using opcodes.
                elif opcode_list[i]=="KEEP_GOING": 
                    pass
                ## The start of a RF pulse
                elif opcode_list[i]=="pulse":
                    ## Load pulse instructions
                    rf_channel, phase, amp, freq = data_field_list[i]    
                    ## Get the registers on which pulse parameters are saved on the board.
                    freq_register = self.registers[rf_channel]['freq'].index(freq)
                    phase_register = self.registers[rf_channel]['phase'].index(phase)
                    amp_register = self.registers[rf_channel]['amp'].index(amp)
                    if rf_channel=='RF1':
                        ## enable RF1 and leave RF2 untouched
                        RF1_enable = self.spinapi.TX_ENABLE
                        RF1_params = (freq_register, phase_register, amp_register, RF1_enable, self.spinapi.NO_PHASE_RESET)
                    elif rf_channel=='RF2':
                        ## enable RF2 and leave RF1 untouched
                        RF2_enable = self.spinapi.TX_ENABLE
                        RF2_params = (freq_register, phase_register, amp_register, RF2_enable, self.spinapi.NO_PHASE_RESET)
                ## The end of a RF pulse 
                elif opcode_list[i]=="pulse-end":
                    rf_channel, _, _, _ = data_field_list[i]    
                    if rf_channel=='RF1':
                        ## disable RF1 and leave RF2 untouched
                        RF1_enable = self.spinapi.TX_DISABLE
                        RF1_params = (0, 0, 0, RF1_enable, self.spinapi.NO_PHASE_RESET)
                    elif rf_channel=='RF2':
                        ## disable RF2 and leave RF1 untouched
                        RF2_enable = self.spinapi.TX_DISABLE
                        RF2_params = (0, 0, 0, RF2_enable, self.spinapi.NO_PHASE_RESET)
                    pass
                ## If no opcode detected, it's a turn_on/turn_off situation.
                else:
                    channel = channel_list[i] ## which channel to change
                    new_bit = str(data_field_list[i]) ## On or off ?
                    self.flags = self.flags[:12-channel] + new_bit + self.flags[13-channel:] ## update flags
                duration = time_list[i+1] - time_list[i_saved] 
                if (duration >= 5.0/self.get_ref_freq()): ## minimum pulse length is 5 clock cycles. If duration is smaller than that, repeat loop without appending result (flags will remain changed).
                    opcode, data_field, duration = self.autolongdelay(opcode, data_field, duration) ## will add a LONG_DELAY opcode if needed.
                    TTL_params = (self.flags, opcode, data_field, duration)
                    result.append([TTL_params, RF1_params, RF2_params])
                    if ref!="":
                        ref_dict[ref]=len(result)-1
                    break ## break 'while' statement if a result was appended.
                i+=1
            i+=1

        ## In this final preprocess loop, replace refs for their matching address in pulse_blaster memory.
        final_result = []
        for i, (x, RF1_params, RF2_params) in enumerate(result):
            flags, opcode, data_field, duration = x
            if opcode==self.spinapi.Inst.END_LOOP or opcode==self.spinapi.Inst.BRANCH:
                try:
                    data_field = ref_dict[data_field]
                except KeyError:
                    raise PulseBlasterDDSII300Error("ref '"+data_field+"' not found.")
            final_result.append([[flags, opcode, data_field, duration], RF1_params, RF2_params])
        
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
                raise PulseBlasterDDSII300Error("You asked for a delay longer than %0.0f days."%(ultra_max_duration/60./60./24.))
            elif duration > max_duration:  
                opcode = self.spinapi.Inst.LONG_DELAY
                data_field = int(duration//max_duration + 1) ## number of repetition. total duration will be duration*data_field
                duration = duration/float(data_field)
            else:
                pass
        else:
            if duration > max_duration:
                raise PulseBlasterDDSII300Error("Autolongdelay can't be called because the opcode is already taken.")
            else:
                pass
        return opcode, data_field, duration
        
    
    def plot_loaded_sequence(self, show_channel="all", ax=None):
        """
        Show the sequence computed from the preprocess in a matplotlib figure. WARNING: pulses and opcodes are not implemented.
        
        
        - show_channel: A list of channels names to show.
                        If show_channel is "all", all channels in self.instructions will be used.
        - ax: Specify an ax on which to plot the loaded sequence. 
              If None, each channel will get its own new ax, on a new figure.

        TODO: Add pulses.
        """
            
        ## Select channels to plot.
        if show_channel=="all":
            channels = {}
            channel_values = list(set([inst[1] for inst in self.instructions if inst[1] != None]))
            for chan in channel_values:
                name = 'channel '+str(chan)
                for key, v in list(self.channels.items()):
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
            ax_.set_xlim([0, c*(self.lab.total_duration)])
        
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
                    print("Opcode effects are not considered in the plot.")
                    continue
                if flags[-channel]=="1":
                    ax_.fill_between([c*timer, c*timer+c*duration], 0, [1,1])
                timer+=duration

        plt.show()
        return
    
    def pulse(self, rf_channel=None, length=None, phase=None, amp=None, freq=None, rewind=False, opcode_str="", data_field=0, ref=""):
        """
        Instruction to add a pulse.
        
        - length, phase, amp, freq: Parameters of the pulse. If not specified, defaults will be used.
        - opcode_str: add an opcode to the instruction.
        - data_field: The data field used by the opcode, if opcode_str was specified.
        - ref: A reference string for eventual opcode (optional).
        - rewind: After updating time_cursor, go back in time by 'rewind' seconds.
                  If rewind is "start", go back to initial time cursor position. This will update self.total_duration but keep self.time_cursor the same.
        """
        ## Use default values if inputs were not specified
        rf_channel = self.rf_channel_format(rf_channel)
        if length==None:
            length = self.default_length[rf_channel]
        if phase==None:
            phase = self.default_phase[rf_channel]
        if amp==None:
            amp = self.default_amp[rf_channel]
        if freq==None:
            freq = self.default_freq[rf_channel]
        
        # phase = (phase + self.lab.time_cursor*freq)%360
        
        ## Add opcode instruction if needed
        if opcode_str!="":
            self.opcode(opcode_str, data_field)
        
        ## Add specified freq, phase and amp to registers if they are not already there.
        if not freq in self.registers[rf_channel]['freq']:
            self.add_freq_to_register(rf_channel, freq)
        if not phase in self.registers[rf_channel]['phase']:
            self.add_phase_to_register(rf_channel, phase)            
        if not amp in self.registers[rf_channel]['amp']:
            self.add_amp_to_register(rf_channel, amp)        
        
        ## Update instructions
        RF_params = (rf_channel, phase, amp, freq)
        self.instructions.append([self.lab.time_cursor, None, "pulse", RF_params, ref])
        self.instructions.append([self.lab.time_cursor + length, None, "pulse-end", RF_params, ""])
        self.lab.update_time_cursor(length, rewind)
        return
    

    def cw(self, rf_channel=None, freq=None, amp=None):
        """
        Spit a continous wave function of specified frequency and amplitude.
        If arguments are omitted, defaults will be used.
        If rf_channel=='BOTH', freq and amp should be lists with two items. First item for RF1, second item for RF2. Defaults will replace None values as usual.
        """
        ## Replace None values by default settings.
        if rf_channel=='BOTH':
            if amp==None:
                amp = [self.default_amp['RF1'], self.default_amp['RF2']]
            else:
                amp = [self.default_amp['RF'+str(i+1)] if amp[i]==None else amp[i] for i in range(2)]
            if freq==None:
                freq = [self.default_freq['RF1'], self.default_freq['RF2']]
            else:
                freq = [self.default_freq['RF'+str(i+1)] if freq[i]==None else freq[i] for i in range(2)]
        else:
            rf_channel = self.rf_channel_format(rf_channel)
            if amp==None:
                amp = self.default_amp[rf_channel]
            if freq==None:
                freq = self.default_freq[rf_channel]
        amp = float(amp)
        freq = float(freq)
        ## Empty instructions. Can't use intructions if a cw is being generated.
        self.lab.reset_instructions()
        
        ### Program the cw        
        ## Stop previous generation.
        status = self.spinapi.pb_stop() 
        self.check_error(status)
        
        
        
        ## Add specified freq, phase and amp to registers if they are not already there.
        if rf_channel=='BOTH':
            for i in range(2):
                if not (freq[i] in self.registers['RF'+str(i+1)]['freq']):
                    self.add_freq_to_register('RF'+str(i+1), freq[i])       
                if not (amp[i] in self.registers['RF'+str(i+1)]['amp']):
                    self.add_amp_to_register('RF'+str(i+1), amp[i])
        else:
            if not (freq in self.registers[rf_channel]['freq']):
                self.add_freq_to_register(rf_channel, freq)       
            if not (amp in self.registers[rf_channel]['amp']):
                self.add_amp_to_register(rf_channel, amp)
                stop
        
        ## Start programming memory.
        status = self.spinapi.pb_start_programming(self.spinapi.PULSE_PROGRAM)
        self.check_error(status)


        if rf_channel=='BOTH':
            ## Get the registers on which pulse parameters are saved on the board.
            freq_register_RF1 = self.registers['RF1']['freq'].index(freq[0])
            amp_register_RF1 = self.registers['RF1']['amp'].index(amp[0])
            freq_register_RF2 = self.registers['RF2']['freq'].index(freq[1])
            amp_register_RF2 = self.registers['RF2']['amp'].index(amp[1])
            ## Prepare arguments for pb_inst_dds2
            RF1_params = (freq_register_RF1, 0, amp_register_RF1, self.spinapi.TX_ENABLE, self.spinapi.NO_PHASE_RESET)
            RF2_params = (freq_register_RF2, 0, amp_register_RF2, self.spinapi.TX_ENABLE, self.spinapi.NO_PHASE_RESET)
        else:
            ## Get the registers on which pulse parameters are saved on the board.
            freq_register = self.registers[rf_channel]['freq'].index(freq)
            amp_register = self.registers[rf_channel]['amp'].index(amp)
            ## Prepare arguments for pb_inst_dds2
            if rf_channel=='RF1':
                RF1_params = (freq_register, 0, amp_register, self.spinapi.TX_ENABLE, self.spinapi.NO_PHASE_RESET)
                RF2_params = (0, 0, 0, self.spinapi.TX_DISABLE, self.spinapi.NO_PHASE_RESET)
            elif rf_channel=='RF2':
                RF1_params = (0, 0, 0, self.spinapi.TX_DISABLE, self.spinapi.NO_PHASE_RESET)
                RF2_params = (freq_register, 0, amp_register, self.spinapi.TX_ENABLE, self.spinapi.NO_PHASE_RESET)
        
        self.flags = "0"*12 ## Deactivate TTL channels during a cw.
        start = self.spinapi.pb_inst_dds2(*RF1_params, \
                                           *RF2_params, \
                                           int(self.flags,2), self.spinapi.Inst.CONTINUE, 0, 50e9)
        self.check_error(start)
        status = self.spinapi.pb_inst_dds2(*RF1_params, \
                                           *RF2_params, \
                                           int(self.flags,2), self.spinapi.Inst.BRANCH, start, 50e9)
        self.check_error(status)

        ## Stop programming memory.
        status = self.spinapi.pb_stop_programming()
        self.check_error(status)
                
        
        ## Initiate the cw.
        self.start()
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
            raise PulseBlasterDDSII300Error("Wrong opcode. \n"+textwrap.dedent(Pulse_blaster_DDSII300.opcode.__doc__))
        self.keep_going()
        self.instructions.append([self.lab.time_cursor, None, opcode_str, data_field, ref])
        if duration > 0:
            self.lab.update_time_cursor(duration, None)
            self.keep_going()
        return
    
    def read_status(self):
        """
        Reads status of the PulseBlaster. 
        Buggy.
        """
        code = self.spinapi.pb_read_status()
        str_code = bin(code)[2:].zfill(4)
        if str_code[-1]=='1':
            print('Stopped')
        if str_code[-2]=='1':
            print('Reset (or stopped? bug)') ## Appears at times when it should be Stopped. 
        if str_code[-3]=='1':
            print('Running')
        if str_code[-4]=='1':
            print('Waiting')
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
    
    def turn_on(self, channel, duration=None, opcode_str="", data_field=0, ref="", rewind=False):
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
        
    def turn_off(self, channel, duration=None, opcode_str="", ref="", rewind=False):
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
            if 1 <= name <= 12:
                channel = int(name)
            else:
                raise PulseBlasterDDSII300Error("Pulse blaster channel channel must be between 1 and 12 (included)")
        return channel
        
    def start(self):
        """Start generation of the loaded sequence."""
        status = self.spinapi.pb_reset()
        self.check_error(status)
        status = self.spinapi.pb_start()
        self.check_error(status)
        return


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
        self.spinapi = importlib.import_module("mod.instruments.wrappers.dll_spinapi") ## dll wrapper
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
        print('connected to PulseBlasterUSB!.')
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
        
        TODO: should be named add_channel_alias 
        """
        if name in self.available_opcodes():
            raise PulseBlasterUSBError("Failed to add channel, "+name+" is a reserved name.")
        if not (0 < channel < 25):
            raise PulseBlasterUSBError("Failed to add channel, "+name+" must be between 1 and 24.")
        for key, channel_ in list(self.channels.items()):
            if channel==channel_ and key!=name:
                raise PulseBlasterUSBError("Channel "+str(channel)+" is already assigned to '"+key+"'.")
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
            print("pb:", status)
        if status == -1:
            raise PulseBlasterUSBError('Unknown error.')
        if status < -1:
            error = self.spinapi.pb_get_error()
            raise PulseBlasterUSBError(error)
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
                print("PulseBlasterUSB!: No instructions detected. self.load_memory() skipped.")
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
            status = self.spinapi.pb_inst_pbonly(int(flags,2), opcode, data_field, duration*1e9)

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
        time_list, channel_list, opcode_list, data_field_list, ref_list = list(zip(*instructions)) 
        
        ## Make sure each ref is unique.
        for ref in ref_list:
            if ref != "" and ref_list.count(ref)>1:
                raise PulseBlasterUSBError("Pulse blaster: each ref must be unique or an empty string.")
        
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
                raise PulseBlasterUSBError("You need to add a time buffer at the start of sequence when adjusting for trigger latency.")
                
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
                        raise PulseBlasterUSBError("Two different refs detected at the same time.")
                    else:
                        ref = ref_list[i]
                ## Check and assign opcodes/data_field
                if opcode_list[i] in self.available_opcodes():
                    if opcode != self.spinapi.Inst.CONTINUE:
                        raise PulseBlasterUSBError("Two different opcode instructions detected at the same time.")
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
                    raise PulseBlasterUSBError("ref '"+data_field+"' not found.")
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
                raise PulseBlasterUSBError("You asked for a delay longer than %0.0f days."%(ultra_max_duration/60./60./24.))
            elif duration > max_duration:  
                opcode = self.spinapi.Inst.LONG_DELAY
                data_field = int(duration//max_duration + 1) ## number of repetition. total duration will be duration*data_field
                duration = duration/float(data_field)
            else:
                pass
        else:
            if duration > max_duration:
                raise PulseBlasterUSBError("Autolongdelay can't be called because the opcode is already taken.")
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
                for key, v in list(self.channels.items()):
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
            ax_.set_xlim([0, c*(self.lab.total_duration)])
        
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
                    print("Opcode effects are not considered in the plot.")
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
            raise PulseBlasterUSBError("Wrong opcode. \n"+textwrap.dedent(Pulse_blaster_USB.opcode.__doc__))
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
    
    def turn_on(self, channel, duration=None, opcode_str="", data_field=0, ref="", rewind=False):
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
        
    def turn_off(self, channel, duration=None, opcode_str="", ref="", rewind=False):
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
                raise PulseBlasterUSBError("Pulse blaster channel channel must be between 1 and 24 (included)")
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

class PulseBlasterDDSII300Error(nfu.LabMasterError):
    """Errors raised by the PulseBlasterUSB class or by the pulse blaster USB board itself."""
    pass      
        
