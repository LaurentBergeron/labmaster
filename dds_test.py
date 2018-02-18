status = lab.pb.spinapi.pb_stop()
lab.pb.check_error(status)

status = lab.pb.spinapi.pb_start_programming(lab.pb.spinapi.PULSE_PROGRAM)
lab.pb.check_error(status)


start = lab.pb.spinapi.pb_inst_dds2(0, 0, 0, lab.pb.spinapi.TX_ENABLE, lab.pb.spinapi.NO_PHASE_RESET, \
                                    0, 0, 0, lab.pb.spinapi.TX_ENABLE, lab.pb.spinapi.NO_PHASE_RESET, \
                                    0xf, lab.pb.spinapi.Inst.CONTINUE, 0, 1e3)
lab.pb.check_error(start)

    
status = lab.pb.spinapi.pb_inst_dds2(0, 0, 0, lab.pb.spinapi.TX_ENABLE, lab.pb.spinapi.NO_PHASE_RESET, \
                                     0, 0, 0, lab.pb.spinapi.TX_ENABLE, lab.pb.spinapi.NO_PHASE_RESET, \
                                     0x0, lab.pb.spinapi.Inst.BRANCH, start, 1e3)
                          
status = lab.pb.spinapi.pb_stop_programming()
lab.pb.check_error(status)

status = lab.pb.spinapi.pb_reset()
lab.pb.check_error(status)
status = lab.pb.spinapi.pb_start()
lab.pb.check_error(status)






# for i in range(20):
    # lab.pb.flags = '100000000000'
    # status = lab.pb.spinapi.pb_inst_dds2(0, 0, 0, i, lab.pb.spinapi.PHASE_RESET, \
                              # 0, 0, 0, lab.pb.spinapi.TX_ENABLE, lab.pb.spinapi.PHASE_RESET, \
                              # int(lab.pb.flags[::-1],2), lab.pb.spinapi.Inst.CONTINUE, 0, (i+1)*1e3)
    # lab.pb.check_error(status)
    # lab.pb.flags = '000000000000'
    # status = lab.pb.spinapi.pb_inst_dds2(0, 0, 0, i, lab.pb.spinapi.PHASE_RESET, \
                              # 0, 0, 0, lab.pb.spinapi.TX_ENABLE, lab.pb.spinapi.PHASE_RESET, \
                              # int(lab.pb.flags[::-1],2), lab.pb.spinapi.Inst.CONTINUE, 0, (i+1)*1e3)
    # lab.pb.check_error(status)
    