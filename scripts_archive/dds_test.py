status = lab.dds.spinapi.pb_stop()
lab.dds.check_error(status)

status = lab.dds.spinapi.pb_start_programming(lab.dds.spinapi.PULSE_PROGRAM)
lab.dds.check_error(status)


start = lab.dds.spinapi.pb_inst_dds2(0, 0, 0, lab.dds.spinapi.TX_ENABLE, lab.dds.spinapi.NO_PHASE_RESET, \
                                     0, 0, 0, lab.dds.spinapi.TX_ENABLE, lab.dds.spinapi.NO_PHASE_RESET, \
                                     0xf, lab.dds.spinapi.Inst.CONTINUE, 0, 1e3)
lab.dds.check_error(start)

    
status = lab.dds.spinapi.pb_inst_dds2(0, 0, 0, lab.dds.spinapi.TX_ENABLE, lab.dds.spinapi.NO_PHASE_RESET, \
                                      0, 0, 0, lab.dds.spinapi.TX_ENABLE, lab.dds.spinapi.NO_PHASE_RESET, \
                                      0x0, lab.dds.spinapi.Inst.BRANCH, start, 1e3)
                          
status = lab.dds.spinapi.pb_stop_programming()
lab.dds.check_error(status)

status = lab.dds.spinapi.pb_reset()
lab.dds.check_error(status)
status = lab.dds.spinapi.pb_start()
lab.dds.check_error(status)






# for i in range(20):
    # lab.dds.flags = '100000000000'
    # status = lab.dds.spinapi.pb_inst_dds2(0, 0, 0, i, lab.dds.spinapi.PHASE_RESET, \
                              # 0, 0, 0, lab.dds.spinapi.TX_ENABLE, lab.dds.spinapi.PHASE_RESET, \
                              # int(lab.dds.flags[::-1],2), lab.dds.spinapi.Inst.CONTINUE, 0, (i+1)*1e3)
    # lab.dds.check_error(status)
    # lab.dds.flags = '000000000000'
    # status = lab.dds.spinapi.pb_inst_dds2(0, 0, 0, i, lab.dds.spinapi.PHASE_RESET, \
                              # 0, 0, 0, lab.dds.spinapi.TX_ENABLE, lab.dds.spinapi.PHASE_RESET, \
                              # int(lab.dds.flags[::-1],2), lab.dds.spinapi.Inst.CONTINUE, 0, (i+1)*1e3)
    # lab.dds.check_error(status)
    