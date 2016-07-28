try:
    __IPYTHON__
    inside_Ipython = True
except NameError:
    inside_Ipython = False

if inside_Ipython:
    raise RuntimeError, "Lab-Master needs to be launched outside Ipython."

    
import IPython, os

if os.name == 'nt':
    import mod.scipy_fix

IPython.start_ipython()
