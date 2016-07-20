%run launch.ipy


lab = init_lab("awg", "pulse_blaster", "lockin", "scope")
params = init_params("time", "dummy","loops", "tau", "pulse_length", "pulse_phase", "pulse_shape", "pulse_freq", "pulse_amplitude")

try:
    import Hahn
    exec(shortcuts())

    save_to_pickle("example",params)
    
    
    print "--- 2D sweep of tau and loops --- "
    load_from_pickle("example", params, I_swear_to_exec_shortcuts=True) 
    exec(shortcuts())
    tau.v = np.linspace(1*m, 3*m, 3)
    loops.v = range(1, 3)
    loops.sweep_ID = 2
    
    scan_experiment(lab, params, Hahn)
    
    
    print "\n\n --- time sweep --- "
    load_from_pickle("example", params, I_swear_to_exec_shortcuts=True) 
    exec(shortcuts())
    time.v = np.linspace(0,.2,3)
    scan_experiment(lab, params, Hahn)
    
    print "\n\n --- constants (single run) --- """
    load_from_pickle("example", params, I_swear_to_exec_shortcuts=True) 
    exec(shortcuts())
    scan_experiment(lab, params, Hahn)
    
    
        
    for key in params.copy().keys():
        print "\n\n --- will give (not a Parameter) error --- """
        load_from_pickle("example", params, I_swear_to_exec_shortcuts=True) 
        exec(shortcuts())
        params[key]=0
        scan_experiment(lab, params, Hahn)
        raw_input("[Enter]")
    
        
    for key in params.copy().keys():
        print "\n\n --- will give wrong sweep_ID error --- """
        load_from_pickle("example", params, I_swear_to_exec_shortcuts=True) 
        exec(shortcuts())
        params[key].sweep_ID="yo_bitch"
        scan_experiment(lab, params, Hahn)
        raw_input("[Enter]")
    
    
    for key in params.keys():
        print "\n\n --- will give negative sweep_ID error --- """
        load_from_pickle("example", params, I_swear_to_exec_shortcuts=True) 
        params[key].v=range(2)
        params[key].sweep_ID=0
        scan_experiment(lab, params, Hahn)
        raw_input("[Enter]")
    
    
    for key in [x for x in params.keys() if not x == "time"]:
        print "\n\n --- will give array size error --- """
        load_from_pickle("example", params, I_swear_to_exec_shortcuts=True) 
        exec(shortcuts())
        time.v = np.linspace(1*m, 3*m, 3)
        params[key].v = np.linspace(1*m, 3*m, 10)
        params[key].sweep_ID = 1
        scan_experiment(lab, params, Hahn)
        raw_input("[Enter]")
    
    for key in params.keys():
        print "\n\n --- will give empty sweep error --- "
        load_from_pickle("example", params, I_swear_to_exec_shortcuts=True) 
        exec(shortcuts())
        params[key].v = np.linspace(1,3,3)
        params[key].sweep_ID=2
        scan_experiment(lab, params, Hahn)
        raw_input("[Enter]")
    
    
    for key in params.keys():
        print "\n\n --- will give zero length array error --- "
        load_from_pickle("example", params, I_swear_to_exec_shortcuts=True) 
        exec(shortcuts())
        params[key].v = np.array([])
        params[key].sweep_ID=2
        scan_experiment(lab, params, Hahn)
        raw_input("[Enter]")

finally:
    close_lab(lab)

