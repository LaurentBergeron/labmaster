from __future__ import division
"""
Holds all the functions useful for the user. Use 'python _console_launch_.py' to launch LabMaster.
"""
__author__ = "Laurent Bergeron, <laurent.bergeron4@gmail.com>, Camille Bowness <cbowness@sfu.ca>, Adam DeAbreu <adeabreu@sfu.ca>"

## Base modules
import sys
import os 
import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as cst
import glob             ## Use * in file handling
import time             ## Pause script with time.sleep
import timeit           ## Better timer than time
import datetime         ## Includes datetime objects to handle dates.
import importlib        ## More flexible imports
import visa             ## Control visa instruments
import textwrap         ## Auto format documentation strings
import types            ## better type handling
import pickle           ## save and load any instance from python into a .pickle file
import inspect          ## retrieve information on python objects
import shutil           ## high-level system operation
import smtplib          ## SMTP protocol client (to send email)
import xlrd             ## .xlsx read
import xlwt             ## .xlsx write

## Homemade modules
import not_for_user as nfu
import classes
import plotting
import fitting
import instruments
import available_instruments

## Import useful objects to user from other modules
from classes import Lab, Params
from not_for_user import LabMasterError, today, lastID, auto_unit, saving_folders, remove_nan
from units import *
from pydoc import help

        
    
def scan(lab, params, experiment, fig=None, quiet=True, update_plot=True):
    """
    The holy grail of LabMaster.
    Scan parameters value attribute in the order imposed by their sweep_dim.
    For each point in scan, run an experiment as dicted by the experiment module.
    Saves everything under locations defined by saving_folders().

    - lab: Lab instance with required instruments connected.
    - params: Params instance with required parameters.
    - experiment: Module that will rule what is going on during experiment.
    - fig: Give a matplotlib figure object to plot a live result of the scan.
    - quiet: If True, won't ask user if everything is ok. Enable this for overnight runs or if you are overconfident.
    - update_plot: If a figure object is given by the fig argument, update_plot=False will update the figure only once, at the end of the scan.
    """
            
    ## ID is the number indicated after the date in file names.
    ID = nfu.detect_experiment_ID() ## returns the current max ID found in experiment/ folder, plus one (ID is a string)
    
    ## Replace missing functions from experiment module
    fill_experiment_functions(experiment)
    
    ## Get ready once, for experiment.start function.
    nfu.get_ready(lab, params)
    ## Call the start function of experiment module
    experiment.start(lab, params, fig, None, ID)
    ## Get ready once more! Start may have affected things.
    nfu.get_ready(lab, params)

    ## Check if inputs are conform to a bunch of restrictions
    check_params(params)
    check_lab(lab)

    print "ID:",ID,"\n"
    ## data is an array full of zeros matching good dimensions imposed by params.
    data = nfu.zeros(params, experiment)
    ## Create folders for today if they don't exist.
    nfu.create_todays_folder()
    if fig != None:
        ## Initialize the plot on the figure.
        experiment.create_plot(lab, params, fig, data, ID)

    if quiet:
        ## No time for questions.
        pass
    else:
        if raw_input("Is this correct? [Y/n]") not in nfu.positive_answer_Y():
            raise KeyboardInterrupt
            
    print "\n--------------------------------------------\n", experiment.__name__, "\n--------------------------------------------" 
    print params 

        
    ## Up to this point, results will be saved whatever happens.
    try:
        ## Save what we know about the experiment so far in experiment/ folder. 
        save_experiment(None, None, None, ID, "first_time")
        ## Start the sweep! data will be filled with science
        nfu.sweep(lab, params, experiment, data, fig, 1, ID, update_plot)
        error_message = "Scan completed."
    except:        
        error_message = error_manager(as_string=True, all=True)
        raise
    finally:
        ##-------------------------------- All executions in the finally statement should be fail-proof. --------------------------------##
        ## Save experiment info, as well as experiment source code.
        save_experiment(lab, params, experiment, ID, error_message+"\n")
        try:
            ## Call the end function of experiment module
            experiment.end(lab, params, fig, data, ID)
        except:
            print "end function from "+experiment.__name__+" failed.", sys.exc_info()[0].__name__+":",  sys.exc_info()[1]
        ## Call the abort method from every instrument connected to the Lab instance.
        lab.abort_all()
        ## Save params in params/ folder. 
        save_params(params, ID)
        ## Save parameters values and data in sweep/ folder. 
        save_sweep(params, data, ID)
        ## Save fig as pdf in fig/ folder
        save_fig(fig, ID)
        ## Save the script which was started by the %irun magic.
        save_script(ID)
        if fig!=None and update_plot==False:
            try:
                ## Update the figure one last time.
                experiment.update_plot(lab, params, fig, data, ID)
            except:
                print "update_plot from "+experiment.__name__+" failed.", sys.exc_info()[0].__name__+":",  sys.exc_info()[1]
        print "\nsaved as",ID,"\n"
    return
                    



