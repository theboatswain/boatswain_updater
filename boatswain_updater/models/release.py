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

import semantic_version as semantic_version
from boatswain_updater.utils import sys_utils


class Release:
    changelog = ""
    download_url = ""
    download_size = 0

    def __init__(self, version: str = '') -> None:
        super().__init__()
        self.version = version

    @staticmethod
    def fromJson(object_json):

        version = object_json['tag_name']
        release = Release(version)
        release.changelog = object_json['body']

        assets = object_json["assets"]

        if sys_utils.isMac():
            plf = 'macOS'
        elif sys_utils.isWin():
            plf = 'windows'
        else:
            plf = 'unix'

        for asset in assets:
            download_info = asset
            if plf in download_info['name']:
                release.download_url = download_info["browser_download_url"]
                release.download_size = download_info["size"]
        return release

    def getVersion(self):
        return self.version

    def getChangelog(self):
        return self.changelog

    def lessThan(self, release):
        original = semantic_version.Version(self.version)
        new_version = semantic_version.Version(release.version)
        return original < new_version

    def equals(self, release):
        return self.version == release.version

    def lessOrEquals(self, release):
        return self.lessThan(release) or self.equals(release)

    def getDownloadUrl(self):
        return self.download_url
