import exp.exp_rf_scan as experiment

### Definition of parameters #################################
awg_amp   = _defaults_.awg_amp          #pulse
awg_freq  = _defaults_.awg_freq         #pulse
lab.awg.default_channel = "1"                    #determines which channel to use

params = Params("freq;Hz", "amp;mV", "phase;rad", "freq_estimate_min;Hz", "freq_estimate_max;Hz", "delay;s")
params.freq.value = orange(1.6093*GHz, 1.613*GHz, 10*kHz)
params.delay.value = 100*ms

### Min and max current for fitting
params.freq_estimate_min.value = 1.6103*GHz
params.freq_estimate_max.value = 1.6106*GHz


### comment both to plot next data on fig_ref figure
fig_ref = plt.figure()
# fig_ref = None

##############################################################


try:
    lab.awg.cw(awg_freq, awg_amp)
    
    lab.sig_gen.set_freq(params.freq.value[0])
    time.sleep(200*ms) 
    
    scan(lab, params, experiment, fig=fig_ref)
    
except:
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
             "laser current set;"+str(_defaults_.laser_current),
             "laser current read;"+str(lab.laser.get_current()),
             "ND filters;"+ND_filters,
             "sensitivity;"+str(amp_sensitivity), 
             "error;"+error_manager(as_string=True),
             )
