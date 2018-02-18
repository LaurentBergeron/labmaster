import exp.exp_dds_rf_scan as experiment
import exp._defaults_ as _defaults_

params = Params('freq;Hz', 'dds_amp;V', 'freq_estimate_min;Hz', 'freq_estimate_max;Hz', 'delay;s')
params.freq.value = orange(1*MHz, 10*MHz, 100*kHz)
params.delay.value = 100*ms
params.dds_amp.value = _defaults_.dds_amp

## Min and max freq for finding clock transition
params.freq_estimate_min.value = 40*MHz
params.freq_estimate_max.value = 50*MHz

## comment both to plot next data on fig_ref figure
# fig_ref = plt.figure()
fig_ref = None


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
             'dds amplitude;'+str(params.dds_amp.value),
             'freq start;'+str(params.freq.get_start()),
             'freq end;'+str(params.freq.get_end()),
             'freq step;'+str(params.freq.get_step()),
             'delay;'+str(params.delay.value),
             'laser current set;'+str(_defaults_.laser_current),
             'laser current read;'+str(lab.laser.get_current()),
             'ND filters;'+_defaults_.ND_filters,
             'sensitivity;'+str(_defaults_.amp_sensitivity), 
             )