def check_lab(lab):
    """
    Check if every instrument is conform to the rules.
    
    - lab: a Lab instance.
    """
    for instrument in lab.get_objects():
        ## Programmable instruments need a load_memory method.
        if not hasattr(instrument, "load_memory") and instrument.use_memory:
            raise LabMasterError, instrument.name+" needs a load_memory() method."
        ## Every instruments need a close method.
        if not hasattr(instrument, "close"):
            raise LabMasterError, instrument.name+" needs a close() method."
        ## Programmable instruments need an abort method.
        if not hasattr(instrument, "abort"):
            raise LabMasterError, instrument.name+" needs a abort() method."
    return

def check_params(params):
    """
    Checks if every parameter is conform to the rules. 
    Convert lists to numpy arrays.
    
    - params: a Params instance.    
    """
    if params.get_objects()==[]:
        raise LabMasterError, "No parameters detected."
    for key, param in params.get_items():   
        ## Sweep IDs must be int types. 
        if not isinstance(param.sweep_dim, int):
            raise LabMasterError, key+".sweep_dim should be int type, instead of "+str(type(param.sweep_dim))+"."   
        ## Sweep IDs must be positive.     
        if param.sweep_dim < 0:
            raise LabMasterError, key+".sweep_dim is < 0."
        if param.is_not_const():
            ## Convert lists to numpy arrays.
            if isinstance(param.value, list):
                param.value = np.array(param.value)
            ## The length can't be zero.
            if len(param.value) < 1:
                raise LabMasterError, key+".value is an array or list with length zero."
            ## The dimension must be one.
            if param.value.ndim > 1:
                raise LabMasterError, key+".value has a dimension higher than 1."                
            ## The length is restricted to 10^8. 
            if len(param.value) > 1e6:
                raise LabMasterError,param.name+" array will slow Python because it is too large."

    for i in range(1,params.get_dimension()+1):
        ## Empty sweep dimensions are forbidden.
        if params.get_current_sweeps(i)==[]:
            raise LabMasterError, "No sweeps detected at sweep_dim="+str(i)+"."
        ## All parameters from the same sweep dimension must be the same length.
        lengths_by_ID = [len(x.value) for x in params.get_current_sweeps(i)]
        for l in range(len(lengths_by_ID)):
            if not lengths_by_ID[l] == lengths_by_ID[l-1]:
                raise LabMasterError, "Arrays programmed for sweep_dim="+str(i)+" have different lenghts."  
    return

def clean_reset(namespace):
    """
    Reset all Lab instances from namespace (should be globals() most of the time).
    """
    for key, value in namespace.items():
        if key=="Lab": 
            ## Lab is the class definition, obviously doesn't count. 
            continue
        if key[:1] == "_": 
            ## Ipython history doesn't count (it's the same lab instance going by another name)
            continue
        try:
            if str(value.__class__).split(".")[-1] == "Lab" and len(value.get_objects())>0:
                print "-> "+key+".close_all()"
                number_of_failures = value.close_all()
                if number_of_failures > 0:
                    raise LabMasterError, "Lab instance '"+key+"' is unable to close instruments.\nReset aborted. \nPlease close instrument drivers.\n\n\n"
        except AttributeError:
            pass

    del key, value
    return
    
