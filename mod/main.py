"""
Contains all the functions callable from Ipython interface when using '%run _launch.ipy'.

Please read HTML for more info.
"""
__author__ = "Laurent Bergeron, <laurent.bergeron4@gmail.com>"
__version__ = "1.2"   


# Base modules
import sys
import os 
import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as cst
import time 
import timeit
import datetime
import types # for better type handling
import pickle # for saving and loading any instance from python into a .pickle file
import inspect # retrieve information on python objects
import shutil # high-level system operation
from pydoc import help # help function for user
    
# Homemade modules
import not_for_user as nfu
from not_for_user import LabMasterError, today
import classes
import plotting
from instruments import *
from units import *

def available_instruments():
    """
    Return a dictionnary containing all available instruments. This dictionnary doesn't need to be updated from station to station, just fill it up as you add more instruments.
    
    An entry in the dictionnary must be written as shown below:
        key : [list of arguments] 
    where key is instrument name, and [list of arguments] is as follows:
    [class, (optional arguments,), {optional key arguments}]
    
    As you can see, (optional arguments,) has to be a tuple, so don't forget the coma before closing the parenthesis.
                    {optional key arguments} has to be a dictionnary.

    When adding a new instrument to the program, you need to update this list (and code a new instrument class if needed).
    
    It's possible to connect to a generic VISA instrument with no specific class, more info in Lab.add_instrument() documentation.
    """
    ### Update this dictionnary when adding a new instrument or changing connexion settings.
    
    #    name                  class                optional arguments                             optional key arguments
    d = {"awg":             [  Awg,                 ("PXI13::0::0::INSTR",),                        {}  ],
         "lockin":          [  Lockin,              ("GPIB0::12::INSTR",),                          {}  ],
         "pb":              [  Pulse_blaster_usb,   (),                                             {}  ],
         "laser":           [  Laser,               ("USB0::0x1313::0x804A::M00243388::INSTR",),    {}  ],
         "sig_gen":         [  Signal_generator,    ("GPIB0::19::INSTR",),                          {}  ],
         "sig_gen_srs":     [  Signal_generator_srs,("GPIB0::3::INSTR",),                           {}  ],
         "wavemeter":       [  Wavemeter,           (3,),                                           {}  ],
         "usb_counter":     [  Usb_counter,         (0,),                                           {}  ]
         }

    return d

def notebook(*args):
    delimiter = ";"
    date = nfu.today()
    ID = nfu.detect_experiment_ID()
    script_name = nfu.get_script_filename()
    column_name = [script_name, date, "ID"] + [""]*len(args) + ["comment"]
    entry       = ["",          "",   ID] +   [""]*len(args) + [" ".join(sys.argv[1:])]
    for i, arg in enumerate(args):
        column_name[i+3], entry[i+3] = arg.split(delimiter)
    line_format = delimiter.join(column_name)
    with open("notebook.txt", "a") as f:
        if line_format==nfu.get_notebook_line_format(delimiter=delimiter):
            pass
        else:
            f.write(line_format+"\n")
        f.write(delimiter.join(entry)+"\n")
    return
        
        
    
