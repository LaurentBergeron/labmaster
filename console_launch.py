"""
First launch of Ipython, aiming to fix scipy when running under windows.
If an error happens in this script, %tb will be broken in Ipython, so don't use try/except statements.
"""

import os

if "__nonzero__" in globals().keys(): ### do not use this -> try: __IPYTHON__    or %tb will break.
    raise RuntimeError, "Lab-Master needs to be launched outside Ipython."

   
if os.name == 'nt':
    import mod.scipy_fix

import IPython
print "Ipython starting...\n"
IPython.start_ipython(argv=['--InteractiveShellApp.exec_lines=%s'%['print ""', 'print "---> run _launch_.ipy"',"run _launch_.ipy"]])