def error_manager(as_string=False, all=False):
    """
    Get last raised error from sys module. 
    If it's a LabMasterError or one of its subclasses, print the error message in a minimalistic way. To get full traceback, run %tb in Ipython.
    Same for KeyboardInterrupt.
    For every other type of error, raise the error.
    
    - as_string: If as_string is True, return the error message as a string.
                 If as_string is False, just print it to console.
    - all: If all is True, stop traceback and print an error message for every type of error.
    """
    ## Get last raised error from sys module.
    error_type, error_value, error_traceback = sys.exc_info()

    if error_type==None:
        ## No errors found in sys.exc_info().
        ## It's not because an error was found that an error was raised, because try/except statements will save errors to sys.exc_info().
        return ""

    ## Select the message to print.
    if error_type is LabMasterError:
        message = nfu.err_msg()+ str(error_value)
    elif LabMasterError in error_type.__bases__:
        message = error_type.__name__+": "+ str(error_value)
    elif error_type is KeyboardInterrupt:
        message = "Experiment aborted."
    else:
        if all:
            message = error_type.__name__+": "+str(error_value)
        else:
            ## Normal error management.
            raise
    
    ## Load the errors back in the sys module to retrieve them using %tb.
    sys.last_type, sys.last_value, sys.last_traceback = error_type, error_value, error_traceback
    
    if as_string:
        out = message
    else:
        out = ""
        print message+ "\n%tb for full traceback\n"*(error_type is not KeyboardInterrupt)
    return out
    
def export_data(date, IDs, location, output, \
        experiment=None, data_manipulation = None, param_manipulation = None, popts_manipulation = None):
    """
    Manipulate data and params and save them in a customized file.
    
    - date: Date from file name. Has to follow this datetime format: %Y_%m_%d
            %Y is year in four characters.
            %m is month in two characters.
            %d is day in two characters.
            Good format example: 2016_06_24
    - IDs: array of numbers indicated after the date in file name. Can be '0075' or 75.
    - location: Directory in which files will be saved.
    - output: file type of data, either 'npy' or 'txt'.
    - data_manipulation: function to manipulate loaded data in a form to be saved with np.save or np.savetxt
            (see mod/analyze_data.py)
    - param_manipulation: function to manipulate loaded param class into a numpy array to be saved with np.save or
            np.savetxt (see mod/analyze_data.py)
    - popts_manipulation: function to manipulate loaded data and loaded param class to generate fit parameters
            (see mod/analyze_data.py)
    """
    raise LabMasterError, "This function is deprecated. Adam, please update it!"
    popts_ar = None 
    for i, ID in enumerate(IDs):
        print "currently processing: ", ID
        ID = nfu.pad_ID(ID) ## Convert ID to correct format.
        data = load_data(date, ID)
        params = load_params(date, ID)
        popts = load_out(date, ID, experiment=experiment)
        
        if data_manipulation is not None:
            to_save_data = data_manipulation(data)
        else:
            print "need a data manipulation function, nothing was saved"
            return popts
        if param_manipulation is not None:
            to_save_param = param_manipulation(params)
        else:
            print "need a param manipulation function, nothing was saved"
            return popts
        if popts_manipulation is not None:
            popts = popts_manipulation(data, params)

        if popts_ar is None:
            popts_ar = np.empty(shape=(len(IDs), len(popts)))
        popts_ar[i,:] = popts

        if 'npy' in output:
            np.save(location+'/'+date+"_"+ID+"_data.npy",to_save_data)
            np.save(location+'/'+date+"_"+ID+"_params.npy",to_save_param)
        elif 'txt' in output:
            np.savetxt(location+'/'+date+"_"+ID+"_data.npy",to_save_data)
            np.savetxt(location+'/'+date+"_"+ID+"_params.npy",to_save_param)
        plt.savefig(location+date+"_"+ID+"figure.pdf")

    return popts_ar


