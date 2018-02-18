import exp.exp_awg_t1 as experiment
import exp._defaults_ as _defaults_


experiment.PHASE_CYCLING = True
experiment.DELAY_BEFORE_PULSE = False

params = Params('tau;s', 'phase_cycle', 'phase_start', 'time_axis;s', 'bin_length;s',
                'awg_amp;V', 'awg_freq;Hz', 'awg_sample_rate;Hz', 'pi_len;s')

params.awg_amp.value = _defaults_.awg_amp
params.awg_freq.value = _defaults_.awg_freq
params.awg_sample_rate.value = _defaults_.awg_sample_rate
params.pi_len.value = _defaults_.pi_len
params.phase_start.value = 'X'
params.bin_length.value = _defaults_.bin_len
        
params.tau.value = orange(0, 1, ms)

fig_ref = plt.figure()
# fig_ref = None


try:    
    scan(lab, params, experiment, fig=fig_ref, quiet=True)
    
except:
    error_manager()

finally:
    try:
        A, T1 = experiment.out(None, params, None, last_data(), None)
    except:
        print("Couldn't calculate fit parameters.")
        A, T1 = None, None
        
    notebook('T1;'+str(T1),
             'A;'+str(A),
             'awg freq;'+str(params.awg_freq.value),
             'awg amp;'+str(params.awg_amp.value),
             'pi len;'+str(params.pi_len.value),
             'tau start;'+str(params.tau.get_start()),
             'tau end;'+str(params.tau.get_end()),
             'tau step;'+str(params.tau.get_step()),
             'phase cycling;'+('Yes'*experiment.PHASE_CYCLING+'No'*(not experiment.PHASE_CYCLING)),
             'laser current set;'+str(_defaults_.laser_current),
             'laser current read;'+str(lab.laser.get_current()),
             'rf freq;'+str(lab.sig_gen.get_freq()),
             'ND filters;'+_defaults_.ND_filters, 
             'sensitivity;'+str(_defaults_.amp_sensitivity), 
             'bin length;'+str(params.bin_length.value)
             )


    