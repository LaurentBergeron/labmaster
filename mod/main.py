"""
Contains all the functions callable from Ipython interface when using '%run _launch.ipy'.

Please read HTML for more info.
"""
__author__ = "Laurent Bergeron, <laurent.bergeron4@gmail.com>, Camille Bowness <cbowness@sfu.ca>, Adam DeAbreu <adeabreu@sfu.ca>"
__version__ = "1.3"   


# Base modules
import sys
import os 
import glob
import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as cst
import time 
import timeit
import datetime
import importlib
import types # better type handling
import pickle # save and load any instance from python into a .pickle file
import inspect # retrieve information on python objects
import shutil # high-level system operation
import smtplib # SMTP protocol client (send_email)
import xlrd # .xlsx read
import xlwt # .xlsx write
from pydoc import help # help function for user
import visa


# Homemade modules
import not_for_user as nfu
from not_for_user import LabMasterError, today, lastID, auto_unit
import classes
from classes import Lab, Params
import plotting
import instruments
import available_instruments
from units import *


     
        
    
def scan(lab, params, experiment, fig=None, quiet=False, show_plot=True):
    """
    The holy grail of Lab-Master.
    Scan parameters value attribute in the order imposed by their sweep_ID.
    For each point in scan, run an experiment as dicted by experiment module.
    Saves everything under /saved.
    Animated plotting available.
    TODO describe the error management.
    Input
    - lab: Lab instance with required instruments connected.
    - params: Params instance with required parameters ready for scan.
    - experiment: module from experiments folder, will rule what is going on during experiment.
    - quiet: If True, won't print run and won't ask user if everything is ok. Enable this for overnight runs or if you are overconfident.
    """
    output = None    
    ## Check if inputs are conform to a bunch of restrictions
    check_params(params)
    check_experiment(experiment)
    check_lab(lab)    
    
    print "--------------------------------------------\n", experiment.__name__, "\n--------------------------------------------" 
    print params   ## Print the future run.
    if quiet: ## No time for questions.
        pass
    else:
        if raw_input("Is this correct? [Y/n]") not in nfu.positive_answer_Y():
            raise KeyboardInterrupt

    ## data is an array full of zeros matching good dimensions imposed by params. dim 1 is sweep_ID #1, dim 2 is sweep_ID #2 and so on.
    data = nfu.zeros(params, experiment)
    ## Create folders for today if they don't exist
    nfu.create_todays_folder()
    ## Create a figure object.
    if fig != None:
        experiment.create_plot(fig, params, data)
    ## ID is the number indicated after the date in file names.
    ID = nfu.detect_experiment_ID() # returns the current max ID found in saved/experiment/ folder, plus one (result as a string)
    print "ID:",ID,"\n"

    try:
        ## Save what we know about the experiment so far in saved/experiment/ folder. 
        save_experiment(None, None, None, ID, "first_time")
        ## Stuff that needs to be done before the scan.
        nfu.get_ready(lab, params)
        ## Call the start function of experiment module
        experiment.start(lab, params)
        ## Start the sweep! data will be filled with science
        nfu.sweep(lab, params, experiment, data, fig, 1, show_plot)
        ## Call the end function of experiment module
        experiment.end(lab, params)
    finally:
        ################ MAKE SURE EACH STATEMENT HERE IS ERROR PROOF ################
        ## Call the abort method of each instrument connected to the Lab instance.
        lab.abort_all()
        ## Save a simplified version of traceback to saved/experiment/.
        save_experiment(lab, params, experiment, ID, error_manager(as_string=True)+"\n")
        ## Save params in saved/params/ folder. 
        save_params(params, ID)
        ## Save data as numpy array in saved/data/ folder, and as text in saved/datatxt/ if dimension of scan < 2.
        save_data(data, ID)
        ## Save fig as pdf in saved/fig/ folder
        save_fig(fig, ID)
        ## Save the script that executed scan.
        save_script()
        ## Update the figure one last time.
        if fig!= None and show_plot==False:
            try:
                experiment.update_plot(fig, params, data)
            except:
                print "update_plot from "+experiment.__name__+" failed", sys.exc_info()[0].__name__+":",  sys.exc_info()[1]
            
        print "\nsaved as",ID,"\n"

    return



