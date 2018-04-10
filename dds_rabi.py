import exp.exp_dds_rabi as experiment
import exp._defaults_ as _defaults_



params = Params('bin_length;s', 'dds_amp', 'dds_freq;Hz', 'pi_len;s')

params.dds_amp.value =1.0
params.dds_freq.value = _defaults_.dds_freq

params.bin_length.value = _defaults_.bin_len

params.pi_len.value = orange(0,ms, us)
    
fig_ref = plt.figure() 
# fig_ref = None

laser_current_read = 0#lab.laser.get_current()

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
             'dds frequency;'+str(params.dds_freq.value),
             'dds amplitude;'+str(params.dds_amp.value),
             'pi len start;'+str(params.pi_len.get_start()),
             'pi len end;'+str(params.pi_len.get_end()),
             'pi len step;'+str(params.pi_len.get_step()),
             'laser current set;'+str(_defaults_.laser_current),
             'laser current read;'+str(laser_current_read),
             'ND filters;'+_defaults_.ND_filters, 
             'sensitivity;'+str(_defaults_.amp_sensitivity), 
             'bin length;'+str(params.bin_length.value)
             )





