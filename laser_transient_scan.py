import exp.exp_laser_transient_scan as experiment
import exp._defaults_ as _defaults_

experiment.DETECTOR = 'LOCKIN' ## 'LOCKIN' or 'COUNTER'

params = Params('current_japan;A', 'current_eblana;A', 'delay;s')

params.delay.value = 500*ms
params.current_japan.value = orange(87.5*mA, 90*mA, uA)
params.current_eblana.value = 90*mA




fig_ref = plt.figure()
# fig_ref = None

try:
    scan(lab, params, experiment, fig=fig_ref)
except:
    error_manager()
finally:
    notebook('current start japan;'+str(params.current_japan.get_start()),
             'current end japan;'+str(params.current_japan.get_end()),
             'current step japan;'+str(params.current_japan.get_step()),
             'current eblana;'+str(params.current_eblana.get_step()),
             'temperature eblana;'+str(lab.laser_eblana.get_temp()),
             'temperature japan;'+str(lab.laser_japan.get_temp()),
             'delay;'+str(params.delay.value),
             'ND filters 1047;'+_defaults_.ND_filters_1047, 
             'ND filters eblana;'+_defaults_.ND_filters_eblana, 
             'ND filters japan;'+_defaults_.ND_filters_japan
             )
