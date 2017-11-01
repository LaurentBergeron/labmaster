"""
Contains functions used for fitting.
"""
__author__ =  "Laurent Bergeron <laurent.bergeron4@gmail.com>, Adam DeAbreu <adeabreu@sfu.ca>"

## Base modules
import numpy as np
import inspect
import sys
from scipy.optimize import curve_fit

## Homemade modules
from .units import *
from .not_for_user import LabMasterError


    
def fit(fit_func, xdata, ydata,  \
        start=None, initial_guess = None, *fit_args):
    """
    Return popt from the scipy.optimize.curve_fit function. Errors from curve_fit are printed, not raised.
    
    - fit_func: Function to use in fitting.
    - xdata: X array to use in fitting.
    - ydata: Y array to use in fitting.
    - start: Start the fit when xdata is filled with more than 'start' values (other than NaNs). Default is the number of fit_func arguments.
    - initial_guess: Initial guess for the curve_fit function.
    - *fit_args: Addition arguments will be sent to the curve_fit function.
    """
    ## Remove NaNs from arrays.
    xdata = xdata[np.isfinite(ydata)]
    ydata = ydata[np.isfinite(ydata)]
    
    if start==None:
        ## Default for start is the number of fit_func arguments.
        start = len(inspect.getargspec(fit_func).args)
    
    if start > xdata.size:
        ## Start the fit when xdata is filled with more than 'start' values (other than NaNs).
        return

    try:
        popt, pcov = curve_fit(fit_func, xdata, ydata, initial_guess, *fit_args)
    except:
        popt, pcov = None, None
        print("curve_fit failed.", sys.exc_info()[0].__name__+":",  sys.exc_info()[1])

    return popt