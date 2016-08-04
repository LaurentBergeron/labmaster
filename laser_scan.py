import exp.exp_laser_scan as experiment

experiment.USE_WAVEMETER = False

params = Params("current;A", "current_meas;A", "curr_estimate_min;A", "curr_estimate_max;A", "wavelength;m", "delay;s")

params.delay.value = 100*ms
params.current.value = orange(.14,.16,.0001)

### Min and max current for fitting
params.curr_estimate_min.value = 0.146
params.curr_estimate_max.value = 0.149

fig_ref = plt.figure()
# fig_ref = None

    
try:
    lab.laser.set_current(params.current.value[0])
    time.sleep(200*ms)
    
    params.current_meas.value = np.zeros(params.current.size())
    
    scan(lab, params, experiment, fig=fig_ref)
    current_at_min = experiment.out(fig, lab, params)
    
except:
    current_at_min = None
    error_manager()

finally:
    save_script()
    notebook("current start;"+str(params.current.get_start()),
             "current end;"+str(params.current.get_end()),
             "current step;"+str(params.current.get_step()),
             "delay;"+str(params.delay.value),
             "ND filters;"+_defaults_.ND_filters, 
             "sensitivity;"+str(_defaults_.amp_sensitivity), 
             "error;"+error_manager(as_string=True),
             )
