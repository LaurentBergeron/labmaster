"""
First launch of Ipython, aiming to fix scipy when running under windows.
If an error happens in this script, %tb will be broken in Ipython, so don't use try/except statements.
"""
__version__ = "2.0"   

import os

if "__nonzero__" in globals().keys(): ### do not use this -> try: __IPYTHON__    or %tb will break.
    raise RuntimeError, "Lab-Master needs to be launched outside Ipython."

   
if os.name == 'nt':
    import mod.scipy_fix


if (6/7)==0:
    raise SystemError, "\n\n\nLabMaster is coded for float division. Add -Qnew to python flags to use float division.\n\npython -Qnew _console_launch_.py"
else:
    print "\n*Using float division.*\n"
    
import IPython
print "Ipython starting...\n"

## Hail the great LabMaster
ipython_startup = ['from __future__ import division',
                    '__version__ = '+str(__version__),
                   'print ""',
                   'print ""',
                   'print "*** Welcome to the LabMaster v."+str(__version__)+" "*(13-len(str(__version__)))+"***"',
                   'print "*** In case of emergency, try help_please(). ***"',
                   'print ""',
                   'run _reset_.ipy']
                   
             
                   
IPython.start_ipython(argv=['--InteractiveShellApp.exec_lines=%s'%ipython_startup])

