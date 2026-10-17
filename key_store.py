"""Windows DPAPI protected local signing key; never publish .dpapi files."""
import ctypes
from ctypes import wintypes
class Blob(ctypes.Structure):_fields_=[('cbData',wintypes.DWORD),('pbData',ctypes.POINTER(ctypes.c_ubyte))]
def protect(data,decrypt=False):
    buf=(ctypes.c_ubyte*len(data)).from_buffer_copy(data);src=Blob(len(data),buf);dst=Blob()
    lib=ctypes.WinDLL('crypt32',use_last_error=True);kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    if decrypt:ok=lib.CryptUnprotectData(ctypes.byref(src),None,None,None,None,1,ctypes.byref(dst))
    else:ok=lib.CryptProtectData(ctypes.byref(src),'Camper Level release key',None,None,None,1,ctypes.byref(dst))
    if not ok:raise ctypes.WinError(ctypes.get_last_error())
    try:return ctypes.string_at(dst.pbData,dst.cbData)
    finally:kernel.LocalFree(dst.pbData)
