"""
Use lab.abort_all() to cancel the bin tuning.
"""

import exp._defaults_ as _defaults_

lab.dds.default_channel = 'RF1'

lab.dds.add_channel('Xshutter', 2)

lab.reset_instructions()
lab.dds.turn_on('Xshutter', duration=300*ms)
lab.delay(50*ms)
# lab.dds.pulse(length=_defaults_.pi_len, amp=_defaults_.dds_amp, freq=_defaults_.dds_freq)
lab.dds.branch('loop_start', duration=50*ms)


lab.dds.load_memory()
lab.dds.start()







