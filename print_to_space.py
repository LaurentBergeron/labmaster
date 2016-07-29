fig = plt.figure(figsize=(20,13))

while True:
    meas = lab.lockin.measure()
    fig.clear()
    fig.text(0.1, 0.5, str(meas), fontsize=500)
    plt.pause(0.5)