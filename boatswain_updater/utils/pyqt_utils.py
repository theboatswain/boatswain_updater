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
import logging
from contextlib import closing

from PyQt5.QtCore import QFile
from PyQt5.QtGui import QGuiApplication

from boatswain_updater.utils import sys_utils

logger = logging.getLogger(__name__)
ref_dpi = 72 if sys_utils.isMac() else 96
external_pixel_ratio = None
external_font_ratio = None


def disconnectAllSignals(widget):
    try:
        widget.disconnect()
    except TypeError:
        return


def defrostAndSaveInto(filename, destination):
    """
    When the application is being frozen, all resource files will be encoded into the executable file
    This function will extract a file based on it's name and save it into the given destination
    """
    logger.info('Attempting to defrost %s and save into %s' % (filename, destination))
    with closing(QFile(filename)) as frozen_file:
        if frozen_file.open(QFile.ReadOnly):
            frozen_data = bytes(frozen_file.readAll())
            with open(destination, 'wb') as the_file:
                the_file.write(frozen_data)


def getPrimaryScreen():
    return QGuiApplication.primaryScreen()


def rt(pixel):
    if external_pixel_ratio:
        return pixel * external_pixel_ratio
    scale = getPrimaryScreen().logicalDotsPerInch() / ref_dpi
    return round(pixel * scale)


def applyFontRatio(point):
    if external_font_ratio:
        return point * external_font_ratio
    if sys_utils.isMac():
        return point
    return round(point * 0.8)
