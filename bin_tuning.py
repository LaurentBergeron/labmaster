"""
Use lab.abort_all() to cancel the bin tuning.
"""

import exp._defaults_ as _defaults_

lab.awg.set_sample_rate(_defaults_.awg_sample_rate)
lab.awg.set_trigger_mode('trig')
lab.awg.default_channel = '1'

lab.pb.add_channel('awg_trig', 1)
lab.pb.add_channel('Xshutter', 2)

lab.reset_instructions()
lab.pb.turn_on('awg_trig', duration=us, rewind=True, ref='loop_start')
lab.delay(2*us)
lab.pb.turn_on('Xshutter', duration=300*ms)
lab.delay(50*ms)
lab.awg.pulse(length=_defaults_.pi_len, amp=_defaults_.awg_amp, freq=_defaults_.awg_freq)
lab.pb.branch('loop_start', duration=50*ms)


lab.awg.load_memory()
lab.pb.load_memory()
lab.awg.initiate_generation()

lab.pb.start()







