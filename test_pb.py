save_script(__file__)
 
try:
    import exp.test_pb as experiment
    params.add_parameter("tau1:s", "tau2:s")
   
    lab.pb.add_slave("1",1)

    params.tau1.value = np.linspace(5*ms,200*ms,3)
    params.tau1.sweep_ID = 1
    params.tau2.value = np.linspace(5*ms,200*ms,3)
    params.tau2.sweep_ID = 2
    
    scan(lab, params, experiment)
    

except:
    error_manager()
    
