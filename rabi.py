notebook("ND; Red Open, Green 3", "sensitivity; 1e-7")
save_script()

try:
    import exp.exp_rabi as experiment
    params = Params("pi_len:s", "bin_length:s")
        
    lab.pb.add_slave("master_trig", 1)
    lab.pb.add_slave("Xshutter", 2)
    lab.pb.add_slave("binA", 10)
    lab.pb.add_slave("binB", 11)
    lab.pb.add_slave("scope_trig", 17)
    lab.awg.set_default_params(1, amp=1, freq=50*MHz+566)
    
    params.bin_length.value = 100*ms
    params.pi_len.value = np.arange(0,ms, us)
    params.pi_len.sweep_ID = 1
    
    scan(lab, params, experiment)

except:
    error_manager()





