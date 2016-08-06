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
import importlib

# Homemade modules
import not_for_user as nfu
from units import *
import available_instruments
    
class Drawer():
    """ 
    The purpose of the Drawer class is to regroup a specific type of object under the same name.
    The Lab class and the Params class both inherit from the Drawer class.
    Only the attributes corresponding to the specific object type will be considered by methods.
    Though a Drawer can only manage one type of object, any object that inherits from another object is considered to be of that type as well.
    For example, when calling lab.get_objects(), all Intrument instances from lab will be listed, as well as any instance that inherits from Instrument.
    """
    def __init__(self, type_str):
        """Initialize the drawer. Specify the type of objects that the drawer is meant to hold."""
        self.object_type = type_str ## name of the object type the drawer is meant to hold (as a string)
        return

    def __setattr__(self, key, value):
        if key=="object_type":
            self.__dict__[key] = value
        else:
            if key in self.__dict__.keys(): 
                if self.is_object_type(self.__dict__[key]):
                    raise nfu.LabMasterError, "Can't overwrite "+key+" "+self.object_type+"."
                else:
                    self.__dict__[key] = value 
            else:
                self.__dict__[key] = value 
        return
        
    def is_object_type(self, value):
        try:
            classes = [str(x).split(".")[-1] for x in list(value.__class__.__bases__)+[value.__class__]]
            out = self.object_type in classes
        except:
            out = False
        return out
    
    def get_dict(self):
        return {key:value for key, value in self.__dict__.items() if self.is_object_type(value)}
        
    def get_names(self):
        return self.get_dict().keys()
        
    def get_objects(self):
        return self.get_dict().values()
        
    def get_items(self):
        return self.get_dict().items()

    def import_to(self, namespace):
        """ Import classes from drawer in the specified namespace. """
        if isinstance(namespace, types.ModuleType):
            namespace = namespace.__dict__   
        namespace.update(self.get_dict())
        return
        
        
        
    
