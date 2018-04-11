import exp.exp_laser_scan as experiment
import exp._defaults_ as _defaults_

experiment.USE_WAVEMETER = False ## USE_WAVEMETER=True not tested on LabMaster v.2 release.
experiment.DETECTOR = 'LOCKIN' ## 'LOCKIN' or 'COUNTER'
experiment.USE_FIT = False

params = Params('temp_meas;C', 'current;A', 'current_meas;A', 'curr_estimate_min;A', 'curr_estimate_max;A', 'wavelength;m', 'delay;s')

params.delay.value = 500*ms
params.current.value = np.linspace(0.0875,0.09,11)

## Min and max current for finding min. (when USE_FIT is True)
params.curr_estimate_min.value = 0.0875
params.curr_estimate_max.value = 0.09


fig_ref = plt.figure()
# fig_ref = None

try:
    scan(lab, params, experiment, fig=fig_ref)
except:
    error_manager()
finally:
    peak_min, at_curr = None, None
    if experiment.USE_FIT:
        try:
            peak_min, at_curr = experiment.out(None, params, None, last_data(), None)
        except:
            print("Couldn't calculate current at peak minimum.")
    notebook('current at min;'+str(at_curr),
             'current start;'+str(params.current.get_start()),
             'current end;'+str(params.current.get_end()),
             'current step;'+str(params.current.get_step()),
             'average temp;'+str(np.mean(params.temp_meas.value)),
             'delay;'+str(params.delay.value),
             'ND filters 1047;'+_defaults_.ND_filters_1047, 
             'ND filters;'+_defaults_.ND_filters, 
             'sensitivity;'+str(_defaults_.amp_sensitivity),
             'magnetic field;'+str(_defaults_.mag_field)
             )
