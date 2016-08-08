"""
Contains functions not to be used by user, either because they are useless or dangerous! (most probably useless).
Functions you might possibly want to change: save_experiment, save_data, run_experiment, sweep. Proceed with care.
"""
__author__ =  "Laurent Bergeron <laurent.bergeron4@gmail.com>"


class LabMasterError(Exception):
    """ Error of this type will be raised if LabMaster detects something wrong. """
    pass

# Base modules
import sys
import os 
import glob
import numpy as np
import timeit
import time
import inspect
import datetime
import types
import linecache
# Homemade modules
import plotting

    
def sweep(lab, params, experiment, data, fig, current_sweep_ID, show_plot):
    """ 
    Sweeps through all params the same way as for loops, starting with sweep_ID #1. 
    for ... : (sweep #1)
        for ... : (sweep_ID #2)
            .....................
                for ... : (sweep_ID #max)
    This function is recursive, because the number of 'for' loops depends on input parameters.. 
    """


    if params.get_dimension()==0: # This happens if every parameter is a constant.
        run_experiment(lab, params, experiment, data, fig, show_plot)
    else:
        current_sweeps = params.get_current_sweeps(current_sweep_ID)
        for i in range(len(current_sweeps[0].value)): # Here goes one 'for loop' corresponding to current sweep_ID
            update_params(current_sweeps, i) # Update the current value in array (_v attribute)
            
            if current_sweep_ID==params.get_dimension():
                run_experiment(lab, params, experiment, data, fig, show_plot) # If this is the last 'for loop', it's time to run an experiment. End of recursion.

            else:
                sweep(lab, params, experiment, data, fig, current_sweep_ID+1, show_plot) # Else, go for another 'for loop' at the next sweep_ID.

    return
    
def run_experiment(lab, params, experiment, data, fig, show_plot):
    """ 
    Launchs one experiment. This function is called by sweep(), which is called from scan().
    Supports double buffering.
    lab.time_launched has to be zero for the first run of the scan (taken care of if get_ready() was called).
    
    Procedure:
    1) Execute experiment.sequence()
    2) Load memory of instruments with double-buffering
    3) Load memory of instruments without double-buffering
    4) Wait for time parameters
    5) Execute experiment.launch()
    6) Execute experiment.sequence() with next parameter values.
    7) Load memory of instruments with double-buffering
    8) Wait for end of experiment
    9) Store the result of experiment.get_data() in data array.
    10) Update figure
    11) On next run_experiment call, start at 3).
    """
    # First run only.
    ########################if lab.time_launched == 0:
    # Read experiment sequence.
    read_sequence(lab, params, experiment)
    ########################    # Load memory of ping pong instruments.
    ########################    for instrument in lab.get_ping_pong_instruments():
    ########################        instrument.load_memory_ping_pong()
    # Load memory of instruments who can't ping_pong.
    for instrument in [x for x in lab.get_memory_instruments() if (not x.use_pingpong)]:
        instrument.load_memory()
    # The starting pistol.
    experiment.launch(lab, params)
    # Save time at which the experiment really starts.
    lab.time_launched = timeit.default_timer()
    # Read next sequence and load memory of ping_pong instruments while the previous experiment is running.
    ########################load_future_params(lab, params, experiment)
    # Wait for the end of experiment. 
    while (timeit.default_timer() < lab.time_launched + lab.total_duration):
        pass
    # Update data array.
    data[params.get_data_indices()] = experiment.get_data(lab, params)
    # Update fig.
    if show_plot and fig != None:
        experiment.update_plot(fig, params, data)
        plotting.plt.pause(1e-6)
    return 

def read_sequence(lab, params, experiment):
    """
    First resets everything that is instructions related, then executes experiment.sequence()
    """
    # Reset everything instructions related from lab, as well as the instructions of each memory instrument.
    lab.reset_instructions()
    # Run the sequence function from experiment module (custom function defined by user) which should fill the instructions attribute of instruments with memory.
    experiment.sequence(lab, params)
    # Add a buffer of 20 ms to the experiments (timeit.default_timer() worst case precision is 1/60th of a second. Should be microsecond precision on Windows.)
    # Second reason for doing this is to let some space for the awg to get its granularity right.
    lab.delay(lab.end_buffer)
    return

