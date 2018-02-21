import exp.exp_dds_t1 as experiment
import exp._defaults_ as _defaults_


experiment.PHASE_CYCLING = True
experiment.DELAY_BEFORE_PULSE = False

params = Params('tau;s', 'phase_cycle', 'time_axis;s', 'bin_length;s',
                'dds_amp;V', 'dds_freq;Hz', 'pi_len;s')

params.dds_amp.value = 1.0
params.dds_freq.value = _defaults_.dds_freq
params.pi_len.value = _defaults_.pi_len
params.bin_length.value = _defaults_.bin_len
        
params.tau.value = orange(0, 1, ms)
fig_ref = plt.figure()
# fig_ref = None

laser_current_read = 0# lab.laser.get_current()

try:    
    scan(lab, params, experiment, fig=fig_ref)
    
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
             'dds freq;'+str(params.dds_freq.value),
             'dds amp;'+str(params.dds_amp.value),
             'pi len;'+str(params.pi_len.value),
             'tau start;'+str(params.tau.get_start()),
             'tau end;'+str(params.tau.get_end()),
             'tau step;'+str(params.tau.get_step()),
             'phase cycling;'+yes_or_no(experiment.PHASE_CYCLING),
             'delay before pulse;'+yes_or_no(experiment.DELAY_BEFORE_PULSE),
             'laser current set;'+str(_defaults_.laser_current),
             'laser current read;'+str(laser_current_read),
             'ND filters;'+_defaults_.ND_filters, 
             'sensitivity;'+str(_defaults_.amp_sensitivity), 
             'bin length;'+str(params.bin_length.value)
             )


    