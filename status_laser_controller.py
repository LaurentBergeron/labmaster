fig = plt.figure(figsize=(18,8))

while True:
    meas_curr = lab.laserITC.get_current()
    meas_temp = lab.laserITC.get_temp()
    fig.clear()
    fig.text(0.03, 0.25, 'I = '+str(meas_curr), fontsize=100)
    wavenum = -4.5548e-4*(meas_curr*1e3)**2-0.0245*meas_curr*1e3+7824.543
    fig.text(0.03, 0.5, 'k @40C = '+str(wavenum), fontsize=100)
    fig.text(0.03, 0.75, 'T = '+str(meas_temp), fontsize=100)
    plt.pause(0.5)