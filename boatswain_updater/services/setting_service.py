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

from PyQt5.QtCore import QSettings

from boatswain_updater.utils.constants import UPDATER

settings: QSettings = QSettings()


def getSettingsValue(key, default_value=''):
    return settings.value("%s/%s" % (UPDATER, key), default_value)


def setSettingsValue(key, value):
    settings.setValue("%s/%s" % (UPDATER, key), value)


def removeSetting(key):
    settings.remove("%s/%s" % (UPDATER, key))
