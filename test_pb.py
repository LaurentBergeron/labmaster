save_script()
 
try:
    import exp.exp_test_pb as experiment
    params = Params("tau1;s", "tau2;s")
   
    lab.pb.add_slave("slave",17)

    params.tau1.value = np.linspace(50*ms,200*ms,5)
    params.tau1.sweep_ID = 1
    params.tau2.value = np.linspace(50*ms,200*ms,5)
    params.tau2.sweep_ID = 2
    
    # fig_ref = plt.figure()
    fig_ref = None
    
    scan(lab, params, experiment, fig=fig_ref, quiet=True)
    

except:
    error_manager()
    