def check_experiment(experiment):
    """
    Check if experiment module is conform to the rules.
    
    Rules
    - Must have functions named "launch", "get_data", "sequence", "begin" and "end". If function is not found, an empty function will replace it, so no error will be raised.
    
    Plotting rules
    - If plotting is enabled and get_data returns more than one value, the scan has to be 1D.
    
    Input
    - experiment: Module loaded to be used as experiment in a scan function.
    - dimension: Dimension of scan. You can get this value directly with params.get_dimension().
    """
    # A very boring function
    def empty(a, b):
        """ Will replace missing functions in the experiment module. """
        return 0 # has to be zero for get_data()

    # Check experiment attributes for needed function names.
    if not hasattr(experiment, "launch"):
        print nfu.warn_msg()+experiment.__name__+" has no function named launch. Not very useful."
        experiment.launch = empty
    if not hasattr(experiment, "get_data"):
        experiment.launch = empty
    if not hasattr(experiment, "sequence"):
        experiment.sequence = empty
    if not hasattr(experiment, "start"):
        experiment.start = empty
    if not hasattr(experiment, "end"):
        experiment.end = empty
    if not hasattr(experiment, "create_plot"):
        experiment.create_plot = plotting.create_plot_auto
    if not hasattr(experiment, "update_plot"):
        experiment.update_plot = plotting.update_plot_auto
    
    return 


def check_lab(lab):
    """
    Check if every instrument is conform to the rules.
    
    Rules
    - Every instrument needs a close() method.
    - If an instrument has memory, it needs a load_memory() method.
    - If an instrument is set to double buffering, it needs a load_memory_ping_pong() method.
    
    Input
    - lab: a Lab instance.
    """
    for instrument in lab.get_classes():
        if not hasattr(instrument, "load_memory") and instrument.use_memory:
            raise LabMasterError, instrument.name+" needs a load_memory() method."
        if not hasattr(instrument, "load_memory_ping_pong") and instrument.is_ping_pong:
            raise LabMasterError, instrument.name+" needs a load_memory_ping_pong() method."
        if not hasattr(instrument, "close"):
            raise LabMasterError, instrument.name+" needs a close() method."
        if not hasattr(instrument, "abort"):
            raise LabMasterError, instrument.name+" needs a abort() method."
    return

def check_params(params):
    """
    Checks if every parameter is conform to the rules.
    
    Rules
    - params can't be empty of parameters.
    - Every parameter has to be a Parameter instance.
    - The attribute sweep_ID must be an int and > 0.
    - Parameter value can't be an empty array or empty list.
    - There can be no empty sweeps on a sweep_ID smaller than the maximum sweep_ID.
    - Arrays scheduled for the same sweep_ID must have the same length.
    
    Plotting rules
    - Sweep dimension can't be higher than two.
    - params.xaxis must be a valid parameter name.
    - params.xaxis can't refer to a constant.
    - If 2D plotting, params.yaxis must be a valid parameter name.
    - If 2D plotting, params.yaxis can't refer to a constant.
    - If 2D plotting, params.graph2Dtype must be a valid name.
    
    Input
    - params: a Params instance.
    """
    if params.get_classes()==[]:
        raise LabMasterError, "No parameters detected."
        
    # Single parameter attribute checks
    for key, param in params.get_items():   
        if not isinstance(param, classes.Parameter):
            raise LabMasterError, key+" should be a Parameter instance, instead of "+str(type(param))+"."   
        if not isinstance(param.sweep_ID, int):
            raise LabMasterError, key+".sweep_ID should be int type, instead of "+str(type(param.sweep_ID))+"."               
        if param.sweep_ID < 0:
            raise LabMasterError, key+".sweep_ID is < 0."
        if param.is_not_const():
            if len(param.value) < 1:
                raise LabMasterError, key+".value is an array or list with length zero."
            if len(param.value) > 1e6:
                print nfu.warn_msg()+param.name+" array is very large and takes a lot of memory. Consider using a smaller array."
    # Sweep checks
    for i in range(1,params.get_dimension()+1):
        if params.get_current_sweeps(i)==[]:
            raise LabMasterError, "No sweeps detected at sweep_ID #"+str(i)+"."
        lengths_by_ID = [len(x.value) for x in params.get_current_sweeps(i)]
        for l in range(len(lengths_by_ID)):
            if not lengths_by_ID[l] == lengths_by_ID[l-1]:
                raise LabMasterError, "Arrays programmed for sweep ID #"+str(i)+" have different lenghts."  
    
    
    # Plotting warnings

    return