def update_params(swept_params, i):
    """ Updates the attribute _v (current value) of the parameters that are swept to their ith value. """
    for param in swept_params:
        param._update(i)
    return
            

    
def load_future_params(lab, params, experiment):
    """ 
    Get the value of parameters for the next time run_experiment will be called, and load memory of ping pong instruments according to those values.
    Careful here: params values are changed inside this function. params._save_values() has to be called at the start, and params._load_values() has to be called at the end.   
    """
    params._save_values() # Here you have to save parameters current values, because they will be updated.
    current_sweep_ID = params.get_dimension() # this is true because load_future_params() is always called during run_experiment()
    load_them = False
    while current_sweep_ID > 0:            
        current_sweeps = params.get_current_sweeps(current_sweep_ID)
        i = current_sweeps[0].i # take index from any param, they all share the same.
        try:
            for param in current_sweeps:
                param._update(i+1) # if i+1 is too big for the array, it will raise IndexError.
            load_them =  True
            break
        except IndexError:
            # since the current loop is finished, reset current_sweeps to beginning of their respective array
            for param in current_sweeps:
                param._update(0) 
            # and decrement current_sweep_ID by one to get to the other loop.
            current_sweep_ID -= 1
    
    if load_them: # if load_them is False, it means that all the arrays are at the end, meaning there is no next parameters in line.
        read_sequence(lab, params, experiment)
        for instrument in lab.get_ping_pong_instruments():
            instrument.load_memory_ping_pong() 
    params._load_values() # Go back to values that were saved using params._save_values()
    return

def get_ready(lab, params):
    """ Stuff that has to be done in scan() before calling sweep() """
    lab.time_launched = 0
    for param in params.get_constants():
        param.v = param.value
        param.i = 0
    for param in params.get_sweeps():
        param._update(0)
    if "awg" in lab.get_names():
        lab.awg.reset_warnings()
    return

    
def detect_experiment_ID():
    """ Read the maximum ID from files under experiment/. Add one to this result and return it as a string with padded zeros if ID < 10000. """
    date = today()
    prefix = saving_folder()+"experiment/"+date+"/"+date+"_"
    # two purges to get a list of IDs in folder
    first_purge = [filename[len(prefix):].split("_")[0] for filename in glob.glob(prefix+"*.txt")] # 1st purge: get .txt files with correct prefix.
    second_purge = []
    for x in first_purge:
        try:
            second_purge.append(int(x)) # 2nd purge: thing between prefix and .txt has to be castable into an int.
        except:
            pass
    if second_purge == []: # if no files survived the purge
        ID = "0000"
    else:
        ID = pad_ID(max(second_purge)+1)
    return ID
    
def pad_ID(ID):
    """ Return the input ID as a string padded with zeros """
    return str(ID).zfill(4) # pad with zeros

def size_of_get_data_return(experiment):
    """
    In experiment .py file, read the get_data function source code and retrieve return values as texts. Result will depend on the number of comas in this string.
    Thus the special rules for experiment.get_data: there can only be one return, and return values have to be floats.
    """
    linecache.clearcache() # clear this cache or inspect.getsource() will not used last updated experiment.
    source = inspect.getsource(experiment.get_data) # get source code for experiment.get_data()
    try:
        source = source.split("return")[1] # remove everything before "return"
        source = source.split("\n")[0] # remove everything after the first "\n" encountered
        source = source.split("#")[0] # remove comment
        source = source.split(",") # split source in a list where each member was separated by a coma
        size = len(source) 
    except:
        raise LabMasterError, "Could not extract the number of return values of "+experiment.__name__+".get_data(). Check doc for proper formatting." #TODO: better message
    return size



def zeros(params, experiment):
    """ 
    Initializes data to zeros. Size of array will depend on dimension of sweep, lenght of parameter values, and size of get_data return. 
    dim 1 is sweep_ID #1, dim 2 is sweep_ID #2 and so on.
    """
    dimension = params.get_dimension()
    array_shape = [len(params.get_current_sweeps(i)[0].value)  for i in range(1,dimension+1) ]
    get_data_size =  size_of_get_data_return(experiment)
    if get_data_size > 1:
        array_shape.append(get_data_size)
    
    if dimension==0:
        array =  np.zeros(1)
    else:
        array = np.zeros(shape=array_shape)
    array[:] = np.nan
    return array




