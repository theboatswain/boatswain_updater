#  This file is part of Boatswain.
#
#      Boatswain<https://github.com/theboatswain> is free software: you can redistribute it and/or modify
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

CREATE_NO_WINDOW = 0x08000000


def locationIsWritable(path):
    if os.path.isdir(path):
        return isDirWritable(path)
    if os.path.isfile(path):
        return isFileWritable(path)
    return False


def isFileWritable(file):
    return isDirWritable(os.path.dirname(file))


def isDirWritable(directory):
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
        # For MacOS, we will use osascript for asking privileges permission
        commands.append(["osascript", "-e",
                         "do shell script " + quoteAppleScript(quoteShell(argv)) + " with administrator privileges"])
    elif sys_utils.isLinux():
        # For Linux, there are many different distro, so, we will try each of them
        # If all are failed, the fall back to sudo
        if os.environ.get("DISPLAY"):
            commands.append(["pkexec"] + argv)
            commands.append(["gksudo"] + argv)
            commands.append(["kdesudo"] + argv)
        commands.append(["sudo"] + argv)
    elif sys_utils.isWin():
        # For window machine, we expect to have the script to ask for permission inside the .bat file already
        commands.append(argv)
    else:
        raise NotImplementedError('Unable to recognise platform %s' % sys.platform)
    for command in commands:
        try:
            if sys_utils.isWin():
                return subprocess.call(command, stdin=None, stdout=None, stderr=None, shell=False,
                                       creationflags=CREATE_NO_WINDOW)
            else:
                return subprocess.call(command, stdin=None, stdout=None, stderr=None, shell=False)
        except OSError as e:
            if e.errno != errno.ENOENT or command[0] == "sudo":
                raise e
