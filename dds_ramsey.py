import exp.exp_dds_ramsey as experiment
import exp._defaults_ as _defaults_
import exp._sequences_ as _sequences_

experiment.PHASE_CYCLING = True

params = Params('tau;s', 'phase_cycle', 'phase_start', 'time_axis;s', 'bin_length;s',
                'dds_amp;V', 'dds_freq;Hz', 'pi_len;s', 'sequence', 'loops')
                
params.phase_start.value = 'X'
params.bin_length.value = _defaults_.bin_len
params.dds_amp.value = _defaults_.dds_amp
params.dds_freq.value = _defaults_.dds_freq
params.pi_len.value = _defaults_.pi_len


params.tau.value = orange(0, 20, 10*ms)

fig_ref = plt.figure()
# fig_ref = None
    

try:    
    scan(lab, params, experiment, fig=fig_ref, quiet=True)

except:
    error_manager()
finally:
    
    try:
        A, period = experiment.out(None, params, None, last_data(), None)
    except:
        raise #TODO
        print("Couldn't calculate fit parameters.")
        A, period = None, None
    notebook('period;'+str(period),
             'dds freq;'+str(params.dds_freq.value),
             'dds amp;'+str(params.dds_amp.value),
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
             'bin length;'+str(params.bin_length.value),
             'phase start;'+params.phase_start.value
             )

    