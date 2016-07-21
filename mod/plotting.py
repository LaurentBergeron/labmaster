"""
Contains functions used for plotting with the wonderful module which is matplotlib.
"""
__author__ =  "Laurent Bergeron <laurent.bergeron4@gmail.com>, Adam DeAbreu <adeabreu@sfu.ca>"

# Base modules
import numpy as np
import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d as plt3d
import pylab

# Homemade modules
from units import *
from not_for_user import LabMasterError
### automatic plotsdef create_plot_auto(fig, params, data):    if len(data.shape) == 1:        xlabel = sorted([x.name for x in params.get_current_sweeps(1)])[0]        createfig_XY(fig, xlabel, "data", 1, "--o")    elif len(data.shape) == 2:        xlabel = sorted([x.name for x in params.get_current_sweeps(1)])[0]        createfig_XY(fig, xlabel, "data", data.shape[1], "--o")        pass    else:        raise LabMasterError, "data dimension is too damn high (for plotting). Turn off plotting."    return            def update_plot_auto(fig, params, data):    if fig == None:        return    if len(data.shape) == 1:        _, xparam = sorted([(x.name, x) for x in params.get_current_sweeps(1)])[0]        updatefig_XY(fig, xparam.value, data)    elif len(data.shape) == 2 and params.get_dimension()==2:        _, xparam = sorted([(x.name, x) for x in params.get_current_sweeps(1)])[0]        _, yparam = sorted([(y.name, y) for y in params.get_current_sweeps(2)])[0]        updatefig_XY(fig, xparam.value, data[:,yparam.i], line_index=yparam.i)    elif len(data.shape) == 2 and params.get_dimension()==1:        _, xparam = sorted([(x.name, x) for x in params.get_current_sweeps(1)])[0]        for i in range(data.shape[1]):            updatefig_XY(fig, xparam.value, data[:,i], line_index=i)    return        # XY plotdef createfig_XY(fig, xlabel, ylabel, num_lines, *plot_args):    ax = fig.add_subplot(111)    ax.get_xaxis().get_major_formatter().set_useOffset(False)    ax.get_yaxis().get_major_formatter().set_useOffset(False)    ax.set_xlabel(xlabel)    ax.set_ylabel(ylabel)    for i in range(num_lines):        #lines, = ax.plot([])        ax.plot([], *plot_args)    returndef updatefig_XY(fig, xdata, ydata, line_index=0):    for child in [x for x in fig.axes[0].get_children() if isinstance(x, mpl.text.Text)]:        try:            child.remove()        except NotImplementedError:            pass    fig.axes[0].lines[line_index].set_xdata(xdata)    fig.axes[0].lines[line_index].set_ydata(ydata)    fig.axes[0].relim()    fig.axes[0].autoscale()    return# surface plotdef createfig_surface(fig, xlabel, ylabel, zlabel):    ax = fig.gca(projection='3d')    ax.set_xlabel(xlabel)    ax.set_ylabel(ylabel)    ax.set_zlabel(zlabel)    return def updatefig_surface(fig, xdata, ydata, zdata):    for child in [x for x in fig.axes[0].get_children() if type(x)==plt3d.art3d.Poly3DCollection]:        child.remove()    for child in [x for x in fig.axes[0].get_children() if isinstance(x, mpl.text.Text)]:        try:            child.remove()        except NotImplementedError:            pass    Y, X = np.meshgrid(ydata, xdata)    fig.axes[0].plot_surface(X, Y, np.nan_to_num(zdata), rstride=1, cstride=1)    fig.axes[0].relim()    fig.axes[0].autoscale()    return# image plotdef createfig_image(fig, xlabel, xdata, ylabel, ydata):    ax = fig.gca()    ax.set_xlabel(xlabel)    ax.set_ylabel(ylabel)    ax.imshow(np.zeros((len(xdata),len(ydata))), origin="lower", extent=(xdata[0], xdata[-1], ydata[0], ydata[-1]), aspect="auto")    return def updatefig_image(fig, array):    fig.axes[0].images[0].set_data(np.nan_to_num(array.T))                fig.axes[0].images[0].set_norm(mpl.colors.Normalize(vmin=np.min(array), vmax=np.max(array)))    return

def update_curve_fit(fig, fit_func, xdata, ydata, nargs, line_index, \
        initial_guess = None, *fit_args):

    xdata = xdata[np.isfinite(ydata)]
    ydata = ydata[np.isfinite(ydata)]

    if nargs > xdata.size:
        updatefig_XY(fig, xdata, ydata, line_index = line_index)
        return

    from scipy.optimize import curve_fit

    popt, pcov = curve_fit(fit_func, xdata, ydata, initial_guess, *fit_args)
    display_string = ', '.join(['%0.4f'%x for x in popt])
    fit_curve = fit_func(xdata, *popt)

    updatefig_XY(fig, xdata, fit_curve, line_index = line_index)
    ### update fit values
    ax = fig.axes[0]
    ax.text(0.05,0.95,display_string, transform = ax.transAxes, fontsize=15)
    return