def clean_start(namespace):
    """
    Reset all Lab instances from namespace (should be globals() most of the time).
    """
    
    ### Close connected instrument drivers
    for key, value in namespace.items():
        if key in ("Lab", "value"):
            continue
        if key[:1] == "_":
            continue
        try:
            if str(value.__class__).split(".")[-1] == "Lab":
                if len(value.get_classes())>0:
                    print "-> "+key+".close_all()"
                    number_of_failures = value.close_all()
                    if number_of_failures > 0:
                        raise LabMasterError, "Lab instance "+key+" is unable to close instruments.\nReset aborted. \nPlease close instrument drivers before the environnement reset caused by _reset_.ipy.\n\n\n"
        except AttributeError:
            pass

    del key, value
    return
    
def error_manager(as_string=False, all=True):
    """
    Get last raised error from sys module. 
    If it's a LabMasterError or one of its subclasses, print the error message in a minimalistic way. To get full traceback, run %tb in Ipython.
    Same for KeyboardInterrupt.
    For every other type of error, raise it once again.
    
    Input
    - as_string: If as_string is True, return the error message as a string.
                 If as_string is False, just print it to console.
    - all: If all is True, stop traceback and print an error message for every type of error.

    Output
    - The error message as a string, if as_string is True
    """
    error_type, error_value, error_traceback = sys.exc_info()
    if error_type == None:
        return "Scan successful."
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
            raise
    sys.last_type, sys.last_value, sys.last_traceback = error_type, error_value, error_traceback
    if as_string:
        out = message
    else:
        out = ""
        print message+ "\n%tb for full traceback\n"*(error_type is not KeyboardInterrupt)
    return out
    
def export_data(date, IDs, location, output, \
        data_manipulation = None, param_manipulation = None, popts_manipulation = None):
    """
    export data and params to a single file
    
    Input
    - date: Date from file name. Has to follow this datetime format: %Y_%m_%d
            %Y is year in four characters.
            %m is month in two characters.
            %d is day in two characters.
            Good format example: 2016_06_24
    - IDs: array of numbers indicated after the date in file name. Can be '0075' or 75
    - location: Directory in which files will be saved
    - output: file type of data, either 'npy' or 'txt'
    - data_manipulation: function to manipulate loaded data in a form to be saved with np.save or np.savetxt
            (see analyze_data.py)
    - param_manipulation: function to manipulate loaded param class into a numpy array to be saved with np.save or
            np.savetxt (see analyze_data.py)
    - popts_manipulation: function to manipulate loaded data and loaded param class to generate fit parameters
            (see analyze_data.py)
    """
    popts_ar = None 
    for i, ID in enumerate(IDs):
        print ID
        ID = str(ID).zfill(4)
        fig, data, params, popts = load_plot(date, ID)

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
            popts = popts_manipulation(data, params, fig)

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

def help_please():
    """
Use ? after an object to get documentation. With ?? you get source code.
Python advice: Type help() for interactive help, or help(object) for help about object.
Lab-Master users manual is located under doc/_Lab-Master_users-manual_
For a more detailed doc of the source code of Lab-Master, you will find HTML help under doc/_Lab-Master_html_"""
    print help_please.__doc__
    return

def last_data():
    return load_data(today(), lastID())
    
def last_datatxt():
    return load_datatxt(today(), lastID())
    
def last_params(output=None):
    return load_params(today(), lastID(), output=output)
    
