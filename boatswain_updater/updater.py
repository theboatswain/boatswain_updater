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
from typing import List

from PyQt5.QtCore import pyqtSignal, QCoreApplication, QSize, QObject
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from boatswain_updater.exceptions.installation import InstallationFailedException

from boatswain_updater.models.feed import Feed
from boatswain_updater.models.release import Release
from boatswain_updater.services import setting_service, core
from boatswain_updater.updater_ui import UpdaterUi
from boatswain_updater.utils import pyqt_utils, release_utils
from boatswain_updater.utils.constants import SKIP_RELEASE
from boatswain_updater.utils.pyqt_utils import rt

logger = logging.getLogger(__name__)


class Updater(QObject):
    installed = pyqtSignal()
    _latest_release: Release = Release()
    _releases: List[Release] = []
    _updates: List[Release] = []
    _silent = False
    _auto_install = False

    def __init__(self, parent, feed: Feed) -> None:
        super().__init__(parent)
        self._parent = parent
        self.dialog = QDialog(parent)
        self.ui = UpdaterUi(self.dialog)
        self.dialog.ui = self.ui
        self.feed = feed

    def _showDialog(self):
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.dialog.width()) / 2
        y = (screen_geometry.height() - self.dialog.height()) / 2.8
        self.dialog.move(x, y)
        self.dialog.show()

    def checkForUpdate(self, silent=False, auto_install=False):
        """
        Check for new update, if yes, then show the update confirmation window
        :param silent: whether or not we show the loading window
        """
        self._silent = silent
        self._auto_install = auto_install
        if not silent:
            self._showDialog()
        self.setupLoadingUi()
        self.feed.ready.connect(self.handleFeedReady)
        logger.info("Starting to fetch update info...")
        self.feed.load()

    def handleFeedReady(self):
        release = Release(QApplication.applicationVersion())
        self._updates = self.feed.getUpdates(release)
        if len(self._updates) > 0:
            self._latest_release = self._updates[0]

        if len(self._updates) == 0:
            self.setupNoUpdatesUi()
            logger.info("No release found.")
            return

        latest_version = self._latest_release.getVersion()
        skip_release = setting_service.getSettingsValue(SKIP_RELEASE) == latest_version
        if latest_version:
            self.setupUpdateUi()
            if self._silent and not skip_release and not self._auto_install:
                self._showDialog()
            elif not skip_release and self._auto_install:
                self.onButtonInstall()

    def setIcon(self, pixmap: QPixmap):
        self.ui.label_icon.setPixmap(pixmap)
        self.ui.label_icon.setHidden(False)

    def setupNoUpdatesUi(self):
        if self._silent:
            return
        self.resetUi()
        self.dialog.setMinimumSize(QSize(rt(500), rt(120)))
        self.dialog.resize(rt(500), rt(120))
        show_widgets = [self.ui.label_info_no_updates, self.ui.button_confirm, self.ui.label_headline_no_updates,
                        self.ui.main_container, self.ui.label_icon]
        for widget in show_widgets:
            widget.show()
        self.ui.button_confirm.setFocus()
        self.ui.label_headline_no_updates.setText(self.replaceAppVars(self.ui.label_headline_no_updates.text()))
        self.ui.button_confirm.clicked.connect(self.dialog.accept)
        self.dialog.adjustSize()

    def startDownload(self):
        logger.info("Starting to download release %s..." % self._latest_release.version)
        self.feed.downloadRelease(self._latest_release)
        self.disableButtons(True)

    def setupUpdateUi(self):
        self.resetUi()
        self.ui.label_icon.show()
        self.dialog.setMinimumSize(QSize(rt(346 * 2), rt(346)))
        self.dialog.resize(rt(346 * 2), rt(346))
        show_widgets = [self.ui.main_container, self.ui.label_changelog, self.ui.button_skip,
                        self.ui.button_cancel, self.ui.button_install, self.ui.label_info, self.ui.release_notes,
                        self.ui.label_headline]
        for widget in show_widgets:
            widget.show()
        labels = [self.ui.label_headline, self.ui.label_info]
        for label in labels:
            label.setText(self.replaceAppVars(label.text()))
        self.ui.label_changelog.setHtml(release_utils.generateChangelogDocument(self._updates))
        self.ui.label_changelog.setOpenExternalLinks(True)
        self.ui.label_changelog.setReadOnly(True)

        self.ui.button_confirm.clicked.connect(self.dialog.accept)
        self.ui.button_skip.clicked.connect(self.skipRelease)
        self.ui.button_cancel.clicked.connect(self.dialog.reject)

        self.ui.button_install.setFocus()
        self.ui.button_install.clicked.connect(self.onButtonInstall)
        self.dialog.adjustSize()

    def onButtonInstall(self):
        self.setupDownloadingUi()
        self.feed.download_finished.connect(self.handleDownloadFinished)
        self.feed.download_error.connect(self.handleDownloadError)
        self.feed.download_progress.connect(self.updateProgressBar)
        self.startDownload()

    def skipRelease(self):
        setting_service.setSettingsValue(SKIP_RELEASE, self._latest_release.getVersion())
        self.dialog.reject()

    def handleDownloadFinished(self):
        self.setupInstallingUi()

    def handleDownloadError(self, message):
        message_box = QMessageBox(self.dialog)
        message_box.setIcon(QMessageBox.Warning)
        message_box.setText(self.tr("There was an error while downloading the update."))
        message_box.setInformativeText(message)
        message_box.show()
        self.dialog.reject()

    def disableButtons(self, disable: bool):
        buttons = [self.ui.button_cancel, self.ui.button_confirm, self.ui.button_install, self.ui.button_skip]

        for button in buttons:
            button.setDisabled(disable)

    def setupLoadingUi(self):
        if self._silent:
            return
        self.resetUi()
        self.dialog.setMinimumSize(QSize(rt(500), rt(120)))
        self.dialog.resize(rt(500), rt(120))
        self.ui.main_container.show()
        self.ui.label_headline_loading.show()
        self.ui.progress_bar.show()
        self.ui.progress_bar.setMaximum(0)
        self.ui.progress_bar.setMinimum(0)
        self.ui.label_icon.show()
        self.dialog.adjustSize()

    def setupDownloadingUi(self):
        self.resetUi()
        self.dialog.setWindowTitle(self.tr("Updating") + " %s…" % QApplication.applicationName())
        self.dialog.setMinimumSize(QSize(rt(500), rt(120)))
        self.dialog.resize(rt(500), rt(120))
        show_widgets = [self.ui.main_container, self.ui.label_icon, self.ui.progress_bar, self.ui.label_downloading,
                        self.ui.button_cancel_loading, self.ui.progress_label]
        for widget in show_widgets:
            widget.show()

        self.ui.button_cancel_loading.setEnabled(True)
        self.ui.button_cancel_loading.setFocus()
        self.ui.button_cancel_loading.clicked.connect(self.dialog.reject)
        self.dialog.adjustSize()

    def setupInstallingUi(self):
        self.resetUi()
        self.dialog.setWindowTitle(self.tr("Updating") + " %s…" % QApplication.applicationName())
        self.dialog.setMinimumSize(QSize(rt(500), rt(120)))
        self.dialog.resize(rt(500), rt(120))
        show_widgets = [self.ui.main_container, self.ui.label_icon,
                        self.ui.button_install_and_relaunch, self.ui.label_install_and_relaunch]
        for widget in show_widgets:
            widget.show()

        self.updateProgressBar(self._latest_release.download_size, self._latest_release.download_size)

        self.ui.button_install_and_relaunch.setEnabled(True)
        self.ui.button_install_and_relaunch.setFocus()
        self.ui.button_install_and_relaunch.clicked.connect(self.installUpdate)
        self.dialog.adjustSize()
        if self._auto_install:
            self.installUpdate()

    def installUpdate(self):
        logger.info("Starting to install update...")
        file = self.feed.getDownloadFile()
        try:
            core.installUpdate(file)
            self.installed.emit()
            self.dialog.accept()
        except InstallationFailedException:
            self.setupInstallFailedUi()

    def setupInstallFailedUi(self):
        self.resetUi()
        self.dialog.setMinimumSize(QSize(rt(500), rt(120)))
        self.dialog.resize(rt(500), rt(120))
        show_widgets = [self.ui.main_container, self.ui.label_icon, self.ui.label_info_unable_update,
                        self.ui.label_headline_unable_update]
        for widget in show_widgets:
            widget.show()
        self.ui.label_info_unable_update.setText(self.replaceAppVars(self.ui.label_info_unable_update.text()))
        self.dialog.adjustSize()

    def resetUi(self):
        hidden_widgets = [self.ui.main_container, self.ui.label_icon, self.ui.label_headline_loading,
                          self.ui.label_info, self.ui.release_notes, self.ui.button_install_and_relaunch,
                          self.ui.label_headline, self.ui.label_downloading, self.ui.label_install_and_relaunch,
                          self.ui.label_info_no_updates, self.ui.label_headline_no_updates,
                          self.ui.label_headline_unable_update, self.ui.label_info_unable_update,
                          self.ui.label_changelog, self.ui.progress_bar, self.ui.button_skip,
                          self.ui.button_cancel, self.ui.button_cancel_loading, self.ui.button_confirm,
                          self.ui.button_install, self.ui.progress_label]

        for widget in hidden_widgets:
            widget.hide()
            pyqt_utils.disconnectAllSignals(widget)
        self.ui.progress_bar.reset()
        self.dialog.adjustSize()

    def replaceAppVars(self, string):
        new_str = string.replace("$APP_NAME$", QCoreApplication.applicationName())
        new_str = new_str.replace("$CURRENT_VERSION$", QCoreApplication.applicationVersion())
        new_str = new_str.replace("$UPDATE_VERSION$", self._latest_release.getVersion())
        new_str = new_str.replace("$UPDATE_LINK$", self._latest_release.getDownloadUrl())
        return new_str

    def updateProgressBar(self, bytes_received, bytes_total):
        self.ui.progress_bar.show()
        self.ui.progress_bar.setMaximum(bytes_total / 1024)
        self.ui.progress_bar.setValue(bytes_received / 1024)
        self.ui.progress_label.show()
        mb_received = bytes_received / 1024 / 1024
        mb_total = bytes_total / 1024 / 1024
        self.ui.progress_label.setText("%.2f MB of %.2f MB" % (mb_received, mb_total))
