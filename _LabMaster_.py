"""
LabMaster launcher. 
For an easy double-click start whichs fixes scipy when using Windows.

Windows:
    - "cmd": Classic Windows cmd.exe.
    - "Console2": A better Windows command prompt.
Unix:
    Not implemented
"""

console = "Console2" ## choose from the list in header documentation


import os

## WINDOWS
if os.name == "nt":
    ## Classic cmd.exe start
    if console=="cmd":
        os.system("python _console_launch_.py")
    
    ## Console2 start
    elif console=="Console2":
        ## Path to executable.
        console_path = "C:\LabMaster\doc\Console2"
        ## Executable name.
        console_exe = "Console"
        
        ## Add Console2 folder to path & Launch Console2.
        os.system("set PATH=%PATH%;"+console_path+"&set LABMASTER=TRUE&"+console_exe) 
        ##------------------------------------------------------------------------------------------------------
        ## Up to this point, Console2 looks for startup.bat (located in Console2 folder) and execute it. 
        ## If this doesn't work, make sure that Edit/Settings/Console/Shell is targeting the startup.bat file.
        ##------------------------------------------------------------------------------------------------------

    else:
        ## If using another console, add a similar launcher here.
        print "LabMaster launcher works for Console2 only."
        print "Execute 'python first_launch.py' from a console to launch LabMaster."
## UNIX
elif os.name=="posix":
    ### If planning to port LabMaster to Linux or MacOS, add a similar launcher here
    print "LabMaster launcher is Windows compatible only."
    print "Execute 'python first_launch.py' from a console to launch LabMaster."
## FANCY OS.
else:
    print "LabMaster launcher is not available for your os."
    print "Execute 'python first_launch.py' from a console to launch LabMaster."
