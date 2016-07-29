#!/usr/bin/env python
from subprocess import call

dir = "C:/LabMaster"
cmdline = "Console.exe"
rc = call(cmdline, cwd=dir) # run `cmdline` in `dir`