class Lab(Drawer):
    """
    The main purpose of this class is to keep track of every initialized instrument. It's a Drawer class with "Instrument" as type.
    The second purpose of this class is to manage timing during instruction commands and during experiment execution.
    """
    def __init__(self, *names):
        """ Initialize a Lab instance. """
        Drawer.__init__(self, "Instrument")
        self.time_cursor = 0 ## Keeps track of current time when loading instructions
        self.total_duration = 0 ## The time at which the experiment ends, aka the duration of experiment.
        self.time_launched = 0 ## The time at which last experiment was launched. Must be initialized to zero.
        self.end_buffer = 20*ms ## Add a delay to the end of each experiment (suggested 20 ms). (timeit.default_timer() worst case precision is 1/60th of a second. Should be microsecond precision on Windows, but still, better be safe.) Second reason for doing this is to let some space for the awg to get its granularity right (so in any case the time buffer should be higher than granularity/sample_rate).
        self.add_instrument(*names)
        
        self.free_evolution_time = 0 ## each time the delay() function is called, this variable += the duration of delay.
        return
        
    def abort(self, name):
        try: 
            self.__dict__[name].abort()
        except:
            print name+" abort failed; ", sys.exc_info()[0].__name__+":",  sys.exc_info()[1]
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
        
        for name in names:
            try:
                ## Be sure instrument is not to be overwritten.
                if name in self.get_names():
                    raise nfu.LabMasterError, name+" is already connected."
                    
                ## Case for generic VISA instrument, with custom name and custom visa_ID
                if name[:4]=="VISA":
                    print "Generic VISA instrument requested."
                    _, new_name, visa_ID = "".join(name.split()).split(",")
                    print "Name: "+new_name+" \nVisaID: "+visa_ID
                    import mod.instruments.visa_instruments
                    module_name = "visa_instruments"
                    class_name = "Default_visa"
                    opt_args = (visa_ID,)
                    opt_keyargs = {}
                else:
                    ## look if requested instrument is available
                    if name not in available_instruments.__dict__:
                        raise nfu.LabMasterError, "Requested instrument "+name+" not found in available_instruments module."
                    module_name = available_instruments.__dict__[name][0]
                    class_name = available_instruments.__dict__[name][1]
                    opt_args = available_instruments.__dict__[name][2]
                    opt_keyargs = available_instruments.__dict__[name][3]

                module = importlib.import_module("mod.instruments."+module_name)
                class_ = module.__dict__[class_name]
            
                ## init requested instrument
                self.__dict__[name] = class_(name, self, *opt_args, **opt_keyargs)
            except:
                raise
                print "Can't add "+name+" ->  "+ sys.exc_info()[0].__name__+": "+str(sys.exc_info()[1])
                
                
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
            print  name+" failed to close; ", sys.exc_info()[0].__name__+":",  sys.exc_info()[1]
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
        return [instr for instr in self.get_objects() if instr.use_memory]
        
    def get_ping_pong_instruments(self):
        """ Return connected instruments which have ping pong (double-buffering) memory capacity. """
        return [instr for instr in self.get_memory_instruments() if instr.use_pingpong]

        
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
        

    def reload(self, name):
        self.close(name)
        self.add_instrument(name)
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
               If rewind is "start", do not update time cursor.
        """
        self.time_cursor += instruction_duration

        ### The time for current instruction is higher than the final time we have stored, set the final time to current instruction time.
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
    def __init__(self, name, parent, use_memory=False, use_pingpong=False):
        """ 
        Initialize generic attributes of an instrument.

        Input
        - name: Name of instrument. It has to match lab's attribute for the instrument.
        - parent: A link to the lab instance from which the instrument is a child. Useful to call access lab attributes and call lab methods.
        - use_memory: If True, the instrument needs a load_memory method(), which will be called during an experiment.
        - use_pingpong: If True, the instrument needs a load_memory_ping_pong() method, which will be called during an experiment instead of load_memory().
        """
        self.lab = parent
        self.name = name
        self.use_memory = use_memory
        self.use_pingpong = use_pingpong
        self.instructions = []
        if not use_memory and self.use_pingpong:  
            raise LabMasterError, self.name+" is set to use pingpong but has no memory."
        return

    def reload(self):
        self.lab.reload(self.name)
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
            arg_list = arg.replace(" ","").replace("\t","").replace("\n","").split(";")
            name = arg_list[0]
            try:
                self.__dict__[name] = Parameter(name, unit=arg_list[1])
            except IndexError:
                self.__dict__[name] = Parameter(name)
        return
        
    def get_constants(self):
        return [param for param in self.get_objects() if param.is_const()]
        
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
        return [param for param in self.get_objects() if param.is_not_const() and param.sweep_ID > 0]
    
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
                string +=  param.name+" from "+nfu.auto_unit(param.value[0],param.unit)+" to "+nfu.auto_unit(param.value[-1],param.unit)+" with "+nfu.auto_unit(param.get_step(), param.unit)+" step size.\n"
            string +=  "\n"
        if as_string:
            out = string
        else:
            out = ""
            print string
        return out
        
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
        
    def auto_unit(self, i=None):
        if self.is_const():
            out = nfu.auto_unit(self.value, self.unit)
        else:
            if i==None:
                out = nfu.auto_unit(self.v, self.unit)
            else:
                out = nfu.auto_unit(self.value[i], self.unit)
        return out
        
    def is_const(self):
        return not self.is_not_const()
        
    def is_not_const(self):
        return isinstance(self.value, (list, np.ndarray))
    
    def get_end(self):
        try:
            end = self.value[-1]
        except (IndexError, TypeError):
            end = self.value
        return end
        
    
    def get_start(self):
        try:
            start = self.value[0]
        except (IndexError, TypeError):
            start = self.value
        return start
    
    
    def get_step(self):
        try:
            step = self.value[1]-self.value[0]
        except (IndexError, TypeError):
            step = None
        return step
        
        
    def set_ith_value(self, new_v):
        if self.is_const():
            self.value = new_v
        else:
            self.value[self.i] = new_v
        return
    
    def get_size(self):
        try:
            size = len(self.value)
        except TypeError:
            size = 1
        return size
        
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
        
        