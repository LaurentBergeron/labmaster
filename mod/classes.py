"""
Defines the Parameter class.
Parameter is a Locked class (look for Locked documentation in not_for_user module).
Every parameter used in lab experiments should be a Parameter instance, except time which is a Time_parameter and has a few more properties. Time_parameter inherits from Parameter.
"""
__author__ =  "Laurent Bergeron <laurent.bergeron4@gmail.com>"

# Base modules
import numpy as np
import timeit
import types
import sys

# Homemade modules
import not_for_user as nfu
from units import *

    
class Drawer():
    """    
    """
    def __init__(self, type_str):
        self.class_type = type_str
    
    def is_class_type(self, value):
        try:
            classes = [str(x).split(".")[-1] for x in list(value.__class__.__bases__)+[value.__class__]]
            return self.class_type in classes
        except:
            return False
        
    
    def get_dict(self):
        return {key:value for key, value in self.__dict__.items() if self.is_class_type(value)}
    def get_names(self):
        return [key for key, value in self.__dict__.items() if self.is_class_type(value)]
    def get_classes(self):
        return [value for value in self.__dict__.values() if self.is_class_type(value)]
    def get_items(self):
        return [(key, value) for key, value in self.__dict__.items() if self.is_class_type(value)]
        
    def get_arb_class(self):
        """ Returns an arbitrary class from class drawer. Returns -1 if no class was found. """
        if self.get_dict()=={}:
            return -1;
        else:
            return self.get_dict().itervalues().next()

    def import_to(self, namespace):
        """ Import classes from drawer in the specified namespace. """
        if isinstance(namespace, types.ModuleType):
            namespace = namespace.__dict__   
        namespace.update(self.get_dict())
        return
        

    def __setattr__(self, key, value):
        if key=="class_type":
            self.__dict__[key] = value
        else:
            if key in self.__dict__.keys(): 
                if self.is_class_type(self.__dict__[key]):
                    raise nfu.LabMasterError, "Can't overwrite "+key+" "+self.class_type+"."
                else:
                    self.__dict__[key] = value 
            else:
                self.__dict__[key] = value 
        return 
        
        
    