def fill_experiment_functions(experiment):
    """
    Check experiment module for missing functions. 
    If a function is missing, it will be replaced by an empty one, with the exception of create_plot and update_plot.
    If one of create_plot or update_plot is missing, both will be replaced by the automatic plotting functions from the plotting module.
    
    - experiment: Module to be used as experiment in a scan function.
    """
    def empty(lab, params, fig, data, ID):
        """A very boring function."""
        return 

    ## List of functions that can be defined in an experiment module.
    available_functions = ("launch",
                           "get_data",
                           "sequence",
                           "start",
                           "end",
                           "out",
                           "create_plot",
                           "update_plot")

    ## Each function from the previous list must have the same arguments as empty().
    required_num_args = len(inspect.getargspec(empty).args)

    for func_name in available_functions:
        try:
            if len(inspect.getargspec(experiment.__dict__[func_name]).args) != required_num_args:
                raise LabMasterError, "Function "+func_name+" from "+experiment.__name__+" requires "+str(required_num_args)+" arguments."
        except KeyError:
            ## If an experiment module misses a function, a KeyError will be raised. A default function is then assigned.
            if func_name=="create_plot" or func_name=="update_plot":
                experiment.create_plot = plotting.create_plot_auto
                experiment.update_plot = plotting.update_plot_auto
            else:
                experiment.__dict__[func_name] = empty
    
    return 
    
    
def help_please():
    """
    Use ? after an object to get documentation. With ?? you get source code.
    Python advice: Type help() for interactive help, or help(object) for help about object.
    LabMaster users manual is located under doc/_LabMaster_users-manual_
    For a more detailed doc of the source code of LabMaster, you will find HTML help under doc/_LabMaster_html_
    """
    print textwrap.dedent(help_please.__doc__)
    print "Available functions:"
    funcs = [x[0] for x in inspect.getmembers(sys.modules[__name__], inspect.isfunction) if x[0] not in ("hack_time", "tea")]
    N = len(funcs)
    first_col = []
    second_col = []
    third_col = []
    for i in range(0,N,3):
        try:
            first_col.append(funcs[i])
        except IndexError:
            first_col.append("")
        try:
            second_col.append(funcs[i+1])
        except IndexError:
            second_col.append("")
        try:
            third_col.append(funcs[i+2])
        except IndexError:
            third_col.append("")
    first_maxlen = len(max(first_col, key=len))
    second_maxlen = len(max(second_col, key=len))
    for i,j,k in zip(first_col, second_col, third_col):
        print "%s\t%s\t%s" % (i.ljust(first_maxlen, " "), j.ljust(second_maxlen, " "), k)
    return

    
def last_data():
    """
    Load data from the last scan.
    Is the same as load_data(today(), lastID()).
    """
    return load_data(today(), lastID())
    
def last_sweep():
    """
    Load full sweep from the last scan.
    Is the same as load_sweep(today(), lastID()).
    """
    return load_sweep(today(), lastID())
    
def last_params(output=None):
    """
    Load params from last scan.
    Is the same as load_params(today(), lastID()).
    
    - experiment_name: Use create_plot and update_plot from this experiment.
    - output: If None, will return the whole params instance.
              If a string, will return the parameter from params with that name.
    """
    return load_params(today(), lastID(), output=output)
    
def last_plot(experiment_name=None):
    """
    Show figure from the last scan.
    Is the same as load_plot(today(), lastID()).
    
    - experiment_name: Use create_plot and update_plot from this experiment.
    """
    return load_plot(today(), lastID(), experiment_name=experiment_name)
    
def last_out(experiment_name=None):
    """
    Call experiment.out() from the last scan.
    Is the same as load_out(today(), lastID()).
    
    - experiment_name: Use a specific experiment module.
    """
    return load_out(today(), lastID(), experiment_name=experiment_name)

