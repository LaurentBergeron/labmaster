"""
LabMaster launcher. 
For an easy double-click start whichs fixes scipy when using Windows.

Windows:
    - "Console2"
    - "cmd"
Unix:
    Not implemented
"""

console = "Console2" ## choose from the list in header documentation


import os

## WINDOWS
if os.name == "nt":
    ## Classic cmd.exe start
    if console=="cmd":
        os.system("python console_launch.py")
    
    ## Console2 start
    elif console=="Console2":
        ## Path to add to the PATH environnement variable.
        console_path = "C:\LabMaster\Console2"
        ## Executable name of the desired console.
        console_exe = "Console"
        with open("Console2/startup.bat", "w") as f:
            f.write("@ECHO off\n") ## because nobody wants to see this.
            f.write("python console_launch.py\n") ## 'cd ..' is called in first_launch.pys
            f.write("cmd\n") ## launch Console2.
        os.system("set PATH=%PATH%;"+console_path+"&"+console_exe) ## Add Console2 folder to path & Launch Console2.
        ##------------------------------------------------------------------------------------------------------
        ## Up to this point, Console2 looks for startup.bat (located in Console2 folder) and execute it. 
        ## If this doesn't work, make sure that Edit/Settings/Console/Shell is targeting the startup.bat file.
        ##------------------------------------------------------------------------------------------------------

        ## Reset the startup.bat file to normal use.
        with open("Console2/startup.bat", "w") as f:
            f.write("@ECHO off\n")
            f.write("cmd\n")
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
