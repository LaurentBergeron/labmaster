import exp.exp_dds_nmr as experiment
import exp._defaults_ as _defaults_
import exp._sequences_ as _sequences_


experiment.PHASE_CYCLING = True

params = Params('loops', 'tau;s', 'phase_cycle', 'phase_start', 'time_axis;s', 'bin_length;s',
                'dds_amp;V', 'dds_freq;Hz', 'pi_len;s', 'sequence_name', 'sequence')

params.sequence_name.value = 'HAHN'
params.sequence.value = _sequences_.__dict__[params.sequence_name.value] ## From the _sequences_ module using sequence_name 
params.phase_start.value = 'X'
params.bin_length.value = _defaults_.bin_len
params.pi_len.value = _defaults_.pi_len
params.dds_amp.value = 1.0
params.dds_freq.value = _defaults_.dds_freq
    
params.loops.sweep_dim=2
# params.loops.value = 1
params.loops.value = orange(1, 10, 1)

# params.tau.value = 10*ms
params.tau.value = orange(0, 20, 10*ms)

fig_ref = plt.figure()
# fig_ref = None
    

try:    
    scan(lab, params, experiment, fig=fig_ref, quiet=True)
except:
    error_manager()
finally:
    try:
        A, T2 = experiment.out(None, params, None, last_data(), None)
    except:
        print("Couldn't calculate fit parameters.")
        A, T2 = None, None
    notebook('sequence;'+params.sequence_name.value,
             'T2;'+str(T2),
             'A;'+str(A),
             'dds freq;'+str(params.dds_freq.value),
             'dds amp;'+str(params.dds_amp.value),
             'pi len;'+str(params.pi_len.value),
             'tau start;'+str(params.tau.get_start()),
             'tau end;'+str(params.tau.get_end()),
             'tau step;'+str(params.tau.get_step()),
             'loops start;'+str(params.loops.get_start()),
             'loops end;'+str(params.loops.get_end()),
             'loops step;'+str(params.loops.get_step()),
             'phase cycling;'+('Yes'*experiment.PHASE_CYCLING+'No'*(not experiment.PHASE_CYCLING)),
             'laser current set;'+str(_defaults_.laser_current),
             # 'laser current read;'+str(lab.laser.get_current()),
             'rf freq;'+str(lab.sig_gen_srs.get_freq()),
             'ND filters;'+_defaults_.ND_filters, 
             'sensitivity;'+str(_defaults_.amp_sensitivity), 
             'bin length;'+str(params.bin_length.value),
             'phase start;'+params.phase_start.value
             )

    
