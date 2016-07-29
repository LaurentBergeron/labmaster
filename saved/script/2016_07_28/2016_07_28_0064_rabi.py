import exp.exp_rabi as experiment
import exp._defaults_ as _defaults_

save_script()

awg_amp = _defaults_.awg_amp
awg_freq = _defaults_.awg_freq
bin_len = _defaults_.bin_len
awg_sample_rate = 976*MHz
amp_sensitivity = 1e-7
ND_filters = "Red Open, Green 3"

try:
    lab.pb.add_slave("master_trig", 1)
    lab.pb.add_slave("Xshutter", 2)
    lab.pb.add_slave("binA", 10)
    lab.pb.add_slave("binB", 11)
    lab.pb.add_slave("scope_trig", 17)
    
    lab.awg.set_default_params("1", amp=awg_amp, freq=awg_freq)
    lab.awg.set_sample_clock_rate(awg_sample_rate)
    lab.awg.set_trigger_mode("1", "trig")
    
    params = Params("pi_len:s", "bin_length:s")
    
    params.bin_length.value = bin_len

    params.pi_len.sweep_ID = 1
    params.pi_len.value = np.arange(0,ms, us)
    
    fig_ref = plt.figure() 
    # fig_ref = None
    
    fit_pi_len = scan(lab, params, experiment, fig=fig_ref)

except:
    error_manager()
    fit_pi_len = None
    
finally:
    notebook("fitted pi_len;"+str(fit_pi_len),
             "awg frequency;"+str(awg_freq),
             "awg amplitude;"+str(awg_amp),
             "pi len start;"+str(params.pi_len.get_start()),
             "pi len end;"+str(params.pi_len.get_end()),
             "pi len step;"+str(params.pi_len.get_step()),
             "ND filters;"+ND_filters, 
             "sensitivity;"+str(amp_sensitivity), 
             "bin length;"+str(bin_len),
             "error;"+error_manager(as_string=True),
             )





