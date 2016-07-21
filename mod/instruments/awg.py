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
        
        
class Awg(Instrument):
    """
    First use procedure: TODO
    I recommend to use the Soft Front Panel to debug.
    """
    def __init__(self, name, parent, resource):
        Instrument.__init__(self, name, parent, use_memory=True, is_ping_pong=False)
        self.AgM8190 = importlib.import_module("mod.instruments.wrappers.dll_AgM8190")
        self.wfmGenLib2 = importlib.import_module("mod.instruments.wrappers.dll_wfmGenLib2")
        # options
        self.verbose =False
        self.skip_warning = False
        self.adjust_trig_latency = True # if True, needs a time buffer at the start (2 us should be enough)
        self.channels_to_load = [1]
        self.coupled = False # coupled channels
        # default pulse
        self.default_delay = {}
        self.default_length = {}
        self.default_freq = {}
        self.default_phase = {}
        self.default_amp = {}
        self.default_offset = {}
        self.default_shape = {}
        self.set_default_params("1", delay=0, length=0, freq=0, phase=0, amp=1.0, offset=0.0, shape="square")
        self.set_default_params("2", delay=0, length=0, freq=0, phase=0, amp=1.0, offset=0.0, shape="square")
        # awg characteristics
        self.granularity = 64
        self.tick = (5*self.granularity)
        self.minimum_idle_count = 10*self.granularity + 5*self.granularity # 10*64 to account for minimum idle command, 5*64 for minimum segment length
        # Visa type attributes
        self.session = vt.ViSession()
        self.error_code = vt.ViInt32()
        self.error_message = (vt.ViChar*256)()
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
            self.set_sample_clock_rate(9e9)
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
        if status not in (0, None):
            self.AgM8190.GetError(self.session, ct.byref(self.error_code), 255, self.error_message)
            raise AgM8190Error, self.error_message.value+" (code "+str(self.error_code.value)+")"
        return
    
    def delay_big(self, channel, duration): #, rewind=None):
        """ didnt figure how rewind would behave here, TODO."""
        sample_rate = self.get_sample_clock_rate()
        counts = int(duration*sample_rate)
        seg_loops = counts//self.tick + 1
        if seg_loops < 2**32:
            self.delay(duration)
        else:
            max_time = (2**32)*self.tick/sample_rate
            self.delay(max_time - us)
            self.pulse(str(channel), length=us, amp=0, freq=0, phase=0, shape="square")
            self.delay_big(duration-max_time)
        return
        
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
        
    def get_sample_clock_rate(self):
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
        time.sleep(0.1) # needed to let some time to initiate. 
        return
        
    def load_memory(self):
        global time_start
        time_start = time.time()
        for channel in self.channels_to_load:
            channel = str(channel)
            time_clearing_stuff = time.time()
            status = self.abort_generation(channel)
            self.check_error(status)
            self.AgM8190.SequenceTableReset(self.session, channel)
            self.check_error(status)
            status = self.AgM8190.WaveformClearAll(self.session, channel)
            self.check_error(status)
            print "abort_gen duration", time.time()-time_clearing_stuff
            C_blocks=[]
            self.preprocess(channel, C_blocks)
            if C_blocks==[]:
                print "empty instructions for channel"+channel
                continue
            
            
            segment_ID_idle = vt.ViInt32(0)
            segment_ID = vt.ViInt32(0)
            data = (vt.ViInt32 * 6)()
            
            waveform_int16_idle = (vt.ViInt16*self.tick)() # initialized with zeros
            # Define and download the "idle" segment
            status = self.AgM8190.WaveformCreateChannelWaveformInt16(self.session, channel, len(waveform_int16_idle), waveform_int16_idle, ct.byref(segment_ID_idle))
            self.check_error(status)
        
            for i, (wfm_command, args) in enumerate(C_blocks):
                time_one_block = time.time()
                if wfm_command=="block":
                    waveform_int16, _, _ = args
                    seg_loops = 1
                    time_wfmCreateChannel = time.time()
                    # Define and download the segment
                    status = self.AgM8190.WaveformCreateChannelWaveformInt16(self.session, channel, len(waveform_int16), waveform_int16, ct.byref(segment_ID))
                    self.check_error(status)
                    print "Wfm Create Channel duration:", time.time()-time_wfmCreateChannel
                    segment_ID_active = segment_ID.value
                elif wfm_command=="idle":
                    delay = args     
                    seg_loops = int(delay/len(waveform_int16_idle))
                    if seg_loops > 2**32:
                        raise nfu.LabMasterError, "Maximum number of loops reached (2^32). Use the delay_big() method to get around this issue."
                    segment_ID_active = segment_ID_idle.value
                    
                time_select_segments = time.time()
                # Select the segments
                status = self.AgM8190.SetAttributeViInt32(self.session, channel, self.AgM8190.ATTR_WAVEFORM_ACTIVE_SEGMENT, segment_ID_active)
                self.check_error(status)
                print "Wfm select segment duration:", time.time()-time_select_segments
                
                data[0] = 0
                if i == 0:
                    data[0] += self.AgM8190.control["InitMarkerSequence"]
                if i == len(C_blocks)-1:
                    data[0] += self.AgM8190.control["EndMarkerSequence"]
                data[0] += self.AgM8190.control["MarkerEnable"] # Control
                data[1] = 1 # Sequence Loop Count
                data[2] = seg_loops # Segment Loop Count
                data[3] = segment_ID_active  # Segment ID
                data[4] = 0 # Segment Start Offset (0 = no offset)
                data[5] = 0xffffffff # Segment End Offset (0xffffffff = no offset)
                time_SequenceTable = time.time()
                status = self.AgM8190.SequenceTableSetData(self.session, channel, i, 6, data)
                self.check_error(status)
                print "SequenceTable duration:", time.time()-time_SequenceTable
                print "One block duration:", time.time()-time_one_block
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
            
            time_sequencer_and_output_on = time.time()
            # Choose correct sequencer mode
            status = self.AgM8190.SetAttributeViInt32(self.session, channel, self.AgM8190.ATTR_ARBITRARY_SEQUENCING_MODE, self.AgM8190.VAL_SEQUENCING_MODE_ST_SEQUENCE)
            self.check_error(status)

            # Turn Output On
            status = self.AgM8190.SetAttributeViBoolean(self.session, channel, self.AgM8190.ATTR_OUTPUT_ENABLED, True)
            self.check_error(status)
            
            print "sequencer and output on duration", time.time() - time_sequencer_and_output_on 
        print "time to load awg:", time.time()-time_start
        return
        
    def load_memory_ping_pong(self):
        self._current_buffer = (self._current_buffer+1)%2
        return
        
    
    def marker(self, channel, rewind=None):
        self.instructions.append([self.lab.time_cursor, str(channel), "marker", None])
        self.lab.update_instructions_timing(0., rewind)
        return
        
    def preprocess(self, channel, result):
        """ 
        input result must be an empty list. 
        
        """ 
        import time
        show_clipping_warning = True
        short_size = (2**16-1)
        preprocess_time_start = time.time()
        pulse_times, pulse_lengths, pulse_freqs, pulse_phases, pulse_amps, pulse_shapes, marker_times = self.unzip_instructions(channel)

        # If there's no instructions for this channel, what's the point?
        if (pulse_times+marker_times)==[]:
            return

        # Get useful info from awg
        sample_rate = self.get_sample_clock_rate()
        awg_amp = self.get_amplitude(channel)
        
        # add marker specs to pulses specs
        times = pulse_times + marker_times
        lengths = pulse_lengths + [128./sample_rate]*len(marker_times) # the pulse generated by a marker is max 128 samples.
        freqs = pulse_freqs + [0]*len(marker_times) # marker freq doesn't matter
        phases = pulse_phases + [0]*len(marker_times) # marker phase doesn't matter
        amps = pulse_amps + [0]*len(marker_times) # marker amplitude will be added to other pulses, needs to be zero.
        shapes = pulse_shapes + ["square"]*len(marker_times) # marker shape doesn't matter
        
        # Sort every list in time ascending order
        indices = sorted(range(len(times)),key=times.__getitem__)
        times = [times[i] for i in indices]
        lengths = [lengths[i] for i in indices]
        freqs = [freqs[i] for i in indices]
        phases = [phases[i] for i in indices]
        amps = [amps[i] for i in indices]
        shapes = [shapes[i] for i in indices]
        # Add a final point to the times list
        times += [self.lab.total_duration]

        # Find number of blocks. One block is a set of pulses, either overlapping or separated by less then self.minimum_idle_count (converted to time). They are to be separated by idle commands in awg memory.
        minimum_idle_time = self.minimum_idle_count/sample_rate
        blocks = []
        i = 0  
        while True:
            block = []
            time_to_beat = times[i]+lengths[i]+minimum_idle_time # if the start of a pulse beats this time, a new block is created.
            while True:
                wfm_start = int(times[i]*sample_rate) # start of pulse in terms of sample counts.
                wfm_length = int(lengths[i]*sample_rate)-1 # length of pulse in terms of sample counts.
                if wfm_start < self.minimum_idle_count: # deal with an idle block smaller than minimum at the start of sequence.
                    wfm_length += wfm_start
                    wfm_start = 0
                if freqs[i] > 0:
                    wfm_period = sample_rate/freqs[i] # period of pulse in terms of sample counts.
                else:
                    wfm_period = -1 # no sine will be factored in wfmGenLib2
                wfm_phase = phases[i]*np.pi/180. # phase in radians
                wfm_amp = amps[i] # amps will be changed for int16 format later on.
                wfm_shape = self.wfmGenLib2.shapes_code[shapes[i]] # code for the shape as interpreted by wfmGenLib2
                block.append([wfm_start, wfm_length, wfm_period, wfm_phase, wfm_amp, wfm_shape])
                if times[i+1] > time_to_beat: # if the start of next pulse beats this time, a new block is created.
                    break
                else:# else, continue the while statement and the next pulse will be appended to current block
                    i += 1
                    if i > len(freqs)-1:
                        break
                    if time_to_beat < (times[i]+lengths[i]+minimum_idle_time): # update time_to_beat if end of current pulse is higher.
                        time_to_beat = times[i]+lengths[i]+minimum_idle_time
            blocks.append(block)
            i+=1
            if i > len(freqs)-1:
                break
                
        
        
        if self.adjust_trig_latency:
            trigger_latency = 10240 # latency for trigger in terms of sample rate. There is an uncertainty of (+0/+64).
        else:
            trigger_latency = 0
        
        
        # Add the first idle block.
        first_padded_block_start = int(np.min([item[0] for item in blocks[0]]))//self.tick*self.tick - trigger_latency
        if self.minimum_idle_count < first_padded_block_start:
            result.append( ["idle", first_padded_block_start] )
        else:
            if trigger_latency > 0:
                raise nfu.LabMasterError, "You must add a time buffer at the beginning of experiment if using adjust_trig_latency=True."

        for b, block in enumerate(blocks):
            # Find block min and max for padding
            block_start = int(np.min([item[0] for item in block]))
            block_end = int(np.max([item[0]+item[1] for item in block]))
            padded_block_start = block_start//self.tick*self.tick
            if block_end%self.tick==0:
                padded_block_end = block_end
            else:
                padded_block_end = block_end//self.tick*self.tick + self.tick
            # print "padded", padded_block_start, block_start, block_end, padded_block_end
            # Declare C variables
            C_countFreq = ct.c_int(len(block))
            C_blockStart = ct.c_longlong(padded_block_start)
            C_wfmstart = (ct.c_longlong*len(block))()
            C_wfmlength = (ct.c_longlong*len(block))()
            C_arrPeriod = (ct.c_double*len(block))()
            C_arrPhase = (ct.c_double*len(block))()
            C_arrAmp = (ct.c_double*len(block))()
            C_arrShape = (ct.c_int*len(block))()
            C_arrOut_int16 = (ct.c_short*(padded_block_end-padded_block_start))()
            # fill C arrays with respective pulse specs.
            for p, item in enumerate(block):
                C_wfmstart[p] = ct.c_longlong(item[0])
                C_wfmlength[p] = ct.c_longlong(item[1])
                C_arrPeriod[p] = ct.c_double(item[2])
                C_arrPhase[p] = ct.c_double(item[3])
                C_arrAmp[p] = ct.c_double(item[4])
                C_arrShape[p] = ct.c_int(item[5])
            self.wfmGenLib2.wfmgen(C_countFreq, C_blockStart, C_wfmstart, C_wfmlength, C_arrPeriod, C_arrPhase, C_arrAmp, C_arrShape, C_arrOut_int16, ct.c_double(awg_amp))
            # Clip block amplitude if to high.
            if np.max(C_arrOut_int16) > short_size:
                print nfu.warn_msg()+"Amplitude of the sum of pulses ("+str(np.max(C_arrOut_int16)/short_size*awg_amp)+" V) is higher awg amplitude ("+str(awg_amp)+" V). Waveform will be clipped."
                if not self.skip_warning:
                    if raw_input("Do you want to continue anyway? [Y/n]") in nfu.positive_answer_Y():
                        show_clipping_warning = False
                    else:
                        raise KeyboardInterrupt
                for i, item in enumerate(C_arrOut_int16):
                    if item > 0:
                        C_arrOut_int16[i] = min(item, short_size)
                    else:
                        C_arrOut_int16[i] = max(item, -short_size)
            

            # Add markers
            for time in marker_times:
                if padded_block_start <= time*sample_rate < padded_block_end:
                    index = int(time*sample_rate - padded_block_start)
                    C_arrOut_int16[index] += 1
                                
                    
                
            result.append( ["block", (C_arrOut_int16, padded_block_start, padded_block_end)] )
            
            # add an idle block if it's not the end.
            if b < len(blocks) - 1:
                next_padded_block_start = int(np.min([item[0] for item in blocks[b+1]]))//self.tick*self.tick
                result.append( ["idle", next_padded_block_start-padded_block_end] )
            # add an idle block if it's the end AND there is a delay closing the sequence. # TODO: really useful to do this?
            elif (b == len(blocks) - 1):
                end_of_experiment = int((self.lab.total_duration-self.lab.end_buffer)*sample_rate) 
                if (padded_block_end < end_of_experiment):
                    result.append( ["idle", end_of_experiment-padded_block_end] )

        print "preprocess duration", time.time() - preprocess_time_start
        return 
        
    def print_loaded_sequence(self, channel, divider=None, ax=None):
        # TODO: have two plots for both channels
        if self.lab.total_duration == 0:
            raise nfu.LabMasterError, "No sequence is loaded."

        sample_rate = self.get_sample_clock_rate()

        C_blocks = []
        self.preprocess("1", C_blocks)

        prefix, c = "", 1#nfu.time_auto_label(self.lab)

        if ax==None:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_xlabel("Time ("+prefix+"s)")
            # Span time for all experiment duration
            ax.set_xlim([0, c*(self.lab.total_duration - self.lab.end_buffer)])
            
        for i, (wfm_command, args) in enumerate(C_blocks):
            if wfm_command=="idle":
                continue
            (waveform, block_start, block_end) = args
            if divider==None:
                divider_ = 1
                while True:
                    linspace_size = int((block_end-block_start)/divider_)
                    arange_step = divider_/sample_rate
                    if linspace_size < 10000:
                        break
                    divider_ *= 2
            else:
                divider_ = int(divider)
                linspace_size = int((block_end-block_start)/divider_)
                arange_step = divider_/sample_rate
            numpy_wfm = np.ctypeslib.as_array(waveform)[::divider_]
            print str(i+1)+nfu.number_suffix(i+1), "block: one point in plot for", divider_, "points in awg."
            try:
                t = np.linspace(block_start/sample_rate, block_end/sample_rate-divider_/sample_rate, linspace_size)
                ax.plot(c*t, numpy_wfm ,'o', mew=0)
            except ValueError: # sometimes one point will be lost to the [::divider] operation. 
                t = np.linspace(block_start/sample_rate, block_end/sample_rate, linspace_size+1)
                ax.plot(c*t, numpy_wfm ,'o', mew=0)
        



        plt.show()
        
        return
    
    def pulse_BB1_pi(self, channel, length=None, phase=None, amp=None, freq=None, shape=None):
        if length==None:
            length = self.default_length[str(channel)]
        if phase==None:
            phase = self.default_phase[str(channel)]
        self.pulse(channel, pi_len=pi_len, phase=phase,            amp=amp, freq=freq, shape=shape)
        self.delay(5*us)
        self.pulse(channel, pi_len=pi_len, phase=phase+0.5806*180, amp=amp, freq=freq, shape=shape)
        self.delay(5*us)
        self.pulse(channel, pi_len=pi_len, phase=phase+1.7411*180, amp=amp, freq=freq, shape=shape)
        self.delay(5*us)
        self.pulse(channel, pi_len=pi_len, phase=phase+1.7411*180, amp=amp, freq=freq, shape=shape)
        self.delay(5*us)
        self.pulse(channel, pi_len=pi_len, phase=phase+0.5806*180, amp=amp, freq=freq, shape=shape)
        return
        
    def pulse_BB1_piby2(self, channel, length=None, phase=None, amp=None, freq=None, shape=None):
        if length==None:
            length = self.default_length[str(channel)]
        if phase==None:
            phase = self.default_phase[str(channel)]
        self.pulse(channel, pi_len=pi_len/2., phase=phase,            amp=amp, freq=freq, shape=shape)
        self.delay(5*us)
        self.pulse(channel, pi_len=pi_len,    phase=phase+0.54*180,   amp=amp, freq=freq, shape=shape)
        self.delay(5*us)
        self.pulse(channel, pi_len=pi_len,    phase=phase+1.6194*180, amp=amp, freq=freq, shape=shape)
        self.delay(5*us)
        self.pulse(channel, pi_len=pi_len,    phase=phase+1.6194*180, amp=amp, freq=freq, shape=shape)
        self.delay(5*us)
        self.pulse(channel, pi_len=pi_len,    phase=phase+0.54*180,   amp=amp, freq=freq, shape=shape)
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
            raise nfu.LabMasterError, shapes[i]+" is not a valid shape. Refer to dll_wfmGenLib2.py for valid shapes."
            
        # update instructions
        self.instructions.append([self.lab.time_cursor, str(channel), "pulse", (length, freq, phase, amp, shape)])
        self.lab.update_instructions_timing(length, rewind)       
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
                    raise nfu.LabMasterError, "awg channel "+str(channel)+" amplitude is not in the permitted range: "+nfu.auto_unit(min_amp, unit="V")+" to "+nfu.auto_unit(max_amp, unit="V")+"."
            elif channel_route=="DC":
                max_amp = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DC_AMPLITUDE_MAX)
                min_amp = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DC_AMPLITUDE_MIN)
                if min_amp <= amp <= max_amp:
                    self.set_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DC_AMPLITUDE, amp)
                else:
                    raise nfu.LabMasterError, "awg channel "+str(channel)+" amplitude is not in the permitted range: "+nfu.auto_unit(min_amp, unit="V")+" to "+nfu.auto_unit(max_amp, unit="V")+"."
            elif channel_route=="AC":
                max_amp = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_AC_AMPLITUDE_MAX)
                min_amp = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_AC_AMPLITUDE_MIN)
                if min_amp <= amp <= max_amp:
                    self.set_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_AC_AMPLITUDE, amp)
                else:
                    raise nfu.LabMasterError, "awg channel "+str(channel)+" amplitude is not in the permitted range: "+nfu.auto_unit(min_amp, unit="V")+" to "+nfu.auto_unit(max_amp, unit="V")+"."
            print "awg channel "+str(channel)+" amplitude set to "+nfu.auto_unit(amp, unit="V")+"."
        return


    def set_arm_mode(self, channel, query):
        if query=="armed":
            self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_ARM_MODE, self.AgM8190.VAL_ARM_MODE_ARMED) 
        elif query=="self":
            self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_ARM_MODE, self.AgM8190.VAL_ARM_MODE_SELF) 
        else:
            raise nfu.LabMasterError, str(query)+" is not a valid input." 
        print "awg channel "+str(channel)+" arm mode set to "+str(query)+"."
        return
        
    def set_channel_coupling(self, query):
        if query=="on":
            self.set_ViInt32_attribute("", self.AgM8190.ATTR_INSTRUMENT_CHANNEL_COUPLING_ENABLED, self.AgM8190.VAL_CHANNEL_COUPLING_STATE_ON)
        elif query=="off":
            self.set_ViInt32_attribute("", self.AgM8190.ATTR_INSTRUMENT_CHANNEL_COUPLING_ENABLED, self.AgM8190.VAL_CHANNEL_COUPLING_STATE_OFF)
        else:
            raise nfu.LabMasterError, str(query)+" is not a valid input."                 
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
                raise nfu.LabMasterError, str(query)+" is not a valid input." 
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
        if query=="gated":
            status = self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_GATE_MODE, self.AgM8190.VAL_GATE_MODE_GATED)
        elif query in "trig":
            status = self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_GATE_MODE, self.AgM8190.VAL_GATE_MODE_TRIGGERED)
        else:
            raise nfu.LabMasterError, str(query)+" is not a valid input."
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
                    raise nfu.LabMasterError, "awg channel "+str(channel)+" offset is not in the permitted range: "+nfu.auto_unit(min_offset, unit="V")+" to "+nfu.auto_unit(max_offset, unit="V")+"."
            elif channel_route=="DC":
                max_offset = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DC_OFFSET_MAX)
                min_offset = self.get_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DC_OFFSET_MIN)
                if min_offset <= offset <= max_offset:
                    self.set_ViReal64_attribute(channel, self.AgM8190.ATTR_ARBITRARY_DC_OFFSET, offset)
                else:
                    raise nfu.LabMasterError, "awg channel "+str(channel)+" offset is not in the permitted range: "+nfu.auto_unit(min_offset, unit="V")+" to "+nfu.auto_unit(max_offset, unit="V")+"."
            elif channel_route=="AC":
                if offset==0:
                    pass # print "awg channel "+str(channel)+" offset is always 0 V when using AC route."
                else:
                    raise nfu.LabMasterError, "awg channel "+str(channel)+" offset has to be 0 V when using AC route."
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
                raise nfu.LabMasterError, 'internal ref clock is not available currently. Try "AXI" instead'
                self.set_ViInt32_attribute("", self.AgM8190.ATTR_OUTPUT_REFERENCE_CLOCK_SOURCE, self.AgM8190.VAL_REFERENCE_CLOCK_SOURCE_INTERNAL)
            elif query == "external":
                self.set_ViInt32_attribute("", self.AgM8190.ATTR_OUTPUT_REFERENCE_CLOCK_SOURCE, self.AgM8190.VAL_REFERENCE_CLOCK_SOURCE_EXTERNAL)
            else:
                raise nfu.LabMasterError, str(query)+" is not a valid input."      
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
                raise nfu.LabMasterError, str(query)+" is not a valid input."     
            print "awg sample clock output route set to "+str(query)+"." 
        return    
        
    def set_sample_clock_rate(self, rate):
        current_rate = self.get_sample_clock_rate()
        if current_rate == rate:
            print "awg sample rate is "+nfu.auto_unit(rate, "Sa/s")+"."
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
                raise nfu.LabMasterError, str(query)+" is not a valid input."   
            print "awg channel "+str(channel)+" sample clock source route set to "+str(query)+"." 
            self.check_error(status)
        return  

    def set_trigger_mode(self, channel, query):
        if query=="auto":
            self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_MODE, self.AgM8190.VAL_TRIGGER_MODE_AUTO)
        elif query == "trig":
            self.set_ViInt32_attribute(channel, self.AgM8190.ATTR_TRIGGER_MODE, self.AgM8190.VAL_TRIGGER_MODE_TRIGGERED)
        else:
            raise nfu.LabMasterError, str(trigger_mode)+" is not a valid input."
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
        
    def string_sequence(self, channel, string, BB1=False):
        """ uses default delay, length, amplitude, freq and shape. not space/enter/tab sensitive"""
        clean_string = string.replace(" ", "").replace("\n", "").replace("\t", "")
        for token in clean_string.split(","):
            try:
                if ("t" in token) or ("tau" in token):
                    if "/" in token:
                        tau = self.default_delay[str(channel)]/float(token.split("/")[-1])
                    elif "*" in token:  
                        tau = self.default_delay[str(channel)]*float(token.split("*")[-1])
                    else:
                        tau = self.default_delay[str(channel)]
                    self.delay(tau)
                elif ("X" in token) or ("Y" in token):
                    # X or Y phase
                    if "X" in token:
                        phase=0
                    elif "Y" in token:
                        phase=90
                    # add 180 if minus sign is present
                    if "-" in token:
                        phase +=180
                    # BB1 option
                    if BB1:
                        if "/" not in token:
                            self.pulse_BB1_pi(str(channel), length=length, phase=phase) 
                        if "/2" in token:
                            self.pulse_BB1_piby2(str(channel), length=length, phase=phase)      
                        else:
                            raise nfu.LabMasterError, "BB1 option is valid for pi or pi/2 pulse lengths only."
                    else:
                        # pulse length divider/multiplier
                        if "/" in token:
                            length=self.default_length[str(channel)]/float(token.split("/")[-1])
                        if "*" in token:
                            length=self.default_length[str(channel)]*float(token.split("*")[-1])
                        else:
                            length=self.default_length[str(channel)]
                        self.pulse(str(channel), length=length, phase=phase)
                elif token=="":
                    pass
                else:
                    raise ValueError
            except ValueError:
                raise nfu.LabMasterError, "Token '"+str(token)+"' for "+self.__class__.__name__+"."+str(inspect.stack()[0][3])+" was not recognized. \n\n"+self.__class__.__name__+"."+str(inspect.stack()[0][3])+" docstring:\n"+Awg.string_sequence.__doc__+"\n"
        return
        
    

    def unzip_instructions(self, channel):
        instructions_pulse = [inst for inst in self.instructions if inst[1]==str(channel) and inst[2]=="pulse"] # select pulse instructions corresponding to input channel.
        instructions_marker = [inst for inst in self.instructions if inst[1]==str(channel) and inst[2]=="marker"] # select marker instructions corresponding to input channel.
        instructions_pulse.sort()# Sort instructions in time ascending order. sorted() takes first column as default.
        instructions_marker.sort()
        times = [inst[0] for inst in instructions_pulse]
        marker_times = [inst[0] for inst in instructions_marker]
        lengths, phases, amps, freqs, shapes = map(lambda x:[x]*len(instructions_pulse), [0]*5) # sorry I was having fun. This is equivalent to [0]*len(instructions_pulse), [0]*len(instructions_pulse), [0]*len(instructions_pulse), [0]*len(instructions_pulse), [0]*len(instructions_pulse)
        for i, inst in enumerate(instructions_pulse):
            lengths[i], freqs[i], phases[i], amps[i], shapes[i] = inst[3]
        return times, lengths, freqs, phases, amps, shapes, marker_times

class AgM8190Error(nfu.LabMasterError):
    pass       

        
