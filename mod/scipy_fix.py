# -*- coding: utf-8 -*-

# KeyboardInterrupt fixes from:
#   https://github.com/scipy/scipy/pull/3880
# by Christian Lupien (2014-12-18)

# prevent interference with KeyboardInterrupt on Windows
# due to Fortran libraries
# See stackoverflow for explanation:
# http://stackoverflow.com/questions/15457786/ctrl-c-crashes-python-after-importing-scipy-stats

from __future__ import absolute_import

import imp
import ctypes
import os

INSTALL = False

dirname = imp.find_module('scipy')[1]
config_file = os.path.join(dirname, '__config__.py')

if os.path.exists(config_file):
    with open(config_file, 'rb') as fid:
        text = fid.read()
    if 'mkl_blas' in text:
        INSTALL = True

def handler(sig):
    try:
        import _thread
    except ImportError:
        import thread as _thread
    _thread.interrupt_main()
    return 1 # do not execute any other handlers.

def load_lib(name):
    """ Load a numpy dll by first trying a specific location, the
        uses the dll search path which is hopefully set correctly
        On my system the dlls are in C:\\Python27\\DLLs
    """
    try:
        ctypes.CDLL('C:/Python27/Lib/site-packages/numpy/core/'+name)
    except WindowsError:
        ctypes.CDLL(name)

if INSTALL:
    # load numpy math and fortran libraries (but do not import numpy)
    load_lib('libmmd.dll')
    load_lib('libifcoremd.dll')
    load_lib('libiomp5md.dll')
    load_lib('svml_dispmd.dll')

    # install handler
    routine = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_uint)(handler)

    ctypes.windll.kernel32.SetConsoleCtrlHandler(routine, 1)
    
    print "scipy fixed."