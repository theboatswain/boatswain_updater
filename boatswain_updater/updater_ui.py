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

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt

from boatswain_updater.utils.custom_ui import BQSizePolicy
from boatswain_updater.utils.pyqt_utils import rt, applyFontRatio


class UpdaterUi:
    template = 'UpdateUi'

    def __init__(self, dialog) -> None:
        dialog.setMinimumSize(QSize(rt(400), rt(120)))
        dialog.setModal(True)
        self.main_layout = QtWidgets.QVBoxLayout(dialog)
        self.main_layout.setContentsMargins(rt(20), rt(11), rt(11), rt(11))
        self.main_layout.setSpacing(0)
        self.main_container = QtWidgets.QWidget(dialog)
        self.grid_layout = QtWidgets.QGridLayout(self.main_container)
        self.grid_layout.setContentsMargins(0, rt(6), 0, 0)
        self.grid_layout.setHorizontalSpacing(24)
        self.grid_layout.setVerticalSpacing(6)
        self.label_headline = QtWidgets.QLabel(self.main_container)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(applyFontRatio(105))
        self.label_headline.setFont(font)
        self.grid_layout.addWidget(self.label_headline, 0, 2, 1, 1)

        self.label_headline_loading = QtWidgets.QLabel(self.main_container)
        self.grid_layout.addWidget(self.label_headline_loading, 0, 2, 1, 1)

        self.label_downloading = QtWidgets.QLabel(self.main_container)
        self.label_downloading.setFont(font)
        self.grid_layout.addWidget(self.label_downloading, 0, 2, 1, 1)

        self.label_install_and_relaunch = QtWidgets.QLabel(self.main_container)
        self.label_install_and_relaunch.setFont(font)
        self.grid_layout.addWidget(self.label_install_and_relaunch, 0, 2, 1, 1)

        self.progress_bar = QtWidgets.QProgressBar(self.main_container)
        self.grid_layout.addWidget(self.progress_bar, 1, 2, 2, 1)

        self.label_headline_no_updates = QtWidgets.QLabel(self.main_container)
        self.grid_layout.addWidget(self.label_headline_no_updates, 0, 2, 1, 1)

        self.label_info_no_updates = QtWidgets.QLabel(self.main_container)
        self.grid_layout.addWidget(self.label_info_no_updates, 1, 2, 2, 1)

        self.label_headline_unable_update = QtWidgets.QLabel(self.main_container)
        self.grid_layout.addWidget(self.label_headline_unable_update, 0, 2, 1, 1)

        self.label_info_unable_update = QtWidgets.QLabel(self.main_container)
        self.label_info_unable_update.setTextFormat(Qt.RichText)
        self.label_info_unable_update.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.label_info_unable_update.setOpenExternalLinks(True)
        self.grid_layout.addWidget(self.label_info_unable_update, 1, 2, 2, 1)

        self.label_icon = QtWidgets.QLabel(self.main_container)
        self.label_icon.setSizePolicy(BQSizePolicy(width=QtWidgets.QSizePolicy.Minimum))
        self.grid_layout.addWidget(self.label_icon, 0, 0, 3, 1)
        self.label_info = QtWidgets.QLabel(self.main_container)
        self.label_info.setSizePolicy(BQSizePolicy(width=QtWidgets.QSizePolicy.Expanding))
        self.label_info.setWordWrap(True)
        self.grid_layout.addWidget(self.label_info, 1, 2, 2, 1)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.release_notes = QtWidgets.QLabel(self.main_container)
        self.release_notes.setFont(font)
        self.release_notes.setSizePolicy(BQSizePolicy(width=QtWidgets.QSizePolicy.Expanding))
        self.grid_layout.addWidget(self.release_notes, 2, 2, 1, 1)
        self.main_layout.addWidget(self.main_container)
        self.label_changelog = QtWidgets.QTextBrowser(self.main_container)
        self.label_changelog.setSizePolicy(BQSizePolicy(height=QtWidgets.QSizePolicy.Expanding))
        self.grid_layout.addWidget(self.label_changelog, 3, 2, 1, 1)

        self.button_container = QtWidgets.QWidget(dialog)
        self.button_container.setSizePolicy(BQSizePolicy(height=QtWidgets.QSizePolicy.Minimum))
        self.horizontal_layout = QtWidgets.QHBoxLayout(self.button_container)
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout.setSpacing(rt(12))
        self.button_skip = QtWidgets.QPushButton(self.button_container)
        self.horizontal_layout.addWidget(self.button_skip)
        self.progress_label = QtWidgets.QLabel(self.button_container)
        self.horizontal_layout.addWidget(self.progress_label)
        spacer_item1 = QtWidgets.QSpacerItem(rt(40), rt(20),
                                             QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontal_layout.addItem(spacer_item1)
        self.button_cancel = QtWidgets.QPushButton(self.button_container)
        self.horizontal_layout.addWidget(self.button_cancel)
        self.button_install = QtWidgets.QPushButton(self.button_container)
        self.horizontal_layout.addWidget(self.button_install)
        self.button_install_and_relaunch = QtWidgets.QPushButton(self.button_container)
        self.horizontal_layout.addWidget(self.button_install_and_relaunch)
        self.button_confirm = QtWidgets.QPushButton(self.button_container)
        self.horizontal_layout.addWidget(self.button_confirm)
        self.button_cancel_loading = QtWidgets.QPushButton(self.button_container)
        self.horizontal_layout.addWidget(self.button_cancel_loading)
        self.grid_layout.addWidget(self.button_container, 4, 2, 1, 1)

        self.retranslateUi()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.label_headline_loading.setText(_translate(self.template, "Loading update information…"))
        self.label_headline.setText(_translate(self.template, "A new version of $APP_NAME$ is available!"))
        self.label_info.setText(_translate(self.template, "$APP_NAME$ $UPDATE_VERSION$ is now available "
                                                          "-- you have $CURRENT_VERSION$. "
                                                          "Would you like to update now?\n"))
        self.release_notes.setText(_translate(self.template, "Release Notes:"))
        self.label_info_no_updates.setText(_translate(self.template, "There are currently no updates available."))
        self.label_downloading.setText(_translate(self.template, "Downloading update…"))
        self.label_headline_no_updates.setText(_translate(self.template, "You are using $APP_NAME$ $CURRENT_VERSION$."))
        self.button_cancel_loading.setText(_translate(self.template, "Cancel"))
        self.button_install.setText(_translate(self.template, "Install Update"))
        self.button_install_and_relaunch.setText(_translate(self.template, "Install and Relaunch"))
        self.label_install_and_relaunch.setText(_translate(self.template, "Ready to Install"))
        self.button_confirm.setText(_translate(self.template, "OK"))
        self.button_cancel.setText(_translate(self.template, "Remind Me Later"))
        self.button_skip.setText(_translate(self.template, "Skip This Version"))
        self.label_headline_unable_update.setText(_translate(self.template, 'Installation failed'))
        self.label_info_unable_update.setText(_translate(self.template,
                                                         'Please download and install the update manually at '
                                                         '<a href="$UPDATE_LINK$">here</>!'))