def load_data(date, ID):
    """
    Load data from a .npy file in data/ folder. 
    
    - date: Date from file name. Has to follow this datetime format: %Y_%m_%d
            %Y is year in four characters.
            %m is month in two characters.
            %d is day in two characters.
            Good format example: 2016_06_24
    - ID: Number indicated after the date in file name.
    """
    return load_sweep(date, ID)['DATA']
    
def load_sweep(date, ID):
    """
    Load sweep from a .npy file in sweep/ folder. 
    
    - date: Date from file name. Has to follow this datetime format: %Y_%m_%d
            %Y is year in four characters.
            %m is month in two characters.
            %d is day in two characters.
            Good format example: 2016_06_24
    - ID: Number indicated after the date in file name.
    """
    ID = nfu.pad_ID(ID) ## Convert ID to correct format.
    file_format = nfu.filename_format(date, ID, script_name=False)
    main_saving_loc = saving_folders()[0] ## Load from the first element of saving_folders()
    
    try:
        ## Find the file matching date and ID
        matching_file = [filename for filename in glob.glob(main_saving_loc+"sweep/"+date+"/*") if file_format in filename][0]
    except IndexError:
        raise LabMasterError, "Date or ID does not match any existing file."
        
    return np.load(matching_file)
    
def load_params(date, ID, output=None):
    """
    Load params from a .pickle file in params/ folder.
    
    - date: Date from file name. Has to follow this datetime format: %Y_%m_%d
            %Y is year in four characters.
            %m is month in two characters.
            %d is day in two characters.
            Good format example: 2016_06_24
    - ID: Number indicated after the date in file name.
    - output: If None, will return the whole params instance.
              If a string, will return the parameter from params with that name.
    """
    ID = nfu.pad_ID(ID) ## Convert ID to correct format.
    file_format = nfu.filename_format(date, ID, script_name=False)
    main_saving_loc = nfu.saving_folders()[0]
    try:
        matching_file = [filename for filename in glob.glob(main_saving_loc+"params/"+date+"/*") if file_format in filename][0]
    except IndexError:
        raise LabMasterError, "Date or ID does not match any existing file."
    with open(matching_file, "rb") as f:
        params = pickle.load(f)
    if output==None:
        return params
    else:
        try:
            return params.__dict__[output]
        except KeyError:
            raise nfu.LabMasterError, "Requested output not found in params attributes."
    return

def load_plot(date, ID, experiment_name=None, fig=None):
    """
    Show figure generated by data, params and experiment from specified date and ID.
    
    - date: Date from file name. Has to follow this datetime format: %Y_%m_%d
            %Y is year in four characters.
            %m is month in two characters.
            %d is day in two characters.
            Good format example: 2016_06_24
    - ID: Number indicated after the date in file name.
    - experiment_name: Use create_plot and update_plot from this experiment instead.
    - fig: Plot the result on the given figure.
    """
    ID = nfu.pad_ID(ID) ## Convert ID to correct format.
    main_saving_loc = saving_folders()[0] ## Load from the first element of saving_folders()
    
    try:
        ## If experiment_name was omitted, find the matching experiment module by looking into experiment/ folder.
        if experiment_name==None:
            file_format = nfu.filename_format(date, ID, script_name=False)
            matching_file = [filename for filename in glob.glob(main_saving_loc+"experiment/"+date+"/*") if file_format in filename][0]
            with open(matching_file) as f:
                experiment_name = f.read().split("### Experiment: ")[-1].split("\n")[0][:-3]
        experiment = importlib.import_module(experiment_name)
    except ImportError, IndexError:
        ## ImportError will be raised if experiment_name is wrong.
        ## IndexError will be raised if date and ID don't match any file.
        print "Could not import experiment. Using auto plotting from plotting module."
        experiment = None
        
    if fig==None:
        fig = plt.figure()
    lab = None ## fake lab to input to create_plot and update_plot. If those functions needed lab, an error will be raised.
    params = load_params(date, ID)
    data = load_data(date, ID)
    
    if experiment==None:
        plotting.create_plot_auto(lab, params, fig, data, ID)
        plotting.update_plot_auto(lab, params, fig, data, ID)
    else:
        experiment.create_plot(lab, params, fig, data, ID)
        experiment.update_plot(lab, params, fig, data, ID)
        
    return fig
    
