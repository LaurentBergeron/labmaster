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
import inspect
import sys
from scipy.optimize import curve_fit

# Homemade modules
from units import *
from not_for_user import LabMasterError


##-------------------------------  automatic plotting -----------------------------------------------##

def create_plot_auto(lab, params, fig, data, ID):
    if len(data.shape) == 1:
        xlabel = sorted([x.name for x in params.get_current_sweeps(1)])[0]
        createfig_XY(fig, xlabel, "data", 1, "--o")
    elif len(data.shape) == 2:
        xlabel = sorted([x.name for x in params.get_current_sweeps(1)])[0]
        createfig_XY(fig, xlabel, "data", data.shape[1], "--o")
    else:
        raise LabMasterError, "data dimension is too damn high (for plotting). Turn off plotting."
    return
        
    
def update_plot_auto(lab, params, fig, data, ID):
    if fig == None:
        return
    if len(data.shape) == 1:
        _, xparam = sorted([(x.name, x) for x in params.get_current_sweeps(1)])[0]
        updatefig_XY(fig, xparam.value, data)
    elif len(data.shape) == 2 and params.get_dimension()==2:
        _, xparam = sorted([(x.name, x) for x in params.get_current_sweeps(1)])[0]
        _, yparam = sorted([(y.name, y) for y in params.get_current_sweeps(2)])[0]
        updatefig_XY(fig, xparam.value, data[:,yparam.i], line_index=yparam.i)
    elif len(data.shape) == 2 and params.get_dimension()==1:
        _, xparam = sorted([(x.name, x) for x in params.get_current_sweeps(1)])[0]
        for i in range(data.shape[1]):
            updatefig_XY(fig, xparam.value, data[:,i], line_index=i)
    return


##------------------------------- fitting functions ------------------------------------------------------##
    
def fit(fit_func, xdata, ydata,  \
        nargs=None, initial_guess = None, *fit_args):
        
    xdata = xdata[np.isfinite(ydata)]
    ydata = ydata[np.isfinite(ydata)]
    
    if nargs==None:
        nargs = len(inspect.getargspec(fit_func).args) - 1
    
    if nargs >= xdata.size:
        return

    try:
        popt, pcov = curve_fit(fit_func, xdata, ydata, initial_guess, *fit_args)
    except:
        print "curve_fit raised "+sys.exc_info()[0].__name__
        popt = None
    return popt
    
    
    
##-------------------------------  XY plot ----------------------------------------------------------##

def createfig_XY(fig, xlabel, ylabel, num_lines, *plot_args):
    ax = fig.add_subplot(111)
    ax.get_xaxis().get_major_formatter().set_useOffset(False)
    ax.get_yaxis().get_major_formatter().set_useOffset(False)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    for i in range(num_lines):
        ax.plot([], *plot_args)
    return

def add_lines(fig, num_lines, *plot_args):
    ax = fig.axes[0]
    for i in range(num_lines):
        ax.plot([], *plot_args)

def updatefig_XY(fig, xdata, ydata, line_index=0):
    ax = fig.axes[0]
    for child in [x for x in ax.get_children() if isinstance(x, mpl.text.Text)]:
        try:
            child.remove()
        except NotImplementedError:
            pass          
    ax.lines[line_index].set_xdata(xdata)
    ax.lines[line_index].set_ydata(ydata)
    ax.relim()
    ax.autoscale()
    return

##------------------------------- surface plot ------------------------------------------------------##

def createfig_surface(fig, xlabel, ylabel, zlabel):
    ax = fig.gca(projection='3d')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    return 

def updatefig_surface(fig, xdata, ydata, zdata):
    ax = fig.axes[0]
    for child in [x for x in ax.get_children() if type(x)==plt3d.art3d.Poly3DCollection]:
        child.remove()
    for child in [x for x in ax.get_children() if isinstance(x, mpl.text.Text)]:
        try:
            child.remove()
        except NotImplementedError:
            pass
    Y, X = np.meshgrid(ydata, xdata)
    ax.plot_surface(X, Y, np.nan_to_num(zdata), rstride=1, cstride=1)
    ax.relim()
    ax.autoscale()
    return

    
##------------------------------- image plot --------------------------------------------------------##

def createfig_image(fig, xlabel, xdata, ylabel, ydata):
    ax = fig.gca()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.imshow(np.zeros((len(xdata),len(ydata))), origin="lower", extent=(xdata[0], xdata[-1], ydata[0], ydata[-1]), aspect="auto")
    return 

def updatefig_image(fig, array):
    ax = fig.axes[0]
    ax.images[0].set_data(np.nan_to_num(array.T))            
    ax.images[0].set_norm(mpl.colors.Normalize(vmin=np.min(array), vmax=np.max(array)))
    return


