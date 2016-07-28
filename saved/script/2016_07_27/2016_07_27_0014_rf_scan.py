
save_script()

try:
    import exp.exp_rf_scan as experiment
    params = Params("freq:Hz")
    
    lab.awg.set_trigger_mode("1", "auto")
    lab.awg.adjust_trig_latency = False
    lab.awg.set_sample_clock_rate(276*MHz)
    lab.awg.pulse("1", length=100*ms, freq=50*MHz, amp=1)
    lab.awg.load_memory()
    lab.awg.use_memory = False
    lab.awg.initiate_generation(1)
    
    params.freq.value = np.arange(1.608*GHz, 1.613*GHz, 5*kHz)
    
    
    
    fig_ref = plt.figure()
    # fig_ref = None
    
    scan(lab, params, experiment, fig=fig_ref)
except:
    error_manager()
finally:
    lab.awg.use_memory = True