import exp.exp_rabi as experiment
import exp._defaults_ as _defaults_

awg_amp = _defaults_.awg_amp
awg_freq = _defaults_.awg_freq
awg_sample_rate = 976*MHz
pi_len = _defaults_.pi_len
laser_curr = _defaults_.laser_current
rf_freq = _defaults_.sig_gen_freq
lab.awg.default_channel = "1"

params = Params("pi_len;s", "bin_length;s")

params.bin_length.value = _defaults_.bin_len

params.pi_len.sweep_ID = 1
params.pi_len.value = orange(0,ms, us)
    
fig_ref = plt.figure() 
# fig_ref = None

try:
    lab.pb.add_slave("master_trig", 1)
    lab.pb.add_slave("Xshutter", 2)
    lab.pb.add_slave("binA", 10)
    lab.pb.add_slave("binB", 11)
    lab.pb.add_slave("scope_trig", 17)
    
    lab.awg.set_default_params(amp=awg_amp, freq=awg_freq)
    lab.awg.set_sample_clock_rate(awg_sample_rate)
    lab.awg.set_trigger_mode("trig")
    
    scan(lab, params, experiment, fig=fig_ref)
    fit_pi_len = experiment.out(lab, params, fig, data, None)

except:
    fit_pi_len = None
    error_manager()
    
finally:
    notebook("fitted pi_len;"+str(fit_pi_len),
             "awg frequency;"+str(awg_freq),
             "awg amplitude;"+str(awg_amp),
             "pi len start;"+str(params.pi_len.get_start()),
             "pi len end;"+str(params.pi_len.get_end()),
             "pi len step;"+str(params.pi_len.get_step()),
             "laser current set;"+str(_defaults_.laser_current),
             "laser current read;"+str(lab.laser.get_current()),
             "rf freq;"+str(lab.sig_gen.get_freq()),
             "ND filters;"+_defaults_.ND_filters, 
             "sensitivity;"+str(_defaults_.amp_sensitivity), 
             "bin length;"+str(params.bin_length.value),
             "error;"+error_manager(as_string=True),
             )





