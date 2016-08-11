"""
Contains functions used for plotting with the wonderful module which is matplotlib.
"""
__author__ =  "Laurent Bergeron <laurent.bergeron4@gmail.com>"

## Base modules
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d as plt3d
import inspect
import sys
from scipy.optimize import curve_fit

## Homemade modules
from units import *
from not_for_user import LabMasterError


##-------------------------------  automatic plotting -----------------------------------------------##

def create_plot_auto(lab, params, fig, data, ID):
    """
    If one of create_plot or update_plot function is omitted from the experimented module, this function will be used instead.
    Create a simple XY plot based on parameter arrays and sweep IDs.
    """
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
    """
    If one of create_plot or update_plot function is omitted from the experimented module, this function will be used instead.
    Update a plot created using create_plot_auto().
    """
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

    
    
##-------------------------------  XY plot ----------------------------------------------------------##

def createfig_XY(fig, xlabel, ylabel, num_lines, *plot_args):
    """
    Create a simple plot.
    
    - fig: A figure object.
    - xlabel: X label to the plot.
    - ylabel: Y label to the plot.
    - num_lines: Number of lines to be plotted.
    - *plot_args: Additional arguments will be sent to the plot function.
    """
    ax = fig.add_subplot(111)
    ax.get_xaxis().get_major_formatter().set_useOffset(False)
    ax.get_yaxis().get_major_formatter().set_useOffset(False)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    for i in range(num_lines):
        ax.plot([], *plot_args)
    return

def add_lines(fig, num_lines, *plot_args):
    """
    Add lines to a plot created using createfig_XY().
    
    - fig: A figure object.
    - num_lines: Number of lines to be plotted.
    - *plot_args: Additional arguments will be sent to the plot function.
    """
    ax = fig.axes[0]
    for i in range(num_lines):
        ax.plot([], *plot_args)

def updatefig_XY(fig, xdata, ydata, line_index=0):
    """
    Update a plot created using createfig_XY().
    
    - fig: A figure object.
    - xdata: X array.
    - ydata: Y array.
    - line_index: index of the line to update.
    """
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
    """
    Create a surface plot.
    
    - fig: A figure object.
    - xlabel: X label to the plot.
    - ylabel: Y label to the plot.
    - zlabel: Z label to the plot.
    """
    ax = fig.gca(projection='3d')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    return 

def updatefig_surface(fig, xdata, ydata, zdata, *plot_args):
    """
    Update a plot created using createfig_surface().
    
    - fig: A figure object.
    - xdata: X array (size M).
    - ydata: Y array (size N).
    - zdata: Z array (size MxN).
    - *plot_args: Additional arguments will be sent to the plot_surface function.
    """
    ax = fig.axes[0]
    for child in [x for x in ax.get_children() if type(x)==plt3d.art3d.Poly3DCollection]:
        child.remove()
    for child in [x for x in ax.get_children() if isinstance(x, mpl.text.Text)]:
        try:
            child.remove()
        except NotImplementedError:
            pass
    Y, X = np.meshgrid(ydata, xdata)
    ax.plot_surface(X, Y, np.nan_to_num(zdata), rstride=1, cstride=1, *plot_args)
    ax.relim()
    ax.autoscale()
    return

    
##------------------------------- image plot --------------------------------------------------------##

def createfig_image(fig, xlabel, xdata, ylabel, ydata):
    """
    Create an image plot.
    
    - fig: A figure object.
    - xlabel: X label to the plot.
    - xdata: X array (size M).
    - ylabel: Y label to the plot.
    - ydata: Y array (size N).
    """
    ax = fig.gca()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.imshow(np.zeros((len(xdata),len(ydata))), origin="lower", extent=(xdata[0], xdata[-1], ydata[0], ydata[-1]), aspect="auto")
    return 

def updatefig_image(fig, array):
    """
    Create an image plot.
    
    - fig: A figure object.
    - array: Z array (size MxN).
    """
    ax = fig.axes[0]
    ax.images[0].set_data(np.nan_to_num(array.T))            
    ax.images[0].set_norm(mpl.colors.Normalize(vmin=np.min(array), vmax=np.max(array)))
    return