def scan(lab, params, experiment, quiet=False, show_plot=True, no_plot=False):
    """
    The holy grail of Lab-Master.
    Scan parameters value attribute in the order imposed by their sweep_ID.
    For each point in scan, run an experiment as dicted by experiment module.
    Saves everything under /saved.
    Animated plotting available.
    
    Input
    - lab: Lab instance with required instruments connected.
    - params: Params instance with required parameters ready for scan.
    - experiment: module from experiments folder, will rule what is going on during experiment.
    - quiet: If True, won't print run and won't ask user if everything is ok. Enable this for overnight runs or if you are overconfident.
    """
    
    # Check if inputs are conform to a bunch of restrictions
    check_params(params, no_plot)
    check_experiment(experiment)
    check_lab(lab)
    
    if quiet: # No time for questions.
        pass
    else:
        print "--------------------------------------------\n", experiment.__name__, "\n--------------------------------------------" 
        print params   # Print the future run.
        if raw_input("Is this correct? [Y/n]") not in nfu.positive_answer_Y():
            raise KeyboardInterrupt

    # data is an array full of zeros matching good dimensions imposed by params. dim 1 is sweep_ID #1, dim 2 is sweep_ID #2 and so on.
    data = nfu.zeros(params, experiment)
    # Create folders for today if they don't exist
    nfu.create_todays_folder()
    # Create a figure object.
    if not no_plot:
        fig = experiment.create_plot(params, data)
    else:
        fig = None
    # ID is the number indicated after the date in file names.
    ID = nfu.detect_experiment_ID() # returns the current max ID found in saved/experiment/ folder, plus one (result as a string)
    print "ID:",ID,"\n"
    # Save what we know about the experiment so far in saved/experiment/ folder. 
    save_experiment(None, None, None, ID, "first_time")
    try:
        # Stuff that needs to be done before the scan.
        nfu.get_ready(lab, params)
        # Call the start function of experiment module
        experiment.start(lab, params)
        # Start the sweep! data will be filled with science
        nfu.sweep(lab, params, experiment, data, fig, 1, show_plot)
        # Call the end function of experiment module
        experiment.end(lab, params)
    except:
        # On any error catched, print a simplified version of traceback to saved/experiment/.
        save_experiment(lab, params, experiment, ID, error_manager(as_string=True, all=True))
        raise
    finally:
        # Call the abort method of each instrument connected to the Lab instance.
        lab.abort_all()
        # Save params in saved/params/ folder. 
        save_params(params, ID)
        # Save data as numpy array in saved/data/ folder, and as text in saved/datatxt/ if dimension of scan < 2.
        save_data(data, ID)
        # Save fig as pdf in saved/fig/ folder
        save_fig(fig, ID)
    # Save the rest about experiment in saved/experiment/ folder.         
    save_experiment(lab, params, experiment, ID, "Scan successful.")
    # Update the figure for the first time if show_plot is False
    if not show_plot:
        experiment.plot(fig, params, data)
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

def check_params(params, no_plot):
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
         
    # Sweep checks
    for i in range(1,params.get_dimension()+1):
        if params.get_current_sweeps(i)==[]:
            raise LabMasterError, "No sweeps detected at sweep_ID #"+str(i)+"."
        lengths_by_ID = [len(x.value) for x in params.get_current_sweeps(i)]
        for l in range(len(lengths_by_ID)):
            if not lengths_by_ID[l] == lengths_by_ID[l-1]:
                raise LabMasterError, "Arrays programmed for sweep ID #"+str(i)+" have different lenghts."  
    
    
    # Plotting warnings
    if not no_plot:
        pass

    return

def clean_start(namespace, close_figs=False):
    """
    Reset all Lab and Params instances from namespace.
    """
    if close_figs:
        plt.close("all")
    try:
        namespace["_INTERACTIVE_START_"]
    except KeyError:
        raise LabMasterError, "Scripts must be run interactively (-i flag) to prevent losing connection with instruments."
    
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
                        raise LabMasterError, "Lab instance "+key+" is unable to close instruments. \nPlease close instrument drivers before the environnement reset caused by launch.ipy.\n\n\n"
        except AttributeError:
            pass

    del key, value
    return
    
def error_manager(as_string=False, all=False):
    """
    Get last raised error from sys module. 
    If it's a LabMasterError or one of its subclasses, print the error message in a minimalistic way. To get full traceback, run %tb in Ipython.
    Same for KeyboardInterrupt.
    For every other type of error, raise it once again.
    
    Input
    - as_string: If as_string is True, return the error message as a string.
                 If as_string is False, just print it to console.
    - all: If all is True, stop traceback and return an error message for every type of error.

    Output
    - The error message as a string, if as_string is True
    """
    error_type = sys.exc_info()[0]
    error_value = sys.exc_info()[1]
    if error_type is LabMasterError:
        message = nfu.err_msg()+ str(error_value)+ "\n"
    elif LabMasterError in error_type.__bases__:
        message = error_type.__name__+": "+ str(error_value)+ "\n"
    elif error_type is KeyboardInterrupt:
        message = "Experiment aborted.\n"
    else:
        if all:
            message = error_type.__name__+": "+str(error_value)
        else:
            raise
    sys.last_type, sys.last_value, sys.last_traceback = sys.exc_info()
    if as_string:
        return message
    else:
        print message+ "%tb for full traceback\n"*(error_type is not KeyboardInterrupt)
    return
    
def help_please():
    """
    Some advice on how to get advice.
    """
    print "Use ? after an object to get documentation."
    print "Python advice: Type help() for interactive help, or help(object) for help about object."
    print "Lab-Master users manual is located under doc/_Lab-Master_users-manual_"
    print "For a more detailed doc of the source code, you will find HTML help under doc/_Lab-Master_html_"
    return
    
    
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
    return np.load("saved/data/"+nfu.filename_format(date, ID)+".npy")
    
