import exp.exp_rabi as experiment
import exp._defaults_ as _defaults_

awg_amp = _defaults_.awg_amp
awg_freq = _defaults_.awg_freq
awg_sample_rate = 976*MHz
pi_len = _defaults_.pi_len
laser_curr = _defaults_.laser_current
rf_freq = _defaults_.sig_gen_freq

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
    
    lab.awg.set_default_params("1", amp=awg_amp, freq=awg_freq)
    lab.awg.set_sample_clock_rate(awg_sample_rate)
    lab.awg.set_trigger_mode("1", "trig")
    
    fit_pi_len = scan(lab, params, experiment, fig=fig_ref)

except:
    fit_pi_len = None
    error_manager()
    
finally:
    save_script()
    notebook("fitted pi_len;"+str(fit_pi_len),
             "awg frequency;"+str(awg_freq),
             "awg amplitude;"+str(awg_amp),
             "pi len start;"+str(params.pi_len.get_start()),
             "pi len end;"+str(params.pi_len.get_end()),
             "pi len step;"+str(params.pi_len.get_step()),
             "laser current;"+str(laser_curr),
             "rf freq;"+str(rf_freq),
             "ND filters;"+_defaults_.ND_filters, 
             "sensitivity;"+str(_defaults_.amp_sensitivity), 
             "bin length;"+str(params.bin_length.value),
             "error;"+error_manager(as_string=True),
             )





