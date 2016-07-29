import exp._defaults_ as _defaults_

try:    
    lab.awg.set_sample_clock_rate(276*MHz)
    lab.awg.set_trigger_mode("1", "trig")
    
    lab.pb.add_slave("awg_trig", 1)
    lab.pb.add_slave("Xshutter", 2)
    lab.pb.add_slave("scope_trig", 17)
    
    lab.reset_instructions()
    lab.pb.turn_on("awg_trig", time_on=us, rewind="start")
    lab.delay(2*us)
    lab.pb.turn_on("Xshutter", time_on=300*ms)
    lab.delay(50*ms)
    lab.pb.turn_on("scope_trig", time_on=ms, rewind="start")
    lab.awg.pulse("1", length=_defaults_.pi_len, amp=_defaults_.awg_amp, freq=_defaults_.awg_freq)
    lab.delay(50*ms)
    lab.awg.load_memory()
    lab.pb.load_memory()
    lab.awg.initiate_generation("1")
    
    while True:
        lab.pb.start()
        time.sleep(lab.total_duration )

except:
    error_manager()





