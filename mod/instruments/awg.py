__author__ =  "Laurent Bergeron <laurent.bergeron4@gmail.com>"

# Base modules
import inspect
import numpy as np
import visa as vi
import ctypes as ct
import matplotlib.pyplot as plt
import importlib
import time
import os

# Homemade modules
import wrappers.visa_types as vt
from ..units import *
from ..classes import Instrument
from .. import not_for_user
nfu = not_for_user


class Awg_M8190A(Instrument):
    """
    First use procedure: TODO
    I recommend to use the Soft Front Panel to debug.
    """
    def __init__(self, name, parent, resource):
        Instrument.__init__(self, name, parent, use_memory=True, use_pingpong=False)
        self.AgM8190 = importlib.import_module("mod.instruments.wrappers.dll_AgM8190")
        self.wfmGenLib2 = importlib.import_module("mod.instruments.wrappers.dll_wfmGenLib2")
        ## options
        self.verbose = False
        self.adjust_trig_latency = True # if True, needs a time buffer at the start (2 us should be enough)
        self.channels_to_load = [1]
        self.coupled = False # coupled channels
        self.marker_enable = True
        self.iscontinuous = False #This gets set to true using the CW method
        ## default pulse
        #default values are dictionaries with values defined below in set_default_params
        self.default_delay = {}
        self.default_length = {}
        self.default_freq = {}
        self.default_phase = {}
        self.default_amp = {}
        self.default_offset = {}
        self.default_channel = {}
        #Shape defines the shape of the envelope
        self.default_shape = {}
        self.set_default_params("1", delay=0, length=0, freq=0, phase=0, amp=1.0, offset=0.0, shape="square")
        self.set_default_params("2", delay=0, length=0, freq=0, phase=0, amp=1.0, offset=0.0, shape="square")
        self.default_pulse_factor="length"
        # awg characteristics
        self.granularity = 64
        self.tick = (5*self.granularity) # has to be >= 5*granularity and a multiple of granularity
        self.minimum_delay_count = 5*self.granularity + self.tick # 5*granularity to account for minimum idle command, self.tick to account for padding.
        # niquist sampling values for continous waveform (cw)
        self.niquist_threshold = 4  ## Min factor between frequency and sample rate.
        # Visa type attributes
        self.session = vt.ViSession()
        self.error_code = vt.ViInt32()
        self.error_message = (vt.ViChar*256)()
        # Individual show warnings
        self.show_warning_amp_clipping = True
        self.show_warning_freqrangeAC = True
        self.show_warning_loop_start = True
        self.show_warning_loop_end = True
        self.show_warning_no_inst1 = True
        self.show_warning_no_inst2 = True
        # instrument initilization
        current_dir = os.getcwd() # sometimes Keysight changes the current directory in the console.
        status = self.AgM8190.init(resource, True, True, ct.byref(self.session))
        os.chdir(current_dir)
        if self.verbose:
            print "AgM8190 init status", status
        try:
            self.check_error(status)
            status = self.AgM8190.reset(self.session)
            self.check_error(status)
            self.set_ref_clock_route("AXI")
            self.set_sample_clock_output_route("internal")
            self.set_sample_rate(9e9)
            self.set_channel_coupling("off")
            for channel in ("1", "2"):
                self.abort_generation(channel)
                status = self.AgM8190.SetAttributeViInt32(self.session, channel, self.AgM8190.ATTR_ARBITRARY_BIT_RESOLUTION_MODE, self.AgM8190.VAL_BIT_RESOLUTION_MODE_SPEED) # Set bit mode to 12-bit (only mode available)
                self.check_error(status)
                self.set_sample_clock_source_route(channel, "internal")
                self.set_channel_route(channel, "AC")
                self.set_amplitude(channel, self.default_amp[channel])
                self.set_offset(channel, self.default_offset[channel])
                self.set_arm_mode(channel, "self")
                self.set_trigger_mode(channel, "trig")
                self.set_gate_mode(channel, "trig")
        except:
            self.close()
            raise
        return

    def abort(self):
        self.use_memory = True
        self.abort_generation(1)
        self.abort_generation(2)
        return

    def abort_generation(self, channel):
        status = self.AgM8190.ChannelAbortGeneration(self.session, str(channel))
        self.check_error(status)
        return

    def close(self):
        # close all previously opened sessions if they were not closed because of bad user.
        for i in range(1,self.session.value):
            self.AgM8190.close(i) # will return negative if session was closed correctly.
        # close current session, can raise error.
        status = self.AgM8190.close(self.session)
        if self.verbose:
            print "AgM8190 close status", status
        return status


    def check_error(self, status):
        if self.verbose:
            print "awg:", status
        if not(status==0 or status==None):
            self.AgM8190.GetError(self.session, ct.byref(self.error_code), 255, self.error_message)
            raise AgM8190Error, self.error_message.value+" (code "+str(self.error_code.value)+")"
        return

    def cw(self, channel, freq=None, amp=None):
        if freq==None:
            freq = self.default_freq[str(channel)]
        self.lab.reset_instructions()
        self.set_trigger_mode(channel, "auto")
        self.adjust_trig_latency = False
        new_sample_rate = self.cw_optimal_sample_rate(freq)
        self.set_sample_rate(new_sample_rate)
        self.pulse(channel, length=self.tick/new_sample_rate, freq=freq, amp=amp, phase=0)
        self.channels_to_load = [channel]
       
        self.load_memory(is_cw=True)
        self.initiate_generation(1)
        self.iscontinous=True


    def cw_optimal_sample_rate(self, frequency):
        """
        samples_per_period figures out how many integer multiples of the frequency
        fits in the max sampling rate.
        """
        max_sample_rate = self.get_ViReal64_attribute("", self.AgM8190.ATTR_ARBITRARY_SAMPLE_RATE_MAX)
        N_periods = int(np.ceil(self.granularity*frequency/max_sample_rate))
        if N_periods > self.granularity/self.niquist_threshold:
            raise AgM8190Error, "Input frequency is too large for niquist_threshold. Please choose a new frequency because Niquist."
        
        return self.granularity/(N_periods/frequency)

    def force_trigger(self):
        status = self.AgM8190.SendSoftwareTrigger(self.session)
        self.check_error(status)
        return

    def get_amplitude(self, channel):
        channel_route = self.get_channel_route(channel)
        if channel_route=="DAC":
            amp = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DAC_AMPLITUDE)
        elif channel_route=="DC":
            amp = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DC_AMPLITUDE)
        elif channel_route=="AC":
            amp = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_AC_AMPLITUDE)
        return amp

    def get_arm_mode(self, channel):
        result = self.get_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_ARM_MODE)
        if result==self.AgM8190.VAL_ARM_MODE_SELF:
            mode = "self"
        elif result==self.AgM8190.VAL_ARM_MODE_ARMED:
            mode = "armed"
        return mode

    def get_channel_route(self, channel):
        result = self.get_ViInt32_attribute(channel, self.AgM8190.ATTR_OUTPUT_ROUTE)
        if result==self.AgM8190.VAL_OUTPUT_ROUTE_AC:
            route = "AC"
        elif result==self.AgM8190.VAL_OUTPUT_ROUTE_DC:
            route = "DC"
        elif result==self.AgM8190.VAL_OUTPUT_ROUTE_DAC:
            route = "DAC"
        return route

    def get_channel_coupling(self):
        result = self.get_ViInt32_attribute("", self.AgM8190.ATTR_INSTRUMENT_CHANNEL_COUPLING_ENABLED)
        if result==self.AgM8190.VAL_CHANNEL_COUPLING_STATE_ON:
            coupling = "on"
        elif result==self.AgM8190.VAL_CHANNEL_COUPLING_STATE_OFF:
            coupling = "off"
        return coupling

    def get_gate_mode(self, channel):
        result = self.get_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_GATE_MODE)
        if result==self.AgM8190.VAL_GATE_MODE_GATED:
            mode = "gated"
        elif result==self.AgM8190.VAL_GATE_MODE_TRIGGERED:
            mode = "trig"
        return mode

    def get_offset(self, channel):
        channel_route = self.get_channel_route(channel)
        if channel_route=="DAC":
            offset = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DAC_OFFSET)
        elif channel_route=="DC":
            offset = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DC_OFFSET)
        elif channel_route=="AC":
            offset = float(0)
        return offset


    def get_ref_clock_route(self):
        result = self.get_ViInt32_attribute("", self.AgM8190.ATTR_OUTPUT_REFERENCE_CLOCK_SOURCE)
        if result==self.AgM8190.VAL_REFERENCE_CLOCK_SOURCE_AXI:
            route = "AXI"
        elif result==self.AgM8190.VAL_REFERENCE_CLOCK_SOURCE_INTERNAL:
            route = "internal"
        elif result==self.AgM8190.VAL_REFERENCE_CLOCK_SOURCE_EXTERNAL:
            route = "external"
        return route

    def get_sample_clock_output_route(self):
        result = self.get_ViInt32_attribute("", self.AgM8190.ATTR_SAMPLE_CLOCK_OUTPUT)
        if result==self.AgM8190.VAL_SAMPLE_CLOCK_OUTPUT_INTERNAL:
            route = "internal"
        elif result==self.AgM8190.VAL_SAMPLE_CLOCK_OUTPUT_EXTERNAL:
            route = "external"
        return route

    def get_sample_rate(self):
        sample_rate = self.get_ViReal64_attribute("", self.AgM8190.ATTR_ARB_SAMPLE_RATE)
        return sample_rate

    def get_sample_clock_source_route(self, channel):
        result = vt.ViInt32()
        status = self.AgM8190.SampleClockGetSampleClockSource(self.session, str(channel), ct.byref(result))
        self.check_error(status)
        if result.value == self.AgM8190.VAL_SAMPLE_CLOCK_SOURCE_INTERNAL:
            route = "internal"
        elif result.value == self.AgM8190.VAL_SAMPLE_CLOCK_SOURCE_EXTERNAL:
            route = "external"
        return route

    def get_trigger_mode(self, channel):
        result = self.get_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_MODE)
        if result==self.AgM8190.VAL_TRIGGER_MODE_AUTO:
            mode = "auto"
        elif result==self.AgM8190.VAL_TRIGGER_MODE_TRIGGERED:
            mode = "trig"
        return mode

    def get_ViInt32_attribute(self, string, attr):
        result = vt.ViInt32()
        status = self.AgM8190.GetAttributeViInt32(self.session, str(string), attr, ct.byref(result))
        self.check_error(status)
        return result.value

    def get_ViReal64_attribute(self, string, attr):
        result = vt.ViReal64()
        status = self.AgM8190.GetAttributeViReal64(self.session, str(string), attr, ct.byref(result))
        self.check_error(status)
        return result.value

    def initiate_generation(self, channel):
        status = self.AgM8190.ChannelInitiateGeneration(self.session, str(channel))
        self.check_error(status)
        time.sleep(2*10240/self.get_sample_rate()) ## needed to let some time to initiate. This time is related to trigger latency according to Keysight. I put 2 times the latency just to be sure.
        return

    def load_memory(self, is_cw=False):
        # global time_start
        # time_start = time.time()
        for channel in self.channels_to_load:
            channel = str(channel)

            ### Abort current awg signal generation
            status = self.abort_generation(channel)
            self.check_error(status)

            ### Preprocess: Merge pulses and markers into blocks, detect delays.
            segments={}
            self.preprocess(channel, segments, is_cw)
            if segments=={}: ## skip the rest of the loop if no instructions are detected.
                if channel=="1" and self.show_warning_no_inst1:
                    print nfu.warn_msg()+"awg: no instructions for channel1"
                    self.show_warning_no_inst1 = False
                    continue
                if channel=="2" and self.show_warning_no_inst2:
                    print nfu.warn_msg()+"awg: no instructions for channel2"
                    self.show_warning_no_inst2 = False
                    continue

            ### Reset the sequence table
            self.AgM8190.SequenceTableReset(self.session, channel)
            self.check_error(status)
            ### Clear waveform data in awg memory.
            status = self.AgM8190.WaveformClearAll(self.session, channel)
            self.check_error(status)


            segment_ID_delay = vt.ViInt32(0) ## Segment ID for the zero amplitude waveform used for delays.
            segment_ID = vt.ViInt32(0) ## Segment ID for block type waveforms (will increment by one for each different block)
            data = (vt.ViInt32 * 6)() ## Array intented for the SequenceTableSetData() function
            waveform_int16_delay = (vt.ViInt16*self.tick)() ## waveform used for delay sequences (initialized with zeros)


            ### For each segment, load the sequence table accordingly. The process will differ if the segment is a "block" or a "delay".
            for i, (segment_type, segment_info, sequence_info) in enumerate(zip(segments["type"], segments["segment_info"], segments["sequence_info"])):
                if segment_type=="block":
                    waveform_int16 = segment_info["waveform"]
                    is_start_of_a_sequence = sequence_info["is_start"]
                    is_end_of_a_sequence = sequence_info["is_end"]
                    sequence_loops = sequence_info["loops"]
                    segment_loops = 1
                    if is_start_of_a_sequence and is_end_of_a_sequence:
                        segment_loops = sequence_loops
                        sequence_loops = 1
                        is_start_of_a_sequence = False
                        is_end_of_a_sequence = False
                    ### Load the block waveform in awg memory
                    status = self.AgM8190.WaveformCreateChannelWaveformInt16(self.session, channel, len(waveform_int16), waveform_int16, ct.byref(segment_ID))
                    self.check_error(status)
                    segment_ID_active = segment_ID
                elif segment_type=="delay":
                    is_start_of_a_sequence = sequence_info["is_start"]
                    is_end_of_a_sequence = sequence_info["is_end"]
                    sequence_loops = sequence_info["loops"]
                    segment_loops = int(segment_info["duration"]/len(waveform_int16_delay))
                    if is_start_of_a_sequence and is_end_of_a_sequence:
                        sequence_loops = 1
                        is_start_of_a_sequence = False
                        is_end_of_a_sequence = False
                        segment_loops *= sequence_loops
                    if segment_loops > 2**32-1:
                        raise AgM8190Error, "Maximum number of segment loops reached (2^32)."
                    ### Load the delay waveform in awg memory (could be outside of loop to reduce loading time, but then you have to deal with linear playtime requirements because of memory jumps.)
                    status = self.AgM8190.WaveformCreateChannelWaveformInt16(self.session, channel, len(waveform_int16_delay), waveform_int16_delay, ct.byref(segment_ID_delay))
                    self.check_error(status)
                    segment_ID_active = segment_ID_delay


                ### Prepare the data array
                data[0] = 0 ## data = 0 if nothing is special about the segment
                if self.marker_enable:
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


                ### Load the sequence table in awg memory.
                status = self.AgM8190.SequenceTableSetData(self.session, channel, i, 6, data)
                self.check_error(status)


                ########## idle command - max delay is 2**25 sample counts - deprecated ##########
                # data[0] += self.AgM8190.control["CommandFlag"] # Control
                # data[1] = 1 # Sequence Loop Count (N/A)
                # data[2] = 0 # Command Code (0 = idle command)
                # data[3] = 0 # Idle sample (value to be played during idle, int16 format)
                # data[4] = delay # Idle delay
                # data[5] = 0 # Not used (must be 0)
                # status = self.AgM8190.SequenceTableSetData(self.session, channel, i, 6, data)
                # self.check_error(status)
                ##################################################################################

            ### Choose correct sequencer mode
            if is_cw: 
                ## In continous waveform, only one segment is played.
                status = self.AgM8190.SetAttributeViInt32(self.session, channel, self.AgM8190.ATTR_ARBITRARY_SEQUENCING_MODE, self.AgM8190.VAL_SEQUENCING_MODE_ARBITRARY)
                self.check_error(status)
            else:
                ## Scenario mode for complex sequences (enables internal looping)
                status = self.AgM8190.SetAttributeViInt32(self.session, channel, self.AgM8190.ATTR_ARBITRARY_SEQUENCING_MODE, self.AgM8190.VAL_SEQUENCING_MODE_ST_SCENARIO)
                self.check_error(status)

            ### Turn Output On
            status = self.AgM8190.SetAttributeViBoolean(self.session, channel, self.AgM8190.ATTR_OUTPUT_ENABLED, True)
            self.check_error(status)


        # print "time to load awg:", time.time()-time_start
        return

    def load_memory_pingpong(self):
        self._current_buffer = (self._current_buffer+1)%2
        return

    def loop_start(self, channel, num_loops, autopad=True):
        """
        autopad=False is at your own risk
        """
        ### Add a tiny delay to start loop on a tick.
        if autopad:
            sample_rate = self.get_sample_rate()
            sample_counts = int(self.lab.time_cursor*sample_rate)
            if sample_counts%320 == 0:
                padded_counts = sample_counts
            else:
                padded_counts = sample_counts//self.tick*self.tick + self.tick
            self.lab.delay((padded_counts-sample_counts)/sample_rate)

        ### Insert instruction here
        self.instructions.append([self.lab.time_cursor, str(channel), "loop_start", num_loops])

        return

    def loop_end(self, channel, autopad=True):
        """
        autopad=False is at your own risk
        """
        ### Add a tiny delay to end loop on a tick.
        if autopad:
            sample_rate = self.get_sample_rate()
            sample_counts = int(self.lab.time_cursor*sample_rate)
            if sample_counts%320 == 0:
                padded_counts = sample_counts
            else:
                padded_counts = sample_counts//self.tick*self.tick + self.tick
            self.lab.delay((padded_counts-sample_counts)/sample_rate)
        ### Insert instruction here
        self.instructions.append([self.lab.time_cursor, str(channel), "loop_end", None])

        ### Update time cursor to account for all the loops.
        for inst in reversed(self.instructions):
            if inst[2]=="loop_end":
                raise AgM8190Error, "Nested internal loops are impossible."
            if inst[2]=="loop_start":
                time_started = inst[0]
                num_loops = inst[3]
                break

        ############################################ TEMPORARY FIX #########################################################
        # change when it's possible to call a loop start/end in the middle of a delay.
        min_length = self.tick/sample_rate
        self.pulse(1, length = min_length, amp=0, freq=0)
        self.lab.delay((self.lab.time_cursor - time_started)*(num_loops - 1) - min_length)
        ####################################################################################################################
        # self.lab.delay((self.lab.time_cursor - time_started)*(num_loops - 1))

        return

    def marker(self, channel):
        self.instructions.append([self.lab.time_cursor, str(channel), "marker", None])
        return

    def preprocess(self, channel, segments, is_cw):
        """
        input segments must be a dictionnary.
        """
        if not isinstance(segments, dict):
            raise AgM8190Error, "Input 'segments' should be an empty dictionnary."
        segments.clear()
        segments.update({"type":[], "segment_info":[], "sequence_info":[]})

        short_size = (2**16-1)
        # preprocess_time_start = time.time()


        ### Unzip user instructions
        channel_instructions = [inst for inst in self.instructions if inst[1]==str(channel)]
        if channel_instructions==[]:
            return  #if there's no instructions for this channel, what's the point?

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
        if (marker_times != []) and (not self.marker_enable):
            raise AgM8190Error, "Activate the marker_enable option when using markers."

        ### Get useful info from awg
        sample_rate = self.get_sample_rate()
        awg_amp = self.get_amplitude(channel)

        ### Combine marker specs and pulses specs (the trick is to consider each marker as a zero amplitude pulse: preprocess will pad correctly, then after padding markers will be added to the waveform)
        marker_count = len(marker_times)

        times += marker_times
        lengths += [128/sample_rate]*marker_count # a marker lasts for 128 samples (number doesn't really matter though because of padding. just needs to be small)
        freqs += [0]*marker_count # marker freq doesn't matter
        phases += [0]*marker_count # marker phase doesn't matter
        amps += [0]*marker_count # marker amplitude will be added to other pulses, needs to be zero.
        shapes += ["square"]*marker_count # marker shape doesn't matter

        ### Sort every list in time ascending order
        indices = sorted(range(len(times)),key=times.__getitem__)

        times = [times[i] for i in indices]
        lengths = [lengths[i] for i in indices]
        freqs = [freqs[i] for i in indices]
        phases = [phases[i] for i in indices]
        amps = [amps[i] for i in indices]
        shapes = [shapes[i] for i in indices]

        ### Add a final point to the times list
        times += [self.lab.total_duration]

        ### Merge pulses into blocks.
        ### One block is a set of pulses, either overlapping or separated by less then minimum_delay_time.
        minimum_delay_time = self.minimum_delay_count/sample_rate
        blocks = []
        i = 0
        while True:
            current_block = {"wfm_starts":[], "wfm_ends":[], "wfm_lengths":[], "wfm_periods":[], "wfm_phases":[], "wfm_amps":[], "wfm_shapes":[]}
            time_to_beat = times[i]+lengths[i]+minimum_delay_time # if the start of a pulse beats this time, a new block is created.
            while True:
                wfm_start = int(times[i]*sample_rate) # start of pulse in terms of sample counts.
                wfm_end = int((times[i]+lengths[i])*sample_rate) # length of pulse in terms of sample counts.
                if freqs[i] > 0:
                    wfm_period = sample_rate/freqs[i] # period of pulse in terms of sample counts.
                else:
                    wfm_period = -1 # no sine will be factored in wfmGenLib2
                wfm_phase = phases[i]*np.pi/180. # phase in radians
                if self.marker_enable:
                    wfm_amp = int(amps[i]*2047/awg_amp) # amps in int16 format (with MarkerEnable activated)
                else:
                    wfm_amp = int(amps[i]*32767/awg_amp) # amps in int16 format (without MarkerEnable activated)
                wfm_shape = self.wfmGenLib2.shapes_code[shapes[i]] # code for the shape as interpreted by wfmGenLib2
                current_block["wfm_starts"].append(wfm_start)
                current_block["wfm_ends"].append(wfm_end)
                current_block["wfm_lengths"].append(wfm_end-wfm_start)
                current_block["wfm_periods"].append(wfm_period)
                current_block["wfm_phases"].append(wfm_phase)
                current_block["wfm_amps"].append(wfm_amp)
                current_block["wfm_shapes"].append(wfm_shape)
                if times[i+1] > time_to_beat: # if the start of next pulse beats this time, a new block is created.
                    break
                else: # else, continue the while statement and the next pulse will be appended to current block
                    i+=1
                    if i > len(freqs)-1:
                        break
                    if time_to_beat < (times[i]+lengths[i]+minimum_delay_time): # update time_to_beat if end of current pulse is higher.
                        time_to_beat = times[i]+lengths[i]+minimum_delay_time
            blocks.append(current_block)
            i+=1
            if i > len(freqs)-1:
                break


        ### Adjust trigger latency if option is activated. This will chop 10240 counts from the start of sequence. The experiment needs a time buffer.
        if self.adjust_trig_latency:
            trigger_latency = 10240 # latency for trigger in terms of sample rate. There is an uncertainty of (+0/+64).
        else:
            trigger_latency = 0


        ### Add the first delay block.
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
                raise AgM8190Error, "You must add a time buffer at the beginning of experiment if using adjust_trig_latency=True."

        _magic_crop = False
        _blabla= True
        for b, block in enumerate(blocks):
            if _magic_crop:
                if _blabla:
                    _blabla = False
                    continue
                lag = (saved_loop_end - saved_loop_start)*(saved_loop_nums - 1)
                for i in range(len(block["wfm_starts"])):
                    block["wfm_starts"][i] -= lag
                    block["wfm_ends"][i] -= lag
                _magic_crop = False
            ### Find block min and max for padding
            block_start = int(np.min(block["wfm_starts"]))
            block_end = int(np.max(block["wfm_ends"]))
            segment_start = block_start//self.tick*self.tick
            if block_end%self.tick==0:
                segment_end = block_end
            else:
                segment_end = block_end//self.tick*self.tick + self.tick

            ### Declare C variables.
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

            ### Compute the sum of pulses.
            self.wfmGenLib2.wfmgen(C_countFreq, C_blockStart, C_wfmstart, C_wfmlength, C_arrPeriod, C_arrPhase, C_arrAmp, C_arrShape, C_arrOut_int16)

            ### Clip block amplitude if to high.
            if np.max(C_arrOut_int16) > short_size: # TODO: error because C_arrOut_int16 is limited to short. needs to be in C code.
                if self.show_clipping_warning:
                    print nfu.warn_msg()+"Amplitude of the sum of pulses ("+str(np.max(C_arrOut_int16)/short_size*awg_amp)+" V) is higher awg amplitude ("+str(awg_amp)+" V). Waveform will be clipped."
                for i, item in enumerate(C_arrOut_int16):
                    if item > 0:
                        C_arrOut_int16[i] = min(item, short_size)
                    else:
                        C_arrOut_int16[i] = max(item, -short_size)


            ### Add markers
            for time_ in marker_times:
                if segment_start <= int(time_*sample_rate) < segment_end:
                    index = int(time_*sample_rate - segment_start)
                    C_arrOut_int16[index] += 1


            ### Append "block" type segment to result.
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
                

            ### Add a delay block if it's not the end.
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
                    _magic_crop = True
                    saved_loop_end = segment_end

        ### Add the tiniest delay to indicate end of last sequence except if loading a continous waveform (cw)
        if not is_cw:
            segments["type"].append("delay")
            segments["segment_info"].append({"duration":self.tick})
            segments["sequence_info"].append({"is_start":False, "is_end":True, "loops":1})



        ### Detect long delays
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
        # TODO check segments and assert that there is as many start loops as end loops
        # print "preprocess duration", time.time() - preprocess_time_start
        return

    def preprocess_loops(self, loop_start_times, loop_end_times, loop_nums, segment_start, segment_end):
        is_start_of_a_sequence = False
        loops_count = 1
        is_end_of_a_sequence = False

        sample_rate = self.get_sample_rate()
        ### Find out if a loop starts in this segment
        count = 0
        for t, time_ in enumerate(loop_start_times):
            if segment_start <= int(time_*sample_rate) < segment_end:
                is_start_of_a_sequence=True
                loops_count = int(loop_nums[t])
                count+=1
        if count>1 and self.show_warning_loop_start:
            print nfu.warn_msg()+"Many loop starts detected in the same segment."
            self.show_warning_loop_start = False

        ### Find out if a loop ends in this segment
        count = 0
        for t, time_ in enumerate(loop_end_times):
            if segment_start < int(time_*sample_rate) <= segment_end:
                is_end_of_a_sequence=True
                count+=1
        if count>1 and self.show_warning_loop_end:
            print nfu.warn_msg()+"Many loop ends detected in the same segment."
            self.show_warning_loop_end = False

        if is_start_of_a_sequence:
            self._saved_loop_segment_start = segment_start
            self._saved_loop_num = loops_count
        if is_end_of_a_sequence:
            loop_duration = segment_end-self._saved_loop_segment_start
            self._crop_next_delay = int(loop_duration*(self._saved_loop_num - 1)) - 320

        return is_start_of_a_sequence, is_end_of_a_sequence, loops_count

    def print_loaded_sequence(self, channel, divider=None, ax=None):
        # TODO: have two plots for both channels
        if self.lab.total_duration == 0:
            raise AgM8190Error, "No sequence is loaded."

        sample_rate = self.get_sample_rate()

        segments = {}
        self.preprocess("1", segments)

        prefix, c = "", 1#nfu.time_auto_label(self.lab)

        if ax==None:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_xlabel("Time ("+prefix+"s)")
            # Span time for all experiment duration
            ax.set_xlim([0, c*(self.lab.total_duration - self.lab.end_buffer)])

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
            print str(i+1)+nfu.number_suffix(i+1), "block: one point in plot for", divider_, "points in awg."
            try:
                t = np.linspace(segment_start/sample_rate, segment_end/sample_rate-divider_/sample_rate, linspace_size)
                ax.plot(c*t, numpy_wfm ,'o', mew=0)
            except ValueError: # sometimes one point will be lost to the [::divider] operation.
                t = np.linspace(segment_start/sample_rate, segment_end/sample_rate, linspace_size+1)
                ax.plot(c*t, numpy_wfm ,'o', mew=0)

        plt.show()

        return



    def pulse(self, channel, length=None, phase=None, amp=None, freq=None, shape=None, rewind=None):
        # TODO: check if input is OK. Niquist freq, min pulse length, phase between -360 and 360, shape in valid options.
        if length==None:
            length = self.default_length[str(channel)]
        if phase==None:
            phase = self.default_phase[str(channel)]
        if amp==None:
            amp = self.default_amp[str(channel)]
        if freq==None:
            freq = self.default_freq[str(channel)]
        if shape==None:
            shape = self.default_shape[str(channel)]

        # check shape
        if shape not in self.wfmGenLib2.shapes_code.keys():
            raise AgM8190Error, shapes[i]+" is not a valid shape. Refer to dll_wfmGenLib2.py for valid shapes."

        # check freq
        if freq > 2*self.get_sample_rate():
            raise AgM8190Error, "Nyquist sampling criterion violated."
        if (not 50*MHz <= freq <= 5*GHz) and self.get_channel_route(1)=="AC":
            if self.show_warning_freqrangeAC:
                print nfu.warn_msg()+"AWG frequency is out of the 50MHz - 5GHz range in AC mode. Amplitude can be attenuated."
                self.show_warning_freqrangeAC = False

        # update instructions
        self.instructions.append([self.lab.time_cursor, str(channel), "pulse", (length, freq, phase, amp, shape)])
        self.lab.update_time_cursor(length, rewind)
        return

    def pulse_BB1_pi(self, channel, pi_len=None, phase=None, pi_amp=None, freq=None, shape=None):
        if phase==None:
            phase = self.default_phase[str(channel)]

        self.pulse(channel, length=pi_len, phase=phase,            amp=pi_amp, freq=freq, shape=shape)
        self.delay(5*us)
        self.pulse(channel, length=pi_len, phase=phase+0.5806*180, amp=pi_amp, freq=freq, shape=shape)
        self.delay(5*us)
        self.pulse(channel, length=pi_len, phase=phase+1.7411*180, amp=pi_amp, freq=freq, shape=shape)
        self.delay(5*us)
        self.pulse(channel, length=pi_len, phase=phase+1.7411*180, amp=pi_amp, freq=freq, shape=shape)
        self.delay(5*us)
        self.pulse(channel, length=pi_len, phase=phase+0.5806*180, amp=pi_amp, freq=freq, shape=shape)
        return

    def pulse_BB1_piby2(self, channel, pi_len=None, piby2_len=None, phase=None, pi_amp=None, piby2_amp=None, freq=None, shape=None):
        if pi_len==None:
            pi_len = self.default_length[str(channel)]
        if piby2_len==None:
            piby2_len = pi_len/2.
        if pi_amp==None:
            pi_amp = self.default_amp[str(channel)]
        if piby2_amp==None:
            piby2_amp = pi_amp/2.
        if phase==None:
            phase = self.default_phase[str(channel)]


        self.pulse(channel, length=piby2_len, phase=phase,            amp=piby2_amp, freq=freq, shape=shape)
        self.delay(5*us)
        self.pulse(channel, length=pi_len,    phase=phase+0.54*180,   amp=pi_amp, freq=freq, shape=shape)
        self.delay(5*us)
        self.pulse(channel, length=pi_len,    phase=phase+1.6194*180, amp=pi_amp, freq=freq, shape=shape)
        self.delay(5*us)
        self.pulse(channel, length=pi_len,    phase=phase+1.6194*180, amp=pi_amp, freq=freq, shape=shape)
        self.delay(5*us)
        self.pulse(channel, length=pi_len,    phase=phase+0.54*180,   amp=pi_amp, freq=freq, shape=shape)
        return

    def reset_warnings(self):
        """ Call this function inside nfu.get_ready() """
        self.show_warning_amp_clipping = True
        self.show_warning_freqrangeAC = True
        self.show_warning_loop_start = True
        self.show_warning_loop_end = True
        self.show_warning_no_inst1 = True
        self.show_warning_no_inst2 = True
        return


    def set_amplitude(self, channel, amp):
        current_amp = self.get_amplitude(channel)
        if amp==current_amp:
            print "awg channel "+str(channel)+" amplitude is "+nfu.auto_unit(amp, unit="V")+"."
        else:
            channel_route = self.get_channel_route(channel)
            if channel_route=="DAC":
                max_amp = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DAC_AMPLITUDE_MAX)
                min_amp = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DAC_AMPLITUDE_MIN)
                if min_amp <= amp <= max_amp:
                    self.set_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DAC_AMPLITUDE, amp)
                else:
                    raise AgM8190Error, "Channel "+str(channel)+" amplitude is not in the permitted range: "+nfu.auto_unit(min_amp, unit="V")+" to "+nfu.auto_unit(max_amp, unit="V")+"."
            elif channel_route=="DC":
                max_amp = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DC_AMPLITUDE_MAX)
                min_amp = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DC_AMPLITUDE_MIN)
                if min_amp <= amp <= max_amp:
                    self.set_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DC_AMPLITUDE, amp)
                else:
                    raise AgM8190Error, "Channel "+str(channel)+" amplitude is not in the permitted range: "+nfu.auto_unit(min_amp, unit="V")+" to "+nfu.auto_unit(max_amp, unit="V")+"."
            elif channel_route=="AC":
                max_amp = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_AC_AMPLITUDE_MAX)
                min_amp = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_AC_AMPLITUDE_MIN)
                if min_amp <= amp <= max_amp:
                    self.set_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_AC_AMPLITUDE, amp)
                else:
                    raise AgM8190Error, "Channel "+str(channel)+" amplitude is not in the permitted range: "+nfu.auto_unit(min_amp, unit="V")+" to "+nfu.auto_unit(max_amp, unit="V")+"."
            print "awg channel "+str(channel)+" amplitude set to "+nfu.auto_unit(amp, unit="V")+"."
        return


    def set_arm_mode(self, channel, query):
        if self.get_arm_mode(channel)==query:
            print "awg channel "+str(channel)+" arm mode is "+str(query)+"."
        else:
            if query=="armed":
                self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_ARM_MODE, self.AgM8190.VAL_ARM_MODE_ARMED)
            elif query=="self":
                self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_ARM_MODE, self.AgM8190.VAL_ARM_MODE_SELF)
            else:
                raise AgM8190Error, str(query)+" is not a valid input."
            print "awg channel "+str(channel)+" arm mode set to "+str(query)+"."
        return

    def set_channel_coupling(self, query):
        if self.get_channel_coupling()==query:
            print "awg channel coupling is "+str(query)+"."
        else:
            if query=="on":
                self.set_ViInt32_attribute("", self.AgM8190.ATTR_INSTRUMENT_CHANNEL_COUPLING_ENABLED, self.AgM8190.VAL_CHANNEL_COUPLING_STATE_ON)
            elif query=="off":
                self.set_ViInt32_attribute("", self.AgM8190.ATTR_INSTRUMENT_CHANNEL_COUPLING_ENABLED, self.AgM8190.VAL_CHANNEL_COUPLING_STATE_OFF)
            else:
                raise AgM8190Error, str(query)+" is not a valid input."
            print "awg channel coupling set to "+str(query)+"."
        return

    def set_channel_route(self, channel, query):
        current_route = self.get_channel_route(channel)
        if query==current_route:
            print "awg channel "+str(channel)+" route is "+str(query)+"."
        else:
            if query=="AC":
                self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_OUTPUT_ROUTE, self.AgM8190.VAL_OUTPUT_ROUTE_AC)
            elif query=="DC":
                self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_OUTPUT_ROUTE, self.AgM8190.VAL_OUTPUT_ROUTE_DC)
            elif query=="DAC":
                self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_OUTPUT_ROUTE, self.AgM8190.VAL_OUTPUT_ROUTE_DAC)
            else:
                raise AgM8190Error, str(query)+" is not a valid input."
            print "awg channel "+str(channel)+" route set to "+str(query)+"."
        return

    def set_default_params(self, channel, delay=None, length=None, freq=None, phase=None, amp=None, offset=None, shape=None):
        if delay!=None:
            self.default_delay[str(channel)] = delay
        if length!=None:
            self.default_length[str(channel)] = length
        if freq!=None:
            self.default_freq[str(channel)] = freq
        if phase!=None:
            self.default_phase[str(channel)] = phase
        if amp!=None:
            self.default_amp[str(channel)] = amp
        if offset!=None:
            self.default_offset[str(channel)] = offset
        if shape!=None:
            self.default_shape[str(channel)] = shape
        return


    def set_gate_mode(self, channel, query):
        if self.get_gate_mode(channel)==query:
            print "awg channel "+str(channel)+" gate mode is "+str(query)+"."
        else:
            if query=="gated":
                status = self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_GATE_MODE, self.AgM8190.VAL_GATE_MODE_GATED)
            elif query in "trig":
                status = self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_GATE_MODE, self.AgM8190.VAL_GATE_MODE_TRIGGERED)
            else:
                raise AgM8190Error, str(query)+" is not a valid input."
            print "awg channel "+str(channel)+" gate mode set to "+str(query)+"."
        return

    def set_offset(self, channel, offset):
        current_offset = self.get_offset(channel)
        if offset==current_offset:
            print "awg channel "+str(channel)+" offset is "+nfu.auto_unit(offset, unit="V")+"."
        else:
            channel_route = self.get_channel_route(channel)
            if channel_route=="DAC":
                max_offset = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DAC_OFFSET_MAX)
                min_offset = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DAC_OFFSET_MIN)
                if min_offset <= offset <= max_offset:
                    self.set_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DAC_OFFSET, offset)
                else:
                    raise AgM8190Error, "Channel "+str(channel)+" offset is not in the permitted range: "+nfu.auto_unit(min_offset, unit="V")+" to "+nfu.auto_unit(max_offset, unit="V")+"."
            elif channel_route=="DC":
                max_offset = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DC_OFFSET_MAX)
                min_offset = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DC_OFFSET_MIN)
                if min_offset <= offset <= max_offset:
                    self.set_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DC_OFFSET, offset)
                else:
                    raise AgM8190Error, "Channel "+str(channel)+" offset is not in the permitted range: "+nfu.auto_unit(min_offset, unit="V")+" to "+nfu.auto_unit(max_offset, unit="V")+"."
            elif channel_route=="AC":
                if offset==0:
                    pass # print "awg channel "+str(channel)+" offset is always 0 V when using AC route."
                else:
                    raise AgM8190Error, "Channel "+str(channel)+" offset has to be 0 V when using AC route."
                return
            print "awg channel "+str(channel)+" offset set to "+nfu.auto_unit(offset, unit="V")+"."
        return

    def set_ref_clock_route(self, query):
        current_route = self.get_ref_clock_route()
        if query==current_route:
            print "awg ref clock route is "+current_route+"."
        else:
            if query=="AXI":
                self.set_ViInt32_attribute("", self.AgM8190.ATTR_OUTPUT_REFERENCE_CLOCK_SOURCE, self.AgM8190.VAL_REFERENCE_CLOCK_SOURCE_AXI)
            elif query == "internal":
                raise AgM8190Error, 'internal ref clock is not available currently. Try "AXI" instead'
                self.set_ViInt32_attribute("", self.AgM8190.ATTR_OUTPUT_REFERENCE_CLOCK_SOURCE, self.AgM8190.VAL_REFERENCE_CLOCK_SOURCE_INTERNAL)
            elif query == "external":
                self.set_ViInt32_attribute("", self.AgM8190.ATTR_OUTPUT_REFERENCE_CLOCK_SOURCE, self.AgM8190.VAL_REFERENCE_CLOCK_SOURCE_EXTERNAL)
            else:
                raise AgM8190Error, str(query)+" is not a valid input."
            print "awg ref clock route set to "+str(query)+"."
        return

    def set_sample_clock_output_route(self, query):
        current_route = self.get_sample_clock_output_route()
        if query==current_route:
            print "awg sample clock output route is "+str(query)+"."
        else:
            if query in "internal":
                self.set_ViInt32_attribute("", self.AgM8190.ATTR_SAMPLE_CLOCK_OUTPUT, self.AgM8190.VAL_SAMPLE_CLOCK_OUTPUT_INTERNAL)
            elif query in "external":
                self.set_ViInt32_attribute("", self.AgM8190.ATTR_SAMPLE_CLOCK_OUTPUT, self.AgM8190.VAL_SAMPLE_CLOCK_OUTPUT_EXTERNAL)
            else:
                raise AgM8190Error, str(query)+" is not a valid input."
            print "awg sample clock output route set to "+str(query)+"."
        return

    def set_sample_rate(self, rate):
        #sample rate in Hz (samples/second)
        max_sample_rate = self.get_ViReal64_attribute("", self.AgM8190.ATTR_ARBITRARY_SAMPLE_RATE_MAX)
        min_sample_rate = self.get_ViReal64_attribute("", self.AgM8190.ATTR_ARBITRARY_SAMPLE_RATE_MIN)
        current_rate = self.get_sample_rate()
        if current_rate == rate:
            print "awg sample rate is "+nfu.auto_unit(rate, "Sa/s")+"."
        else:
            if rate < min_sample_rate:
                raise AgM8190Error, "Requested sample rate is lower than minimum allowed, "+nfu.auto_unit(min_sample_rate, "Hz")+"."
            elif rate > max_sample_rate:
                raise AgM8190Error, "Requested sample rate is higher than maximum allowed, "+nfu.auto_unit(max_sample_rate, "Hz")+"."
            else:
                self.set_ViReal64_attribute("", self.AgM8190.ATTR_ARB_SAMPLE_RATE, rate)
                print "awg sample rate set to "+nfu.auto_unit(rate, "Sa/s")+"."
        return

    def set_sample_clock_source_route(self, channel, query):
        current_route = self.get_sample_clock_source_route(channel)
        if query==current_route:
            print "awg channel "+str(channel)+" sample clock source route is "+str(query)+"."
        else:
            if query == "internal":
                status = self.AgM8190.SampleClockSetSampleClockSource(self.session, channel, self.AgM8190.VAL_SAMPLE_CLOCK_SOURCE_INTERNAL)
            elif query == "external":
                status = self.AgM8190.SampleClockSetSampleClockSource(self.session, channel, self.AgM8190.VAL_SAMPLE_CLOCK_SOURCE_EXTERNAL)
            else:
                raise AgM8190Error, str(query)+" is not a valid input."
            print "awg channel "+str(channel)+" sample clock source route set to "+str(query)+"."
            self.check_error(status)
        return

    def set_trigger_mode(self, channel, query):
        if self.get_trigger_mode(channel)==query:
            print "awg channel "+str(channel)+" trigger mode is "+str(query)+"."
        else:
            if query=="auto":
                self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_MODE, self.AgM8190.VAL_TRIGGER_MODE_AUTO)
            elif query == "trig":
                self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_MODE, self.AgM8190.VAL_TRIGGER_MODE_TRIGGERED)
            else:
                raise AgM8190Error, str(query)+" is not a valid input."
            print "awg channel "+str(channel)+" trigger mode set to "+str(query)+"."
        return

    def set_ViInt32_attribute(self,  string, attr, value):
        value = vt.ViInt32(value)
        status = self.AgM8190.SetAttributeViInt32(self.session, str(string), attr, value)
        self.check_error(status)
        return

    def set_ViReal64_attribute(self, string, attr, value):
        value = vt.ViReal64(value)
        status = self.AgM8190.SetAttributeViReal64(self.session, str(string), attr, value)
        self.check_error(status)
        return

    def string_sequence(self, channel, string, loops=1, BB1=False, pulse_factor=None):
        """ uses default delay, length, amplitude, freq and shape. not space/enter/tab sensitive"""
        clean_string = (string.replace(" ", "").replace("\n", "").replace("\t", ""))
        if pulse_factor==None:
            pulse_factor = self.default_pulse_factor
        if loops > 1:
            self.loop_start(channel, loops)
        for tok, token in enumerate(clean_string.split(",")):
            phase = self.default_phase[str(channel)]
            length = self.default_length[str(channel)]
            tau = self.default_delay[str(channel)]
            amp = self.default_amp[str(channel)]

            try:
                if ("t"==token.split("/")[0].split("*")[0]) or ("tau"==token.split("/")[0].split("*")[0]):
                    if "/" in token:
                        factor = 1/float(token.split("/")[-1])
                    elif "*" in token:
                        factor = float(token.split("*")[-1])
                    else:
                        factor = 1
                    self.delay(tau*factor)
                elif ("X" in token) or ("Y" in token):
                    # X or Y phase
                    if "X" in token:
                        phase+=0
                    elif "Y" in token:
                        phase+=90
                    # add 180 if minus sign is present
                    if "-" in token:
                        phase +=180
                    # pulse length (or amp) divider/multiplier
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
                    # BB1 option
                    if BB1:
                        if factor==1:
                            self.pulse_BB1_pi(str(channel), pi_len=self.default_length[str(channel)], phase=phase, pi_amp=amp)
                        elif factor==0.5:
                            self.pulse_BB1_piby2(str(channel), pi_len=self.default_length[str(channel)], piby2_len=length, phase=phase, pi_amp=self.default_amp[str(channel)],  piby2_amp=amp)
                        else:
                            raise AgM8190Error, "BB1 option is valid for pi or pi/2 pulses only."
                    else:
                        self.pulse(str(channel), length=length, phase=phase, amp=amp)

                elif token=="":
                    pass
                else:
                    raise ValueError
            except ValueError:
                raise AgM8190Error, "Token '"+str(token)+"' for "+self.__class__.__name__+"."+str(inspect.stack()[0][3])+" was not recognized. \n\n"+self.__class__.__name__+"."+str(inspect.stack()[0][3])+" docstring:\n"+textwrap.dedent(Awg.string_sequence.__doc__)+"\n"
        if loops > 1:
            self.loop_end(channel)
        return



class AgM8190Error(nfu.LabMasterError):
    """Errors raised by the instrument"""
    pass
