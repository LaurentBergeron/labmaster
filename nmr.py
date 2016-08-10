import exp.exp_nmr as experiment
import exp._defaults_ as _defaults_
import exp._sequences_ as _sequences_


experiment.LOADED_SEQUENCE = _sequences_.HAHN
experiment.PHASE_CYCLING = True
lab.awg.default_channel = "1"

params = Params("loops", "tau;s", "phase_cycle", "phase_start", "time_axis;s", "bin_length;s",
                "awg_amp;V", "awg_freq;Hz", "awg_sample_rate;Hz", "pi_len;s")
                
params.phase_start.value = "X"
params.bin_length.value = _defaults_.bin_len
params.pi_len.value = _defaults_.pi_len
params.awg_amp.value = _defaults_.awg_amp
params.awg_freq.value = _defaults_.awg_freq
params.awg_sample_rate.value = 976*MHz
    
params.loops.sweep_ID = 1
# params.loops.value = 1
params.loops.value = orange(1, 3, 1)

params.tau.sweep_ID = 1
params.tau.value = 10*ms
# params.tau.value = orange(0, 20, 10*ms)

fig_ref = plt.figure()
# fig_ref = None
    

try:    
    scan(lab, params, experiment, fig=fig_ref, quiet=True)
    A, T2 = experiment.out(lab, params, fig, data, None)
except:
    A, T2 = None, None
    error_manager()
finally:
    notebook("sequence;"+str([key for key, value in _sequences_.__dict__.items() if value==experiment.LOADED_SEQUENCE][0]),
             "T2;"+str(T2),
             "A;"+str(A),
             "awg freq;"+str(awg_freq),
             "awg amp;"+str(awg_amp),
             "pi len;"+str(pi_len),
             "tau start;"+str(params.tau.get_start()),
             "tau end;"+str(params.tau.get_end()),
             "tau step;"+str(params.tau.get_step()),
             "loops start;"+str(params.loops.get_start()),
             "loops end;"+str(params.loops.get_end()),
             "loops step;"+str(params.loops.get_step()),
             "phase cycling;"+("Yes"*experiment.PHASE_CYCLING+"No"*(not experiment.PHASE_CYCLING)),
             "laser current set;"+str(_defaults_.laser_current),
             "laser current read;"+str(lab.laser.get_current()),
             "rf freq;"+str(lab.sig_gen.get_freq()),
             "ND filters;"+_defaults_.ND_filters, 
             "sensitivity;"+str(_defaults_.amp_sensitivity), 
             "bin length;"+str(params.bin_length.value),
             "phase start;"+params.phase_start.value,
             "error;"+error_manager(as_string=True),
             )

    