class Lab(Drawer):
    """
    The main purpose of this class is to keep track of every initialized instrument. It's a Drawer class with "Instrument" as type.
    The second purpose of this class is to manage timing during instruction commands and during experiment execution.
    """
    def __init__(self, *names):
        """ Initialize a Lab instance. """
        Drawer.__init__(self, "Instrument")
        self.time_cursor = 0 # Keeps track of current time when loading instructions
        self.total_duration = 0 # The time at which the experiment ends, aka the duration of experiment.
        self.time_launched = 0 # The time at which last experiment was launched. Must be initialized to zero.
        self.end_buffer = 20*ms # Add a delay to the end of each experiment (suggested 20 ms). (timeit.default_timer() worst case precision is 1/60th of a second. Should be microsecond precision on Windows, but still, better be safe.) Second reason for doing this is to let some space for the awg to get its granularity right (so in any case the time buffer should be higher than granularity/sample_rate).
        self.add_instrument(*names)
        
        self.free_evolution_time = 0 # each time the delay() function is called, this variable += the duration of delay.
        return
        
    def abort(self, name):
        try: 
            self.__dict__[name].abort()
        except:
            print name+" abort failed."
        return
            
    def abort_all(self):
        for name in self.get_names():
            self.abort(name)
        return
        
    def add_instrument(self, *names):
        """
        Connect to the specified instruments and add them as attributes to Lab.
        
        Input
        - *names: As many instrument names as you want. The name has to match a key in available_instruments() dictionnary.
                  You can connect to a generic VISA instrument by starting the name with VISA, following with custom name and VISA connexion ID, all separated by comas (not space sensitive).
                      ex: "VISA, death_ray, GPIB0::12::INSTR"
        """
        from mod.main import available_instruments
        for name in names:
            available = available_instruments()

            # Case for generic VISA instrument, with custom name and custom visa_ID
            if name[:4]=="VISA":
                print "Generic VISA instrument requested."
                _, new_name, visa_ID = "".join(name.split()).split(",")
                print "Name: "+new_name+" \nVisaID: "+visa_ID
                available[name[5:]] = [Default_visa, (visa_ID)]
            
            # Be sure instrument is not to be overwritten.
            if name in self.get_names():
                raise nfu.LabMasterError, name+" is already connected."
                
            # look if requested instrument is available
            if name in available.keys():
                class_ = available[name][0]
                opt_args = available[name][1]
                opt_keyargs = available[name][2]
            else:
                raise nfu.LabMasterError, "Requested instrument "+name+" not found in available list."
            
            try:
                # init requested instrument
                self.__dict__[name] = class_(name, self, *opt_args, **opt_keyargs)
            except:
                print "Can't add "+name+"."
                raise
        return
    
    def __str__(self):
        return self.print_connected(as_string=True)
    
    def close(self, name):
        """ 
        Close one instrument.
        
        Input
        - name: Name of instrument to close.

        Output
        - 0 if instrument was succesfully closed, else 1.
        """
        try:
            self.__dict__[name].close()
            del self.__dict__[name]
            print name+" closed."
            return 0
        except KeyError:
            raise nfu.LabMasterError, name+" was not found in lab's instruments."
        except:
            print  name+" failed to close.", sys.exc_info()[0].__name__+":",  sys.exc_info()[1]
            return 1 
            
    def close_all(self):
        """
        Call the close() method of each connected instrument. 
        Lab-Master authors take no responsibilty for anything that could happen if the close_all() method is not called before leaving the Ipython console.
        
        Output
        - The number of instruments who failed to close. 0 if everything when all right.
        """
        failed = 0
        for name in sorted(self.get_names()):    
            failed += self.close(name)
        return failed
    
    def delay(self, length):
        """ 
        Add a delay to an instructions for memory loading.
        
        Input
        - length: Duration of delay.
        """
        self.free_evolution_time += length
        self.update_time_cursor(length, None)
        return
        
    def get_memory_instruments(self):
        """ Return connected instruments which have memory capacity. """
        return [instr for instr in self.get_classes() if instr.use_memory]
        
    def get_ping_pong_instruments(self):
        """ Return connected instruments which have ping pong (double-buffering) memory capacity. """
        return [instr for instr in self.get_memory_instruments() if instr.is_ping_pong]

        
    def print_connected(self, as_string=False):
        """ Print connected instruments. """
        string = ""
        string+= "intruments connected:\n"
        if self.get_names()==[]:
            string += "   None"
        else:
            string+= "   "+"\n   ".join(sorted(self.get_names()))+"\n"
        if as_string:
            return string
        else:
            print string
        return
        

    def print_loaded_sequence(self):
        """ 
        Plot the loaded sequence of memory instruments in a pretty matplotlib figure. 
        An instrument needs a print_loaded_sequence() method to be shown in the plot.
        """
        instruments = [instr for instr in self.get_classes() if hasattr(instr, "print_loaded_sequence")]
        
        prefix, c = nfu.time_auto_label(self)


            
        fig, axes = plt.subplots(len(instruments), 1, sharex=True)
        for ax, instrument in zip(axes, instruments):
            instrument.print_loaded_sequence(ax=ax)
        plt.show()
        return
        
    def reset_instructions(self):
        """ Reset everything instructions related from lab, as well as the instructions of each memory instrument. """
        for instrument in self.get_memory_instruments():
            instrument.instructions = []
        self.time_cursor = 0
        self.total_duration = 0
        
    def rewind(self, length):
        """ 
        Add a negative delay to an instructions for memory loading.
        
        Input
        - length: Duration of rewind.
        """
        self.delay(-length)
        return

    def update_time_cursor(self, instruction_duration, rewind):
        """
        Add current instruction duration to self.time_cursor. 
        It has to be called after each time an instruction is appended.
        
        Input
        - instruction_duration: duration of currently loaded instruction.
        - rewind: After updating time_cursor, call the rewind method with rewind as input.
               If rewind is the string "start", call the rewind method with instruction_duration as input (go back to )
        """
        self.time_cursor += instruction_duration

        # The time for current instruction is higher than the final time we have stored, set the final time to current instruction time.
        if self.time_cursor > self.total_duration:
            self.total_duration = self.time_cursor

        if rewind == "start":
            self.time_cursor -= instruction_duration
        elif rewind:
            self.time_cursor -= rewind

            
        if self.time_cursor < 0:
            raise nfu.LabMasterError, "Instructions led to a negative time. Going back in time is not implemented (todo list)."

        
        return
        
        