def create_todays_folder():
    """ Create those folders if they don't exist. """
    for section in ["data", "experiment","data_txt","fig","script","params"]:
        folder_name = saving_folder()+section+"/"+datetime.date.today().strftime("%Y_%m_%d")
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
    return 
    


def auto_unit(value, unit, decimal=None):
    """ Return value and unit as a compact string with automatic prefix. Ex, (50e9, "Hz") will output "50 GHz". """
    has_unit = (unit!="") # boolean value
    if value == 0: # don't want to deal with 0
        return "0"+has_unit*(" "+unit) 
    try:
        exp = int(np.floor(np.log10(abs(value))/3.))*3 # exponent of value (scientific notation) rounded down to a multiple of 3.
        index = exp/3+3
        if 0 <= index < 7:
            prefix = ["n", "u", "m", "", "k", "M", "G"][index]
        else:
            raise IndexError # needs to be done to avoid negative indexes. pico is not giga.
        if has_unit:
            if unit=="s":
                if value < 1:
                    value_out = value*(10**(-exp)) # update value to account for prefix
                else:
                    value_out = value
                    prefix = ""
            else:
                value_out = value*(10**(-exp)) # update value to account for prefix
        else:
            value_out = value
        if decimal:
            str_fmt = "%0."+str(decimal)+"f"
        else:
            if float("%s"%(value_out))%1>0:
                str_fmt = "%s" # with decimals
            else:
                str_fmt = "%i" # without decimals
        result = str_fmt%(value_out)+has_unit*(" "+prefix+unit)
    except:
        result = str(value)+has_unit*(" "+unit) # if something goes wrong, return this simple format.
    return result
    
    
def get_notebook_line_format(delimiter="\t"):
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

def saving_folder():
    return "saved/"
    
def get_script_filename():
    return sys.argv[0]
    
def filename_format(date, ID, script_name=True):
    return date+"_"+ID+"_"+script_name*get_script_filename()[:-3]
    
def today():
    return datetime.date.today().strftime("%Y_%m_%d")

def lastID():
    return pad_ID(int(detect_experiment_ID())-1)
    
def print_loaded_sequence_auto_label(lab):
    index=int(np.floor(np.log10(lab.total_duration - lab.end_buffer)/3))
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

def number_suffix(n):
    """ Returns the number suffix correponding to input n. """
    return ("st"*(n==1) + "nd"*(n==2) + "rd"*(n==3) + "th"*(n>3))


def tea():
    """Says Eddie the computer."""
    print "You ordered: tea.\nPlease wait will the Nutrimatic Drinks Dispenser prepares your: tea."
    for i in range(3):
        print "."*(i+1)
        time.sleep(1)
    time.sleep(2)
    for i in range(5000):
        print "."*(i%500 +1)
    raise SystemError, "You are an ignorant monkey."
    return


def hack_time():
    """Hackerman is in control here."""
    import sys
    import msvcrt
    if os.name=="nt":
        enter = "\r"
    else:
        enter = "\n"
    yes = "\t[YES]\t NO "
    no = "\t YES \t[NO]"
    yes_or_no = yes
    print "\n\n\tYOU'RE ABOUT \n\tTO HACK TIME,\n\tARE YOU SURE?\n"
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
            elif pressed==enter:
                if yes_or_no==yes:
                    print "\n\n"
                    for i in range(10000):
                        N = ((i//1000+1)%3+1)
                        sys.stdout.write("    HACKING TIME"+"."*N+" "*(3-N)+"\t\t\tYEARS HACKED: "+str(int(np.exp(i/800.)))+"\r")
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
                    print "\n\n\n    YOU ARE NOW IN THE VIKING AGE. LABMASTER TAKES TO RESPONSIBILITY IN DAMAGES CAUSED BY LASER RAPTORS."
                    break
                elif yes_or_no==no:
                    print "\n\nWHAT?? YOU ARE A CHICKEN."
                    break