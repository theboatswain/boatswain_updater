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
import logging
from contextlib import closing

from PyQt5.QtCore import QFile

logger = logging.getLogger(__name__)


def disconnectAllSignals(widget):
    try:
        widget.disconnect()
    except TypeError:
        return


def defrostAndSaveInto(filename, destination):
    logger.info('Attempting to defrost %s and save into %s' % (filename, destination))
    with closing(QFile(filename)) as frozen_file:
        if frozen_file.open(QFile.ReadOnly):
            frozen_data = bytes(frozen_file.readAll())
            with open(destination, 'wb') as the_file:
                the_file.write(frozen_data)
