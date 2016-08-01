import exp.exp_rf_scan as experiment


laser_curr = _defaults_.laser_current
awg_amp = _defaults_.awg_amp
awg_freq = _defaults_.awg_freq
awg_sample_rate = 976*MHz

params = Params("freq;Hz", "freq_estimate_min;Hz", "freq_estimate_max;Hz", "delay;s")

params.freq.value = orange(1.6093*GHz, 1.613*GHz, 10*kHz)
params.delay.value = 100*ms

### Min and max current for fitting
params.freq_estimate_min.value = 1.6103*GHz
params.freq_estimate_max.value = 1.6106*GHz


### comment both to plot next data on fig_ref figure
fig_ref = plt.figure() 
# fig_ref = None
    
try:
    ### cw function ##################################
    lab.reset_instructions()
    lab.awg.set_trigger_mode("1", "auto")
    lab.awg.adjust_trig_latency = False
    lab.awg.set_sample_clock_rate(awg_sample_rate)
    lab.awg.pulse("1", length=100*ms, freq=awg_freq, amp=awg_amp)
    lab.awg.load_memory()
    lab.awg.use_memory = False
    lab.awg.initiate_generation(1)
    ##################################################
    
    lab.sig_gen.set_freq(params.freq.value[0])
    time.sleep(200*ms) 
    
    freq_at_clock = scan(lab, params, experiment, fig=fig_ref)
    
except:
    freq_at_clock = None
    error_manager()
    
finally:
    save_script()
    notebook("Clock trans. freq;"+str(freq_at_clock),
             "awg frequency;"+str(awg_freq),
             "awg amplitude;"+str(awg_amp),
             "freq start;"+str(params.freq.get_start()),
             "freq end;"+str(params.freq.get_end()),
             "freq step;"+str(params.freq.get_step()),
             "delay;"+str(params.delay.value),
             "laser current;"+str(laser_curr),
             "ND filters;"+ND_filters,
             "sensitivity;"+str(amp_sensitivity), 
             "error;"+error_manager(as_string=True),
             )