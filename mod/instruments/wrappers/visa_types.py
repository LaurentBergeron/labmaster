"""
ctypes wrapper for the typedefs in IviVisaType.h.
"""

__author__ =  "Laurent Bergeron <laurent.bergeron4@gmail.com>"


from ctypes import *

ViUInt64 = c_ulonglong
ViInt64 = c_longlong
ViPUInt64 = POINTER(ViUInt64)
ViAUInt64 = POINTER(ViUInt64)
ViPInt64 = POINTER(ViInt64)
ViAInt64 = POINTER(ViInt64)

ViUInt32 = c_ulong
ViInt32 = c_long
ViPUInt32 = POINTER(ViUInt32)
ViAUInt32 = POINTER(ViUInt32)
ViPInt32 = POINTER(ViInt32)
ViAInt32 = POINTER(ViInt32)

ViUInt16 = c_ushort
ViInt16 = c_short
ViPUInt16 = POINTER(ViUInt16)
ViAUInt16 = POINTER(ViUInt16)
ViPInt16 = POINTER(ViInt16)
ViAInt16 = POINTER(ViInt16)

ViUInt8 = c_ubyte
ViInt8 = c_byte
ViPUInt8 = POINTER(ViUInt8)
ViAUInt8 = POINTER(ViUInt8)
ViPInt8 = POINTER(ViInt8)
ViAInt8 = POINTER(ViInt8)

ViChar = c_char
ViPChar = POINTER(ViChar)
ViAChar = POINTER(ViChar)

ViByte = c_byte
ViPByte = POINTER(ViByte)
ViAByte = POINTER(ViByte)

ViAddr = c_void_p
ViPAddr = POINTER(ViAddr)
ViAAddr = POINTER(ViAddr)

ViReal32 = c_float
ViPReal32 = POINTER(ViReal32)
ViAReal32 = POINTER(ViReal32)

ViReal64 = c_double
ViPReal64 = POINTER(ViReal64)
ViAReal64 = POINTER(ViReal64)

ViBuf = ViPByte
ViPBuf = ViPByte
ViABuf = POINTER(ViPByte)

ViString = ViPChar
ViPString = ViPChar
ViAString = POINTER(ViPChar)

ViRsrc = ViString
ViPRsrc = ViString
ViARsrc = POINTER(ViString)

ViBoolean = ViUInt16
ViPBoolean = POINTER(ViBoolean)
ViABoolean = POINTER(ViBoolean)

ViStatus = ViInt32
ViPStatus = POINTER(ViStatus)
ViAStatus = POINTER(ViStatus)

ViVersion = ViInt32
ViPVersion = POINTER(ViVersion)
ViAVersion = POINTER(ViVersion)

ViObject = ViUInt32
ViPObject = POINTER(ViObject)
ViAObject = POINTER(ViObject)

ViSession = ViObject
ViPSession = ViSession
ViASession = ViSession

ViAttr = ViUInt32

ViConstString = POINTER(ViChar)

VI_SUCCESS = c_ulong(0)
VI_NULL = c_int(0)
VI_TRUE = c_int(1)
VI_FALSE = c_int(0)







