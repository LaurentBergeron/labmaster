lab.usb_counter.initiate_timer(1.)
while not lab.usb_counter.timer_is_stopped():
    pass
        
    print(lab.usb_counter.read(2))
    