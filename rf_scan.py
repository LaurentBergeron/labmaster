notebook("current; 0.1463A", "ND; Red Open, Green 3.0", "sensitivity; 1e-7")
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
    
    params.freq.value = np.arange(1.608*GHz, 1.613*GHz, 3*kHz)
    
    scan(lab, params, experiment, show_plot = True)
except:
    error_manager()
finally:
    lab.awg.use_memory = True