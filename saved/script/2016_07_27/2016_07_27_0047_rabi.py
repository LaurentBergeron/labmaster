notebook("ND; Red Open, Green 3", "sensitivity; 1e-7")
save_script()

try:
    import exp.exp_rabi as experiment
    lab.awg.set_trigger_mode("1", "trig")
    params = Params("pi_len:s", "bin_length:s")
        
    lab.pb.add_slave("master_trig", 1)
    lab.pb.add_slave("Xshutter", 2)
    lab.pb.add_slave("binA", 10)
    lab.pb.add_slave("binB", 11)
    lab.pb.add_slave("scope_trig", 17)
    lab.awg.set_default_params(1, amp=200*mV, freq=50*MHz)
    
    lab.awg.set_sample_clock_rate(276*MHz)
    lab.awg.set_trigger_mode("1", "trig")
    
    params.bin_length.value = 100*ms
    params.pi_len.value = np.arange(0,ms, us)*0
    params.pi_len.sweep_ID = 1
    
    fig_ref = plt.figure() 
    # fig_ref = None
    
    scan(lab, params, experiment, fig=fig_ref)

except:
    error_manager()





