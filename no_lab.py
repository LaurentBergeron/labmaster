notebook("current; 1.64A", "ND; Red Open, Green 3", "sensitivity; 1e-7")

save_script()

import timeit
time_1 = timeit.default_timer()

try:
    import exp.exp_no_lab as experiment
    params = Params("x", "y")

    params.x.value = np.linspace(0,6,6)
    params.x.sweep_ID = 1
    # params.y.value = np.linspace(0,3,3)
    # params.y.sweep_ID = 2
    
    scan(lab, params, experiment, quiet=True)
    

except:
    error_manager()
finally:
    time_2 = timeit.default_timer()
    print "time spent: %3.3f" % (time_2-time_1)
    
