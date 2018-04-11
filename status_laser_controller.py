fig = plt.figure(figsize=(18,6))

while True:
    meas_curr = lab.laserITC.get_current()
    meas_temp = lab.laserITC.get_temp()
    fig.clear()
    fig.text(0.03, 0.3, 'curr = '+str(meas_curr), fontsize=100)
    fig.text(0.03, 0.7, 'temp = '+str(meas_temp), fontsize=100)
    plt.pause(0.5)