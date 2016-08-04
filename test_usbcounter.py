save_script(__file__)

try:
    import exp.exp_test_usbcounter as experiment
    params.add_parameter("countA", "countB")
    
    lab.pb.add_slave("scope", 2)
    lab.pb.add_slave("scope_trig", 3)
    lab.pb.add_slave("send_count", 12)
    lab.pb.add_slave("binA", 10)
    lab.pb.add_slave("binB", 11)
    
    params.countA.value = np.linspace(10,20,3)
    params.countA.sweep_ID = 1
    params.countB.value = np.linspace(40,20,3)
    params.countB.sweep_ID = 1
    
    scan(lab, params, experiment)

except:
    error_manager()
    
