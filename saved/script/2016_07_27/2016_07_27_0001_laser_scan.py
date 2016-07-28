notebook("ND; Red 0.3, Green 3.0", "sensitivity; 1e-7")
save_script()

try:
    import exp.exp_laser_scan as experiment
    params = Params("current:A", "wavelength:m")

    params.current.value = np.arange(.14,.16,.0001)
    
    fig_ref = plt.figure()
    # fig_ref = None
    
    lab.laser.set_current(params.current.value[0])
    time.sleep(100*ms)
    
    scan(lab, params, experiment, fig=fig_ref)
    
except:
    error_manager()
    