def load_out(date, ID, fig=None, experiment_name=None):
    """
    Show figure generated by data, params and experiment from specified date and ID.
    
    - date: Date from file name. Has to follow this datetime format: %Y_%m_%d
            %Y is year in four characters.
            %m is month in two characters.
            %d is day in two characters.
            Good format example: 2016_06_24
    - fig: If experiment.out requires a fig, input it here.
    - ID: Number indicated after the date in file name.
    - experiment_name: Use a specific experiment module.
    """
    ID = nfu.pad_ID(ID) ## Convert ID to correct format.
    main_saving_loc = saving_folders()[0] ## Load from the first element of saving_folders()

    try:
        ## If experiment_name was omitted, find the matching experiment module by looking into experiment/ folder.
        if experiment_name==None:
            file_format = nfu.filename_format(date, ID, script_name=False)
            ## Find the file matching date and ID
            matching_file = [filename for filename in glob.glob(main_saving_loc+"experiment/"+date+"/*") if file_format in filename][0]
            with open(matching_file) as f:
                experiment_name = f.read().split("### Experiment: ")[-1].split("\n")[0][:-3]
        experiment = importlib.import_module(experiment_name)
    except ImportError, IndexError:
        ## ImportError will be raised if experiment_name is wrong.
        ## IndexError will be raised if date and ID don't match any file.
        raise LabMasterError, "Could not import experiment."

    lab = None ## fake lab to input to create_plot and update_plot. If those functions needed lab, an error will be raised.
    params = load_params(date, ID)
    data = load_data(date, ID)
    try: 
        out = experiment.out(lab, params, fig, data, ID)
    except AttributeError:
        print experiment.__name__+" has no out function."
        out = None
    return out
    
    
def notebook(*args):
    """
    Update the notebook.txt file according to input arguments.
    Arguments should be strings that respect this format: 'column_name;column_value'. 
    If the column name format matchs the previous one, only the values will be written to notebook.txt.
    Script name, date and ID are automatically written, as well as flags arguments from the %irun magic.
    """
    filename="notebook" ## Name under which to save the .txt file (default is 'notebook')
    delimiter=';' ## The delimiter must match notebook_to_xls().
    date = nfu.today()
    ID = nfu.pad_ID(int(nfu.detect_experiment_ID())-1)
    script_name = nfu.get_script_filename()
    column_name = [script_name, date, "ID"] + [""]*len(args) + ["comment"]
    entry       = ["",          "",   ID] +   [""]*len(args) + [" ".join(sys.argv[1:])]
    for i, arg in enumerate(args):
        column_name[i+3], entry[i+3] = arg.split(delimiter)
    line_format = delimiter.join(column_name)+delimiter
    with open(filename+".txt", "a") as f:
        if line_format==nfu.get_notebook_line_format(delimiter=delimiter):
            pass
        else:
            f.write("\n"+line_format+"\n")
        f.write(delimiter.join(entry)+"\n")
        notebook_to_xls(filename=filename)
    return
       
def notebook_to_xls(filename="notebook", delimiter = ';'):
    """
    Convert a .txt file to a .xls spreadsheet file.
    
    - filename: Name of the .txt file to convert.
    - delimiter: The delimiter must match notebook().
    """
    boldblue_fmt = xlwt.easyxf('font: color-index blue, bold on')
    bold_fmt = xlwt.easyxf('font: bold on')
    with open(filename+".txt", 'r+') as f:
        row_list = []
        for row in f:
            row_list.append(row.split(delimiter))
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet1')
        for i, row in enumerate(row_list):
            for j, item in enumerate(row):
                if row[0]!="":
                    if j < 2:
                        fmt = boldblue_fmt
                    else:
                        fmt = bold_fmt
                else:
                    fmt=xlwt.easyxf("")
                worksheet.write(i, j, item, fmt)
                
    try:
        workbook.save(filename + '.xls')
    except IOError:
        print "Close notebook.xls to update."
    return


