import exp.exp_test_awgpb as experiment

params = Params("dummy")
    
params.dummy.value = np.linspace(0,1,1000)


try:    
    lab.pb.add_slave("master_trig", 1)
    lab.pb.add_slave("Xshutter", 3)
    
    lab.awg.default_channel = "1"
    lab.awg.set_default_params(length=100*us, amp=1, freq=50*MHz)
    lab.awg.set_sample_rate(9*GHz)
    lab.awg.set_trigger_mode("trig")

    scan(lab, params, experiment, quiet=True)

except:
    error_manager()

    
