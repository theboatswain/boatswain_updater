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
import argparse
import json
import logging
import os
import sys
import tempfile

from PyQt5.QtCore import Qt, QCoreApplication, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow

from boatswain_updater.models.app_to_update import AppToUpdate
from boatswain_updater.models.feed import Feed
from boatswain_updater.updater import Updater
from boatswain_updater.utils import pyqt_utils

TMP_DIR = tempfile.gettempdir()
PEM_FILE = os.path.join(TMP_DIR, "cacert.pem")


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()


def deFrostPem():
    """
    When the application is being frozen, all resource files will be encoded into the executable file
    And with the requests library, it required to have the cacert.pem file available and accessible as a normal file
    thus caused the problem of invalid path: :/certifi/cacert.pem
    This function will workaround the problem by reading the content of the pem file and write it into app data folder
    and then relink back the location of REQUESTS_CA_BUNDLE into this file
    """
    if not os.path.isfile(PEM_FILE):
        pyqt_utils.defrostAndSaveInto(':/certifi/cacert.pem', PEM_FILE)

    if os.path.isfile(PEM_FILE):
        os.environ['REQUESTS_CA_BUNDLE'] = PEM_FILE


def getUpdaterConfiguration():
    # The configuration file have to be in the same folder with this app
    # To avoid any sort of attacking by calling it from other untrusted script/application
    original_app = AppToUpdate()
    json_file_conf = os.path.join(original_app.resource_dir, "update.json")
    with open(json_file_conf) as f:
        return json.load(f)


def onApplicationInstalled():
    os.execlp(sys.executable, *sys.argv)


def run():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--log-level', dest='loglevel', type=str, default='FATAL',
                        help='Set log level, DEBUG > INFO > WARN > ERROR > FATAL. Default FATAL')
    parser.add_argument('--checking-mode', dest='checking', type=bool, default=False,
                        help='Only do the checking new version')

    args = parser.parse_args()
    data = getUpdaterConfiguration()
    logging.basicConfig(level=logging.getLevelName(args.loglevel))
    QApplication.setAttribute(Qt.AA_DisableHighDpiScaling)
    QCoreApplication.setApplicationVersion(data['Version'])
    QCoreApplication.setApplicationName(data['Name'])
    deFrostPem()

    feed = Feed(data['Repo'])
    if args.checking:
        releases = feed.makeLoadRequest(feed.url)
        feed.onLoadFinished(releases)
        last_release = feed.getLatestRelease()
        print(json.dumps({
            'has_release': last_release is not None,
            'last_release': {} if not last_release else last_release.__dict__
        }))
        sys.exit(0)

    app = QApplication(sys.argv)

    window = MainWindow()
    pixmap = QIcon(data['Icon']).pixmap(QSize(64, 64))
    update_dialog = Updater(None, feed)
    update_dialog.setIcon(pixmap)
    update_dialog.installed.connect(onApplicationInstalled)
    update_dialog.checkForUpdate(silent=False)
    window.hide()

    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
