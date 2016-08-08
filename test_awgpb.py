import exp.exp_test_awgpb as experiment

params = Params("loops", "tau;s")
    
params.loops.sweep_ID = 1
# params.loops.value = 1
params.loops.value = orange(1, 3, 1)

params.tau.sweep_ID = 1
params.tau.value = 10*ms
# params.tau.value = orange(0, 20, 10*ms)

try:    
    lab.pb.add_slave("master_trig", 1)
    lab.pb.add_slave("Xshutter", 2)
    
    lab.awg.default_channel = "1"
    lab.awg.set_default_params(length=100*us, amp=1, freq=100*MHz)
    lab.awg.set_sample_rate(9*GHz)
    lab.awg.set_trigger_mode("trig")

    scan(lab, params, experiment, quiet=True)

except:
    error_manager()

    
