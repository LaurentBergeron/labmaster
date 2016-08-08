"""
Python wrapper for wfmGenLib2.dll
wfmGenLib2 computes the sum of different pulses.
wfmGenLib2 base was taken from wfmGenLib by Kevin Morse <kjm2@sfu.ca>.
Edit the shapes_code dictionnaries when including a new enveloppe shape in wfmGenLib2.
"""
__author__ =  "Laurent Bergeron <laurent.bergeron4@gmail.com>"

from ctypes import *

## Load wfmGenLib2.dll
dll = cdll.LoadLibrary("mod/instruments/extern/wfmGenLib2.dll")


## Dictionnary that translates the shape string to the number in wfmGenLib2 enum.
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