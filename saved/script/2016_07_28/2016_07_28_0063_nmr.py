import exp.exp_nmr as experiment
import exp._defaults_ as _defaults_
import exp._sequences_ as _sequences_

save_script()

experiment.LOADED_SEQUENCE = _sequences_.HAHN
PHASE_CYCLING = True
awg_amp = _defaults_.awg_amp
awg_freq = _defaults_.awg_freq
awg_sample_rate = 976*MHz
pi_len = _defaults_.pi_len

params = Params("loops", "tau:s", "phase_cycle", "phase_start", "time_axis:s", "bin_length:s")
params.phase_start.value = "X"
params.bin_length.value = _defaults_.bin_len
    
params.loops.sweep_ID = 1
# params.loops.value = 1
params.loops.value = np.arange(1, 3, 1)

params.tau.sweep_ID = 1
params.tau.value = 10*ms
# params.tau.value = np.arange(0, 20, 10*ms)

fig_ref = plt.figure()
# fig_ref = None
    

try:
    
    lab.pb.add_slave("master_trig", 1)
    lab.pb.add_slave("Xshutter", 2)
    lab.pb.add_slave("binA", 10)
    lab.pb.add_slave("binB", 11)
    lab.pb.add_slave("scope_trig", 17)

    lab.awg.set_default_params("1", length=pi_len, amp=_defaults_.awg_amp, freq=_defaults_.awg_freq)
    lab.awg.set_sample_clock_rate(976*MHz)
    lab.awg.set_trigger_mode("1", "trig")

    if PHASE_CYCLING:
        params.phase_cycle.sweep_ID = 2
        params.phase_cycle.value = ["","-"]
    else:
        params.phase_cycle.value = ""

    params.time_axis.sweep_ID = 0
    params.time_axis.value = np.zeros(params.tau.size()*params.loops.size())

    A, T2 = scan(lab, params, experiment, fig=fig_ref, quiet=True)

except:
    A, T2 = None, None
    error_manager()

    notebook("loaded sequence;"+str([key for key, value in _sequences_.__dict__.items() if value==experiment.LOADED_SEQUENCE][0]),
             "T2;"+str(T2),
             "A;"+str(A),
             "awg frequency;"+str(awg_freq),
             "awg amplitude;"+str(awg_amp),
             "pi len;"+str(pi_len),
             "tau start;"+str(params.tau.get_start()),
             "tau end;"+str(params.tau.get_end()),
             "tau step;"+str(params.tau.get_step()),
             "loops start;"+str(params.loops.get_start()),
             "loops end;"+str(params.loops.get_end()),
             "loops step;"+str(params.loops.get_step()),
             "phase cycling;"+("Yes"*PHASE_CYCLING+"No"*PHASE_CYCLING),
             "ND filters;"+_defaults_.ND_filters, 
             "sensitivity;"+str(_defaults_.amp_sensitivity), 
             "bin length;"+str(params.bin_length.value),
             "phase_start;"+params.phase_start.value,
             "error;"+error_manager(as_string=True),
             )

    