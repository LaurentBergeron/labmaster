import os
acpmg = [66, 67, 68]

lvl0 = [126] + range(152,164)

lvl1 = [164, 165, 166] + range(169,181)

XY = [186, 187]

mrev = [193, 195]

lvl2 = range(30,42)

titles = ['acpmg', 'lvl0', 'lvl1', 'xy16', 'mrev16', 'lvl2']
ar_IDs = [acpmg, lvl0, lvl1, XY, mrev, lvl2]
dates = ['2016_07_27']*5 + ['2016_07_28']

def data_manipulation(data):
    """ will work for phase flipping experiment where data is a (N,2) array """
    size_array = np.min(np.sum(np.isfinite(data),0),0)
    save_data = np.abs(data[:size_array,0] - data[:size_array,1])
    return save_data

def param_manipulation(params):
    save_param = params.time_axis.value
    save_param = save_param[save_param > 0]
    return save_param

total = 0
total = sum([len(x) for x in ar_IDs])
popts = np.empty(shape=(total, 2))

count = 0
for i, IDs in enumerate(ar_IDs):
    location = '../2016_07_27_runs/'+titles[i]+'/'
    if not os.path.exists(location):
        os.makedirs(location)
    popts[count:count+len(ar_IDs[i]),:] = export_data(dates[i], IDs, location, '.npy', data_manipulation, param_manipulation)
    count += len(ar_IDs[i])

