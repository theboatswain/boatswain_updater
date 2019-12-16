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
import os
import shutil
import tempfile
import zipfile

from boatswain_updater import resources_utils
from boatswain_updater.exceptions.installation import InstallationFailedException, ReleaseFolderStructureIncorrect
from boatswain_updater.models.app_to_update import AppToUpdate
from boatswain_updater.utils import sys_utils, pyqt_utils, permission_utils

logger = logging.getLogger(__name__)


def installUpdate(update_file: str):
    """
    Install the update from the given update file as Zip
    """

    logger.info('Starting update')
    logger.info('Extracting update...')
    extract_to = tempfile.mkdtemp(suffix='', prefix='boatswain_x_zip_', dir=None)
    zip_file = zipfile.ZipFile(update_file, 'r')
    for file in zip_file.infolist():
        zip_file.extract(file, extract_to)
        os.chmod(os.path.join(extract_to, file.filename), 0o755)  # make executable
    zip_file.close()
    original_app = AppToUpdate()

    update_app_path = os.path.join(extract_to, os.path.basename(original_app.folder))

    logger.info('Update data path: ' + update_app_path)
    if not verifyUpdateStructure(update_app_path, original_app):
        logger.error('Update app: %s and original app: %s are not the same structure'
                     % (update_app_path, original_app.folder))
        raise ReleaseFolderStructureIncorrect()

    if original_app.hasPermission():
        copyFolderNoRoot(update_app_path, original_app)
    else:
        copyFolderWithRoot(update_app_path, original_app)


def verifyUpdateStructure(update_app_path: str, original_app: AppToUpdate):
    relative_exe_location = original_app.getRelativeExecutable()
    return os.path.isfile(os.path.join(update_app_path, relative_exe_location))


def copyFolderNoRoot(update_app_path: str, original_app: AppToUpdate):
    """
    If we have permission to write in the destination, no need to do anything too complex
    Move the extracted files into the destination folder
    """
    logger.info("Starting to move files from %s -> %s" % (update_app_path, original_app.folder))
    try:
        shutil.rmtree(original_app.folder)
        files = os.listdir(update_app_path)
        for f in files:
            shutil.move(os.path.join(update_app_path, f), os.path.join(original_app.folder, f))
    except OSError as e:
        logger.error("Exception occurred, rolling back to the earlier backed up version.\n Exception: %s", e)
        raise InstallationFailedException()


def copyFolderWithRoot(update_app_path: str, original_app: AppToUpdate):
    """
    In case we don't have permission, we will start an external script and ask for an executing permission
    """
    if sys_utils.isMac() or sys_utils.isLinux():
        fd, installer = tempfile.mkstemp(suffix='.sh')
        pyqt_utils.defrostAndSaveInto(resources_utils.getResource('installers/posix/installer.sh'), installer)
    else:
        fd, installer = tempfile.mkstemp(suffix='.bat')
        pyqt_utils.defrostAndSaveInto(resources_utils.getResource('installers/windows/installer.bat'), installer)

    os.chmod(installer, 0o755)  # make executable
    command = [installer, update_app_path, original_app.folder]

    logger.info("Calling command %s" % ' '.join(command))
    try:
        res_code = permission_utils.runAsAdmin(command)
        if res_code == 0:
            return
        else:
            logger.error("Exception occurred, exit code: %d" % res_code)
    except OSError as e:
        logger.error("Exception occurred, rolling back to the earlier backed up version.\n Exception: %s", e)
    finally:
        os.close(fd)
    raise InstallationFailedException()
