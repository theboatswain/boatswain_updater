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

import functools
import os
import tempfile
from typing import List

import requests
from PyQt5.QtCore import QObject, pyqtSignal, QUrl
from PyQt5.QtWidgets import QApplication

from boatswain_updater.models.release import Release
from boatswain_updater.services import setting_service
from boatswain_updater.services.worker_service import Worker, threadpool
from boatswain_updater.utils import release_utils
from boatswain_updater.utils.constants import SKIP_RELEASE


class Feed(QObject):
    url: QUrl = None
    all_releases: List[Release] = []
    last_release: Release = None
    download_file: str = None
    n_redirects: int = 0
    __feed_ready: bool = False
    ready = pyqtSignal()
    load_error = pyqtSignal(str)
    download_finished = pyqtSignal()
    download_error = pyqtSignal(str)
    download_progress = pyqtSignal(int, int)

    def __init__(self, github_user_repo):
        super().__init__()
        self.__feed_ready = False
        self.url = 'https://api.github.com/repos/%s/releases' % github_user_repo

    def isReady(self):
        return self.__feed_ready

    def getUpdates(self, min_release: Release) -> List[Release]:
        updates = []
        for rls in self.all_releases:
            if min_release.lessThan(rls):
                updates.append(rls)
        return updates

    def getReleases(self):
        return self.all_releases

    def load(self):
        worker = Worker(self.makeLoadRequest, self.url)
        worker.signals.result.connect(self.onLoadFinished)
        worker.signals.error.connect(self.handleDownloadError)
        threadpool.start(worker)

    def getLatestRelease(self):
        release = Release(QApplication.applicationVersion())
        _updates = self.getUpdates(release)
        if len(_updates) > 0:
            last_release = _updates[0]
            skip_release = setting_service.getSettingsValue(SKIP_RELEASE) == last_release.getVersion()
            if not skip_release:
                return last_release
        return None

    def onLoadFinished(self, releases):
        self.all_releases = releases
        self.all_releases.sort(key=functools.cmp_to_key(release_utils.compareRelease))
        self.__feed_ready = True
        self.ready.emit()

    def makeLoadRequest(self, url, progress_callback=None):
        releases = requests.get(url)
        result = []
        for rls in releases.json():
            new_release = Release.fromJson(rls)
            if new_release.download_size:
                result.append(new_release)
        return result

    def getDownloadFile(self) -> str:
        return self.download_file

    def downloadRelease(self, rls: Release):
        worker = Worker(self.makeDownloadRequest, rls.getDownloadUrl())
        worker.signals.result.connect(self.handleDownloadFinished)
        worker.signals.progress.connect(self.handleDownloadProgress)
        worker.signals.error.connect(self.handleDownloadError)
        self.last_release = rls
        threadpool.start(worker)

    def makeDownloadRequest(self, url: str, progress_callback):
        file_name = QUrl(self.last_release.download_url).fileName()
        fd, download_file = tempfile.mkstemp(suffix=file_name)
        byte_received = 0
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(download_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                    byte_received += 8192
                    progress_callback.emit(byte_received)
        os.close(fd)
        return download_file

    def handleDownloadProgress(self, bytes_received):
        self.download_progress.emit(bytes_received, self.last_release.download_size)

    def handleDownloadFinished(self, download_file):
        if not os.path.isfile(download_file):
            self.download_error.emit(self.tr("No data received from server"))
            return
        self.download_file = download_file
        self.download_finished.emit()

    def handleDownloadError(self, exception: Exception):
        self.download_error.emit(str(exception))