class Instrument():
    """
    Instrument class. Every instrument should inherit from this class.
    """
    def __init__(self, name, parent, use_memory=False, is_ping_pong=False):
        """ 
        Initialize generic attributes of an instrument.

        Input
        - name: Name of instrument. It has to match lab's attribute for the instrument.
        - parent: A link to the lab instance from which the instrument is a child. Useful to call access lab attributes and call lab methods.
        - use_memory: If True, the instrument needs a load_memory method(), which will be called during an experiment.
        - is_ping_pong: If True, the instrument needs a load_memory_ping_pong() method, which will be called during an experiment instead of load_memory().
        """
        self.lab = parent
        self.name = name
        self.use_memory = use_memory
        self.is_ping_pong = is_ping_pong
        if use_memory:     
            self.instructions = []
            if self.is_ping_pong:
                self._current_buffer = 0   
            else:
                self._current_buffer = None
        else:
            self.instructions = None
            self._current_buffer = None
            if self.is_ping_pong:
                self.is_ping_pong = False
                print nfu.warn_msg()+self.name+" is set to ping_pong but has no memory. is_ping_pong attribute set back to False.\n"
            
        return
    
    def delay(self, length):
        """ 
        Add a delay to instructions for memory loading. Can be called by any Instrument instance or by a Lab instance. 
        
        Input
        - length: Duration of delay.
        """
        
        self.lab.delay(length)
        return


class Params(Drawer):
    """
    The main purpose of this class is to keep track of every parameter. It's a Drawer class with "Parameter" as type.
    """
    def __init__(self, *args):
        Drawer.__init__(self, "Parameter")
        self.add_parameter(*args)
        return 

    def __str__(self):
        return self.print_run(as_string=True)

        
    def add_parameter(self, *args):
        for arg in args:
            arg_list = arg.replace(" ","").replace("\t","").replace("\n","").split(":")
            name = arg_list[0]
            try:
                self.__dict__[name] = Parameter(name, unit=arg_list[1])
            except IndexError:
                self.__dict__[name] = Parameter(name)
        return
        
    def get_constants(self):
        return [param for param in self.get_classes() if param.is_const()]
        
    def get_current_sweeps(self, current_sweep_ID):
        return [param for param in self.get_sweeps() if param.sweep_ID==current_sweep_ID] 
    
    def get_data_indices(self):
        indices = []
        for i in range(1, self.get_dimension()+1):
            select_params = [y for y in self.get_sweeps() if y.sweep_ID==i]
            indices.append(select_params[0].i)
        return tuple(indices)
            
    def get_dimension(self):
        return max([0]+[param.sweep_ID for param in self.get_sweeps()])
    
    def get_sweeps(self):
        return [param for param in self.get_classes() if param.is_not_const() and param.sweep_ID > 0]

    def get_times(self):
        return [param for param in self.get_sweeps() if hasattr(param, "time")]
    
    def print_run(self, as_string=False):
        """ 
        Print the scheduled run in the most human readable way. 
        
        Input
        - as_string: If as_string is True, return the scheduled run as a string.
                     If as_string is False, just print it to console.

        Output
        - The scheduled run as a string, if as_string is True
        """
        string = ""
        # print constants
        if self.get_constants() != []:
            string +=  "Constants:\n"
            for param in self.get_constants():
                string +=  param.name+" = "+nfu.auto_unit(param.value,param.unit)+"\n"
            string +=  "\n"
        # print sweeps
        for i in range(1, self.get_dimension()+1):
            string +=  str(i)+nfu.number_suffix(i)+" sweep:\n"
            for param in self.get_current_sweeps(i):
                string +=  param.name+" from "+nfu.auto_unit(param.value[0],param.unit)+" to "+nfu.auto_unit(param.value[-1],param.unit)+" in "+str(len(param.value))+" steps.\n"
            string +=  "\n"
        if as_string:
            return string
        else:
            print string
        return
        
    def _save_values(self):
        for param in self.get_sweeps():
            param._saved_v = param.v
            param._saved_i = param.i
        
    def _load_values(self):
        for param in self.get_sweeps():
            param.v = param._saved_v
            param.i = param._saved_i

    
    
            
