fig = plt.figure(figsize=(12,6))

while True:
    meas = lab.lockin.get_X()
    fig.clear()
    fig.text(0.1, 0.5, str(meas), fontsize=100)
    plt.pause(0.5)