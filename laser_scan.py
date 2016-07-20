notebook("ND; Red 0.3, Green 3.0", "sensitivity; 1e-7")
save_script()

try:
    import exp.exp_laser_scan as experiment
    params = Params("current:A", "wavelength:m")

    params.current.value = np.arange(.14,.16,.0001)
    
    scan(lab, params, experiment, show_plot = True)
    
except:
    error_manager()
    
