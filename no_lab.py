import timeit
time_1 = timeit.default_timer()

import exp.exp_no_lab as experiment
params = Params('x', 'y')

params.x.value = np.linspace(0,1,1001)
params.x.sweep_dim = 1
params.y.value = ['a','b']
params.y.sweep_dim = 2
    
try:
    scan(lab, params, experiment, fig=plt.figure())

except:
    error_manager()

finally:
    time_2 = timeit.default_timer()
    print(('time spent: %3.3f' % (time_2-time_1)))
    
