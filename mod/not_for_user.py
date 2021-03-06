"""
Functions for the internal processes of LabMaster.
"""
__author__ =  "Laurent Bergeron <laurent.bergeron4@gmail.com>"


class LabMasterError(Exception):
    """ Error of this type will be raised if LabMaster detects something wrong. """
    pass

## Base modules
import sys
import os 
import numpy as np
import matplotlib.pyplot as plt
import glob             ## Use * in file handling
import time             ## Pause script with time.sleep
import timeit           ## Better timer than time
import inspect          ## Retrieve information on python objects
import linecache        ## Required before some inspect functions.
import datetime         ## Includes datetime objects to handle dates.
import types            ## better type handling
## Homemade modules
from . import plotting
from .units import *

  
def auto_unit(value, unit, decimal=None):
    """ 
    Return value and unit as a compact string with automatic prefix. Ex: (50e9, "Hz") will output "50 GHz". 
    
    - value: Value of the thing.
    - Unit: Unit of the value.
    - decimal: Force a number of decimals.
    """
    ## Case if value is a string.
    if isinstance(value, str):
        return "'"+str(value)+"'"
        
    ## Case if value is None.
    if isinstance(value, type(None)):
        return "N/A"

    value = float(str(value)) ## Gets rid of awful Python decimals.
    if value == 0:
        ## don't want to deal with 0
        return "0 "+unit 
    try:
        ## exponent of value (scientific notation) rounded down to a multiple of 3.
        exp = int(np.floor(np.log10(abs(value))/3.0))*3 
        ## index in prefix list.
        index = exp//3+3
        
        if 0 <= index < 7:
            prefix = ["n", "u", "m", "", "k", "M", "G"][index]
        else:
            ## needs to be done to avoid negative indexes. pico is not giga.
            raise IndexError 
            
        if unit=="s":
            ## Special case for seconds.
            if value < 1:
                ## update value to account for prefix
                value_out = value*(10**(-exp)) 
            else:
                ## Do not update value (kilo seconds are a weird.)
                value_out = value
                prefix = ""
        else:
            ## update value to account for prefix
            value_out = value*(10**(-exp)) 
        
        if decimal:
            str_fmt = "%0."+str(decimal)+"f"
        else:
            if float("%s"%(value_out))%1>0:
                ## with decimals
                str_fmt = "%s" 
            else:
                ## without decimals
                str_fmt = "%i" 
       
        result = str_fmt%(value_out)+" "+prefix+unit
    except:
        ## if something goes wrong, return this simple format.
        result = str(value)+" "+unit
    
    ## Remove space at the end if it ends with a space.
    if result[-1]==' ':
        result = result[:-1]
    return result
    
def create_todays_folder():
    """ Create those folders if they don't exist. """
    for saving_loc in saving_folders():
        for section in ["experiment","fig","script","params","sweep","custom"]:
            folder_name = saving_loc+"/"+section+"/"+datetime.date.today().strftime("%Y-%m-%d")
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
    return 
    
    
def detect_experiment_ID():
    """ Read the maximum ID from files under experiment/. Add one to this result and return it as a string with padded zeros if ID < 10000. """
    date = today()
    main_saving_loc = saving_folders()[0]
    prefix =main_saving_loc+"experiment/"+date+"/"+date+"_"
    ## Two purges to get a list of IDs in folder.
    ## 1st purge: get .txt files with correct prefix.
    first_purge = [filename[len(prefix):-4].split("_")[0] for filename in glob.glob(prefix+"*.txt")] 
    second_purge = []
    for x in first_purge:
        try:
            ## 2nd purge: thing between last '_' and .txt has to be castable into an int.
            second_purge.append(int(x)) 
        except:
            pass
    if second_purge == []: 
        ## If no files survived the purge, create the first file of the folder.
        ID = "0000"
    else:
        ## If files were found, next ID will be one more than the maximum found. 
        ID = pad_ID(max(second_purge)+1)
    return ID
    
def err_msg():
    """ Beginning of LabMaster error message. Unfortunately Windows doesn't support ASCII color commands. """
    if os.name=="nt":
        return "---> ERROR: "
    else:
        return "\033[31mERROR: \033[0m"
        
def warn_msg():
    """ Beginning of LabMaster warning message. Unfortunately Windows doesn't support ASCII color commands. """
    if os.name=="nt":
        return "Warning: "
    else:
        return "\033[33mWarning: \033[0m"

    
def filename_format(date, ID, script_name=True):
    """Format of a filename. Be aware that loading previous files with LabMaster load functions will not work if you edit this function."""
    ## Be aware that loading previous files with LabMaster load functions will not work if you edit this function.
    return date+"_"+ID+"_"+script_name*get_script_filename()[:-3]

    
def get_notebook_line_format(delimiter=';'):
    """Get the format for notebook column names."""
    with open("notebook.txt","r") as f:
        lines = f.read().split("\n")
    i = len(lines)
    first_char = ""
    while first_char==delimiter or first_char=="":
        i -= 1
        try:
            first_char = lines[i][0]
        except IndexError:
            first_char = lines[i]
        if i < 0:
            break
    
    return lines[i]