def orange(start, stop, step):
    """
    Same as numpy.arange with one extra point.
    orange stands for optimal range. 
    May occasional return two extra points because of float additions (happened to me once.)    
    """
    return np.arange(start, stop+step, step)
  

def require_comments(*args):
    """
    Force user to flag a comment when using %irun.
    An error will be raised if one of the arguments is not found in the flags.
    The whole process will be skipped if 'skip' is in the arguments.
    """
    if "skip" not in sys.argv:
        for required_comment in args:
            if required_comment not in " ".join(sys.argv):
                raise LabMasterError, "You forgot to write "+required_comment+" in flags. Shame."
    return
    
    
def save_experiment(lab, params, experiment, ID, error_string):
    """
    Save info about scan under experiment/, such as:
    * Time launched, time ended, total duration.
    * Errors raised during sweep if any.
    * Connected instruments.
    * Description of the sweep.
    * Experiment module source code.
    
    - lab: Lab instance used in scan.
    - params: Params instance used in scan.
    - experiment: Module from experiments folder used in scan.
    - ID: Number indicated after the date in file name.
    - error_string: Error message to save.
                    If error_string is 'first_time', will create a new file, save the launch time only.
    """
    time_launched_string = "Time launched:  "
    datetime_format = "%Y-%b-%d %H:%M:%S"
    try:
        for saving_loc in saving_folders():
            filename = saving_loc+"experiment/"+today()+"/"+nfu.filename_format(today(), ID)+".txt"
            if error_string == "first_time":
                ## This is the first call to save_experiment().
                with open(filename, "a") as f:    
                    ## Write time launched.
                    f.write(time_launched_string+datetime.datetime.now().strftime(datetime_format)+"\n")
            else:
                ## This is the second (and last) call to save_experiment(). 
                with open(filename, "r") as f:    
                    ## Get time launched from the heading of the file.
                    contents = f.read()
                    time_launched = datetime.datetime.strptime(contents.split(time_launched_string)[-1].split("\n")[0], datetime_format)
                with open(filename, "a") as f:     
                    ## Write a whole bunch of useful stuff here.
                    time_ended = datetime.datetime.now().replace(microsecond=0)
                    f.write("Time ended:     "+time_ended.strftime(datetime_format)+"\n")
                    f.write("Total duration: "+str(time_ended-time_launched)+"\n\n")
                    f.write(error_string+"\n\n")
                    f.write("### "+str(lab)+"\n\n")
                    f.write("### Scheduled run \n"+str(params)+"\n")
                    f.write("### Experiment: "+experiment.__name__+".py\n"+inspect.getsource(experiment))
    except:
        print "save_experiment() failed. ", sys.exc_info()[0].__name__+":",  sys.exc_info()[1]
    return
    
def save_params(params, ID):
    """ 
    Save params instance with pickle under saved/params/ folder.
    Extract them with ease using the load_params() function.
    
    Input
    - params: Params instance.
    - ID: Number indicated after the date in file name.
    """
    try:
        for saving_loc in nfu.saving_folders():
            filename = saving_loc+"params/"+today()+"/"+nfu.filename_format(today(), ID)[:-3]+".pickle"
            with open(filename, "wb") as f:
                pickle.dump(params, f, pickle.HIGHEST_PROTOCOL) # Pickle using the highest protocol available.
    except:
        print "save_params() failed."
    return


def save_script(ID):
    """
    Copy the script launched by %irun to script/
    
    - ID: Number indicated after the date in file name.
    """
    try:
        for saving_loc in saving_folders():
            new_filename = saving_loc+"script/"+today()+"/"+nfu.filename_format(today(), ID)+".py"
            ## Copy a file.
            shutil.copy(nfu.get_script_filename(), new_filename)     
    except:
        print "save_script() failed. ", sys.exc_info()[0].__name__+":",  sys.exc_info()[1]
    return
    
