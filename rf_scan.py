import exp.exp_rf_scan as experiment
import exp._defaults_ as _defaults_

params = Params('freq;Hz', 'awg_amp;V', 'awg_freq;Hz', 'freq_estimate_min;Hz', 'freq_estimate_max;Hz', 'delay;s')
params.freq.value = orange(1.6093*GHz, 1.613*GHz, 10*kHz)
params.delay.value = 100*ms
params.awg_amp.value = _defaults_.awg_amp
params.awg_freq.value = _defaults_.awg_freq

## Min and max freq for finding clock transition
params.freq_estimate_min.value = 1.6103*GHz
params.freq_estimate_max.value = 1.6106*GHz

## comment both to plot next data on fig_ref figure
fig_ref = plt.figure()
# fig_ref = None


try:
    scan(lab, params, experiment, fig=fig_ref)
except:
    error_manager()
finally:
    try:
        peak_min, at_freq = experiment.out(None, params, None, last_data(), None)
    except:
        print("Couldn't calculate frequency at peak minimum.")
        peak_min, at_freq = None, None
    notebook('Clock trans. freq;'+str(at_freq),
             'awg frequency;'+str(params.awg_freq.value),
             'awg amplitude;'+str(params.awg_amp.value),
             'freq start;'+str(params.freq.get_start()),
             'freq end;'+str(params.freq.get_end()),
             'freq step;'+str(params.freq.get_step()),
             'delay;'+str(params.delay.value),
             'laser current set;'+str(_defaults_.laser_current),
             'laser current read;'+str(lab.laser.get_current()),
             'ND filters;'+_defaults_.ND_filters,
             'sensitivity;'+str(_defaults_.amp_sensitivity), 
             )