def last_plot(experiment_name=None):
    return load_plot(today(), lastID(), experiment_name=experiment_name)
    
def load_data(date, ID):
    """
    Load data from a .npy file in saved/data/ folder. 
    
    Input
    - date: Date from file name. Has to follow this datetime format: %Y_%m_%d
            %Y is year in four characters.
            %m is month in two characters.
            %d is day in two characters.
            Good format example: 2016_06_24
    - ID: Number indicated after the date in file name.
    
    Output
    - the loaded numpy array.
    """
    file_format = nfu.filename_format(date, ID, script_name=False)
    try:
        matching_file = [filename for filename in glob.glob(nfu.saving_folder()+"data/"+date+"/*") if file_format in filename][0]
    except IndexError:
        raise LabMasterError, "Date or ID does not match any existing file."
    return np.load(matching_file)
    
def load_datatxt(date, ID):
    """
    Load data from a .txt file in saved/data_txt/ folder. 
    
    Input
    - date: Date from file name. Has to follow this datetime format: %Y_%m_%d
            %Y is year in four characters.
            %m is month in two characters.
            %d is day in two characters.
            Good format example: 2016_06_24
    - ID: Number indicated after the date in file name.
    
    Output
    - the loaded numpy array.
    """
    file_format = nfu.filename_format(date, ID, script_name=False)
    try:
        matching_file = [filename for filename in glob.glob(nfu.saving_folder()+"datatxt/"+date+"/*") if file_format in filename][0]
    except IndexError:
        try:
            size_of_data = load_data(date, ID).size
        except:
            size_of_data = 0
        if size_of_data > 2:
            raise LabMasterError, "No datatxt was collected for this experiment, dimension of data > 2."
        else:
            raise LabMasterError, "Date or ID does not match any existing file."
    return np.load(matching_file)

    
def load_params(date, ID, output=None):
    """
    Load params from a .pickle file in saved/params/ folder.
    
    Input
    - date: Date from file name. Has to follow this datetime format: %Y_%m_%d
            %Y is year in four characters.
            %m is month in two characters.
            %d is day in two characters.
            Good format example: 2016_06_24
    - ID: Number indicated after the date in file name.
    - output: If None, will return the whole params instance.
              If a string, will return the parameter from params with that name.

    Output
    - Either a Params instance or the specified Parameter instance, depending on output value.
    """
    file_format = nfu.filename_format(date, ID, script_name=False)
    try:
        matching_file = [filename for filename in glob.glob(nfu.saving_folder()+"params/"+date+"/*") if file_format in filename][0]
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
    try:
        if experiment_name==None:
            file_format = nfu.filename_format(date, ID, script_name=False)
            matching_file = [filename for filename in glob.glob(nfu.saving_folder()+"experiment/"+date+"/*") if file_format in filename][0]
            "Date or ID does not match any existing experiment file."
            with open(matching_file) as f:
                experiment_name = f.read().split("### Experiment: ")[-1].split("\n")[0][:-3]
        experiment = importlib.import_module(experiment_name)
    except ImportError, IndexError:
        print "Could not import experiment. Using auto plotting from plotting module."
        experiment = None
    if fig==None:
        fig = plt.figure()
    params = load_params(date, ID)
    data = load_data(date, ID)
    try:
        experiment.create_plot(fig, params, data)
        scan_out = experiment.update_plot(fig, params, data)
    except AttributeError:
        plotting.create_plot_auto(fig, params, data)
        plotting.update_plot_auto(fig, params, data)
        scan_out = None
    return fig, data, params, scan_out
    
def notebook(*args):
    delimiter = ";"
    date = nfu.today()
    ID = nfu.detect_experiment_ID()
    script_name = nfu.get_script_filename()
    column_name = [script_name, date, "ID"] + [""]*len(args) + ["comment"]
    entry       = ["",          "",   ID] +   [""]*len(args) + [" ".join(sys.argv[1:])]
    for i, arg in enumerate(args):
        column_name[i+3], entry[i+3] = arg.split(delimiter)
    line_format = delimiter.join(column_name)+delimiter
    with open("notebook.txt", "a") as f:
        if line_format==nfu.get_notebook_line_format(delimiter=delimiter):
            pass
        else:
            f.write("\n"+line_format+"\n")
        f.write(delimiter.join(entry)+"\n")
        notebook_to_xlsx()
    return
       
