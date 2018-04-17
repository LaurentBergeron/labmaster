import exp.exp_laser_scan as experiment
import exp._defaults_ as _defaults_

experiment.USE_WAVEMETER = False ## USE_WAVEMETER=True not tested on LabMaster v.2 release.
experiment.DETECTOR = 'LOCKIN' ## 'LOCKIN' or 'COUNTER'
experiment.USE_FIT = False

params = Params('current;A', 'delay;s')

params.delay.value = 500*ms
params.current.value = orange(0.0875,0.09,1e-6)


if experiment.USE_WAVEMETER:
    params.add_parameter('wavelength;m')

if experiment.USE_FIT:
    ## Min and max current for finding min
    params.add_parameter('curr_estimate_min;A', 'curr_estimate_max;A')
    params.curr_estimate_min.value = 0.0875
    params.curr_estimate_max.value = 0.09


fig_ref = plt.figure()
# fig_ref = None

try:
    scan(lab, params, experiment, fig=fig_ref)
except:
    error_manager()
finally:
    if experiment.USE_FIT:
        peak_min, at_curr = experiment.out(None, params, None, last_data(), None)
    else:
        peak_min = at_curr = 'not fitted'
    notebook('current start;'+str(params.current.get_start()),
             'current end;'+str(params.current.get_end()),
             'current step;'+str(params.current.get_step()),
             'temperature;'+str(lab.laser.get_temp()),
             'delay;'+str(params.delay.value),
             'ND filters 1047;'+_defaults_.ND_filters_1047, 
             'ND filters;'+_defaults_.ND_filters_ITC, 
             'magnetic field;'+str(_defaults_.mag_field),
             'current at min;'+str(at_curr),
             'peak minimum;'+str(peak_min)
             )