class Parameter():
    def __init__(self, name, unit=""):
        self.name = name 
        self.value = 0
        self.sweep_ID = 1
        self.unit = unit
        self.v = None
        self.i = None
        self._saved_v = None
        self._saved_i = None
        return

    def is_const(self):
        return not self.is_not_const()
        
    def is_not_const(self):
        return isinstance(self.value, (list, np.ndarray))
                
    def scan_with(self, param, *args):
        if param.is_const():
            raise nfu.LabMasterError, param.name+" is not currently configured to be swept."
        if len(args)==2:
            begin, end = args
            self.sweep_ID = param.sweep_ID
            self.value = np.linspace(begin,end,len(param.value))
        elif len(args)==1:
            step = args
            self.sweep_ID = param.sweep_ID
            self.value = np.linspace(0,step_size*(len(param.value)-1),len(param.value))
        return
        
    def set_ith_value(self, new_value):
        if self.is_const():
            self.value = new_value
        else:
            self.value[self.i] = new_value
        return
    
    def size(self):
        if self.is_const():
            size = 1
        else:
            size = len(self.value)
        return size

    def __setattr__(self, key, value):
        self.__dict__[key] = value
        if key=="time" and (not isinstance(value, Time_parameter)):
            raise nfu.LabMasterError, "time attribute is reserved for a Time_parameter instance."
        else:
            self.__dict__[key] = value 
        if key in ("sweep_ID", "value") and hasattr(self, "time"):
            saved_step = self.time.step
            self.disable_time()
            self.enable_time(saved_step)
        return
        
    def __str__(self):
        string = "name: "+self.name
        string += "\nvalue type: "+str(type(self.value))
        string += "\nvalue: "
        if self.is_const():
            string += nfu.auto_unit(self.value,self.unit)
        else:
            string += nfu.auto_unit(self.value[0],self.unit)+" to "+nfu.auto_unit(self.value[-1],self.unit)+" in "+str(len(self.value))+" steps."
        string += "\nsweep ID #"+str(self.sweep_ID)    
        return string
    
    def _update(self, i):
        if self.is_not_const():
            self.i = i
            self.v = self.value[i]
            if hasattr(self, "time"):
                self.time.v = self.time.value[i]
        return 
    
    ### deprecated ###
    # def enable_time(self,step):
        # """ update __setattr__ accordingly if any change is made to this method """
        # self.time = Time_parameter(self.name+"_time")
        # self.time.step = step
        # self.time.sweep_ID = self.sweep_ID
        # if self.is_const():
            # self.time.value = 0
        # else:   
            # self.time.value = np.linspace(step, step*(len(self.value)), len(self.value))
        # return
    # def disable_time(self):
        # del self.time
        # return
    ################## 
        
        
class Time_parameter(Parameter):
    """ deprecated """
    def __init__(self, name):
        Parameter.__init__(self, name, 0, "s")
        self._first_launch_time = 0
        self.lag_tolerance = 0.25 # if the program lags more than lag_tolerance seconds, will display warning message
        self.lag_warning_was_shown = False
        return
        
    def enable_time(self, step):
        raise nfu.LabMasterError, "What did you smoke?"
        
    def wait(self):
        if self.is_not_const():
            if self._first_launch_time == 0:
                self._first_launch_time = timeit.default_timer() # time() returns epoch time
            if timeit.default_timer() > (self.v + self._first_launch_time + self.lag_tolerance):
                if not self.lag_warning_was_shown:
                    print nfu.warn_msg()+"Time lag of "+self.name+" is higher than "+str(int(self.lag_tolerance*1000))+"ms. Do not trust "+self.name+" values."
                    self.lag_warning_was_shown = True
            else:
                while timeit.default_timer() < self.v + self._first_launch_time:
                    pass
        return
    
    def reset(self):
        self.lag_warning_was_shown = False
        self._update_value(0)
        return
        
    

class Locked:
    """ deprecated """
    """
    This class is designed to provide locking features to another class. 
    The attribute _locked can be accessed at all times. 
    When _locked is False:
        Everything will behave as normal.
    When _locked is True:
        1) It won't be possible to create new attributes anymore. 
            Ex: "tau.bachibouzouk=0" will generate an error.
        2) Attributes starting with an underscore (_) can't be set. They can still be accessed.
            Ex: "tau.v=0" will generate an error, but "print tau.v" will work.
    There is no reason for user to create a new attribute, if it happens it's probably an error, thus the error message. 
    If really for some reason the user wants to create a new attribute, or change an attribute starting with _ to a new value, set _locked to False. 
        Ex: tau._locked=False
    """
    def __init__(self):
        return

    def __setattr__(self, key, value):
        if key=="_locked": 
            # Changing the lock is always priority.
            self.__dict__[key] = value
        else:
            if self._locked:  
                # If locked
                if not hasattr(self, key):
                    # If attribute is not in the class, deny change.
                    raise nfu.LabMasterError, "."+key+" declaration denied. "+key+" is not a valid attribute."
                elif key[:1]=="_":
                    # If attribute begins with _, deny change.
                    raise nfu.LabMasterError, "Access to ."+key+" denied."
                else:
                    # Attribute is not concerned by lock, change it as usual.
                    self.__dict__[key] = value
            else:
                # If unlocked, change the value as usual.
                self.__dict__[key] = value 
        return 
    
    def alohomora(self):
        self._locked = False
    def colloportus(self):
        self._locked = True
        
        