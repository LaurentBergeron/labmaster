notebook("ND; Red Open, Green 3", "sensitivity; 1e-7")
save_script()

try:
    import exp.exp_t1 as experiment
    from exp._sequences_ import *
    params = Params("loops", "tau:s", "phase_cycle", "phase_start", "time_axis", "bin_length:s")
    
    lab.pb.add_slave("master_trig", 1)
    lab.pb.add_slave("Xshutter", 2)
    lab.pb.add_slave("binA", 10)
    lab.pb.add_slave("binB", 11)
    lab.pb.add_slave("scope_trig", 17)
    
    lab.awg.set_sample_clock_rate(976*MHz)
    lab.awg.set_trigger_mode("1", "trig")
    
    lab.awg.set_default_params("1", length=31.5*us, amp=200*mV , freq=50*MHz - 3.76*kHz)
    
    params.bin_length.value = 150*ms
    params.phase_start.value = "X"
        
    params.tau.sweep_ID = 1
    # params.tau.value = 20*ms
    params.tau.value = np.arange(0, 180, 2)

    
    params.phase_cycle.sweep_ID = 2
    params.phase_cycle.value = ["","-"]
    # params.phase_cycle.value = ""
    
    params.time_axis.sweep_ID = 0
    params.time_axis.value = np.zeros(params.tau.size()*params.loops.size())
    
    fig_ref = plt.figure()
    # fig_ref = None
    
    experiment.DELAY_BEFORE = False
        
    scan(lab, params, experiment, fig=fig_ref, quiet=True)
    
except:
    error_manager()



    