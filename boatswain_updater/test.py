import logging
import os
import sys

from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel

from boatswain_updater.utils import pyqt_utils
from boatswain_updater.utils.custom_ui import BQSizePolicy

from boatswain_updater.models.feed import Feed
from boatswain_updater.updater import Updater


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setSizePolicy(BQSizePolicy(h_stretch=1))
        central_widget = QWidget(self)
        central_widget.setSizePolicy(BQSizePolicy(h_stretch=1))
        main_layout = QVBoxLayout(central_widget)
        self.version = QLabel(central_widget)
        self.version.setText("Current version: " + QApplication.applicationVersion())
        main_layout.addWidget(self.version)
        self.setCentralWidget(central_widget)


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


def onApplicationInstalled():
    os.execlp(sys.executable, *sys.argv)


def run():
    QApplication.setAttribute(Qt.AA_DisableHighDpiScaling)
    QCoreApplication.setApplicationVersion("0.0.0")
    QCoreApplication.setApplicationName("BoatswainUpdater")
    app = QApplication(sys.argv)

    deFrostPem()

    window = MainWindow()
    feed = Feed('theboatswain/boatswain_updater')
    update_dialog = Updater(window, feed)
    update_dialog.installed.connect(onApplicationInstalled)
    update_dialog.checkForUpdate(silent=False, auto_install=True)
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    logging.basicConfig(filename='/tmp/boatswain.log', level=logging.DEBUG)
    PEM_FILE = "/tmp/cacert.pem"
    run()