def get_ready(lab, params):
    """ Stuff that has to be done in scan() before calling sweep(). """
    for param in params.get_constants():
        ## Initialize each constant.
        param.v = param.value
        param.i = 0
    for param in params.get_sweeps():
        ## Initialize each array to first element.
        param._update(0)
    for instrument in lab.get_objects():    
        ## Reset warnings
        if hasattr(instrument, "reset_warnings"):
            instrument.reset_warnings()
    return
    
def get_script_filename():
    """Get the name of the script that launched by %irun."""
    return sys.argv[0]
    

def lastID():
    """Return last saved ID."""
    return pad_ID(int(detect_experiment_ID())-1)
     
def remove_nan(array):
    return array[np.logical_not(np.isnan(array))]
    
def number_suffix(n):
    """ Returns the number suffix correponding to input n. """
    return ("st"*(n==1) + "nd"*(n==2) + "rd"*(n==3) + "th"*(n>3))
    
def pad_ID(ID):
    """ Return the input ID as a string padded with zeros """
    return str(ID).zfill(4) 
    
    
def plot_loaded_sequence_auto_label(lab):
    """Automatic prefix and multiplier for time labels in plot_loaded_sequence methods."""
    index=int(np.floor(np.log10(lab.total_duration)//3))
        
    if 0 <= (index+3) < 3:
        prefix = ["n", "u", "m"][index+3]
        c = 10**(-3*(index))
    else:
        prefix = ""
        c = 1
    return prefix, c
    
def positive_answer_N():
    """ List of valid positive answers if default is N (y/N)."""
    return ["y","Y","yes","Yes","YES","fuck yeah"]
    
def positive_answer_Y():
    """ List of valid positive answers if default is Y (Y/n)."""
    return positive_answer_N()+[""]
    
    
def run_experiment(lab, params, experiment, data, fig, file_ID, update_plot):
    """ 
    Launchs one experiment. This function is called by sweep(), which is called from scan().
   
    Procedure:
    1) Reset instructions related objects.
    2) Execute experiment.sequence().
    3) Load memory of instruments.
    4) Execute experiment.launch().
    5) Wait for end of experiment.
    6) Store the result of experiment.get_data() in data array.
    7) Update figure.
    """
    ## Reset everything instructions related from lab, as well as the instructions of each memory instrument.
    lab.reset_instructions()
    ## Run the sequence function from experiment module (custom function defined by user) which should fill the instructions attribute of instruments with memory.
    experiment.sequence(lab, params, fig, data, file_ID)
    ## Load memory of instruments who can't ping_pong.
    for instrument in lab.get_memory_instruments():
        instrument.load_memory()
    ## The starting pistol.
    experiment.launch(lab, params, fig, data, file_ID)
    ## Save time at which the experiment starts.
    lab.time_launched = timeit.default_timer()
    ## Wait for the end of experiment. 
    while (timeit.default_timer() < lab.time_launched + lab.total_duration + 20*ms): ## timeit.default_timer() worst case precision is roughly 20 ms. Should be microsecond precision on Windows.
        pass 
    ## Update data array.
    data[params.get_data_indices()] = experiment.get_data(lab, params, fig, data, file_ID)
    if update_plot and fig != None:
        ## Update figure.
        experiment.update_plot(lab, params, fig, data, file_ID)
        ## Update the display.
        plotting.plt.pause(1e-6)
    return 

def saving_folders():
    """Where to save all the juicy stuff."""
    subfolder = str(datetime.datetime.today().year)+"/LabMasterData/"
    return ["C:/Data/"+subfolder, "C:/Backup/"+subfolder]
    
def size_of_get_data_return(experiment):
    """
    In experiment .py file, read the get_data function source code to find the size of get_data output.
    Thus the special rules for experiment.get_data: there can only be one return, and return values have to be separated by comas.
    """
    ## clear this cache or inspect.getsource() will not used last updated experiment.
    linecache.clearcache() 
    ## get source code for experiment.get_data()
    source = inspect.getsource(experiment.get_data) 
    try:
        ## remove everything before "return"
        source = source.split("return")[1] 
        ## remove everything after the first "\n" encountered
        source = source.split("\n")[0] 
        ## remove comment
        source = source.split("#")[0] 
        ## split source in a list where each member was separated by a coma
        source = source.split(",") 
        size = len(source) 
    except:
        raise LabMasterError("Could not extract the number of return values of "+experiment.__name__+".get_data().\nSpecial rules for experiment.get_data: there can only be one return, and return values have to be separated by comas.\n Look at source code (nfu.size_of_get_data_return??) to understand how the return value is read.")
    return size
  
def sweep(lab, params, experiment, data, fig, current_sweep_dim, file_ID, update_plot):
    """ 
    Sweeps through all params the same way as for loops, starting with sweep_dim #1. 
    for ... : (sweep #1)
        for ... : (sweep_dim #2)
            .....................
                for ... : (sweep_dim #max)
    This function is recursive. The number of 'for' loops depends on input parameters.
    """


    if params.get_dimension()==0: 
        ## This happens if every parameter is a constant. Run experiment only once.
        run_experiment(lab, params, experiment, data, fig, file_ID, update_plot)
    else:
        current_sweeps = params.get_current_sweeps(current_sweep_dim)
        ## Here goes one 'for loop' corresponding to current sweep_dim
        for i in range(len(current_sweeps[0].value)): 
            ## Update the current value in array (_v attribute)
            update_params(current_sweeps, i) 
            
            if current_sweep_dim==params.get_dimension():
                ## If this is the last 'for' loop, it's time to run an experiment. End of recursion.
                run_experiment(lab, params, experiment, data, fig, file_ID, update_plot) 
            else:
                ## Else, go for another 'for' loop at the next sweep_dim.
                sweep(lab, params, experiment, data, fig, current_sweep_dim+1, file_ID, update_plot) 

    return

   
    
    
def today():
    """Format of the date in filename. Be aware that loading previous files with LabMaster load functions will not work if you edit this function."""
    ## Be aware that loading previous files with LabMaster load functions will not work if you edit this function.    
    return datetime.date.today().strftime("%Y-%m-%d")

def update_params(swept_params, i):
    """ Updates the attribute _v (current value) of the parameters that are swept to their ith value. """
    for param in swept_params:
        param._update(i)
    return
    


def zeros(params, experiment):
    """ 
    Initializes data to NaNs. Size of array will depend on dimension of sweep, lenght of parameter values, and size of get_data return. 
    dim 1 is sweep_dim #1, dim 2 is sweep_dim #2 and so on.
    """
    ## dimension of the sweep
    dimension = params.get_dimension()
    ## Shape of the array depends on the length of parameters.
    array_shape = [len(params.get_current_sweeps(i)[0].value)  for i in range(1,dimension+1) ]
    
    ## size of the get_data output.
    get_data_size =  size_of_get_data_return(experiment)
    if get_data_size > 1:
        ## Add a dimension if get_data has multiple return values.
        array_shape.append(get_data_size)
        
    if len(array_shape)==0:
        ## Only one element in the data array.
        data = np.zeros(1)
    else:
        data = np.zeros(shape=array_shape)
    
    ## Initialize all data elements to NaNs (NaNs are not plotted on matplotlib figures)
    data[:] = np.nan

    return data




def tea():
    """Says Eddie the computer."""
    print("You ordered: tea.\nPlease wait will the Nutrimatic Drinks Dispenser prepares your: tea.")
    for i in range(3):
        print("."*(i+1))
        time.sleep(1)
    time.sleep(2)
    for i in range(5000):
        print("."*(i%500 +1))
    raise SystemError("You are an ignorant monkey.")
    return


def hack_time():
    """Hackerman is in control here."""
    try:
        import msvcrt
    except ImportError:
        raise LabMasterError("Hacking time is not compatible with your system.")
       
    yes = "\t[YES]\t NO "
    no = "\t YES \t[NO]"
    yes_or_no = yes
    print("\n\n\tYOU'RE ABOUT \n\tTO HACK TIME,\n\tARE YOU SURE?\n")
    sys.stdout.write("%s\r" % yes )
    sys.stdout.flush()
    while True:
        time.sleep(0.01)
        if msvcrt.kbhit():
            pressed = msvcrt.getch()
            if pressed=='\xe0':
                keycode = msvcrt.getch()
                if keycode=='M':
                    yes_or_no = no
                    sys.stdout.write("%s\r" % no )
                    sys.stdout.flush()
                elif keycode=='K':
                    yes_or_no = yes
                    sys.stdout.write("%s\r" % yes )
                    sys.stdout.flush()
            elif pressed=="\r":
                if yes_or_no==yes:
                    print("\n\n")
                    for i in range(10000):
                        N = ((i//1000+1)%3+1)
                        sys.stdout.write("    HACKING TIME"+"."*N+" "*(3-N)+"\t\t\tYEARS HACKED: "+str(int(np.exp(i/800.0)))+"\r")
                        sys.stdout.flush()
                        time.sleep(0.001)
                    sys.stdout.write(" "*100+"\r")
                    sys.stdout.flush()
                    for i in range(6):
                        sys.stdout.write("                                 \r")
                        sys.stdout.flush()
                        time.sleep(0.5)
                        sys.stdout.write("    ERROR! HACKING TOO MUCH TIME!\r")
                        sys.stdout.flush()
                        time.sleep(0.5)
                    print("\n\n\n    GOOD LUCK OUT THERE. WATCH OUT FOR THE LASER RAPTORS.")
                    break
                elif yes_or_no==no:
                    print("\n\nWHAT?? YOU ARE A CHICKEN.")
                    break
    return