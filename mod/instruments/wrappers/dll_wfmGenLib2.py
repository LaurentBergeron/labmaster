"""
Python wrapper for wfmGenLib2.dll, which purpose is to compute a sum of different pulses faster than python would.
wfmGenLib2.dll inpired from wfmGenLib.dll by Kevin Morse <kjm2@sfu.ca>.
"""
__author__ =  "Laurent Bergeron <laurent.bergeron4@gmail.com>"

# Base Modules
from ctypes import *

dll = cdll.LoadLibrary("mod/instruments/extern/wfmGenLib2.dll")

shapes_code = { "square": 0, 
                "gauss": 1
              }
    

def wfmgen(countFreq, blockStart, wfmStart, wfmLength, arrPeriod, arrPhase, arrAmp, arrShape, arrOut):
    return dll.wfmgen(countFreq, blockStart, wfmStart, wfmLength, arrPeriod, arrPhase, arrAmp, arrShape, arrOut)
dll.wfmgen.restype = None
dll.wfmgen.argtype = (
                       c_int, # countFreq
                       c_longlong, # blockStart
                       POINTER(c_longlong), # wfmStart[]
                       POINTER(c_longlong), # wfmLength[]
                       POINTER(c_double), # arrPeriod[]
                       POINTER(c_double), # arrPhase[]
                       POINTER(c_short), # arrAmp[]
                       POINTER(c_int), # arrShape[]
                       POINTER(c_short) # arrOut[]
                      )