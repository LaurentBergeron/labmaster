import exp.exp_rabi as experiment
import exp._defaults_ as _defaults_



params = Params('bin_length;s', 'awg_amp;V', 'awg_freq;Hz', 'awg_sample_rate;Hz', 'pi_len;s')

params.awg_amp.value = _defaults_.awg_amp
params.awg_freq.value = _defaults_.awg_freq
params.awg_sample_rate.value = _defaults_.awg_sample_rate

params.bin_length.value = _defaults_.bin_len

params.pi_len.value = orange(0,ms, us)
    
fig_ref = plt.figure() 
# fig_ref = None

try:    
    scan(lab, params, experiment, fig=fig_ref)

except:
    error_manager()
    
finally:
    try:
        A, fit_pi_len = experiment.out(None, params, None, last_data(), None)
    except:
        print("Couldn't calculate fit parameters.")
        A, fit_pi_len = None, None
    notebook('fitted pi_len;'+str(fit_pi_len),
             'awg frequency;'+str(params.awg_freq.value),
             'awg amplitude;'+str(params.awg_amp.value),
             'pi len start;'+str(params.pi_len.get_start()),
             'pi len end;'+str(params.pi_len.get_end()),
             'pi len step;'+str(params.pi_len.get_step()),
             'laser current set;'+str(_defaults_.laser_current),
             'laser current read;'+str(lab.laser.get_current()),
             'rf freq;'+str(lab.sig_gen.get_freq()),
             'ND filters;'+_defaults_.ND_filters, 
             'sensitivity;'+str(_defaults_.amp_sensitivity), 
             'bin length;'+str(params.bin_length.value)
             )





