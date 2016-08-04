import exp.exp_ramsey as experiment
import exp._defaults_ as _defaults_
import exp._sequences_ as _sequences_

PHASE_CYCLING = False
awg_amp = _defaults_.awg_amp
awg_freq = _defaults_.awg_freq
awg_sample_rate = 976*MHz
pi_len = _defaults_.pi_len
laser_curr = _defaults_.laser_current
rf_freq = _defaults_.sig_gen_freq

params = Params("loops", "tau;s", "phase_cycle", "phase_start", "time_axis;s", "bin_length:s")
params.phase_start.value = "X"
params.bin_length.value = _defaults_.bin_len

params.tau.sweep_ID = 1
# params.tau.value = 10*ms
params.tau.value = orange(0, 20, 10*ms)

fig_ref = plt.figure()
# fig_ref = None
    

try:    
    lab.pb.add_slave("master_trig", 1)
    lab.pb.add_slave("Xshutter", 2)
    lab.pb.add_slave("binA", 10)
    lab.pb.add_slave("binB", 11)
    lab.pb.add_slave("scope_trig", 17)

    lab.awg.set_default_params("1", length=pi_len, amp=awg_amp, freq=awg_freq)
    lab.awg.set_sample_clock_rate(awg_sample_rate)
    lab.awg.set_trigger_mode("1", "trig")

    if PHASE_CYCLING:
        params.phase_cycle.sweep_ID = params.get_dimension() + 1
        params.phase_cycle.value = ["","-"]
    else:
        params.phase_cycle.value = ""

    params.loops.value = 1
    
    params.time_axis.sweep_ID = 0
    params.time_axis.value = np.zeros(params.tau.size())

    
    scan(lab, params, experiment, fig=fig_ref, quiet=True)
    period = experiment.out(fig, lab, params)

except:
    period = None
    error_manager()
finally:
    save_script()
    notebook("period;"+str(period),
             "awg freq;"+str(awg_freq),
             "awg ampl;"+str(awg_amp),
             "pi len;"+str(pi_len),
             "tau start;"+str(params.tau.get_start()),
             "tau end;"+str(params.tau.get_end()),
             "tau step;"+str(params.tau.get_step()),
             "phase cycling;"+("Yes"*PHASE_CYCLING+"No"*(not PHASE_CYCLING)),
             "laser current set;"+str(_defaults_.laser_current),
             "laser current read;"+str(lab.laser.get_current()),
             "rf freq;"+str(lab.sig_gen.get_freq()),
             "ND filters;"+_defaults_.ND_filters, 
             "sensitivity;"+str(_defaults_.amp_sensitivity), 
             "bin length;"+str(params.bin_length.value),
             "phase start;"+params.phase_start.value,
             "error;"+error_manager(as_string=True),
             )

    