def notebook_to_xlsx(filename="notebook"):
    boldblue_fmt = xlwt.easyxf('font: color-index blue, bold on')
    bold_fmt = xlwt.easyxf('font: bold on')
    with open(filename+".txt", 'r+') as f:
        row_list = []
        for row in f:
            row_list.append(row.split(';'))
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
        workbook.save(filename + '.xlsx')
    except IOError:
        print "Close notebook.xlsx to update."
    return


def orange(start, stop, step):
    """ orange stands for omnipotent range """
    return np.arange(start, stop+step, step)

def pickle_save(filename, thing):
    """
    Save a python object to filename.pickle under saved/pickle/ folder. Useful to save params. 
    Do not save lab with this, because instruments will not connect when calling pickle_load().

    Input
    - filename: string to be used as file name. The "pickle/" folder and ".pickle" extension are added automatically. Avoid spaces (as always).
    - thing: python object to be saved.
    """
    if isinstance(thing, classes.Lab):
        raise LabMasterError, "Can't save instrument connexion in the pickle file. It's thus pointless to save a Lab instance."
    if not os.path.exists(nfu.saving_folder()+"pickle"):
        os.makedirs(nfu.saving_folder()+"pickle")
    if os.path.isfile(nfu.saving_folder()+"pickle/"+filename+".pickle"):
        if raw_input(nfu.warn_msg()+"Overwriting "+filename+".pickle? [y/N]") not in nfu.positive_answer_N():
            print "not saved\n"
            return
    with open(nfu.saving_folder()+"pickle/"+filename+".pickle", "wb") as f:
        pickle.dump(thing, f, pickle.HIGHEST_PROTOCOL) # Pickle using the highest protocol available.
        print "saved to saved/pickle/"+filename+".pickle\n"
    return

def pickle_load(filename):
    """
    Return a python object from filename.pickle under saved/pickle/ folder. Useful to load previously saved params.
    Do not load lab with this, because instruments will not connect.
    
    Input
    - filename: Name of the file to load. The "pickle/" folder and ".pickle" extension are added automatically.
    """
    try:
        with open(nfu.saving_folder()+"pickle/"+filename+".pickle", "rb") as f:
            thing = pickle.load(f)
            print "loaded from "+filename+".pickle"
    except IOError:
        raise LabMasterError, filename+".pickle does not exist in the saved/pickle/ folder."
    return thing
    
  

def require_comments(*args):
    if "skip" not in sys.argv:
        for required_comment in args:
            if required_comment not in " ".join(sys.argv):
                raise LabMasterError, "You forgot to write "+required_comment+" in flags. Shame."
    return
    
    
def save_data(data, ID):
    """
    Save precious data to a numpy file under saved/data/. If dimension of data is one or two, also save data to a txt file.
    
    Input
    - data: Numpy array to be saved.
    - ID: Number indicated after the date in file name.
    
    """
    try:
        filename = nfu.saving_folder()+"data/"+today()+"/"+nfu.filename_format(today(), ID) # for the .npy file
        filenametxt = nfu.saving_folder()+"data_txt/"+today()+"/"+nfu.filename_format(today(), ID)+".txt" # for the .txt file
        if isinstance(data, np.ndarray):
            np.save(filename, data) # always save a .npy file
            if data.ndim < 3:
                # if dimension of data is not higher than 2, save a .txt file
                np.savetxt(filenametxt, data)
            else:
                # if dimension of data is higher than 2, leave a message in the .txt file
                with open(filenametxt,"w") as f:
                    f.write("# Array dimension is > 2 thus numpy can't save it as a .txt file.")
        elif data==None:
            pass
        else:
             raise LabMasterError, "data is not a numpy array."
    except:
        print "save_data() failed; ", sys.exc_info()[0].__name__+":",  sys.exc_info()[1]
    return
    
    
