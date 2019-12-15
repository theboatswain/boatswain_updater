#  This file is part of Boatswain.
#
#      Boatswain is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      Boatswain is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with Boatswain.  If not, see <https://www.gnu.org/licenses/>.
#
#

import errno
import os
from shlex import quote
import subprocess
import sys

from boatswain_updater.utils import sys_utils

SEE_MASK_NOCLOSEPROCESS = 0x00000040
SEE_MASK_NO_CONSOLE = 0x00008000


def locationIsWritable(path):
    if os.path.isdir(path):
        return isDirWritable(path)
    if os.path.isfile(path):
        return isFileWritable(path)
    return False


def isFileWritable(file):
    return isDirWritable(os.path.dirname(file))


def isDirWritable(directory):
    if sys_utils.isWin():
        return os.access(directory, os.W_OK)

    try:
        filename = os.path.join(directory, "tmp_file_tester.tmp")
        with open(filename, "w") as f:
            f.write('')
        os.remove(filename)
        return True
    except IOError:
        return False


def quoteShell(args):
    return " ".join(quote(arg) for arg in args)


def quoteAppleScript(string):
    char_map = {
        "\n": "\\n",
        "\r": "\\r",
        "\t": "\\t",
        "\"": "\\\"",
        "\\": "\\\\",
    }
    return '"%s"' % "".join(char_map.get(char, char) for char in string)


def runAsAdmin(argv):
    commands = []
    if sys_utils.isMac():
        commands.append(["osascript", "-e",
                         "do shell script " + quoteAppleScript(quoteShell(argv)) + " with administrator privileges"])
    elif sys_utils.isLinux():
        if os.environ.get("DISPLAY"):
            commands.append(["pkexec"] + argv)
            commands.append(["gksudo"] + argv)
            commands.append(["kdesudo"] + argv)
        commands.append(["sudo"] + argv)
    elif sys_utils.isWin():
        # For window machine, we expect to have the script to ask for permission inside the .bat file already
        pass
    else:
        raise NotImplementedError('Unable to recognise platform %s' % sys.platform)
    for command in commands:
        try:
            return subprocess.call(command, stdin=None, stdout=None, stderr=None, shell=False)
        except OSError as e:
            if e.errno != errno.ENOENT or command[0] == "sudo":
                raise e


# def runWindowsCommandAsAdmin(executor, argv, show_console=True):
#     """
#     Temporary disable cuz ctypes library currently not work with pyqtdeploy
#     Execute an Window CMD as Admin
#     inspired from https://github.com/barneygale/elevate/blob/master/elevate/windows.py
#     :rtype: exit status
#     """
#     import ctypes
#     from ctypes import POINTER, c_ulong, c_char_p, c_int, c_void_p
#     from ctypes.wintypes import HANDLE, BOOL, DWORD, HWND, HINSTANCE, HKEY
#     from ctypes import windll
#
#     # Type definitions
#
#     # PHANDLE = ctypes.POINTER(HANDLE)
#     # PDWORD = ctypes.POINTER(DWORD)
#
#     class ShellExecuteInfo(ctypes.Structure):
#         _fields_ = [
#             ('cbSize', DWORD),
#             ('fMask', c_ulong),
#             ('hwnd', HWND),
#             ('lpVerb', c_char_p),
#             ('lpFile', c_char_p),
#             ('lpParameters', c_char_p),
#             ('lpDirectory', c_char_p),
#             ('nShow', c_int),
#             ('hInstApp', HINSTANCE),
#             ('lpIDList', c_void_p),
#             ('lpClass', c_char_p),
#             ('hKeyClass', HKEY),
#             ('dwHotKey', DWORD),
#             ('hIcon', HANDLE),
#             ('hProcess', HANDLE)]
#
#         def __init__(self, **kw):
#             super(ShellExecuteInfo, self).__init__()
#             self.cbSize = ctypes.sizeof(self)
#             for field_name, field_value in kw.items():
#                 setattr(self, field_name, field_value)
#
#     p_shell_execute_info = POINTER(ShellExecuteInfo)
#
#     # Function definitions
#
#     shell_execute_ex = windll.shell32.ShellExecuteExA
#     shell_execute_ex.argtypes = (p_shell_execute_info,)
#     shell_execute_ex.restype = BOOL
#
#     wait_for_single_object = windll.kernel32.WaitForSingleObject
#     wait_for_single_object.argtypes = (HANDLE, DWORD)
#     wait_for_single_object.restype = DWORD
#
#     close_handle = windll.kernel32.CloseHandle
#     close_handle.argtypes = (HANDLE,)
#     close_handle.restype = BOOL
#
#     params = ShellExecuteInfo(
#         fMask=SEE_MASK_NOCLOSEPROCESS | SEE_MASK_NO_CONSOLE,
#         hwnd=None,
#         lpVerb=b'runas',
#         lpFile=executor.encode('cp1252'),
#         lpParameters=subprocess.list2cmdline(argv).encode('cp1252'),
#         nShow=int(show_console))
#
#     if not shell_execute_ex(ctypes.byref(params)):
#         raise ctypes.WinError()
#
#     handle = params.hProcess
#     ret = DWORD()
#     wait_for_single_object(handle, -1)
#
#     if windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(ret)) == 0:
#         raise ctypes.WinError()
#
#     close_handle(handle)
#     return ret.value
