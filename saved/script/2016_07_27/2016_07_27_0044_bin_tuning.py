save_script()

try:    
    lab.awg.set_sample_clock_rate(276*MHz)
    lab.awg.set_trigger_mode("1", "trig")
    
    lab.pb.add_slave("awg_trig", 1)
    lab.pb.add_slave("Xshutter", 2)
    lab.pb.add_slave("scope_trig", 17)
    
    
    lab.reset_instructions()
    lab.pb.turn_on("awg_trig", time_on=us, rewind="start")
    lab.delay(2*us)
    lab.pb.turn_on("Xshutter", time_on=200*ms)
    lab.delay(50*ms)
    lab.pb.turn_on("scope_trig", time_on=ms, rewind="start")
    lab.awg.pulse(1, length=29*us, amp=200*mV, freq=50*MHz, shape="square")
    lab.delay(50*ms)
    lab.awg.load_memory()
    lab.pb.load_memory()
    lab.awg.initiate_generation(1)
    
    while True:
        lab.pb.start()
        time.sleep(lab.total_duration )

except:
    error_manager()





