"""
Definition of LabMaster generic classes: Drawer, Lab, Instrument, Params, Parameter.
Lab and Params both inherit from the Drawer class.
Lab classe is designed to hold Instrument classes.
Params class is designed to hold Parameter classes. 
"""
__author__ =  "Laurent Bergeron <laurent.bergeron4@gmail.com>"

## Base modules
import numpy as np
import timeit
import types
import sys
import importlib

## Homemade modules
from . import not_for_user as nfu
from .units import *
from . import available_instruments

def all_bases(cls):
    """Return all the parent classes from specified class."""
    c = list(cls.__bases__)
    for base in c:
        c.extend(all_bases(base))
    return c

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
        """ 
        Revamped the __setattr__ method to forbid overwritting an attribute (you don't want to overwrite instrument classes while they are connected). 
        To overwrite an attribute, delete it first using 'del'.
        """
        ## Raise an error is a vilain is trying to overwrite a protected object.
        if (key in list(self.__dict__.keys())) and (key!="object_type"):
            if self.is_object_type(self.__dict__[key]):
                if self.object_type=='Parameter':
                    add_msg = " Use the value attribute."
                else:
                    add_msg = ""
                raise nfu.LabMasterError("Can't overwrite "+key+" "+self.object_type+"."+add_msg)
                
        ## If no error, the classic way to set attributes.
        self.__dict__[key] = value 
        return
    
    

    def is_object_type(self, value):
        """Will return True if input argument is the same type as self.object_type, False if not."""
        try:
            classes = [str(x).split(".")[-1][:-2] for x in list(all_bases(value.__class__))+[value.__class__]]
            out = self.object_type in classes
        except:
            out = False
        return out
    
    def get_dict(self):
        """Return a dictionary with all attributes matching self.object_type."""
        return {key:value for key, value in list(self.__dict__.items()) if self.is_object_type(value)}
        
    def get_names(self):
        """Return a list of names of attributes matching self.object_type."""
        return list(self.get_dict().keys())
        
    def get_objects(self):
        """Return a list of attributes matching self.object_type."""
        return list(self.get_dict().values())
        
    def get_items(self):
        """Return attributes along with their name if they match self.object_type."""
        return list(self.get_dict().items())

    def import_to(self, namespace):
        """Import objects matching self.object_type from drawer in the specified namespace."""
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
        """ Initialize a Lab instance. Connect to instruments specified in arguments."""
        ## Inherit from the Drawer class.
        Drawer.__init__(self, "Instrument") 
        ## Keeps track of current time when loading instructions
        self.time_cursor = 0 
        ## The time at which the experiment ends, aka the duration of experiment.
        self.total_duration = 0 
        ## The time at which the experiment was launched. See nfu.run_experiment().
        self.time_launched = 0
        ## each time the delay() function is called, this variable += the duration of delay. It is the time during which no pulse is applied.
        self.free_evolution_time = 0 
        
        ## Connect to instruments specified in arguments.
        self.add_instrument(*names)
        return
        
    def abort(self, name):
        """Call the abort method of specified instrument. Errors will be printed, not raised."""
        try: 
            self.__dict__[name].abort()
        except:
            print(name+" abort failed; ", sys.exc_info()[0].__name__+":",  sys.exc_info()[1])
        return
            
    def abort_all(self):
        """Call the abort method of all connected instruments. Errors will be printed, not raised."""
        for name in self.get_names():
            self.abort(name)
        return
        
        
    def add_instrument(self, *names):
        """
        Connect to the specified instruments and add them as attributes to Lab. Errors will be printed, not raised.
        The name has to match an object from available_instruments.py module.
        ex: lab.add_instrument("awg", "lockin")
        You can connect to a generic VISA instrument by starting the name with VISA, following with custom name and VISA connexion ID, all separated by comas (not space sensitive).
        ex: lab.add_instrument("VISA, death_ray, GPIB0::12::INSTR")
        """
        for name in names:
            try:
                ## Be sure instrument is not to be overwritten.
                if name in self.get_names():
                    raise nfu.LabMasterError(name+" is already connected.")
                    
                ## Case for generic VISA instrument, with custom name and custom visa_ID
                if name[:4]=="VISA":
                    print("Generic VISA instrument requested.")
                    _, new_name, visa_ID = "".join(name.split()).split(",")
                    print("Name: "+new_name+" \nVisaID: "+visa_ID)
                    module_name = "default_visa"
                    class_name = "Default_visa"
                    opt_args = (visa_ID,)
                    opt_keyargs = {}
                    name = new_name
                else:
                    ## Look if requested instrument is available.
                    if name not in available_instruments.__dict__:
                        raise nfu.LabMasterError("Requested instrument "+name+" not found in available_instruments module.")
                    instrument_specs = available_instruments.__dict__[name]
                    module_name = instrument_specs[0]
                    class_name = instrument_specs[1]
                    opt_args = instrument_specs[2]
                    opt_keyargs = instrument_specs[3]
                
                ## Import module where the class is located. 
                module = importlib.import_module("mod.instruments."+module_name)
                ## Import the class.
                class_ = module.__dict__[class_name]
                
                if not isinstance(opt_args, tuple):
                    ## opt_args has to be a tuple.
                    raise LabMasterError("Optional arguments to "+name+" must be a tuple.") 
                    
                if not isinstance(opt_keyargs, dict):
                    ## opt_keyargs has to be a dict
                    raise LabMasterError("Optional key-arguments to "+name+" must be a dict.")
                    
                ## init requested instrument
                self.__dict__[name] = class_(name, self, *opt_args, **opt_keyargs)
                
            except:
                print("Can't add "+name+" ->  "+ sys.exc_info()[0].__name__+": "+str(sys.exc_info()[1]))
                
                
        return
    
    def __str__(self):
        """ String representation of a Lab class."""
        return self.print_connected(as_string=True)
    
    def close(self, name):
        """ 
        Call the close method of specified instrument. Errors will be printed, not raised.

        Output:
        - 0 if instrument was succesfully closed, else 1.
        """
        try:
            self.__dict__[name].close()
            del self.__dict__[name]
            print(name+" closed.")
            return 0
        except KeyError:
            raise nfu.LabMasterError(name+" was not found in lab's instruments.")
        except:
            print(name+" failed to close. ", sys.exc_info()[0].__name__+":",  sys.exc_info()[1])
            return 1 
            
    def close_all(self):
        """
        Call the close() method of each connected instrument. Errors will be printed, not raised.
        LabMaster authors take no responsibilty for anything that could happen if the close_all() method is not called before leaving the Ipython console.
        
        Output:
        - The number of instruments who failed to close. 0 if everything when all right.
        """
        failed = 0
        for name in sorted(self.get_names()):    
            failed += self.close(name)
        return failed
    
    def delay(self, duration):
        """Update the time cursor by the specified duration (s). Updates self.free_evolution_time."""
        self.free_evolution_time += duration
        self.update_time_cursor(duration, None)
        return
        
    def get_memory_instruments(self):
        """Return connected instruments which have memory capacity."""
        return [instr for instr in self.get_objects() if instr.use_memory]
        
    def print_connected(self, as_string=False):
        """Print connected instruments to the console."""
        string = ""
        string+= "intruments connected:\n"
        if self.get_names()==[]:
            string += "   None"
        else:
            string+= "   "+"\n   ".join(sorted(self.get_names()))+"\n"
        if as_string:
            return string
        else:
            print(string)
        return
        

    def reload(self, name):
        """
        Close and reinitialize the instrument. 
        Avoids to restart the Ipython console on UnboundLocalError class autoreload bug.
        """
        if str(type(self.__dict__[name])).split('.')[-1]=="Default_visa'>":
            self.close(name)
            self.add_instrument("VISA, "+name+", "+self.__dict__[name].visa_ID)
        else:
            self.close(name)
            self.add_instrument(name)
        return
        
    def reset_instructions(self):
        """ Reset everything instructions-related from the Lab instance, as well as the instructions of each memory instrument. """
        for instrument in self.get_memory_instruments():
            instrument.instructions = []
        self.time_cursor = 0
        self.total_duration = 0
        return
        
    def rewind(self, duration):
        """A backwards delay (s)."""
        self.delay(-duration)
        return

    def update_time_cursor(self, instruction_duration, rewind):
        """
        Add current instruction duration to self.time_cursor. 
        It has to be called after each time an instruction is appended.
        
        - instruction_duration: duration to add to the time cursor (s).
        - rewind: If rewind is True, go back to initial time cursor position. This will update self.total_duration but keep self.time_cursor the same.
        """
        ## Update time cursor.
        self.time_cursor += instruction_duration

        ### If the time cursor is higher than the last recorded total_duration, set the self.total_duration = self.time_cursor
        if self.time_cursor > self.total_duration:
            self.total_duration = self.time_cursor

        if rewind:
            ## Go back to initial time cursor position.
            self.time_cursor -= instruction_duration
            
        if self.time_cursor < 0:
            raise nfu.LabMasterError("Instructions led to a negative time. Going back in time is not implemented (todo list).")

        
        return
        
        
