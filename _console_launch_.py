"""
First launch of Ipython, aiming to fix scipy when running under windows.
If an error happens in this script, %tb will be broken in Ipython, so don't use try/except statements.
"""
__version__ = "3.0"   

import os

if "__nonzero__" in list(globals().keys()): 
    raise RuntimeError("Lab-Master needs to be launched outside Ipython.")

##### FIXED IN PYTHON 3.6 #####
# if os.name == 'nt':
    # import mod.scipy_fix
###############################
    
import IPython
print("Ipython starting...\n")

ipython_startup = ['__version__ = '+str(__version__),
                   'print("")',
                   'print("")',
                   'print("*** Welcome to the LabMaster v."+str(__version__)+" "*(13-len(str(__version__)))+"***")',
                   'print("*** In case of emergency, try help_please(). ***")',
                   'print("")',
                   'run _reset_.ipy',
                   '%matplotlib']
                   
IPython.start_ipython(argv=['--InteractiveShellApp.exec_lines=%s'%ipython_startup])

