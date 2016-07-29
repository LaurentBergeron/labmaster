"""
Contains an example file for analyzing data

Must be run after running _launch_.ipy in an ipython environment

Requires functions on how to manipulate the data and the param files
as well as a function on how to create fitting parameters if desired.

Will output fitting parameters as well as saving the data and param files
as .npy (thus not needing all of LabMaster to manipulate) in the location
directory
"""


## Define all IDs and dates for the files to be exported
acpmg = [66, 67, 68]
lvl0 = [126] + range(152,164)
lvl1 = [164, 165, 166] + range(169,181)
XY = [186, 187]
mrev = [193, 195]
lvl2 = range(30,42)
ar_IDs = [acpmg, lvl0, lvl1, XY, mrev, lvl2]

dates = ['2016_07_27']*5 + ['2016_07_28']

## Define file location for exported data to be saved
titles = ['acpmg', 'lvl0', 'lvl1', 'xy16', 'mrev16', 'lvl2']
location = []
for i in range(len(titles)):
    location = location + ['../2016_07_27_runs/'+titles[i]+'/']

## Define functions on how data, params and fitting parameters will be created
def data_manipulation(data):
    """ will work for phase flipping experiment where data is a (N,2) array """
    size_array = np.min(np.sum(np.isfinite(data),0),0)
    save_data = np.abs(data[:size_array,0] - data[:size_array,1])
    return save_data

def param_manipulation(params):
    save_param = params.time_axis.value
    selection = save_param > 0
    selection[0] = True
    save_param = save_param[selection]
    return save_param

def popts_manipulation(data, params, fig):
    size_array = np.min(np.sum(np.isfinite(data),0),0)
    data = np.abs(data[:size_array,0] - data[:size_array,1])

    save_param = params.time_axis.value
    selection = save_param > 0
    selection[0] = True
    param = save_param[selection]

    def fit_func(xdata, A, tau):
        return A*np.exp(-1.*xdata/tau)

    popt = plotting.update_curve_fit(fig, fit_func, param[1:], data[1:], line_index=3, nargs = 2, initial_guess = [data[1], 10] )
    return popt



##iterate through IDs and export data, save figures and return popts

total = 0
total = sum([len(x) for x in ar_IDs])
popts = np.empty(shape=(total, 2))

count = 0
for i, IDs in enumerate(ar_IDs):
    if not os.path.exists(location[i]):
        os.makedirs(location[i])
    popts[count:count+len(ar_IDs[i]),:] = export_data(dates[i], IDs, location[i], '.npy', data_manipulation, param_manipulation, None)
    count += len(ar_IDs[i])

