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

import os
import sys

from boatswain_updater.utils import permission_utils


class AppToUpdate:

    folder: str
    executable: str

    def __init__(self) -> None:
        self.executable = sys.executable
        (all_last_dir, folder) = os.path.split(self.executable)
        (all_before_last_dir, last_dir) = os.path.split(all_last_dir)
        (all_before_before_last_dir, before_last_dir) = os.path.split(all_before_last_dir)
        if last_dir == 'MacOS' and before_last_dir == 'Contents':
            self.folder = all_before_before_last_dir
        else:
            self.folder = all_last_dir

    def hasPermission(self):
        return permission_utils.locationIsWritable(self.folder)

    def getRelativeExecutable(self):
        return self.executable.replace(self.folder + '/', '')
