import exp.exp_laser_scan as experiment
import exp._defaults_ as _defaults_

experiment.USE_WAVEMETER = False ## USE_WAVEMETER=True not tested on LabMaster v.2 release.

params = Params('current;A', 'current_meas;A', 'curr_estimate_min;A', 'curr_estimate_max;A', 'wavelength;m', 'delay;s')

params.delay.value = 100*ms
params.current.value = orange(.14,.16,.0001)

## Min and max current for finding min.
params.curr_estimate_min.value = 0.146
params.curr_estimate_max.value = 0.149

fig_ref = plt.figure()
# fig_ref = None

try:
    scan(lab, params, experiment, fig=fig_ref)
except:
    error_manager()
finally:
    try:
        peak_min, at_curr = experiment.out(None, params, None, last_data(), None)
    except:
        print("Couldn't calculate current at peak minimum.")
        peak_min, at_curr = None, None
    notebook('current at min;'+str(at_curr),
             'current start;'+str(params.current.get_start()),
             'current end;'+str(params.current.get_end()),
             'current step;'+str(params.current.get_step()),
             'delay;'+str(params.delay.value),
             'ND filters;'+_defaults_.ND_filters, 
             'sensitivity;'+str(_defaults_.amp_sensitivity)
             )