def save_sweep(params, data, ID):
    """
    Convert parameter values and data array into a numpy dtype array. Saved to sweep/ folder.
    
    - data: Numpy array to be saved.
    - params: Params instance.
    - ID: Number indicated after the date in file name.
    """
    try:
        for saving_loc in saving_folders():
            filename = saving_loc+"sweep/"+today()+"/"+nfu.filename_format(today(), ID)
            ## An entry in the output array is dedicated to data. Access using 'DATA'.
            sweep_contents = [data]
            dtype_list = [('DATA', (data.dtype, data.shape))]
            ## An entry in the output array is dedicated to sweep dims. Access using 'SWEEPS'.
            sweep_dims = np.array([param.name+'='+str(param.sweep_dim) for param in params.get_sweeps()])
            sweep_contents += [sweep_dims]
            dtype_list += [('SWEEPS', (sweep_dims.dtype,sweep_dims.shape))]
            for param in params.get_sweeps(): 
                if not isinstance(param.value, np.ndarray): 
                    ## Convert lists to numpy arrays.
                    value = np.array(param.value)
                else:
                    value = param.value
                dtype_list += [(param.name, (value.dtype, value.shape))]
                sweep_contents += [value]
            for param in params.get_constants():
                ## Convert constants to numpy format.
                value = np.array(param.value)
                dtype_list += [(param.name, value.dtype)]
                sweep_contents += [value]
            ## Declare the sweep numpy dtype array.
            sweep = np.array([tuple(sweep_contents)], dtype=np.dtype(dtype_list))
            ## Get rid of an extra useless dimension.
            sweep = np.squeeze(sweep) 
            ## Save the result.
            np.save(filename, sweep)
    except:
        print "save_sweep() failed. ", sys.exc_info()[0].__name__+":",  sys.exc_info()[1]   
    return

def save_fig(fig, ID, ext="pdf"):
    """
    Save matplotlib figure to fig/
    
    - fig: Matplotlib figure instance.
    - ID: Number indicated after the date in file name.
    - ext: Extension of the file to save. Supported formats: emf, eps, pdf, png, ps, raw, rgba, svg, svgz.
    """
    if fig != None:
        try:
            for saving_loc in saving_folders():
                fig.savefig(saving_loc+"fig/"+today()+"/"+nfu.filename_format(today(), ID)+"."+ext)
        except:
            print "save_fig() failed. ", sys.exc_info()[0].__name__+":",  sys.exc_info()[1]
    return 
    

def send_email(recipient, add_subject="", add_msg=""):
    """
    Send an email message.
    
    - recipient: Email addresses of recipients (can be a list of emails)
    - add_subject: Text to append to the email subject.
    - add_msg: Text to append to the message.
    """
    try:
        user = 'my.goto.remote.email.2016@gmail.com'
        pwd = 'useless_password_here'

        ltime = time.localtime()
        fin_time = str(ltime[3]).zfill(2)+':'+str(ltime[4]).zfill(2)+', '+str(ltime[2])+'/'+str(ltime[1])

        subject = nfu.get_script_filename()[:3] + ' finished at ' + fin_time
        
        gmail_user = user
        gmail_pwd = pwd
        FROM = user
        TO = recipient if type(recipient) is list else [recipient]
        SUBJECT = subject+add_subject

        TEXT = error_manager(as_string=True)+"\n"
        
        
        ### Prepare actual message
        message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message+add_msg)
        server.close()
    except:
        print "send_email() failed. ", sys.exc_info()[0].__name__+":",  sys.exc_info()[1]
    return


def show_visa():
    """
    Print a list of connected VISA instruments.
    """
    rm = visa.ResourceManager()
    for name, res in rm.list_resources_info().items():
        print name
    return 
    
    
    
    
    
    
    
    
    
  



























  

## EASTER EGGS!
from not_for_user import hack_time, tea

