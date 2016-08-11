import timeit
time_1 = timeit.default_timer()

import exp.exp_no_lab as experiment
params = Params("x", "y")

params.x.value = np.linspace(0,6,6)
params.x.sweep_ID = 1
params.y.value = ['a','b']
params.y.sweep_ID = 2
    
try:
    scan(lab, params, experiment, fig=plt.figure(), quiet=True)

except:
    raise
    error_manager()

finally:
    time_2 = timeit.default_timer()
    print "time spent: %3.3f" % (time_2-time_1)
    