def load_data_txt(date, ID):
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
    return np.loadtxt("saved/data_txt/"+nfu.filename_format(date, ID)+".txt")

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
    filename = "saved/params/"+nfu.filename_format(date, ID)+".pickle"
    with open(filename, "rb") as f:
        params = pickle.load(f)
    if output==None:
        return params
    else:
        try:
            return params.__dict__[output]
        except KeyError:
            raise nfu.LabMasterError, "Requested output not found in params attributes."
    return
    

def pickle_save(filename, thing):
    """
    Save a python object to filename.pickle under saved/pickle/ folder. Useful to save params. 
    Do not save lab with this, because instruments will not connect when calling pickle_load().

    Input
    - filename: string to be used as file name. The "saved/pickle/" folder and ".pickle" extension are added automatically. Avoid spaces (as always).
    - thing: python object to be saved.
    """
    if isinstance(thing, classes.Lab):
        raise LabMasterError, "Can't save instrument connexion in the pickle file. It's thus pointless to save a Lab instance."
    if not os.path.exists("saved/pickle"):
        os.makedirs("saved/pickle")
    if os.path.isfile("saved/pickle/"+filename+".pickle"):
        if raw_input(nfu.warn_msg()+"Overwriting "+filename+".pickle? [y/N]") not in nfu.positive_answer_N():
            print "not saved\n"
            return
    with open("saved/pickle/"+filename+".pickle", "wb") as f:
        pickle.dump(thing, f, pickle.HIGHEST_PROTOCOL) # Pickle using the highest protocol available.
        print "saved to saved/pickle/"+filename+".pickle\n"
    return

def pickle_load(filename):
    """
    Return a python object from filename.pickle under saved/pickle/ folder. Useful to load previously saved params.
    Do not load lab with this, because instruments will not connect.
    
    Input
    - filename: Name of the file to load. The "saved/pickle/" folder and ".pickle" extension are added automatically.
    """
    try:
        with open("saved/pickle/"+filename+".pickle", "rb") as f:
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
    filename = "saved/data/"+nfu.filename_format("today", ID) # for the .npy file
    filenametxt = "saved/data_txt/"+nfu.filename_format("today", ID)+".txt" # for the .txt file
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
    filename = "saved/experiment/"+nfu.filename_format("today", ID)+".txt"
    with open(filename, "a") as f:    
        if error_string == "first_time":
            f.write("Time launched: "+datetime.datetime.now().strftime("%Y-%b-%d %H:%M'%S''")+"\n")
        else:
            f.write("Time ended:    "+datetime.datetime.now().strftime("%Y-%b-%d %H:%M'%S''")+"\n\n")
            f.write(error_string+"\n\n")
            f.write("### "+str(lab)+"\n\n")
            f.write("### Scheduled run \n"+str(params)+"\n")
            f.write("### Experiment: "+experiment.__name__+".py\n"+inspect.getsource(experiment))
    return

def save_params(params, ID):
    """ 
    Save params instance with pickle under saved/params/ folder.
    Extract them with ease using the load_params() function.
    
    Input
    - params: Params instance.
    - ID: Number indicated after the date in file name.
    """
    filename = "saved/params/"+nfu.filename_format("today", ID)+".pickle"
    with open(filename, "wb") as f:
        pickle.dump(params, f, pickle.HIGHEST_PROTOCOL) # Pickle using the highest protocol available.
    return

def save_script():
    """
    Copy script_filename to saved/script/
    Add flaged comments to the header of the copied script file and in notebook.txt
    The file ID will be one more than the maximum ID detected in saved/experiment/ folder.
    
    Input:
        script_filename: Name of the script to save. Use __file__ to get current file name.
    """
    nfu.create_todays_folder()
    ID = nfu.detect_experiment_ID()
    new_filename = "saved/script/"+nfu.filename_format("today", ID)+".py"
    shutil.copy(nfu.get_script_filename(), new_filename)     
    return

def save_fig(fig, ID, ext="pdf"):
    """
    Save matplotlib figure to saved/fig
    
    Input
    - fig: Matplotlib figure instance.
    - ID: Number indicated after the date in file name.
    - ext: Extension of the file to save. Supported formats: emf, eps, pdf, png, ps, raw, rgba, svg, svgz.
    """
    if fig != None:
        fig.savefig("saved/fig/"+nfu.filename_format("today", ID)+"."+ext)
    return 
    

    