class Instrument():
    """
    Contains general attributes and methods that every instrument should have.
    """
    def __init__(self, name, parent, use_memory=False):
        """ 
        Initialize generic attributes of an instrument.
        - name: Name of instrument. It has to match lab's attribute for the instrument.
        - parent: A link to the lab instance from which the instrument is a child. Useful to call access lab attributes and call lab methods. Beware of infinite loopholes!
        - use_memory: If True, the instrument needs a load_memory method(), which will be called during an experiment.
        """
        self.lab = parent
        self.name = name
        self.use_memory = use_memory
        if self.use_memory:
            ## A list of instructions to fill during experiment.sequence().
            self.instructions = []
        return

    def reload(self):
        """
        Close and reinitialize the instrument. 
        Avoids to restart the Ipython console on UnboundLocalError class autoreload bug.
        """
        self.lab.reload(self.name)
        return


class Params(Drawer):
    """
    The main purpose of this class is to keep track of every parameter. It's a Drawer class with "Parameter" as type.
    """
    def __init__(self, *args):
        """Initialize a Params instance. Arguments will be passed on to Parameter declarations."""
        Drawer.__init__(self, "Parameter")
        self.add_parameter(*args)
        return 

    def __str__(self):
        """String representation of the sweep."""
        return self.print_sweep(as_string=True)

        
    def add_parameter(self, *args):
        """
        Add a parameter for each argument. 
        An argument must be the name and unit of the parameter, separated by a semi-column. Not space/tab/enter sensitive. Unit is optional.
        ex: params.add_parameter("tau;s", "loops")
        """
        for arg in args:
            arg_list = arg.replace(" ","").replace("\t","").replace("\n","").split(";")
            name = arg_list[0]
            try:
                unit=arg_list[1]
            except IndexError:
                unit = ""
            self.__dict__[name] = Parameter(name, unit)
        return
        
    def get_constants(self):
        """Return parameters with a constant as their value attribute."""
        return [param for param in self.get_objects() if param.is_const()]
        
    def get_current_sweeps(self, current_sweep_dim):
        """Return list/array parameters that match current_sweep_dim."""
        return [param for param in self.get_sweeps() if param.sweep_dim==current_sweep_dim] 
    
    def get_data_indices(self):
        """Return a list of indices to place the current point in the data array."""
        indices = []
        for i in range(1, self.get_dimension()+1):
            select_params = [y for y in self.get_sweeps() if y.sweep_dim==i]
            indices.append(select_params[0].i)
        return tuple(indices)
            
    def get_dimension(self):
        """Return the maximum sweep_dim."""
        return max([0]+[param.sweep_dim for param in self.get_sweeps()])
    
    def get_sweeps(self):
        """Return parameters with a list or array as their value attribute."""
        return [param for param in self.get_objects() if param.is_not_const() and param.sweep_dim > 0]
    
    def print_sweep(self, as_string=False):
        """ 
        Print the scheduled run in the most human readable way. 
        
        - as_string: If as_string is True, return the scheduled run as a string.
                     If as_string is False, just print it to console.
        """
        string = ""
        ## Print constants.
        if self.get_constants() != []:
            string +=  "Constants:\n"
            for _, param in sorted([(x.name, x) for x in self.get_constants()]):
                string +=  "   "+param.name+" = "+nfu.auto_unit(param.value,param.unit)+"\n"
            string +=  "\n"
        ## Print sweeps.
        for i in range(1, self.get_dimension()+1):
            string +=  str(i)+nfu.number_suffix(i)+" sweep:\n"
            for _, param in sorted([(x.name, x) for x in self.get_current_sweeps(i)]):
                string +=  "   "+param.name+" from "+nfu.auto_unit(param.value[0],param.unit)+" to "+nfu.auto_unit(param.value[-1],param.unit)+" with "+nfu.auto_unit(param.get_step(), param.unit)+" step size.\n"
            string +=  "\n"
        
        if string=="":
            string = "No parameters detected."
        if as_string:
            out = string
        else:
            out = ""
            print(string)
        return out
    
    
            
