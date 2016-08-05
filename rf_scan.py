import exp.exp_rf_scan as experiment

### Definition of parameters #################################
pulseLength = 100*ms                    #pulse
awg_sample_rate = 976*MHz               #This needs to be adjusted
                                        #based on granularity and
                                        #frequency of sample
awg_amp   = _defaults_.awg_amp          #pulse
awg_freq  = _defaults_.awg_freq         #pulse
awg_phase = _defaults_.awg_phase        #pulse
laser_curr = _defaults_.laser_current   #sets current sent to laser
channel_number = "1"                    #determines which channel to use
##############################################################

params = Params("freq;Hz", "amp;mV", "phase;rad", "freq_estimate_min;Hz", "freq_estimate_max;Hz", "delay;s")
params.freq.value = orange(1.6093*GHz, 1.613*GHz, 10*kHz)
params.delay.value = 100*ms

### Min and max current for fitting
params.freq_estimate_min.value = 1.6103*GHz
params.freq_estimate_max.value = 1.6106*GHz


### comment both to plot next data on fig_ref figure
fig_ref = plt.figure()
# fig_ref = None


### cw function ##############################################
lab.awg.set_default_params(channel_number, length=pulseLength,freq=awg_freq, phase=awg_phase, amp=awg_amp)
lab.awg.cw(channel_number, awg_freq, awg_amp, awg_phase, pulseLength)
##################################################

lab.sig_gen.set_freq(params.freq.value[0])
time.sleep(200*ms)

freq_at_clock = scan(lab, params, experiment, fig=fig_ref)
lab.awg.iscontinuous=False

notebook("Clock trans. freq;"+str(freq_at_clock),
         "awg frequency;"+str(awg_freq),
         "awg amplitude;"+str(awg_amp),
         "freq start;"+str(params.freq.get_start()),
         "freq end;"+str(params.freq.get_end()),
         "freq step;"+str(params.freq.get_step()),
         "delay;"+str(params.delay.value),
         "laser current set;"+str(_defaults_.laser_current),
         "laser current read;"+str(lab.laser.get_current()),
         "ND filters;"+ND_filters,
         "sensitivity;"+str(amp_sensitivity),
         "error;"+error_manager(as_string=True),
         )
