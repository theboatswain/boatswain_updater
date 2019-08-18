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

from boatswain_updater.models.release import Release


def compare_release(a: Release, b: Release) -> int:
    if b.lessThan(a):
        return -1
    elif b.equals(a):
        return 0
    else:
        return 1


def generateChangelogDocument(updates):
    changelog = ''
    changelog_releases = updates

    for index, release in enumerate(changelog_releases):
        h2_style = 'font-size: medium;'
        if index > 0:
            h2_style += 'margin-top: 1em;'
        changelog += '<h2 style="' + h2_style + '">' + release.getVersion() + '</h2>'
        changelog += '<p>' + release.getChangelog() + '</p>'
    return changelog
