"""Record runtime, OS and hardware without additional packages."""
import ctypes
import platform
import subprocess
import sys

print('Python:', sys.version.replace('\n', ' '))
print('OS:', platform.platform())
if sys.platform == 'win32':
    import winreg
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as key:
        print('CPU:', winreg.QueryValueEx(key, 'ProcessorNameString')[0].strip())
    class Memory(ctypes.Structure):
        _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong)] + [
            (name, ctypes.c_ulonglong) for name in ('total', 'available', 'page_total', 'page_available',
                                                  'virtual_total', 'virtual_available', 'extended')]
    memory = Memory()
    memory.length = ctypes.sizeof(memory)
    if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)):
        print(f'Physical RAM: {memory.total} bytes ({memory.total / 2**30:.2f} GiB)')
