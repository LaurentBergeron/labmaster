"""
If an error happens in this script, %tb will be broken in Ipython, so don't use try/except statements.
"""

if "__nonzero__" in globals().keys(): ### do not use try: __IPYTHON__ 
    raise RuntimeError, "Lab-Master needs to be launched outside Ipython."


import os
if os.name == 'nt':
    import mod.scipy_fix

    
import IPython
text = '"'
IPython.start_ipython(argv=['--InteractiveShellApp.exec_lines=%s'%['print ""', 'print "---> run _launch_.ipy"',"run _launch_.ipy"]])