def save_experiment(lab, params, experiment, ID, error_string):
    """
    Save info about scan under saved/experiment/, such as:
    - Time launched
    - Errors raised during sweep if any
    - Time ended
    - Connected instruments
    - Parameters
    - experiment .py file
    
    Input
    - lab: Lab instance used in scan.
    - params: Params instance used in scan.
    - experiment: Module from experiments folder used in scan.
    - ID: Number indicated after the date in file name.
    - error_string: Error message to save.
                    If error_string is "first_time", will create a new file, save the launch time and then skip the rest.
    """
    try:
        filename = nfu.saving_folder()+"experiment/"+today()+"/"+nfu.filename_format(today(), ID)+".txt"
        time_launched_string = "Time launched:  "
        time_ended_string    = "Time ended:     "
        datetime_format = "%Y-%b-%d %H:%M:%S"
        with open(filename, "a") as f:    
            if error_string == "first_time":
                f.write(time_launched_string+datetime.datetime.now().strftime(datetime_format)+"\n")
            else:
                f.write(time_ended_string+datetime.datetime.now().strftime(datetime_format)+"\n")
        if error_string != "first_time":
            with open(filename, "r") as f:    
                contents = f.read()
                time_launched = datetime.datetime.strptime(contents.split(time_launched_string)[-1].split("\n")[0], datetime_format)
                time_ended = datetime.datetime.strptime(contents.split(time_ended_string)[-1].split("\n")[0], datetime_format)
            with open(filename, "a") as f:     
                f.write("Total duration: "+str(time_ended-time_launched)+"\n\n")
                f.write(error_string+"\n\n")
                f.write("### "+str(lab)+"\n\n")
                f.write("### Scheduled run \n"+str(params)+"\n")
                f.write("### Experiment: "+experiment.__name__+".py\n"+inspect.getsource(experiment))
    except:
        print "save_experiment() failed; ", sys.exc_info()[0].__name__+":",  sys.exc_info()[1]
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
        filename = nfu.saving_folder()+"params/"+today()+"/"+nfu.filename_format(today(), ID)[:-3]+".pickle"
        with open(filename, "wb") as f:
            pickle.dump(params, f, pickle.HIGHEST_PROTOCOL) # Pickle using the highest protocol available.
    except:
        print "save_params() failed."
    return

def save_script():
    """
    Copy script_filename to saved/script/
    Add flaged comments to the header of the copied script file and in notebook.txt
    The file ID will be maximum ID detected in saved/experiment/ folder.
    
    Input:
        script_filename: Name of the script to save. Use __file__ to get current file name.
    """
    try:
        nfu.create_todays_folder()
        ID = nfu.pad_ID(int(nfu.detect_experiment_ID())-1)
        new_filename = nfu.saving_folder()+"script/"+today()+"/"+nfu.filename_format(today(), ID)+".py"
        shutil.copy(nfu.get_script_filename(), new_filename)     
    except:
        print "save_script() failed; ", sys.exc_info()[0].__name__+":",  sys.exc_info()[1]
    return

def save_fig(fig, ID, ext="pdf"):
    """
    Save matplotlib figure to saved/fig
    
    Input
    - fig: Matplotlib figure instance.
    - ID: Number indicated after the date in file name.
    - ext: Extension of the file to save. Supported formats: emf, eps, pdf, png, ps, raw, rgba, svg, svgz.
    """
    try:
        if fig != None:
            fig.savefig(nfu.saving_folder()+"fig/"+today()+"/"+nfu.filename_format(today(), ID)+"."+ext)
    except:
        print "save_fig() failed; ", sys.exc_info()[0].__name__+":",  sys.exc_info()[1]
    return 
    

def send_email(recipient, add_subject="", add_msg=""):
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
        print "send_email() failed; ", sys.exc_info()[0].__name__+":",  sys.exc_info()[1]
    return


def show_visa():
    rm = visa.ResourceManager()
    for name, res in rm.list_resources_info().items():
        print name
    return 

