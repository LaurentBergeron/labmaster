"""
Definition of arbitrary waveform generator Instrument classes.

Current classes: 
- Awg_M8190A
"""
__author__ =  "Laurent Bergeron <laurent.bergeron4@gmail.com>"

## Base modules
import inspect
import numpy as np
import visa as vi
import ctypes as ct
import matplotlib.pyplot as plt
import importlib
import time
import os
import textwrap  ## Auto format documentation strings

## Homemade modules
from .wrappers import visa_types as vt
from ..units import *
from ..classes import Instrument
from .. import not_for_user
nfu = not_for_user


class Awg_M8190A(Instrument):
    """
    Class allowing to control a Keysight M8190A arbitrary waveform generator instrument.
    
    Installation procedure: 
    1) Good luck.*
    *Seriously, contact Keysight (or Kevin Morse if he's still around) to help you with that. The chassis drivers need to be up to date as well as the actual instrument drivers.
    """
    def __init__(self, name, parent, resource):
        """
        Inherit from Instrument. 
        Import wrappers and initialize instrument drivers.
        Set AWG initial parameters.
        - name: Name to give to the instrument.
        - parent: A reference to the lab instance hosting the instrument.
        - resource: Connection address.
        """
        ##------------------------------------------------ OPTIONS ------------------------------------------------##
        self.verbose = False                ## Print the status of each driver function call.
        self.adjust_trig_latency = True     ## Adjust first duration to remove the 10240 clock cycles trigger latency (needs a time buffer at the start of sequence).
        self.channels_to_load = ["1"]       ## Channels to use in the load_memory function.
        self.coupled = False                ## Option to couple channels.
        self.default_channel = "1"          ## Default channel used by methods.
        self.nyquist_threshold = 4          ## Nyquist sampling values for continous waveform (cw method). Min factor between frequency and sample rate.
        ##---------------------------------------------------------------------------------------------------------##
        ## Inherit from Instrument.
        Instrument.__init__(self, name, parent, use_memory=True)
        ## Import wrappers.
        self.AgM8190 = importlib.import_module("mod.instruments.wrappers.dll_AgM8190")
        self.wfmGenLib2 = importlib.import_module("mod.instruments.wrappers.dll_wfmGenLib2")
        ## AWG characteristics
        self.granularity = 64
        self.tick = (5*self.granularity) ## has to be >= 5*granularity and has to be a multiple of granularity.
        self.minimum_delay_count = 5*self.granularity + self.tick ## 5*granularity to account for minimum idle command, self.tick to account for padding.
        ## Default values are dictionaries with values defined below in set_default_pulse. Key of the dictionary is the channel.
        self.default_delay = {}
        self.default_length = {}
        self.default_freq = {}
        self.default_phase = {}
        self.default_amp = {}
        self.default_shape = {} ## shape of the envelope
        self.set_default_pulse(for_channel="1", delay=0, length=0, freq=0, phase=0, amp=1.0, shape="square")
        self.set_default_pulse(for_channel="2", delay=0, length=0, freq=0, phase=0, amp=1.0, shape="square")
        ## Visa type attributes
        self.session = vt.ViSession()
        self.error_code = vt.ViInt32()
        self.error_message = (vt.ViChar*256)()
        ## Reset show_warning attributes to True.
        self.reset_warnings()
        ## Initialize instrument drivers.
        current_dir = os.getcwd()
        status = self.AgM8190.init(resource, True, True, ct.byref(self.session))
        os.chdir(current_dir) ## on first init, Keysight changes the current directory in the console
        try:
            if self.verbose:
                print("AgM8190 init status: ", status)
            self.check_error(status)
            status = self.AgM8190.reset(self.session)
            self.check_error(status)
            self.set_ref_clock_route("AXI")
            self.set_sample_clock_output_route("internal")
            self.set_sample_rate(9e9)
            self.set_channel_coupling("off")
            for channel in ("1", "2"):
                self.abort_generation(channel=channel)
                ## Set bit mode to 12-bit (14-bit is not available anyway)
                status = self.AgM8190.SetAttributeViInt32(self.session, channel, self.AgM8190.ATTR_ARBITRARY_BIT_RESOLUTION_MODE, self.AgM8190.VAL_BIT_RESOLUTION_MODE_SPEED) 
                self.check_error(status)
                self.set_sample_clock_source_route("internal", channel=channel)
                self.set_channel_route("AC", channel=channel)
                self.set_amplitude(2.0, channel=channel)
                self.set_arm_mode("self", channel=channel)
                self.set_trigger_mode("trig", channel=channel)
                self.set_gate_mode("trig", channel=channel)
        except:
            self.close()
            raise
        print('connected to AWG M8190A.')
        return

    def abort(self):
        """
        To be executed when scan raises on error (Ctrl-C included).
        Abort generation from both channels.
        """
        self.abort_generation(channel=1)
        self.abort_generation(channel=2)
        return

    def abort_generation(self, channel=None):
        """Stop signal generation."""
        channel = self.channel_format(channel)
        status = self.AgM8190.ChannelAbortGeneration(self.session, channel)
        self.check_error(status)
        return

    def close(self):
        """Close instrument drivers."""
        ## close all previously opened sessions if they were not closed because of an evil user.
        for i in range(1,self.session.value):
            self.AgM8190.close(i)
        ## close current session, can raise error.
        status = self.AgM8190.close(self.session)                
        self.check_error(status)
        if self.verbose:
            print("AgM8190 close status", status)
        return status

    def channel_format(self, channel):
        """Convert channel format. Choose self.default_channel if input argument is None."""
        if channel==None:
            out = self.default_channel
        else:
            out = channel
        return str(out)

    def check_error(self, status):
        """Check status returned by a driver function. If different than zero, raise an error."""
        if self.verbose:
            print("awg:", status)
        if not(status==0 or status==None):
            self.AgM8190.GetError(self.session, ct.byref(self.error_code), 255, self.error_message)
            raise AgM8190Error(self.error_message.value+" (code "+str(self.error_code.value)+")")
        return

    def cw(self, freq=None, amp=None, channel=None):
        """
        Spit a continous wave function of specified frequency and amplitude.
        If arguments are omitted, defaults will be used.
        The sample rate will be optimized.
        The trigger mode will be changed to "auto".
        """
        ## Select defaults if parameters were omitted. 
        channel = self.channel_format(channel)
        if freq==None:
            freq = self.default_freq[channel]
        
        ## Optimize sample rate
        new_sample_rate = self.cw_optimal_sample_rate(freq)
        self.set_sample_rate(new_sample_rate)
        
        ## Append a pulse to the instructions.
        self.lab.reset_instructions()
        self.pulse(channel=channel, length=self.tick/new_sample_rate, freq=freq, amp=amp, phase=0)
        
        ## Save channels_to_load and adjust_trig_latency. 
        saved_channels_to_load = self.channels_to_load
        saved_trig_option = self.adjust_trig_latency
        ## Adapt channels_to_load and adjust_trig_latency to cw.
        self.channels_to_load = [channel]
        self.adjust_trig_latency = False
        ## Set trigger mode to trig before loading memory. load_memory works for "trig" mode only.
        self.set_trigger_mode("trig", channel=channel, quiet_for_cw=True)
        self.load_memory(is_cw=True)
        ## Assign channels_to_load and adjust_trig_latency to their previous values.
        self.channels_to_load = saved_channels_to_load
        self.adjust_trig_latency = saved_trig_option
        
        ## Set trigger mode to "auto" and initiate the cw.
        self.set_trigger_mode("auto", channel=channel)
        self.initiate_generation(channel=channel)
        return


    def cw_optimal_sample_rate(self, frequency):
        """Computes the optimal sample rate for a given frequency."""
        ## Get the maximum possible sample rate
        max_sample_rate = self.get_ViReal64_attribute("", self.AgM8190.ATTR_ARBITRARY_SAMPLE_RATE_MAX)
        ## Get the minimum number of waveform periods allowed during a segment the size of granularity.
        N_periods = int(np.ceil(self.granularity*frequency/max_sample_rate))
        if N_periods > self.granularity/self.nyquist_threshold:
            ## If there is more waveform periods then nyquist_threshold allows, raise an error.
            raise AgM8190Error("Input frequency is too large for nyquist_threshold. Please choose a new frequency because Nyquist.")
        ## Return the new optimal sample rate.
        return self.granularity/(N_periods/frequency)

    def force_trigger(self):
        """Send a software trigger to the AWG."""
        status = self.AgM8190.SendSoftwareTrigger(self.session)
        self.check_error(status)
        return

    def get_amplitude(self, channel=None):
        """Return current amplitude setting (V)."""
        channel = self.channel_format(channel)
        channel_route = self.get_channel_route(channel=channel)
        if channel_route=="DAC":
            amp = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DAC_AMPLITUDE)
        elif channel_route=="DC":
            amp = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DC_AMPLITUDE)
        elif channel_route=="AC":
            amp = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_AC_AMPLITUDE)
        return amp

    def get_arm_mode(self, channel=None):
        """Return current arm mode ('self' or 'armed')."""
        channel = self.channel_format(channel)
        result = self.get_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_ARM_MODE)
        if result==self.AgM8190.VAL_ARM_MODE_SELF:
            mode = "self"
        elif result==self.AgM8190.VAL_ARM_MODE_ARMED:
            mode = "armed"
        return mode

    def get_channel_route(self, channel=None):
        """Return current channel route ('AC', 'DC' or 'DAC')."""
        channel = self.channel_format(channel)
        result = self.get_ViInt32_attribute(channel, self.AgM8190.ATTR_OUTPUT_ROUTE)
        if result==self.AgM8190.VAL_OUTPUT_ROUTE_AC:
            route = "AC"
        elif result==self.AgM8190.VAL_OUTPUT_ROUTE_DC:
            route = "DC"
        elif result==self.AgM8190.VAL_OUTPUT_ROUTE_DAC:
            route = "DAC"
        return route

    
    def get_channel_coupling(self):
        """Return current channel coupling state ('on' or 'off')."""
        result = self.get_ViInt32_attribute("", self.AgM8190.ATTR_INSTRUMENT_CHANNEL_COUPLING_ENABLED)
        if result==self.AgM8190.VAL_CHANNEL_COUPLING_STATE_ON:
            coupling = "on"
        elif result==self.AgM8190.VAL_CHANNEL_COUPLING_STATE_OFF:
            coupling = "off"
        return coupling

    def get_gate_mode(self, channel=None):
        """Return current gate mode ('gated' or 'trig')."""
        channel = self.channel_format(channel)
        result = self.get_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_GATE_MODE)
        if result==self.AgM8190.VAL_GATE_MODE_GATED:
            mode = "gated"
        elif result==self.AgM8190.VAL_GATE_MODE_TRIGGERED:
            mode = "trig"
        return mode

    def get_offset(self, channel=None):
        """Return current offset setting (V)."""
        channel = self.channel_format(channel)
        channel_route = self.get_channel_route(channel=channel)
        if channel_route=="DAC":
            offset = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DAC_OFFSET)
        elif channel_route=="DC":
            offset = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DC_OFFSET)
        elif channel_route=="AC":
            offset = float(0)
        return offset


    def get_ref_clock_route(self):
        """Return current route of the reference clock ('AXI', 'internal' or 'external')."""
        result = self.get_ViInt32_attribute("", self.AgM8190.ATTR_OUTPUT_REFERENCE_CLOCK_SOURCE)
        if result==self.AgM8190.VAL_REFERENCE_CLOCK_SOURCE_AXI:
            route = "AXI"
        elif result==self.AgM8190.VAL_REFERENCE_CLOCK_SOURCE_INTERNAL:
            route = "internal"
        elif result==self.AgM8190.VAL_REFERENCE_CLOCK_SOURCE_EXTERNAL:
            route = "external"
        return route

    def get_sample_clock_output_route(self):
        """Return current output route of the sample clock ('internal' or 'external')."""
        result = self.get_ViInt32_attribute("", self.AgM8190.ATTR_SAMPLE_CLOCK_OUTPUT)
        if result==self.AgM8190.VAL_SAMPLE_CLOCK_OUTPUT_INTERNAL:
            route = "internal"
        elif result==self.AgM8190.VAL_SAMPLE_CLOCK_OUTPUT_EXTERNAL:
            route = "external"
        return route

    def get_sample_rate(self):
        """Return current sample rate (Sa/s)."""
        sample_rate = self.get_ViReal64_attribute("", self.AgM8190.ATTR_ARB_SAMPLE_RATE)
        return sample_rate

    def get_sample_clock_source_route(self, channel=None):
        """Return current source route of the sample clock ('internal' or 'external')."""
        channel = self.channel_format(channel)
        result = vt.ViInt32()
        status = self.AgM8190.SampleClockGetSampleClockSource(self.session, channel, ct.byref(result))
        self.check_error(status)
        if result.value == self.AgM8190.VAL_SAMPLE_CLOCK_SOURCE_INTERNAL:
            route = "internal"
        elif result.value == self.AgM8190.VAL_SAMPLE_CLOCK_SOURCE_EXTERNAL:
            route = "external"
        return route

    def get_trigger_mode(self, channel=None):
        """Return current trigger mode ('auto' or 'trig')."""
        channel = self.channel_format(channel)
        result = self.get_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_MODE)
        if result==self.AgM8190.VAL_TRIGGER_MODE_AUTO:
            mode = "auto"
        elif result==self.AgM8190.VAL_TRIGGER_MODE_TRIGGERED:
            mode = "trig"
        return mode

    def get_ViInt32_attribute(self, string, attr):
        """
        Return a ViInt32 attribute from the instrument. Refer to AgM8190 documentation for valid attributes.
        - string: String associated with the attribute (most often the channel or an empty string).
        - attr: Attribute from the AgM8190 wrapper (ex: self.AgM8190.ATTR_TRIGGER_MODE).
        """
        result = vt.ViInt32()
        status = self.AgM8190.GetAttributeViInt32(self.session, str(string), attr, ct.byref(result))
        self.check_error(status)
        return result.value

    def get_ViReal64_attribute(self, string, attr):
        """
        Return a ViReal64 attribute from the instrument. Refer to AgM8190 documentation for valid attributes.
        - string: String associated with the attribute (most often the channel or an empty string).
        - attr: Attribute from the AgM8190 wrapper (ex: self.AgM8190.ATTR_ARBITRARY_AC_AMPLITUDE).
        """
        result = vt.ViReal64()
        status = self.AgM8190.GetAttributeViReal64(self.session, str(string), attr, ct.byref(result))
        self.check_error(status)
        return result.value

    def initiate_generation(self, channel=None):
        """Start signal generation. Start to wait for trigger if trigger mode is 'trig'."""
        channel = self.channel_format(channel)
        status = self.AgM8190.ChannelInitiateGeneration(self.session, channel)
        self.check_error(status)
        ## It's required to let some time to initiate. This time is related to trigger latency according to Keysight. I put 2 times the latency just to be sure.
        time.sleep(2*10240/self.get_sample_rate()) 
        return

    def load_memory(self, is_cw=False):
        """
        For each channel specified in self.channels_to_load:
            Convert the instructions from self.instructions to segments using self.preprocess().
            Load each segment into AWG memory.
        By default, use the scenario sequencing mode. If is_cw is True, use arbitrary sequencing mode instead (single segment mode).
        """
        for channel in self.channels_to_load:
            channel = str(channel)
            if self.get_trigger_mode(channel=channel)=="auto":
                ## If trigger mode is automatic, it means we are outputting a continous waveform. In this case, skip load_memory.
                if channel=="1" and self.show_warning_trig_auto_no_load1:
                    print("AWG channel 1: trigger mode is automatic, load_memory() will be skipped.")
                    self.show_warning_trig_auto_no_load1 = False
                if channel=="2" and  self.show_warning_trig_auto_no_load2:
                    print("AWG channel 2: trigger mode is automatic, load_memory() will be skipped.")
                    self.show_warning_trig_auto_no_load2 = False
                continue

            ## Abort current awg signal generation
            status = self.abort_generation(channel=channel)
            self.check_error(status)
            
            ## skip the rest of the loop if no instructions are detected.
            if [inst for inst in self.instructions if inst[1]==str(channel)]==[]:
                if channel=="1" and self.show_warning_no_inst1:
                    print("AWG channel 1: No instructions detected, load_memory() will be skipped.")
                    self.show_warning_no_inst1 = False
                    continue
                if channel=="2" and self.show_warning_no_inst2:
                    print("AWG channel 2: No instructions detected, load_memory() will be skipped.")
                    self.show_warning_no_inst2 = False
                    continue
                
            ## Preprocess: Merge pulses and markers into blocks, detect delays.
            segments={}
            self.preprocess(channel, segments, is_cw)
                    
            ## Check if number of New sequence match the number of End sequence.
            if not is_cw:
                N_is_start = sum([seq_info["is_start"] for seq_info in segments["sequence_info"]])
                N_is_end = sum([seq_info["is_end"] for seq_info in segments["sequence_info"]])
                if N_is_start!=N_is_start:
                    raise AgM8190Error("The number of 'New sequence' segments doesn't match the number of 'End Sequence' segments.")
            
            ## Reset the sequence table
            self.AgM8190.SequenceTableReset(self.session, channel)
            self.check_error(status)
            ## Clear waveform data in awg memory.
            status = self.AgM8190.WaveformClearAll(self.session, channel)
            self.check_error(status)


            segment_ID_delay = vt.ViInt32(0) ## Segment ID for the zero amplitude waveform used for delays.
            segment_ID = vt.ViInt32(0) ## Segment ID for block type waveforms (will increment by one for each different block)
            data = (vt.ViInt32 * 6)() ## Array intented for the SequenceTableSetData() function
            waveform_int16_delay = (vt.ViInt16*self.tick)() ## waveform used for delay sequences (initialized with zeros)


            ## For each segment, load the sequence table accordingly. The process will differ if the segment is a "block" or a "delay".
            for i, (segment_type, segment_info, sequence_info) in enumerate(zip(segments["type"], segments["segment_info"], segments["sequence_info"])):
                if segment_type=="block":
                    ## Unpack preprocess info.
                    waveform_int16 = segment_info["waveform"]
                    is_start_of_a_sequence = sequence_info["is_start"]
                    is_end_of_a_sequence = sequence_info["is_end"]
                    sequence_loops = sequence_info["loops"]
                    segment_loops = 1
                    ## Loop the segment instead of looping the sequence if both a start and an end are detected.
                    if is_start_of_a_sequence and is_end_of_a_sequence:
                        segment_loops = sequence_loops
                        sequence_loops = 1
                        is_start_of_a_sequence = False
                        is_end_of_a_sequence = False
                    ## Load the block waveform in awg memory
                    status = self.AgM8190.WaveformCreateChannelWaveformInt16(self.session, channel, len(waveform_int16), waveform_int16, ct.byref(segment_ID))
                    self.check_error(status)
                    segment_ID_active = segment_ID
                elif segment_type=="delay":
                    ## Unpack preprocess info.
                    is_start_of_a_sequence = sequence_info["is_start"]
                    is_end_of_a_sequence = sequence_info["is_end"]
                    sequence_loops = sequence_info["loops"]
                    segment_loops = int(segment_info["duration"]/len(waveform_int16_delay))
                    ## Loop the segment more times if both a start and an end are detected.
                    if is_start_of_a_sequence and is_end_of_a_sequence:
                        sequence_loops = 1
                        is_start_of_a_sequence = False
                        is_end_of_a_sequence = False
                        segment_loops *= sequence_loops
                    ## Load the delay waveform in awg memory (could be outside of loop to reduce loading time, but then you have to deal with linear playtime requirements because of memory jumps.)
                    status = self.AgM8190.WaveformCreateChannelWaveformInt16(self.session, channel, len(waveform_int16_delay), waveform_int16_delay, ct.byref(segment_ID_delay))
                    self.check_error(status)
                    segment_ID_active = segment_ID_delay

                if segment_loops > 2**32-1:
                    raise AgM8190Error("Maximum number of segment loops reached (2^32).")
                if sequence_loops > 2**32-1:
                    raise AgM8190Error("Maximum number of sequence loops reached (2^32).")
                    
                ## Prepare the data array
                data[0] = 0 ## data = 0 if nothing is special about the segment
                data[0] += self.AgM8190.control["MarkerEnable"] ## Enable marker
                if is_start_of_a_sequence:
                    data[0] += self.AgM8190.control["InitMarkerSequence"] ## start sequence if it's the start of table or start of a loop
                if is_end_of_a_sequence:
                    data[0] += self.AgM8190.control["EndMarkerSequence"]  ## end sequence if it's the end of a loop
                if i == len(segments["type"])-1:
                    data[0] += self.AgM8190.control["EndMarkerScenario"]  ## end scenario

                data[1] = sequence_loops ## Sequence Loop Count
                data[2] = segment_loops ## Segment Loop Count
                data[3] = segment_ID_active.value  ## Active segment ID
                data[4] = 0 ## Segment Start Offset (0 = no offset)
                data[5] = 0xffffffff ## Segment End Offset (0xffffffff = no offset)


                ## Load the sequence table in awg memory.
                status = self.AgM8190.SequenceTableSetData(self.session, channel, i, 6, data)
                self.check_error(status)


                # ######### idle command - max delay is 2**25 sample counts - deprecated ##########
                # data[0] += self.AgM8190.control["CommandFlag"] ## Control
                # data[1] = 1 ## Sequence Loop Count (N/A)
                # data[2] = 0 ## Command Code (0 = idle command)
                # data[3] = 0 ## Idle sample (value to be played during idle, int16 format)
                # data[4] = delay ## Idle delay
                # data[5] = 0 ## Not used (must be 0)
                # status = self.AgM8190.SequenceTableSetData(self.session, channel, i, 6, data)
                # self.check_error(status)
                # #################################################################################

            ## Choose correct sequencer mode
            if is_cw: 
                ## In continous waveform, only one segment is played.
                status = self.AgM8190.SetAttributeViInt32(self.session, channel, self.AgM8190.ATTR_ARBITRARY_SEQUENCING_MODE, self.AgM8190.VAL_SEQUENCING_MODE_ARBITRARY)
                self.check_error(status)
            else:
                ## Scenario mode for complex sequences (enables internal looping)
                status = self.AgM8190.SetAttributeViInt32(self.session, channel, self.AgM8190.ATTR_ARBITRARY_SEQUENCING_MODE, self.AgM8190.VAL_SEQUENCING_MODE_ST_SCENARIO)
                self.check_error(status)

            ## Turn Output On
            status = self.AgM8190.SetAttributeViBoolean(self.session, channel, self.AgM8190.ATTR_OUTPUT_ENABLED, True)
            self.check_error(status)


        return


    def loop_start(self, num_loops, autopad=True, channel=None):
        """Instruction to start an internal loop at current time cursor.
        autopad=False is at your own risk"""
        channel = self.channel_format(channel)
        ## Add a tiny delay to start loop on a tick.
        if autopad:
            sample_rate = self.get_sample_rate()
            sample_counts = int(self.lab.time_cursor*sample_rate)
            if sample_counts%320 == 0:
                padded_counts = sample_counts
            else:
                padded_counts = sample_counts//self.tick*self.tick + self.tick
            self.lab.delay((padded_counts-sample_counts)/sample_rate)

        ## Insert instruction here
        self.instructions.append([self.lab.time_cursor, channel, "loop_start", num_loops])

        return

    def loop_end(self, autopad=True, channel=None):
        """Instruction to end an internal loop at current time cursor.
        autopad=False is at your own risk"""
        channel = self.channel_format(channel)
        ## Add a tiny delay to end loop on a tick.
        if autopad:
            sample_rate = self.get_sample_rate()
            sample_counts = int(self.lab.time_cursor*sample_rate)
            if sample_counts%320 == 0:
                padded_counts = sample_counts
            else:
                padded_counts = sample_counts//self.tick*self.tick + self.tick
            self.lab.delay((padded_counts-sample_counts)/sample_rate)
        ## Insert instruction here
        self.instructions.append([self.lab.time_cursor, channel, "loop_end", None])

        ## Update time cursor to account for all the loops.
        for inst in reversed(self.instructions):
            if inst[2]=="loop_end":
                raise AgM8190Error("Nested internal loops are impossible.")
            if inst[2]=="loop_start":
                time_started = inst[0]
                num_loops = inst[3]
                break

        ############################################ TEMPORARY FIX #########################################################
        ## change when it's possible to call a loop start/end in the middle of a delay.
        min_length = self.tick/sample_rate
        self.pulse(channel=channel, length = min_length, amp=0, freq=0)
        self.lab.delay((self.lab.time_cursor - time_started)*(num_loops - 1) - min_length)
        ####################################################################################################################
        ## self.lab.delay((self.lab.time_cursor - time_started)*(num_loops - 1))

        return

    def marker(self, channel=None):
        """Instruction to add a marker at current time cursor."""
        channel = self.channel_format(channel)
        self.instructions.append([self.lab.time_cursor, channel, "marker", None])
        return

    def preprocess(self, channel, segments, is_cw):
        """
        Translate self.instructions to AWG language (segments).
        Pulses are first merged into blocks. A block is a set of pulses that are overlapping. Markers are considered as pulses for the 'merging into blocks' operation.
        Adjust the duration of first delay to account for trigger latency if the self.adjust_trig_latency option is activated.
        For each block, execute wfmGenLib2 to compute the sum of the pulses.
        Add markers to the waveform. 
        Between each block is a tiny looped segment.
        Split delay segments if the maximum number of loops was reached.
        
        - segments: An empty dictionary. Will be filled and returned at the end of preprocess.
        - is_cw: The last empty delay will not be loaded for a continous waveform.
        """
        segments.clear()
        segments.update({"type":[], "segment_info":[], "sequence_info":[]})

        short_size = (2**16-1)

        ## Unzip user instructions
        channel_instructions = [inst for inst in self.instructions if inst[1]==str(channel)]
        if channel_instructions==[]:
            ## if there's no instructions, what's the point?
            return  

        times   = [inst[0] for inst in channel_instructions if inst[2]=="pulse"]
        lengths = [inst[3][0] for inst in channel_instructions if inst[2]=="pulse"]
        freqs   = [inst[3][1] for inst in channel_instructions if inst[2]=="pulse"]
        phases  = [inst[3][2] for inst in channel_instructions if inst[2]=="pulse"]
        amps    = [inst[3][3] for inst in channel_instructions if inst[2]=="pulse"]
        shapes  = [inst[3][4] for inst in channel_instructions if inst[2]=="pulse"]

        loop_start_times = [inst[0] for inst in channel_instructions if inst[2]=="loop_start"]
        loop_nums        = [inst[3] for inst in channel_instructions if inst[2]=="loop_start"]

        loop_end_times = [inst[0] for inst in channel_instructions if inst[2]=="loop_end"]

        marker_times = [inst[0] for inst in channel_instructions if inst[2]=="marker"]

        ## Get useful info from awg
        sample_rate = self.get_sample_rate()
        awg_amp = self.get_amplitude(channel=channel)

        ## Combine marker specs and pulses specs (the trick is to consider each marker as a zero amplitude pulse: preprocess will pad correctly, then after padding markers will be added to the waveform)
        marker_count = len(marker_times)

        times += marker_times
        lengths += [128/sample_rate]*marker_count ## a marker lasts for 128 samples (number doesn't really matter though because of padding. just needs to be small)
        freqs += [0]*marker_count ## marker freq doesn't matter
        phases += [0]*marker_count ## marker phase doesn't matter
        amps += [0]*marker_count ## marker amplitude will be added to other pulses, needs to be zero.
        shapes += ["square"]*marker_count ## marker shape doesn't matter

        ## Sort every list in time ascending order
        indices = sorted(list(range(len(times))),key=times.__getitem__)

        times = [times[i] for i in indices]
        lengths = [lengths[i] for i in indices]
        freqs = [freqs[i] for i in indices]
        phases = [phases[i] for i in indices]
        amps = [amps[i] for i in indices]
        shapes = [shapes[i] for i in indices]

        ## Add a final point to the times list
        times += [self.lab.total_duration]

        ## Merge pulses into blocks.
        ## One block is a set of pulses, either overlapping or separated by less then minimum_delay_time.
        minimum_delay_time = self.minimum_delay_count/sample_rate
        blocks = []
        i = 0
        while True:
            current_block = {"wfm_starts":[], "wfm_ends":[], "wfm_lengths":[], "wfm_periods":[], "wfm_phases":[], "wfm_amps":[], "wfm_shapes":[]}
            time_to_beat = times[i]+lengths[i]+minimum_delay_time ## if the start of a pulse beats this time, a new block is created.
            while True:
                wfm_start = int(times[i]*sample_rate) ## start of pulse in terms of sample counts.
                wfm_end = int((times[i]+lengths[i])*sample_rate) ## length of pulse in terms of sample counts.
                if freqs[i] > 0:
                    wfm_period = sample_rate/freqs[i] ## period of pulse in terms of sample counts.
                else:
                    wfm_period = -1 ## no sine will be factored in wfmGenLib2
                wfm_phase = phases[i]*np.pi/180. ## phase in radians
                wfm_amp = int(amps[i]*2047/awg_amp) ## amps in int16 format (with MarkerEnable activated)
                wfm_shape = self.wfmGenLib2.shapes_code[shapes[i]] ## code for the shape as interpreted by wfmGenLib2
                current_block["wfm_starts"].append(wfm_start)
                current_block["wfm_ends"].append(wfm_end)
                current_block["wfm_lengths"].append(wfm_end-wfm_start)
                current_block["wfm_periods"].append(wfm_period)
                current_block["wfm_phases"].append(wfm_phase)
                current_block["wfm_amps"].append(wfm_amp)
                current_block["wfm_shapes"].append(wfm_shape)
                if times[i+1] > time_to_beat: ## if the start of next pulse beats this time, a new block is created.
                    break
                else: ## else, continue the while statement and the next pulse will be appended to current block
                    i+=1
                    if i > len(freqs)-1:
                        break
                    if time_to_beat < (times[i]+lengths[i]+minimum_delay_time): ## update time_to_beat if end of current pulse is higher.
                        time_to_beat = times[i]+lengths[i]+minimum_delay_time
            blocks.append(current_block)
            i+=1
            if i > len(freqs)-1:
                break
        

        ## Adjust trigger latency if option is activated. This will chop 10240 counts from the start of sequence. The experiment needs a time buffer.
        if self.adjust_trig_latency:
            trigger_latency = 10240 ## latency for trigger in terms of sample rate. There is an uncertainty of (+0/+64).
        else:
            trigger_latency = 0


        ## Add the first delay block.
        first_segment_start = int(np.min(blocks[0]["wfm_starts"]))//self.tick*self.tick - trigger_latency
        if self.minimum_delay_count < first_segment_start:
            first_segment_is_block_type = False
            _, is_end_of_a_sequence, loops_count = self.preprocess_loops(loop_start_times, loop_end_times, loop_nums, 0, first_segment_start)
            is_start_of_a_sequence = True
            segments["type"].append("delay")
            segments["segment_info"].append({"duration":first_segment_start})
            segments["sequence_info"].append({"is_start":is_start_of_a_sequence, "is_end":is_end_of_a_sequence, "loops":loops_count})
        else:
            first_segment_is_block_type = True
            if self.adjust_trig_latency:
                raise AgM8190Error("You must add a time buffer at the beginning of experiment if using adjust_trig_latency=True.")

        for b, block in enumerate(blocks):
        
            ##------- Temporary clipping warning message since the other one is now broken. When fixed, delete this message. -------##
            ## This warning may be shown for nothing, depending on the phases of the pulses and the shape of the envelope.
            if sum(block["wfm_amps"])/2047.0>awg_amp:
                if self.show_warning_amp_clipping:
                    print(nfu.warn_msg()+"AWG pulses are overlapping and their amplitude are most likely overloading. \nIn this case, behaviour is unexpected. You should look at pulses on a scope or using self.plot_loaded_sequence(). \nTo avoid this issue, edit the "+self.__class__.__name__+" class so it clips the amplitude. See related TODO in class comments.")
                    input("I saw this message. [ENTER]")
                    self.show_warning_amp_clipping = False
            ##----------------------------------------------------------------------------------------------------------------------##
        
            ## Find block min and max for padding
            block_start = int(np.min(block["wfm_starts"]))
            block_end = int(np.max(block["wfm_ends"]))
            segment_start = block_start//self.tick*self.tick
            if block_end%self.tick==0:
                segment_end = block_end
            else:
                segment_end = block_end//self.tick*self.tick + self.tick

            ## Declare C variables.
            pulse_count = len(block["wfm_starts"])

            C_countFreq = ct.c_int(pulse_count)
            C_blockStart = ct.c_longlong(segment_start)
            C_wfmstart = (ct.c_longlong*pulse_count)(*block["wfm_starts"])
            C_wfmlength = (ct.c_longlong*pulse_count)(*block["wfm_lengths"])
            C_arrPeriod = (ct.c_double*pulse_count)(*block["wfm_periods"])
            C_arrPhase = (ct.c_double*pulse_count)(*block["wfm_phases"])
            C_arrAmp = (ct.c_short*pulse_count)(*block["wfm_amps"])
            C_arrShape = (ct.c_int*pulse_count)(*block["wfm_shapes"])
            C_arrOut_int16 = (ct.c_short*(segment_end-segment_start))()

            ## Compute the sum of pulses.
            self.wfmGenLib2.wfmgen(C_countFreq, C_blockStart, C_wfmstart, C_wfmlength, C_arrPeriod, C_arrPhase, C_arrAmp, C_arrShape, C_arrOut_int16)

            ## Clip block amplitude if to high (BROKEN). 
            ## TODO: Since C_arrOut_int16 is a short, the following 'if' is never True. No warning will be raised for clipping. ##
            ##       This check/clipping will probably need to take place in wfmGenLib2 C code.                                      ##       
            #if np.max(C_arrOut_int16) > short_size: 
            #    if self.show_warning_amp_clipping:
            #        print nfu.warn_msg()+"Amplitude of the sum of pulses ("+str(np.max(C_arrOut_int16)/short_size*awg_amp)+" V) is higher awg amplitude ("+str(awg_amp)+" V). Waveform will be clipped."
            #    for i, item in enumerate(C_arrOut_int16):
            #        if item > 0:
            #            C_arrOut_int16[i] = min(item, short_size)
            #        else:
            #            C_arrOut_int16[i] = max(item, -short_size)
            ##-----------------------------------------------------------------------------------------------------------------------##

            ## Add markers
            for time_ in marker_times:
                if segment_start <= int(time_*sample_rate) < segment_end:
                    index = int(time_*sample_rate - segment_start)
                    C_arrOut_int16[index] += 1


            ## Append "block" type segment to result.
            is_start_of_a_sequence, is_end_of_a_sequence, loops_count = self.preprocess_loops(loop_start_times, loop_end_times, loop_nums, block_start, block_end)
            if first_segment_is_block_type:
                is_start_of_a_sequence=True
            segments["type"].append("block")
            segments["segment_info"].append({"waveform":C_arrOut_int16, "start":segment_start, "end":segment_end})
            segments["sequence_info"].append({"is_start":is_start_of_a_sequence, "is_end":is_end_of_a_sequence, "loops":loops_count})
            if (not first_segment_is_block_type):
                if segments["sequence_info"][-1]["is_start"]:
                    segments["sequence_info"][-2]["is_end"] = True
                if segments["sequence_info"][-2]["is_end"]:
                    segments["sequence_info"][-1]["is_start"] = True
                

            ## Add a delay block if it's not the end.
            if b < len(blocks) - 1:
                next_block_start = int(np.min(blocks[b+1]["wfm_starts"]))
                next_segment_start = next_block_start//self.tick*self.tick
                is_start_of_a_sequence, is_end_of_a_sequence, loops_count = self.preprocess_loops(loop_start_times, loop_end_times, loop_nums, block_end, next_block_start)
                segments["type"].append("delay")
                segments["segment_info"].append({"duration":next_segment_start-segment_end})
                segments["sequence_info"].append({"is_start":is_start_of_a_sequence, "is_end":is_end_of_a_sequence, "loops":loops_count})
                if segments["sequence_info"][-1]["is_start"]:
                    segments["sequence_info"][-2]["is_end"] = True
                if segments["sequence_info"][-2]["is_end"]:
                    segments["sequence_info"][-1]["is_start"] = True
                if is_start_of_a_sequence:
                    saved_loop_start = segment_start
                    saved_loop_nums = loops_count
                if is_end_of_a_sequence:
                    saved_loop_end = segment_end

        ## Add the tiniest delay to indicate end of last sequence except if loading a continous waveform (cw)
        if not is_cw:
            segments["type"].append("delay")
            segments["segment_info"].append({"duration":self.tick})
            segments["sequence_info"].append({"is_start":False, "is_end":True, "loops":1})



        ## Detect long delays
        max_delay = self.tick*(2**32)-1
        segments_ = segments.copy()
        segments.update({"type":[], "segment_info":[], "sequence_info":[]})
        for seg_type, seg_info, seq_info in zip(segments_["type"], segments_["segment_info"], segments_["sequence_info"]):
            if seg_type=="delay":
                delay = seg_info["duration"]
                if delay > max_delay:
                    i=0
                    while delay > max_delay:
                        delay -= max_delay
                        segments["type"].append("delay")
                        segments["segment_info"].append({"duration":max_delay})
                        segments["sequence_info"].append(seq_info)
                        if i==0:
                            segments["sequence_info"][-1]["is_end"] = False
                        else:
                            segments["sequence_info"][-1]["is_start"] = False
                            segments["sequence_info"][-1]["is_end"] = False
                            segments["sequence_info"][-1]["loops"] = 1
                        i+=1
                    segments["type"].append("delay")
                    segments["segment_info"].append({"duration":delay})
                    segments["sequence_info"].append(seq_info)
                    segments["sequence_info"][-1]["is_start"] = False
                    segments["sequence_info"][-1]["loops"] = 1
                    continue

            segments["type"].append(seg_type)
            segments["segment_info"].append(seg_info)
            segments["sequence_info"].append(seq_info)
        
        
        return

    def preprocess_loops(self, loop_start_times, loop_end_times, loop_nums, segment_start, segment_end):
        """
        Subpreprocess for looping calculations. Work in progress.
        """
        is_start_of_a_sequence = False
        loops_count = 1
        is_end_of_a_sequence = False

        sample_rate = self.get_sample_rate()
        ## Find out if a loop starts in this segment
        count = 0
        for t, time_ in enumerate(loop_start_times):
            if segment_start <= int(time_*sample_rate) < segment_end:
                is_start_of_a_sequence=True
                loops_count = int(loop_nums[t])
                count+=1
        if count>1 and self.show_warning_loop_start:
            print(nfu.warn_msg()+"Many loop starts detected in the same segment.")
            self.show_warning_loop_start = False

        ## Find out if a loop ends in this segment
        count = 0
        for t, time_ in enumerate(loop_end_times):
            if segment_start < int(time_*sample_rate) <= segment_end:
                is_end_of_a_sequence=True
                count+=1
        if count>1 and self.show_warning_loop_end:
            print(nfu.warn_msg()+"Many loop ends detected in the same segment.")
            self.show_warning_loop_end = False

        if is_start_of_a_sequence:
            self._saved_loop_segment_start = segment_start
            self._saved_loop_num = loops_count
        if is_end_of_a_sequence:
            loop_duration = segment_end-self._saved_loop_segment_start
            self._crop_next_delay = int(loop_duration*(self._saved_loop_num - 1)) - 320

        return is_start_of_a_sequence, is_end_of_a_sequence, loops_count

    def plot_loaded_sequence(self, divider=None, ax=None, channel=None):
        """
        Show the sequence computed from the preprocess in a matplotlib figure. WARNING: internal loops are not implemented.
        
        - divider: Factor between the number of plotted points and the number of points loaded in the AWG.
                   If omitted, an optimal divider will be used.
        - ax: Specify an ax on which to plot the loaded sequence. 
        
        TODO: Instead of using the preprocess for the input waveforms, read the AWG tables and plot that directly. 
              It will be more representative of what is really loaded, and internal looping will be easy to process.
        """
        channel = self.channel_format(channel)

        sample_rate = self.get_sample_rate()

        segments = {}
        self.preprocess("1", segments, False)
        
        prefix, c = nfu.plot_loaded_sequence_auto_label(self.lab)
    
        if ax==None:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_xlabel("Time ("+prefix+"s)")
            ## Span time for all experiment duration
            ax.set_xlim([0, c*(self.lab.total_duration)])

        for i, (segment_type, segment_info, sequence_info) in enumerate(zip(segments["type"], segments["segment_info"], segments["sequence_info"])):
            if segment_type=="delay":
                continue
            waveform = segment_info["waveform"]
            segment_start = segment_info["start"]
            segment_end = segment_info["end"]
            if divider==None:
                divider_ = 1
                while True:
                    linspace_size = int((segment_end-segment_start)/divider_)
                    arange_step = divider_/sample_rate
                    if linspace_size < 10000:
                        break
                    divider_ *= 2
            else:
                divider_ = int(divider)
                linspace_size = int((segment_end-segment_start)/divider_)
                arange_step = divider_/sample_rate
            numpy_wfm = np.ctypeslib.as_array(waveform)[::divider_]
            print(str(i+1)+nfu.number_suffix(i+1), "block: one point in plot for", divider_, "points in awg.")
            try:
                t = np.linspace(segment_start/sample_rate, segment_end/sample_rate-divider_/sample_rate, linspace_size)
                ax.plot(c*t, numpy_wfm ,'o', mew=0)
            except ValueError: ## sometimes one point will be lost to the [::divider] operation.
                t = np.linspace(segment_start/sample_rate, segment_end/sample_rate, linspace_size+1)
                ax.plot(c*t, numpy_wfm ,'o', mew=0)

        plt.show()

        return



    def pulse(self, length=None, phase=None, amp=None, freq=None, shape=None, rewind=False, channel=None):
        """
        Instruction to add a pulse starting at current time cursor.
        Time cursor updates by the length of the pulse.
        Use pulse_BB1_pi() and pulse_BB1_piby2() for BB1 pulse methods.
        - length: Duration of the pulse.
        - phase: Phase of the pulse relative to t=0.
        - amp: Amplitude of the pulse.
        - freq: Frequency of the pulse. Must respect Nyquist threshold (AWG class option)
        - shape: Shape of the envelope.
        - rewind: Rewind time cursor by 'rewind' seconds after the instruction.        
        """
        channel = self.channel_format(channel)
        if length==None:
            length = self.default_length[channel]
        if phase==None:
            phase = self.default_phase[channel]
        if amp==None:
            amp = self.default_amp[channel]
        if freq==None:
            freq = self.default_freq[channel]
        if shape==None:
            shape = self.default_shape[channel]
            
        ## Check shape
        if shape not in list(self.wfmGenLib2.shapes_code.keys()):
            raise AgM8190Error(shapes[i]+" is not a valid shape. Refer to dll_wfmGenLib2.py for valid shapes.")

        ## Check freq
        if freq > self.nyquist_threshold*self.get_sample_rate():
            raise AgM8190Error("Nyquist sampling criterion violated.")
        if (not 50*MHz <= freq <= 5*GHz) and self.get_channel_route(channel=channel)=="AC":
            if self.show_warning_freqrangeAC:
                print(nfu.warn_msg()+"AWG frequency is out of the 50MHz - 5GHz range for AC mode. Amplitude can be attenuated.")
                self.show_warning_freqrangeAC = False

        ## Update instructions
        self.instructions.append([self.lab.time_cursor, channel, "pulse", (length, freq, phase, amp, shape)])
        self.lab.update_time_cursor(length, rewind)
        return

    def pulse_BB1_pi(self, pi_len=None, phase=None, pi_amp=None, freq=None, shape=None, channel=None):
        """
        Instruction to add a BB1 pi pulse starting at current time cursor.
        The five pulses are separated by a delay (5 us but may change, check in source code).
        Time cursor updates to the end of the BB1 pulse sequence.
        - pi_len: Duration of the pulse.
        - phase: Phase of the pulse relative to t=0.
        - pi_amp: Amplitude of the pulse.
        - freq: Frequency of the pulse. Must respect Nyquist threshold (self.nyquist_threshold option).
        - shape: Shape of the envelope.
        """
        channel = self.channel_format(channel)
        if phase==None:
            phase = self.default_phase[channel]

        self.pulse(channel=channel, length=pi_len, phase=phase,            amp=pi_amp, freq=freq, shape=shape)
        self.lab.delay(5*us)
        self.pulse(channel=channel, length=pi_len, phase=phase+0.5806*180, amp=pi_amp, freq=freq, shape=shape)
        self.lab.delay(5*us)
        self.pulse(channel=channel, length=pi_len, phase=phase+1.7411*180, amp=pi_amp, freq=freq, shape=shape)
        self.lab.delay(5*us)
        self.pulse(channel=channel, length=pi_len, phase=phase+1.7411*180, amp=pi_amp, freq=freq, shape=shape)
        self.lab.delay(5*us)
        self.pulse(channel=channel, length=pi_len, phase=phase+0.5806*180, amp=pi_amp, freq=freq, shape=shape)
        return

    def pulse_BB1_piby2(self, pi_len=None, piby2_len=None, phase=None, pi_amp=None, piby2_amp=None, freq=None, shape=None, channel=None):
        """
        Instruction to add a BB1 pi/2 pulse starting at current time cursor.
        The five pulses are separated by a delay (5 us but may change, check in source code).
        Time cursor updates to the end of the BB1 pulse sequence.
        - pi_len: Duration of the pi pulses.
        - piby2_len: Duration of the pi/2 pulses.
        - phase: Phase of the pulse relative to t=0.
        - pi_amp: Amplitude of the pi pulses.
        - piby2_amp: Amplitude of the pi/2 pulses.
        - freq: Frequency of the pulse. Must respect Nyquist threshold (self.nyquist_threshold option).
        - shape: Shape of the envelope.
        """
        channel = self.channel_format(channel)
        if pi_len==None:
            pi_len = self.default_length[channel]
        if piby2_len==None:
            piby2_len = pi_len/2.
        if pi_amp==None:
            pi_amp = self.default_amp[channel]
        if piby2_amp==None:
            piby2_amp = pi_amp/2.
        if phase==None:
            phase = self.default_phase[channel]

        self.pulse(channel=channel, length=piby2_len, phase=phase,            amp=piby2_amp, freq=freq, shape=shape)
        self.lab.delay(5*us)
        self.pulse(channel=channel, length=pi_len,    phase=phase+0.54*180,   amp=pi_amp, freq=freq, shape=shape)
        self.lab.delay(5*us)
        self.pulse(channel=channel, length=pi_len,    phase=phase+1.6194*180, amp=pi_amp, freq=freq, shape=shape)
        self.lab.delay(5*us)
        self.pulse(channel=channel, length=pi_len,    phase=phase+1.6194*180, amp=pi_amp, freq=freq, shape=shape)
        self.lab.delay(5*us)
        self.pulse(channel=channel, length=pi_len,    phase=phase+0.54*180,   amp=pi_amp, freq=freq, shape=shape)
        return

    def reset_warnings(self):
        """ 
        Reset show_warnings attributes to True. 
        Is called at the beginning of the scan function.
        """
        self.show_warning_amp_clipping = True ## Is shown more often than it should be (waiting to be fixed, see preprocess.)
        self.show_warning_freqrangeAC = True
        self.show_warning_loop_start = True
        self.show_warning_loop_end = True
        self.show_warning_no_inst1 = True
        self.show_warning_no_inst2 = True
        self.show_warning_trig_auto_no_load1 = True
        self.show_warning_trig_auto_no_load2 = True
        return


    def set_amplitude(self, amp, channel=None):
        """Set amplitude setting (V)."""
        channel = self.channel_format(channel)
        current_amp = self.get_amplitude(channel=channel)
        if amp==current_amp:
            print("awg channel "+channel+" amplitude is "+nfu.auto_unit(amp, unit="V")+".")
        else:
            channel_route = self.get_channel_route(channel=channel)
            if channel_route=="DAC":
                max_amp = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DAC_AMPLITUDE_MAX)
                min_amp = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DAC_AMPLITUDE_MIN)
                if min_amp <= amp <= max_amp:
                    self.set_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DAC_AMPLITUDE, amp)
                else:
                    raise AgM8190Error("Channel "+channel+" amplitude is not in the permitted range: "+nfu.auto_unit(min_amp, unit="V")+" to "+nfu.auto_unit(max_amp, unit="V")+".")
            elif channel_route=="DC":
                max_amp = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DC_AMPLITUDE_MAX)
                min_amp = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DC_AMPLITUDE_MIN)
                if min_amp <= amp <= max_amp:
                    self.set_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DC_AMPLITUDE, amp)
                else:
                    raise AgM8190Error("Channel "+channel+" amplitude is not in the permitted range: "+nfu.auto_unit(min_amp, unit="V")+" to "+nfu.auto_unit(max_amp, unit="V")+".")
            elif channel_route=="AC":
                max_amp = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_AC_AMPLITUDE_MAX)
                min_amp = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_AC_AMPLITUDE_MIN)
                if min_amp <= amp <= max_amp:
                    self.set_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_AC_AMPLITUDE, amp)
                else:
                    raise AgM8190Error("Channel "+channel+" amplitude is not in the permitted range: "+nfu.auto_unit(min_amp, unit="V")+" to "+nfu.auto_unit(max_amp, unit="V")+".")
            print("awg channel "+channel+" amplitude set to "+nfu.auto_unit(amp, unit="V")+".")
        return


    def set_arm_mode(self, query, channel=None):
        """Set arm mode ('self' or 'armed')."""
        channel = self.channel_format(channel)
        if self.get_arm_mode(channel=channel)==query:
            print("awg channel "+channel+" arm mode is "+str(query)+".")
        else:
            if query=="armed":
                self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_ARM_MODE, self.AgM8190.VAL_ARM_MODE_ARMED)
            elif query=="self":
                self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_ARM_MODE, self.AgM8190.VAL_ARM_MODE_SELF)
            else:
                raise AgM8190Error(str(query)+" is not a valid input.")
            print("awg channel "+channel+" arm mode set to "+str(query)+".")
        return

    def set_channel_coupling(self, query):
        """Set channel coupling state ('on' or 'off')."""
        if self.get_channel_coupling()==query:
            print("awg channel coupling is "+str(query)+".")
        else:
            if query=="on":
                self.set_ViInt32_attribute("", self.AgM8190.ATTR_INSTRUMENT_CHANNEL_COUPLING_ENABLED, self.AgM8190.VAL_CHANNEL_COUPLING_STATE_ON)
            elif query=="off":
                self.set_ViInt32_attribute("", self.AgM8190.ATTR_INSTRUMENT_CHANNEL_COUPLING_ENABLED, self.AgM8190.VAL_CHANNEL_COUPLING_STATE_OFF)
            else:
                raise AgM8190Error(str(query)+" is not a valid input.")
            print("awg channel coupling set to "+str(query)+".")
        return

    def set_channel_route(self, query, channel=None):
        channel = self.channel_format(channel)
        current_route = self.get_channel_route(channel=channel)
        if query==current_route:
            print("awg channel "+channel+" route is "+str(query)+".")
        else:
            if query=="AC":
                self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_OUTPUT_ROUTE, self.AgM8190.VAL_OUTPUT_ROUTE_AC)
            elif query=="DC":
                self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_OUTPUT_ROUTE, self.AgM8190.VAL_OUTPUT_ROUTE_DC)
            elif query=="DAC":
                self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_OUTPUT_ROUTE, self.AgM8190.VAL_OUTPUT_ROUTE_DAC)
            else:
                raise AgM8190Error(str(query)+" is not a valid input.")
            print("awg channel "+channel+" route set to "+str(query)+".")
        return

    def set_default_pulse(self, for_channel=None, delay=None, length=None, freq=None, phase=None, amp=None, offset=None, shape=None):
        channel = self.channel_format(for_channel)
        if delay!=None:
            self.default_delay[channel] = delay
        if length!=None:
            self.default_length[channel] = length
        if freq!=None:
            self.default_freq[channel] = freq
        if phase!=None:
            self.default_phase[channel] = phase
        if amp!=None:
            self.default_amp[channel] = amp
        if shape!=None:
            self.default_shape[channel] = shape
        return


    def set_gate_mode(self, query, channel=None):
        """Set gate mode ('gated' or 'trig')."""
        channel = self.channel_format(channel)
        if self.get_gate_mode(channel=channel)==query:
            print("awg channel "+channel+" gate mode is "+str(query)+".")
        else:
            if query=="gated":
                status = self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_GATE_MODE, self.AgM8190.VAL_GATE_MODE_GATED)
            elif query in "trig":
                status = self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_GATE_MODE, self.AgM8190.VAL_GATE_MODE_TRIGGERED)
            else:
                raise AgM8190Error(str(query)+" is not a valid input.")
            print("awg channel "+channel+" gate mode set to "+str(query)+".")
        return

    def set_offset(self, offset, channel=None):
        """Set offset setting (V)."""
        channel = self.channel_format(channel)
        current_offset = self.get_offset(channel=channel)
        if offset==current_offset:
            print("awg channel "+channel+" offset is "+nfu.auto_unit(offset, unit="V")+".")
        else:
            channel_route = self.get_channel_route(channel=channel)
            if channel_route=="DAC":
                max_offset = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DAC_OFFSET_MAX)
                min_offset = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DAC_OFFSET_MIN)
                if min_offset <= offset <= max_offset:
                    self.set_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DAC_OFFSET, offset)
                else:
                    raise AgM8190Error("Channel "+channel+" offset is not in the permitted range: "+nfu.auto_unit(min_offset, unit="V")+" to "+nfu.auto_unit(max_offset, unit="V")+".")
            elif channel_route=="DC":
                max_offset = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DC_OFFSET_MAX)
                min_offset = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DC_OFFSET_MIN)
                if min_offset <= offset <= max_offset:
                    self.set_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DC_OFFSET, offset)
                else:
                    raise AgM8190Error("Channel "+channel+" offset is not in the permitted range: "+nfu.auto_unit(min_offset, unit="V")+" to "+nfu.auto_unit(max_offset, unit="V")+".")
            elif channel_route=="AC":
                if offset!=0:
                    raise AgM8190Error("Channel "+channel+" offset has to be 0 V when using AC route.")
                return
            print("awg channel "+channel+" offset set to "+nfu.auto_unit(offset, unit="V")+".")
        return

    def set_ref_clock_route(self, query):
        """Set route of the reference clock ('AXI', 'internal' or 'external')."""
        current_route = self.get_ref_clock_route()
        if query==current_route:
            print("awg ref clock route is "+current_route+".")
        else:
            if query=="AXI":
                self.set_ViInt32_attribute("", self.AgM8190.ATTR_OUTPUT_REFERENCE_CLOCK_SOURCE, self.AgM8190.VAL_REFERENCE_CLOCK_SOURCE_AXI)
            elif query == "internal":
                raise AgM8190Error('internal ref clock is not available currently. Try "AXI" instead')
                self.set_ViInt32_attribute("", self.AgM8190.ATTR_OUTPUT_REFERENCE_CLOCK_SOURCE, self.AgM8190.VAL_REFERENCE_CLOCK_SOURCE_INTERNAL)
            elif query == "external":
                self.set_ViInt32_attribute("", self.AgM8190.ATTR_OUTPUT_REFERENCE_CLOCK_SOURCE, self.AgM8190.VAL_REFERENCE_CLOCK_SOURCE_EXTERNAL)
            else:
                raise AgM8190Error(str(query)+" is not a valid input.")
            print("awg ref clock route set to "+str(query)+".")
        return

    def set_sample_clock_output_route(self, query):
        """Set output route of the sample clock ('internal' or 'external')."""
        current_route = self.get_sample_clock_output_route()
        if query==current_route:
            print("awg sample clock output route is "+str(query)+".")
        else:
            if query in "internal":
                self.set_ViInt32_attribute("", self.AgM8190.ATTR_SAMPLE_CLOCK_OUTPUT, self.AgM8190.VAL_SAMPLE_CLOCK_OUTPUT_INTERNAL)
            elif query in "external":
                self.set_ViInt32_attribute("", self.AgM8190.ATTR_SAMPLE_CLOCK_OUTPUT, self.AgM8190.VAL_SAMPLE_CLOCK_OUTPUT_EXTERNAL)
            else:
                raise AgM8190Error(str(query)+" is not a valid input.")
            print("awg sample clock output route set to "+str(query)+".")
        return

    def set_sample_rate(self, rate):
        """Set sample rate (Sa/s)."""
        max_sample_rate = self.get_ViReal64_attribute("", self.AgM8190.ATTR_ARBITRARY_SAMPLE_RATE_MAX)
        min_sample_rate = self.get_ViReal64_attribute("", self.AgM8190.ATTR_ARBITRARY_SAMPLE_RATE_MIN)
        current_rate = self.get_sample_rate()
        if current_rate == rate:
            print("awg sample rate is "+nfu.auto_unit(rate, "Sa/s")+".")
        else:
            if rate < min_sample_rate:
                raise AgM8190Error("Requested sample rate is lower than minimum allowed, "+nfu.auto_unit(min_sample_rate, "Hz")+".")
            elif rate > max_sample_rate:
                raise AgM8190Error("Requested sample rate is higher than maximum allowed, "+nfu.auto_unit(max_sample_rate, "Hz")+".")
            else:
                self.set_ViReal64_attribute("", self.AgM8190.ATTR_ARB_SAMPLE_RATE, rate)
                print("awg sample rate set to "+nfu.auto_unit(rate, "Sa/s")+".")
        return

    def set_sample_clock_source_route(self, query, channel=None):
        """Set source route of the sample clock ('internal' or 'external')."""
        channel = self.channel_format(channel)
        current_route = self.get_sample_clock_source_route(channel=channel)
        if query==current_route:
            print("awg channel "+channel+" sample clock source route is "+str(query)+".")
        else:
            if query == "internal":
                status = self.AgM8190.SampleClockSetSampleClockSource(self.session, channel, self.AgM8190.VAL_SAMPLE_CLOCK_SOURCE_INTERNAL)
            elif query == "external":
                status = self.AgM8190.SampleClockSetSampleClockSource(self.session, channel, self.AgM8190.VAL_SAMPLE_CLOCK_SOURCE_EXTERNAL)
            else:
                raise AgM8190Error(str(query)+" is not a valid input.")
            print("awg channel "+channel+" sample clock source route set to "+str(query)+".")
            self.check_error(status)
        return

    def set_trigger_mode(self, query, channel=None, quiet_for_cw=False):
        """Set trigger mode ('auto' or 'trig')."""
        channel = self.channel_format(channel)
        if self.get_trigger_mode(channel=channel)==query:
            if not quiet_for_cw:
                print("awg channel "+channel+" trigger mode is "+str(query)+".")
        else:
            if query=="auto":
                self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_MODE, self.AgM8190.VAL_TRIGGER_MODE_AUTO)
            elif query == "trig":
                self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_MODE, self.AgM8190.VAL_TRIGGER_MODE_TRIGGERED)
            else:
                raise AgM8190Error(str(query)+" is not a valid input.")
            if not quiet_for_cw:
                print("awg channel "+channel+" trigger mode set to "+str(query)+".")
        return

    def set_ViInt32_attribute(self, string, attr, value):
        """
        Set a ViInt32 attribute in the instrument. Refer to AgM8190 documentation for valid attributes.
        - string: String associated with the attribute (most often the channel or an empty string).
        - attr: Attribute from the AgM8190 wrapper (ex: self.AgM8190.ATTR_TRIGGER_MODE).
        - value: Int value (may be from the AgM8190 wrapper - ex: self.AgM8190.VAL_TRIGGER_MODE_AUTO).
        """
        value = vt.ViInt32(value)
        status = self.AgM8190.SetAttributeViInt32(self.session, str(string), attr, value)
        self.check_error(status)
        return

    def set_ViReal64_attribute(self, string, attr, value):
        """
        Set a ViReal64 attribute in the instrument. Refer to AgM8190 documentation for valid attributes.
        - string: String associated with the attribute (most often the channel or an empty string).
        - attr: Attribute from the AgM8190 wrapper (ex: self.AgM8190.ATTR_ARBITRARY_AC_AMPLITUDE).
        - value: Float value.
        """
        value = vt.ViReal64(value)
        status = self.AgM8190.SetAttributeViReal64(self.session, str(string), attr, value)
        self.check_error(status)
        return

    def string_sequence(self, string, loops=1, BB1=False, pulse_factor="length", channel=None):
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
        
        - loops: Number of internal loops.
        - pulse_factor: By default, the factor applies to the pulse length. Input pulse_factor='amp' to apply the factor to the pulse amplitude.
                        For delays, the factor always applies on duration.
        - BB1: Convert all pulses to their BB1 equivalent. If this option is activated, the only available factor is 0.5.           
        """
        channel = self.channel_format(channel)
        clean_string = (string.replace(" ", "").replace("\n", "").replace("\t", "").replace("\r", ""))
        if loops > 1:
            self.loop_start(loops, channel=channel)
        for tok, token in enumerate(clean_string.split(",")):
            phase = self.default_phase[channel]
            length = self.default_length[channel]
            tau = self.default_delay[channel]
            amp = self.default_amp[channel]

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
                            raise AgM8190Error("BB1 option is valid for pi or pi/2 pulses only.")
                    else:
                        self.pulse(channel=channel, length=length, phase=phase, amp=amp)

                elif token=="":
                    pass
                else:
                    raise ValueError
            except ValueError:
                raise AgM8190Error("Token '"+str(token)+"' for "+self.__class__.__name__+"."+str(inspect.stack()[0][3])+" was not recognized. \n\n"+self.__class__.__name__+"."+str(inspect.stack()[0][3])+" docstring:\n"+textwrap.dedent(Awg_M8190A.string_sequence.__doc__)+"\n")
        if loops > 1:
            self.loop_end(channel=channel)
        return



class AgM8190Error(nfu.LabMasterError):
    """Errors raised by the instrument"""
    pass