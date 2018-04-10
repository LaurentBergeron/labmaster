import exp.exp_dds_ramsey as experiment
import exp._defaults_ as _defaults_
import exp._sequences_ as _sequences_

experiment.PHASE_CYCLING = False

params = Params('tau;s', 'phase_cycle', 'phase_start', 'time_axis;s', 'bin_length;s',
                'dds_amp', 'dds_freq;Hz', 'pi_len;s', 'sequence', 'loops')
                
params.phase_start.value = 'X'
params.bin_length.value = _defaults_.bin_len
params.dds_amp.value = 1.0
params.dds_freq.value = _defaults_.dds_freq
params.pi_len.value = _defaults_.pi_len


params.tau.value = orange(0, ms, 1*us)

laser_current_read = 0 #lab.laser.get_current()

fig_ref = plt.figure()
# fig_ref = None


try:    
    scan(lab, params, experiment, fig=fig_ref)

except:
    error_manager()
finally:
    
    try:
        A, period = experiment.out(None, params, None, last_data(), None)
    except:
        print("Couldn't calculate fit parameters.")
        A, period = None, None
    notebook('period;'+str(period),
             'dds freq;'+str(params.dds_freq.value),
             'dds amp;'+str(params.dds_amp.value),
             'pi len;'+str(params.pi_len.value),
             'tau start;'+str(params.tau.get_start()),
             'tau end;'+str(params.tau.get_end()),
             'tau step;'+str(params.tau.get_step()),
             'phase cycling;'+yes_or_no(experiment.PHASE_CYCLING),
             'laser current set;'+str(_defaults_.laser_current),
             'laser current read;'+str(laser_current_read),
             'ND filters;'+_defaults_.ND_filters, 
             'sensitivity;'+str(_defaults_.amp_sensitivity), 
             'bin length;'+str(params.bin_length.value),
             'phase start;'+params.phase_start.value
             )

    