class Parameter():
    """
    The Parameter class holds information about a parameter (that's right).
    Important attributes:
    - value: Constant or array. Arrays will be swept according to their sweep_dim
    - i: Current index in the swept array. 
    - v: Current element of the array being swept. v = value[i] (v = value for a constant)
    - sweep_dim: Dimension of the scan on which to sweep the parameter. If sweep_dim=0, the parameter will not be swept.
    """
    def __init__(self, name, unit=""):
        """
        Initialize a Parameter instance.
        - name: name of the parameter, same as params' attribute to access it.
        - unit: unit of the parameter, optional.
        """
        self.name = name
        self.value = 0
        self.sweep_dim = 1 ## Dimension of the scan on which to sweep the parameter. If sweep_dim=0, the parameter will not be swept.
        self.unit = unit
        self.v = None ## Current element of the array being swept. v = value[i] (v = value for a constant)
        self.i = None ## Current index in the swept array. 
        return
        
    def auto_unit(self, i=None):
        """
        Automatic unit format.
        If parameter is a constant, use its '.value' attribute.
        If parameter is an array, use its '.v' attribute, or a specified index (opt argument).
        """
        
        if self.is_const():
            out = nfu.auto_unit(self.value, self.unit)
        else:
            if i==None:
                out = nfu.auto_unit(self.v, self.unit)
            else:
                out = nfu.auto_unit(self.value[i], self.unit)
        return out
        
    def is_const(self):
        """Return True if the '.value' attribute is not indexable, False instead."""
        return not self.is_not_const()
        
    def is_not_const(self):
        """Return True if the '.value' attribute is indexable, False instead."""
        if isinstance(self.value, (list, np.ndarray)):
            out = True
        else:
            out = False
        return out
    
    def get_end(self):
        """Return last element of array."""
        try:
            end = self.value[-1]
        except (IndexError, TypeError):
            end = self.value
        return end
        
    
    def get_start(self):
        """Return first element of array."""
        try:
            start = self.value[0]
        except (IndexError, TypeError):
            start = self.value
        return start
    
    
    def get_step(self):
        """Return step size of array (assuming it's constant)."""
        try:
            step = self.value[1]-self.value[0]
        except (IndexError, TypeError):
            step = None
        return step
        
        
    def set_ith_value(self, new_v):
        """
        Equivalent to self.value[self.i] = new_v.
        For a constant, self.value = new_v.
        """
        if self.is_const():
            self.value = new_v
        else:
            self.value[self.i] = new_v
        return
    
    def get_size(self):
        """
        Return length of array.
        For a constant, return 1.
        """
        try:
            size = len(self.value)
        except TypeError:
            size = 1
        return size
        
    def __str__(self):
        """String representation of a Parameter instance."""
        string = "name: "+self.name
        string += "\nvalue type: "+str(type(self.value))
        string += "\nvalue: "
        if self.is_const():
            string += nfu.auto_unit(self.value,self.unit)
        else:
            string += nfu.auto_unit(self.value[0],self.unit)+" to "+nfu.auto_unit(self.value[-1],self.unit)+" in "+str(len(self.value))+" steps."
        string += "\nsweep on dimension #"+str(self.sweep_dim)    
        return string
    
    def _update(self, i):
        """
        Update '.i' and '.v' attributes according to specified index.
        The function is skipped for constants.
        """
        if self.is_not_const():
            self.i = i
            self.v = self.value[i]
            if hasattr(self, "time"):
                self.time.v = self.time.value[i]
        return 
           
        
